from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

DATABASE_DIR = Path(__file__).parent / "database"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'spend_tracker.db'}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

STATIC_USERNAME = "username"
STATIC_PASSWORD = "password"
SESSION_SECRET_KEY = "spend-tracker-dev-secret-change-me"


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float
    category: str
    spent_on: date = Field(default_factory=date.today)
    notes: Optional[str] = None


class ExpenseCreate(SQLModel):
    title: str
    amount: float
    category: str
    spent_on: Optional[date] = None
    notes: Optional[str] = None


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Spend Tracker", version="1.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("user"))


@app.get("/")
def root(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/login")
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == STATIC_USERNAME and password == STATIC_PASSWORD:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password"},
        status_code=401,
    )


@app.get("/register")
def register_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("register.html", {"request": request, "message": None})


@app.post("/register")
def register_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    message = (
        "This demo uses a static account only. "
        f"Please sign in with username '{STATIC_USERNAME}' and password '{STATIC_PASSWORD}'."
    )
    return templates.TemplateResponse("register.html", {"request": request, "message": message})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")


@app.get("/dashboard")
def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "authenticated": True, "username": request.session.get("user")},
    )


@app.get("/terms")
def terms_page(request: Request):
    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "authenticated": is_authenticated(request),
            "username": request.session.get("user"),
        },
    )


@app.get("/privacy")
def privacy_page(request: Request):
    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request,
            "authenticated": is_authenticated(request),
            "username": request.session.get("user"),
        },
    )


def require_auth(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")


@app.post("/expenses", response_model=Expense)
def create_expense(expense: ExpenseCreate, request: Request):
    require_auth(request)
    with Session(engine) as session:
        db_expense = Expense(**expense.model_dump(exclude_unset=True))
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return db_expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses(request: Request, category: Optional[str] = None):
    require_auth(request)
    with Session(engine) as session:
        statement = select(Expense)
        if category:
            statement = statement.where(Expense.category == category)
        return session.exec(statement).all()


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, request: Request):
    require_auth(request)
    with Session(engine) as session:
        expense = session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense


@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, expense: ExpenseCreate, request: Request):
    require_auth(request)
    with Session(engine) as session:
        db_expense = session.get(Expense, expense_id)
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        for key, value in expense.model_dump(exclude_unset=True).items():
            setattr(db_expense, key, value)
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return db_expense


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, request: Request):
    require_auth(request)
    with Session(engine) as session:
        db_expense = session.get(Expense, expense_id)
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        session.delete(db_expense)
        session.commit()
        return {"message": "Expense deleted"}


@app.get("/summary")
def spend_summary(request: Request):
    require_auth(request)
    with Session(engine) as session:
        expenses = session.exec(select(Expense)).all()
        total = sum(e.amount for e in expenses)
        by_category: dict[str, float] = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount
        return {"total_spent": total, "by_category": by_category}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
