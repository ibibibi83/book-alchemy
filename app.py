import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from data_models import db, Author, Book

# =========================
# App & Config
# =========================

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(BASE_DIR, "data", "library.sqlite")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# Routes
# =========================

# ---------- HOME + SEARCH ----------
@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q")

    if query:
        books = Book.query.filter(
            Book.title.ilike(f"%{query}%")
        ).all()
    else:
        books = Book.query.all()

    return render_template("home.html", books=books)


# ---------- ADD AUTHOR ----------
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"]
        birthdate = datetime.strptime(
            request.form["birthdate"], "%Y-%m-%d"
        ).date()

        date_of_death = request.form.get("date_of_death")
        if date_of_death:
            date_of_death = datetime.strptime(
                date_of_death, "%Y-%m-%d"
            ).date()
        else:
            date_of_death = None

        author = Author(
            name=name,
            birthdate=birthdate,
            date_of_death=date_of_death
        )
        db.session.add(author)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_author.html")


# ---------- ADD BOOK ----------
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.all()

    if request.method == "POST":
        title = request.form["title"]
        author_id = request.form["author_id"]

        book = Book(title=title, author_id=author_id)
        db.session.add(book)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_book.html", authors=authors)


# ---------- DELETE BOOK (Schritt 6) ----------
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    db.session.delete(book)
    db.session.commit()

    return redirect(url_for("home"))


# =========================
# App start
# =========================

if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)
