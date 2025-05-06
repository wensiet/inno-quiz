from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.utils import get_password_hash
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    """Get a user by ID."""
    query = select(User).filter(User.id == user_id)
    result = db.execute(query)
    return result.scalars().first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get a user by username."""
    query = select(User).filter(User.username == username)
    result = db.execute(query)
    return result.scalars().first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email."""
    query = select(User).filter(User.email == email)
    result = db.execute(query)
    return result.scalars().first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users."""
    query = select(User).offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)

    # Create user with specific fields
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=getattr(
            user, "is_superuser", False
        ),  # Set superuser status if provided
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> User | None:
    """Update a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.model_dump(exclude_unset=True)

    # Handle password separately to ensure it's always hashed
    if "password" in update_data:
        password = update_data.pop("password")
        if password:  # Only update if password is not None or empty
            db_user.hashed_password = get_password_hash(password)

    # Update other fields
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> User | None:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user
