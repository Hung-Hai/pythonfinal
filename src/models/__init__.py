from src.models.books_models import BooksModel
from src.models.books_digital_models import BooksDigitalModel
from src.models.books_physical_models import BooksPhysicalModel
from src.models.users_models import UsersModel
from src.models.role_models import RoleModel
from src.models.author_models import AuthorModel
from src.models.author_books_models import AuthorBookModel
from src.models.category_models import CategoriesModel
from src.models.publisher_models import PublishersModel
from src.models.loan_digital_models import DigitalLoansModel
from src.models.loan_physical_models import PhysicalLoansModel
from src.models.rating_models import RatingModel
from src.models.reservation_models import ReservationModel
from src.models.relationship_models import book_category_table

# Registry mapping table names -> model classes
MODEL_REGISTRY = {
    "author": AuthorModel,
    "publisher": PublishersModel,
    "category": CategoriesModel,
    "role": RoleModel,
    "users": UsersModel,
    "books": BooksModel,
    "physical": BooksPhysicalModel,
    "digital": BooksDigitalModel,
    "physical_loan": PhysicalLoansModel,
    "digital_loan": DigitalLoansModel,
    "rating": RatingModel,
    "reservation": ReservationModel,
    "author_book": AuthorBookModel,
}
