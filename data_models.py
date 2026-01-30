"""
Database models for the Book Alchemy application.

Defines SQLAlchemy models for authors and books
and their relationships.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author in the library system.

    Attributes:
        id (int): Primary key.
        name (str): Full name of the author.
        birth_date (date): Date of birth.
        date_of_death (date | None): Date of death, if applicable.
        books (list[Book]): List of books written by the author.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        """
        Returns a string representation of the Author instance.
        """
        return f"<Author {self.name}>"


class Book(db.Model):
    """
    Represents a book in the library system.

    Attributes:
        id (int): Primary key.
        title (str): Title of the book.
        isbn (str): International Standard Book Number (unique identifier).
        author_id (int): Foreign key referencing the author.
        author (Author): Author associated with the book.
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(150), nullable=False)

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("author.id"),
        nullable=False
    )

    def __repr__(self):
        """
        Returns a string representation of the Book instance.
        """
        return f"<Book {self.title}>"
