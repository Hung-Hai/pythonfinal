from typer import Typer

from commands.init_database.main import import_books_from_csv, init_database

app = Typer()


@app.command("init_database")
def cmd_init_database():
    print("Initializing database")
    init_database()

@app.command("import_books")
def cmd_import_books(csv_file_path: str = "test_data/books.csv"):
    print(f"Importing books from {csv_file_path}")
    import_books_from_csv(csv_file_path)

@app.command("run_test")
def cmd_run_test():
    print("Running tests")
    # TODO: Add test execution logic here
    print("Tests executed successfully")


if __name__ == "__main__":
    app()
