from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# ------------------ DATA ------------------

books = [
    {"id": 1, "title": "Atomic Habits", "author": "James Clear", "genre": "Self-help", "is_available": True},
    {"id": 2, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "is_available": True},
    {"id": 3, "title": "After Dark", "author": "Haruki Murakami", "genre": "Japanese Fiction", "is_available": True},
    {"id": 4, "title": "The Psychology of Money", "author": "Morgan Housel", "genre": "Finance", "is_available": True}
]

borrow_records = []
queue = []
record_counter = 1

# ------------------ MODELS ------------------

class BorrowRequest(BaseModel):
    member_name: str
    book_id: int
    days: int = Query(..., ge=1, le=60)
    member_type: str = "regular"

class NewBook(BaseModel):
    title: str
    author: str
    genre: str

# ------------------ HELPERS ------------------

def find_book(book_id):
    for b in books:
        if b["id"] == book_id:
            return b
    return None


def calculate_due_date(days):
    return f"Return in {days} days"


# ------------------ Q1 ------------------

@app.get("/")
def home():
    return {"message": "Welcome to City Public Library "}


# ------------------ Q2 ------------------

@app.get("/books")
def get_books():
    return {"total_books": len(books), "books": books}


# ------------------ Q3 ------------------

@app.get("/books/summary")
def books_summary():
    available = len([b for b in books if b["is_available"]])
    return {"total": len(books), "available": available}


# ------------------ Q4 ------------------

@app.get("/borrow-records")
def get_records():
    return {"total_records": len(borrow_records), "records": borrow_records}

# ------------------ Q19 PART 2 PAGINATION ------------------

@app.get("/borrow-records/page")
def paginate_records(
    page: int = Query(1),
    limit: int = Query(2)
):
    total = len(borrow_records)
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "records": borrow_records[start:end]
    }
# ------------------ Q20 BROWSE ------------------

@app.get("/books/browse")
def browse(
    keyword: str = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 2
):
    result = books.copy()

    #Filter
    if keyword:
        result = [
            b for b in result
            if keyword.lower() in b["title"].lower()
            or keyword.lower() in b["author"].lower()
        ]

    #Validation
    if sort_by not in ["title", "author", "genre"]:
        return {"error": "Invalid sort_by"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    #Sort
    result = sorted(
        result,
        key=lambda b: b[sort_by],
        reverse=(order == "desc")
    )

    #Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "results": paged
    }
# ------------------ Q18 PAGINATION ------------------

@app.get("/books/page")
def paginate_books(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):
    start = (page - 1) * limit
    data = books[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": len(books),
        "total_pages": -(-len(books) // limit),
        "books": data
    }

# ------------------ Q17 SORT ------------------

@app.get("/books/sort")
def sort_books(
    sort_by: str = Query("title"),
    order: str = Query("asc")
):
    # validation
    if sort_by not in ["title", "author", "genre"]:
        return {"message": "Invalid sort_by. Use title, author, or genre"}

    if order not in ["asc", "desc"]:
        return {"message": "Invalid order. Use asc or desc"}

    result = sorted(
        books,
        key=lambda b: b[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(result),
        "books": result
    }


# ------------------ Q10 FILTER ------------------

@app.get("/books/filter")
def filter_books(genre: Optional[str] = None):
    result = books
    if genre:
        result = [b for b in result if genre.lower() in b["genre"].lower()]
    return {"count": len(result), "books": result}


# ------------------ Q16 SEARCH ------------------

@app.get("/books/search")
def search_books(keyword: str = Query(...)):
    result = [
        b for b in books
        if keyword.lower() in b["title"].lower()
        or keyword.lower() in b["author"].lower()
    ]

    if not result:
        return {"message": f"No books found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(result),
        "books": result
    }
# ------------------ Q5 ------------------

@app.get("/books/{book_id}")
def get_book(book_id: int, response: Response):
    book = find_book(book_id)
    if not book:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Book not found"}
    return book


# ------------------ Q6–Q9 BORROW ------------------

@app.post("/borrow")
def borrow_book(req: BorrowRequest, response: Response):
    global record_counter

    book = find_book(req.book_id)
    if not book:
        response.status_code = 404
        return {"message": "Book not found"}

    # member type logic
    if req.member_type == "regular" and req.days > 30:
        return {"message": "Regular members can borrow max 30 days"}
    if req.member_type == "premium" and req.days > 60:
        return {"message": "Premium members can borrow max 60 days"}

    if not book["is_available"]:
        queue.append({"member_name": req.member_name, "book_id": req.book_id})
        return {"message": "Book unavailable, added to queue"}

    book["is_available"] = False

    record = {
        "record_id": record_counter,
        "member_name": req.member_name,
        "book_title": book["title"],
        "due_date": calculate_due_date(req.days)
    }

    record_counter += 1
    borrow_records.append(record)

    response.status_code = 201
    return {"message": "Book borrowed", "record": record}




# ------------------ Q11 ADD BOOK ------------------

@app.post("/books")
def add_book(new: NewBook, response: Response):
    new_id = max(b["id"] for b in books) + 1
    book = {"id": new_id, **new.dict(), "is_available": True}
    books.append(book)
    response.status_code = 201
    return {"message": "Book added", "book": book}


# ------------------ Q12 UPDATE ------------------

@app.put("/books/{book_id}")
def update_book(book_id: int, title: Optional[str] = None):
    book = find_book(book_id)
    if not book:
        return {"message": "Book not found"}

    if title:
        book["title"] = title

    return {"message": "Updated", "book": book}


# ------------------ Q13 DELETE ------------------

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"message": "Book not found"}

    books.remove(book)
    return {"message": "Deleted"}


# ------------------ Q14 RETURN ------------------

@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"message": "Book not found"}

    book["is_available"] = True

    for q in queue:
        if q["book_id"] == book_id:
            queue.remove(q)
            book["is_available"] = False

            new_record = {
                "record_id": len(borrow_records) + 1,
                "member_name": q["member_name"],
                "book_title": book["title"],
                "due_date": "Auto-assigned"
            }

            borrow_records.append(new_record)

            return {
                "message": "returned and re-assigned",
                "assigned_to": q["member_name"]
            }

    return {"message": "returned and available"}


# ------------------ Q19 SEARCH RECORDS ------------------

@app.get("/borrow-records/search")
def search_records(member_name: str = Query(...)):
    result = [
        r for r in borrow_records
        if member_name.lower() in r["member_name"].lower()
    ]

    if not result:
        return {"message": f"No records found for: {member_name}"}

    return {
        "member_name": member_name,
        "total_found": len(result),
        "records": result
    }

