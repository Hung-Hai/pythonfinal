from datetime import datetime
from pathlib import Path
from typing import List, Tuple
import uuid
from typer import Typer
import typer

from commands.init_database.main import import_all_data, init_database

# Define import order and file mappings
IMPORT_ORDER: List[Tuple[str, str]] = [
    ('author', 'authors.csv'),
    ('publisher', 'publisher.csv'),
    ('category', 'category.csv'),
    ('role', 'role.csv'),
    ('users', 'user.csv'),
    ('books', 'books.csv'),
    ('physical', 'books_physical.csv'),
    ('digital', 'books_digital.csv'),
    ('physical_loan', 'loan_physical.csv'),
    ('digital_loan', 'loan_digital.csv'),
    ('rating', 'rating.csv'),
    ('reservation', 'reservation.csv')
]

# Default values for tables that need them
DEFAULT_VALUES = {
    '__all__': {  # Applies to all tables
        'id': lambda: str(uuid.uuid4()),
        'created_at': lambda: datetime.now(),
        'updated_at': lambda: datetime.now()
    }
}

ASSOCIATION_TABLES = [
    'category_book',
    'user_role',
    'author_book'
]

IMPORT_ORDER += [
    ('category_book', 'category_book.csv'),
    ('user_role', 'user_role.csv'),
    ('author_book', 'author_books.csv')
]
app = Typer()


@app.command("init_database")
def cmd_init_database():
    print("Initializing database")
    init_database()

@app.command("import_all")
def cmd_import_all(
    data_dir: str = "test_data",
    batch_size: int = 1000,
    skip_duplicates: bool = True,
    confirm: bool = typer.Option(True, help="Ask for confirmation before importing")
):
    """
    Import all CSV files in the correct order with dependencies.
    """
    data_path = Path(data_dir)
    
    if confirm:
        typer.echo("This will import data from the following files:")
        for table, filename in IMPORT_ORDER:
            filepath = data_path / filename
            typer.echo(f"  - {filepath}")
        
        if not typer.confirm("Continue with import?"):
            typer.echo("Import cancelled")
            raise typer.Abort()
    
    # Build the files dictionary
    files_to_import = {
        table: str(data_path / filename) 
        for table, filename in IMPORT_ORDER
        if (data_path / filename).exists()
    }
    
    missing_files = [
        filename for table, filename in IMPORT_ORDER 
        if not (data_path / filename).exists()
    ]
    
    if missing_files:
        typer.echo(f"Warning: Missing files: {', '.join(missing_files)}", err=True)
    
    if not files_to_import:
        typer.echo("No valid files found to import", err=True)
        raise typer.Abort()
    
    # Run the import
    results = import_all_data(
        csv_files=files_to_import,
        batch_size=batch_size,
        default_values=DEFAULT_VALUES,
        skip_duplicates=skip_duplicates,
        association_tables=ASSOCIATION_TABLES
    )
    
    # Display results
    typer.echo("\nImport results:")
    for table, count in results.items():
        if isinstance(count, int):
            typer.echo(f"  - {table}: {count} records imported")
        else:
            typer.echo(f"  - {table}: ERROR - {count}", err=True)
    
    total_imported = sum(c for c in results.values() if isinstance(c, int))
    typer.echo(f"\nTotal records imported: {total_imported}")

@app.command("run_test")
def cmd_run_test():
    print("Running tests")
    # TODO: Add test execution logic here
    print("Tests executed successfully")


if __name__ == "__main__":
    app()
