from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

DATABASE_DIR = Path(__file__).parent / "database"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'spend_tracker.db'}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SESSION_SECRET_KEY = "spend-tracker-dev-secret-change-me"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float
    category: str
    spent_on: date = Field(default_factory=date.today)
    notes: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")


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


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


@app.get("/")
def root(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/login")
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    info = (
        "Account created — sign in to continue." if request.query_params.get("registered") else None
    )
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None, "info": info}
    )


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user and verify_password(password, user.password_hash):
            request.session["user"] = user.username
            return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password", "info": None},
        status_code=401,
    )


@app.get("/register")
def register_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "register.html", {"request": request, "error": None, "username": None, "email": None}
    )


@app.post("/register")
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    with Session(engine) as session:
        username_taken = session.exec(select(User).where(User.username == username)).first()
        email_taken = session.exec(select(User).where(User.email == email)).first()
        if username_taken and email_taken:
            message = "That username and email are both already registered."
        elif username_taken:
            message = "That username is already taken."
        elif email_taken:
            message = "That email is already registered."
        else:
            user = User(username=username, email=email, password_hash=hash_password(password))
            session.add(user)
            session.commit()
            return RedirectResponse(url="/login?registered=1", status_code=303)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": message, "username": username, "email": email},
        status_code=409,
    )


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


def current_user_id(request: Request, session: Session) -> int:
    user = session.exec(select(User).where(User.username == request.session.get("user"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.id


@app.post("/expenses", response_model=Expense)
def create_expense(expense: ExpenseCreate, request: Request):
    require_auth(request)
    with Session(engine) as session:
        user_id = current_user_id(request, session)
        db_expense = Expense(**expense.model_dump(exclude_unset=True), user_id=user_id)
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return db_expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses(request: Request, category: Optional[str] = None):
    require_auth(request)
    with Session(engine) as session:
        user_id = current_user_id(request, session)
        statement = select(Expense).where(Expense.user_id == user_id)
        if category:
            statement = statement.where(Expense.category == category)
        return session.exec(statement).all()


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, request: Request):
    require_auth(request)
    with Session(engine) as session:
        user_id = current_user_id(request, session)
        expense = session.exec(
            select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        ).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense


@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, expense: ExpenseCreate, request: Request):
    require_auth(request)
    with Session(engine) as session:
        user_id = current_user_id(request, session)
        db_expense = session.exec(
            select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        ).first()
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
        user_id = current_user_id(request, session)
        db_expense = session.exec(
            select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        ).first()
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        session.delete(db_expense)
        session.commit()
        return {"message": "Expense deleted"}


@app.get("/summary")
def spend_summary(request: Request):
    require_auth(request)
    with Session(engine) as session:
        user_id = current_user_id(request, session)
        expenses = session.exec(select(Expense).where(Expense.user_id == user_id)).all()
        total = sum(e.amount for e in expenses)
        by_category: dict[str, float] = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount
        return {"total_spent": total, "by_category": by_category}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
