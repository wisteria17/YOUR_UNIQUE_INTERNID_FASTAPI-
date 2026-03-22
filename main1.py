from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Library Management System")

# ---------------- DATABASE ----------------
books = []
users = []
borrow_records = []

# ---------------- SCHEMAS ----------------
class Book(BaseModel):
    id: int
    title: str
    author: str
    stock: int

class User(BaseModel):
    id: int
    name: str

class Borrow(BaseModel):
    user_id: int
    book_id: int

# ---------------- HELPER FUNCTIONS ----------------
def find_book(book_id):
    for book in books:
        if book.id == book_id:
            return book
    return None

def find_user(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None

# ---------------- BOOK APIs ----------------

# 1 Create book
@app.post("/books")
def create_book(book: Book):
    books.append(book)
    return {"message": "Book added successfully"}

# 2 Get all books
@app.get("/books")
def get_books():
    return books

# 3 Get book by ID
@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# 4 Update book
@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):
    for i, book in enumerate(books):
        if book.id == book_id:
            books[i] = updated_book
            return {"message": "Book updated"}
    raise HTTPException(status_code=404, detail="Book not found")

# 5 Delete book
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404)
    books.remove(book)
    return {"message": "Book deleted"}

# 6 Search books
@app.get("/books/search")
def search_books(q: str):
    return [b for b in books if q.lower() in b.title.lower()]

# 7 Sort books
@app.get("/books/sort")
def sort_books():
    return sorted(books, key=lambda x: x.title)

# 8 Pagination
@app.get("/books/paginate")
def paginate_books(page: int = 1, limit: int = 5):
    start = (page - 1) * limit
    return books[start:start + limit]

# ---------------- USER APIs ----------------

# 9 Create user
@app.post("/users")
def create_user(user: User):
    users.append(user)
    return {"message": "User added"}

# 10 Get users
@app.get("/users")
def get_users():
    return users

# 11 Get user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user

# 12 Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404)
    users.remove(user)
    return {"message": "User deleted"}

# ---------------- BORROW SYSTEM ----------------

# 13 Borrow book
@app.post("/borrow")
def borrow_book(data: Borrow):
    book = find_book(data.book_id)
    user = find_user(data.user_id)

    if not book or not user:
        raise HTTPException(status_code=404, detail="User or Book not found")

    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    book.stock -= 1
    borrow_records.append(data)

    return {"message": "Book borrowed successfully"}

# 14 Return book
@app.post("/return")
def return_book(data: Borrow):
    book = find_book(data.book_id)

    if not book:
        raise HTTPException(status_code=404)

    book.stock += 1

    if data in borrow_records:
        borrow_records.remove(data)

    return {"message": "Book returned"}

# 15 Get all borrowed records
@app.get("/borrowed")
def get_borrowed():
    return borrow_records

# 16 Get user borrowed books
@app.get("/users/{user_id}/borrowed")
def user_borrowed(user_id: int):
    return [b for b in borrow_records if b.user_id == user_id]

# ---------------- EXTRA APIs ----------------

# 17 Update stock
@app.patch("/books/{book_id}/stock")
def update_stock(book_id: int, stock: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404)
    book.stock = stock
    return {"message": "Stock updated"}

# 18 Health check
@app.get("/health")
def health():
    return {"status": "Running"}

# 19 Stats
@app.get("/stats")
def stats():
    return {
        "total_books": len(books),
        "total_users": len(users),
        "borrowed_books": len(borrow_records)
    }

# 20 Root
@app.get("/")
def root():
    return {"message": "Library API is running"}