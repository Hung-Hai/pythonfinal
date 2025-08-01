from src.models.sample_models import *
from src.models.customers_models import *
from src.models.borrow_models import *
from src.models.books_models import *
from src.utils.db_utils import Base, get_database_url

import csv
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


def init_database():
    database_url = get_database_url()
    engine = create_engine(database_url, echo=True)

    # Create all tables in the database
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

logger = logging.getLogger(__name__)

def import_books_from_csv(csv_file_path: str, batch_size: int = 1000) -> None:
    """
    Import books data from CSV file into the database.
    
    Args:
        csv_file_path: Path to the CSV file
        batch_size: Number of records to process before committing (default: 1000)
    """
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as session, open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            books_imported = 0
            batch_count = 0
            books_to_add = []

            for row in csv_reader:
                # Skip if book exists
                if session.query(BooksModel).filter_by(isbn=row['ISBN']).first():
                    logger.debug(f"Book with ISBN {row['ISBN']} already exists, skipping...")
                    continue

                # Validate and prepare book data
                try:
                    book_data = {
                        'id': uuid.uuid4(),
                        'isbn': row['ISBN'],
                        'title': row['Book-Title'],
                        'author': row['Book-Author'],
                        'published_year': int(row['Year-Of-Publication']) if row['Year-Of-Publication'].isdigit() else None,
                        'publisher': row['Publisher'],
                        'image_url_s': row.get('Image-URL-S', ''),
                        'image_url_m': row.get('Image-URL-M', ''),  # Added missing field
                        'image_url_l': row.get('Image-URL-L', ''),  # Fixed field name
                        'total_quantity': 1,
                        'current_quantity': 1
                    }
                    books_to_add.append(BooksModel(**book_data))
                    books_imported += 1
                    batch_count += 1
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping row due to error: {str(e)} - Row: {row}")
                    continue

                # Commit in batches
                if batch_count >= batch_size:
                    try:
                        session.bulk_save_objects(books_to_add)
                        session.commit()
                        books_to_add = []
                        batch_count = 0
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Error committing batch: {str(e)}")
                        raise

            # Commit any remaining records
            if books_to_add:
                try:
                    session.bulk_save_objects(books_to_add)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error committing final batch: {str(e)}")
                    raise

            logger.info(f"Successfully imported {books_imported} books into the database.")

    except Exception as e:
        logger.error(f"Error importing books: {str(e)}", exc_info=True)
        if 'session' in locals():
            session.rollback()
        raise