"""
Flask web application for managing a simple library system.

Features:
- View and search books
- Add authors with birth/death dates
- Add books linked to authors
- Delete books
"""

import os
from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book

# =========================
# App & Config
# =========================

app = Flask(__name__)
app.secret_key = "dev-secret-key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(BASE_DIR, "data", "library.sqlite")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# Helper functions
# =========================

def is_in_future(d: date) -> bool:
    """
    Checks whether a given date is in the future.

    Args:
        d (date): Date to check.

    Returns:
        bool: True if the date is after today, False otherwise.
    """
    return d > date.today()


# =========================
# Routes
# =========================

@app.route("/", methods=["GET"])
def home():
    """
    Home page route.

    Displays all books in the library.
    Supports optional search by book title.
    """
    query = request.args.get("q")

    if query:
        books = Book.query.filter(Book.title.ilike(f"%{query}%")).all()
    else:
        books = Book.query.all()

    return render_template("home.html", books=books)


# ---------- ADD AUTHOR ----------
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Add author route.

    GET:
        Displays the author creation form.

    POST:
        Creates a new author after validating input data.
    """
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            birth_date = datetime.strptime(
                request.form["birth_date"], "%Y-%m-%d"
            ).date()

            date_of_death_raw = request.form.get("date_of_death")
            date_of_death = None

            if date_of_death_raw:
                date_of_death = datetime.strptime(
                    date_of_death_raw, "%Y-%m-%d"
                ).date()

            # Validation
            if is_in_future(birth_date):
                flash("Birth date cannot be in the future.")
                return redirect(url_for("add_author"))

            if date_of_death:
                if is_in_future(date_of_death):
                    flash("Death date cannot be in the future.")
                    return redirect(url_for("add_author"))

                if date_of_death < birth_date:
                    flash("Death date cannot be before birth date.")
                    return redirect(url_for("add_author"))

            # Duplicate check
            existing_author = Author.query.filter_by(
                name=name, birth_date=birth_date
            ).first()
            if existing_author:
                flash("Author already exists.")
                return redirect(url_for("add_author"))

            author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )

            db.session.add(author)
            db.session.commit()

            return redirect(url_for("home"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding author: {e}")
            return redirect(url_for("add_author"))

    return render_template("add_author.html")


# ---------- ADD BOOK ----------
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Add book route.

    GET:
        Displays the book creation form.

    POST:
        Creates a new book linked to an author.
    """
    authors = Author.query.all()

    if request.method == "POST":
        try:
            title = request.form["title"].strip()
            isbn = request.form["isbn"].strip()
            author_id = int(request.form["author_id"])

            # Duplicate check
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                flash("Book with this ISBN already exists.")
                return redirect(url_for("add_book"))

            book = Book(
                title=title,
                isbn=isbn,
                author_id=author_id
            )

            db.session.add(book)
            db.session.commit()

            return redirect(url_for("home"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding book: {e}")
            return redirect(url_for("add_book"))

    return render_template("add_book.html", authors=authors)


# ---------- DELETE BOOK ----------
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete book route.

    Deletes a book by its ID.
    """
    try:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting book: {e}")

    return redirect(url_for("home"))


# =========================
# App start
# =========================

if __name__ == "__main__":
    """
    Application entry point.

    Creates database tables and starts the Flask server.
    """
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)
