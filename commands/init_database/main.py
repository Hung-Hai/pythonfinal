import secrets
from typing import Any, Dict, List, Optional, Union
from src.models import *
from src.models import MODEL_REGISTRY
from src.utils.db_utils import Base, get_database_url

import csv
import uuid
from sqlalchemy import Boolean, Enum, Table, create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
import logging
import pkgutil
import importlib
import src.models  # the package
import src.models.relationship_models
import bcrypt
ID_MAPPINGS: Dict[str, Dict[int, uuid.UUID]] = {}

for module_info in pkgutil.iter_modules(src.models.__path__):
    importlib.import_module(f"src.models.{module_info.name}")


def _hash_password(raw_password: str) -> str:
    """Hash plain text password using bcrypt."""
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _default_password_hash() -> str:
    """Generate a default random password hash if CSV has no password."""
    random_pass = secrets.token_hex(8)  # random 16-char string
    return _hash_password(random_pass)

def init_database():
    database_url = get_database_url()
    engine = create_engine(database_url, echo=True)
    
    Base.metadata.drop_all(engine)

    # Create all tables in the database
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

logger = logging.getLogger(__name__)

def import_all_data(
    csv_files: Dict[str, str],
    batch_size: int = 1000,
    delimiter: str = ';',
    default_values: Optional[Dict[str, Dict[str, Any]]] = None,
    skip_duplicates: bool = True,
    association_tables: Optional[List[str]] = None
) -> Dict[str, Union[int, str]]:
    """
    Import multiple CSV files into corresponding tables, including association tables.
    
    Args:
        csv_files: Dictionary mapping table names to CSV file paths
        batch_size: Number of records per batch commit
        delimiter: CSV delimiter character
        default_values: Default values for specific tables
        skip_duplicates: Whether to skip duplicate records
        association_tables: List of table names that are association tables
        
    Returns:
        Dictionary with import counts per table {'table_name': rows_imported}
    """
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    inspector = inspect(engine)
    results = {}
    default_values = default_values or {}
    association_tables = association_tables or []

    with SessionLocal() as session:
        for table_name, file_path in csv_files.items():
            try:
                if table_name in association_tables:
                    # Handle association table
                    # table_obj = Table(table_name, Base.metadata, autoload_with=engine)
                    records_imported = _import_association_table(
                        session, table_name, file_path, delimiter, batch_size, skip_duplicates
                    )
                else:
                    # Handle regular table
                    records_imported = _import_regular_table(
                        session, table_name, file_path, delimiter, batch_size, 
                        default_values.get(table_name, {}), skip_duplicates
                )

                results[table_name] = records_imported
                logger.info(f"Imported {records_imported} records into {table_name}")

            except Exception as e:
                logger.error(f"Error importing {table_name}: {str(e)}", exc_info=True)
                results[table_name] = f"Error: {str(e)}"
                session.rollback()

    return results

def _import_regular_table(
    session: Session,
    table_name: str,
    file_path: str,
    delimiter: str,
    batch_size: int,
    table_defaults: Dict[str, Any],
    skip_duplicates: bool
) -> int:
    """Import regular tables with UUID remapping for foreign keys.
       If no 'id' column, generate UUIDs and map row_number → UUID.
       Empty string values are converted to NULL.
    """
    inspector = inspect(session.bind)
    model_class = MODEL_REGISTRY.get(table_name)
    if not model_class:
        raise ValueError(f"Model class not found for table: {table_name}")

    pk_column = inspector.get_pk_constraint(table_name)['constrained_columns'][0]
    records_imported = 0
    records_to_add = []

    # Create mapping dict for this table
    ID_MAPPINGS[table_name] = {}

    # Find foreign key columns
    table_obj = Table(table_name, Base.metadata, autoload_with=session.bind)
    fk_columns = {col.name: next(iter(col.foreign_keys)).column.table.name
                  for col in table_obj.columns if col.foreign_keys}

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=delimiter)

        for i, row in enumerate(csv_reader, start=1):
            record_data = {}

            for col in row:
                if not hasattr(model_class, col):
                    continue

                val = row[col].strip() if row[col] is not None else None

                # Convert empty strings to NULL
                if val == "":
                    record_data[col] = None
                    continue

                if col == "password_hash":
                    if val:
                        record_data[col] = _hash_password(val)
                    else:
                        record_data[col] = _default_password_hash()
                    continue

                col_type = getattr(model_class, col).property.columns[0].type
                if isinstance(col_type, Boolean):
                    if val.lower() == "true":
                        record_data[col] = True
                    elif val.lower() == "false":
                        record_data[col] = False
                    else:
                        record_data[col] = None
                    continue

                if isinstance(col_type, Enum):
                    try:
                        # col_type.enum_class is the Python Enum class (e.g. LicenseType)
                        record_data[col] = col_type.enum_class(val)
                    except ValueError:
                        logger.warning(f"Invalid enum value '{val}' for column '{col}'")
                        record_data[col] = None
                    continue

                if col in fk_columns:
                    # Map foreign key IDs (numeric → UUID)
                    ref_table = fk_columns[col]   # referenced table name
                    try:
                        mapped_val = ID_MAPPINGS[ref_table][int(val)]
                        record_data[col] = mapped_val
                    except (ValueError, KeyError):
                        logger.warning(f"Invalid FK mapping for {ref_table}.{val}")
                        continue
                else:
                    record_data[col] = val

            # If CSV has no id column → generate new UUID
            if "id" not in row or row["id"] == "":
                new_uuid = uuid.uuid4()
                record_data[pk_column] = new_uuid
                ID_MAPPINGS[table_name][i] = new_uuid
            else:
                new_uuid = uuid.uuid4()
                record_data[pk_column] = new_uuid
                ID_MAPPINGS[table_name][int(row["id"])] = new_uuid

            # Apply defaults
            for col, val in table_defaults.items():
                if col not in record_data and hasattr(model_class, col):
                    record_data[col] = val() if callable(val) else val

            records_to_add.append(model_class(**record_data))
            records_imported += 1

            if len(records_to_add) >= batch_size:
                session.bulk_save_objects(records_to_add)
                session.commit()
                records_to_add = []

    if records_to_add:
        session.bulk_save_objects(records_to_add)
        session.commit()

    return records_imported



