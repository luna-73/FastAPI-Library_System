# ⭐️ FastAPI Library Book Management System

This project is a backend system built using FastAPI that simulates how a real library works
— managing books, handling borrow/return operations, and implementing search, sorting, and pagination.
---

## 📌 Features

* REST API development using FastAPI
* Pydantic validation for request handling
* Full CRUD operations for books
* Borrow and return workflow system
* Queue-based book allocation
* Search, sorting, and pagination
* Combined browsing API
* Swagger UI testing

---

## 📌 Project Structure

```
main.py
screenshots/
README.md
```

---

## 📌 APIs Implemented

### - Book Management

* Get all books
* Get book by ID
* Add new book
* Update book
* Delete book
* Books summary

### - Borrow Workflow

* Borrow book
* Return book
* Queue system for unavailable books
* Auto reassignment after return

### - Essential Features

* Search books (title + author)
* Sort books (title, author, genre)
* Pagination for books
* Search borrow records
* Pagination for borrow records
* Combined browse endpoint

---

## 📸 Screenshots

All API responses tested using Swagger UI are available in the `screenshots/` folder.

---

## ▶️ How to Run

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Open:
👉 http://127.0.0.1:8000/docs

---

##  What I learned: 
* Structuring APIs properly (especially route ordering)
* Handling edge cases like invalid input and unavailable books
* Writing cleaner logic using helper functions
* Combining multiple features into one endpoint (browse)

---


Built as part of Agentic AI Internship  at **Innomatics Research Labs**