def _import_association_table(
    session: Session,
    table_name: str,
    file_path: str,
    delimiter: str,
    batch_size: int,
    skip_duplicates: bool
) -> int:
    """Import association tables using UUID mapping with FK validation"""
    records_imported = 0
    inserts = []
    
    COLUMN_TO_TABLE = {
        "book_id": "books",
        "author_id": "author",
        "user_id": "users",
        "role_id": "role",
        "category_id": "category",
    }
    
    # Get the table object from metadata
    table_obj = Table(table_name, Base.metadata, autoload_with=session.bind)
    
    # Get all foreign key columns and their referenced tables
    fk_info = []
    for col in table_obj.columns:
        if col.foreign_keys:
            for fk in col.foreign_keys:
                fk_info.append({
                    'col_name': col.name,
                    'ref_table': fk.column.table.name,
                    'ref_col': fk.column.name
                })

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=delimiter)

        for row in csv_reader:
            new_row = {}
            skip_record = False
            
            for col, val in row.items():
                if val is not None:
                    val = val.strip()

                col_type = table_obj.c[col].type
                if isinstance(col_type, Boolean):
                    if val.lower() == "true":
                        new_row[col] = True
                    elif val.lower() == "false":
                        new_row[col] = False
                    else:
                        new_row[col] = None
                    continue
                
                if col.endswith("_id"):
                    # Get referenced table name (e.g., "author_id" → "author")
                    # ref_table = col[:-3]  # Remove "_id" suffix
                    ref_table = COLUMN_TO_TABLE.get(col)
                    
                    if ref_table in ID_MAPPINGS:
                        try:
                            # Convert numeric ID to mapped UUID
                            mapped_id = ID_MAPPINGS[ref_table][int(val)]
                            new_row[col] = mapped_id
                            
                            # Verify the referenced ID exists in the database
                            ref_table_obj = Table(ref_table, Base.metadata, autoload_with=session.bind)
                            exists = session.execute(
                                ref_table_obj.select().where(ref_table_obj.c.id == mapped_id)
                            ).first()
                            
                            if not exists:
                                logger.warning(f"Referenced ID {mapped_id} not found in table {ref_table}")
                                skip_record = True
                                break
                                
                        except (ValueError, KeyError):
                            logger.warning(f"Invalid ID mapping for {ref_table}.{val}")
                            skip_record = True
                            break
                    else:
                        raise ValueError(f"No ID mapping found for table: {ref_table}")
                else:
                    new_row[col] = val

            # Skip if we couldn't map all foreign keys or if references are invalid
            if skip_record or len(new_row) != len(row):
                continue

            # Skip duplicates if needed
            if skip_duplicates:
                filter_conditions = {col: new_row[col] for col in table_obj.primary_key.columns.keys()}
                exists = session.execute(
                    table_obj.select().where(
                        *[getattr(table_obj.c, col) == val for col, val in filter_conditions.items()]
                    )
                ).first()
                if exists:
                    continue

            inserts.append(new_row)
            records_imported += 1

            if len(inserts) >= batch_size:
                try:
                    session.execute(table_obj.insert(), inserts)
                    session.commit()
                    inserts = []
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error inserting batch: {e}")
                    # Optionally: inspect which record caused the error and skip it
                    # For simplicity, we'll just skip the entire batch here
                    inserts = []
                    continue

    if inserts:
        try:
            session.execute(table_obj.insert(), inserts)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting final batch: {e}")
            records_imported -= len(inserts)

    return records_imported