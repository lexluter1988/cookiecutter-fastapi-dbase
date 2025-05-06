## Simple FastAPI Template with sqlalchemy session manager and base mixin for models

Project has alembic, postgresql adapter and generic DBMixin with create, retrieve, update, delete methods 

## Project Structure

```shell
├── REAMDE.md
├── app
├── alembic
│   ├── versions
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── sessionmanager.py
│   ├── main.py
│   ├── settings.py
├── pyproject.toml
```


## Predefined packages

Template uses `poetry` with the following packages

```shell
python = "^3.10"
uvicorn = "^0.34.2"
fastapi = "^0.115.12"
sqlalchemy = "^2.0.40"
email-validator = "^2.2.0"
asyncpg = "^0.30.0"
alembic = "^1.15.2"
pre-commit = "^4.2.0"
greenlet = "^3.2.1"
```

## Database

For now its simple sqlite
And credentials are stored in `.env` file

```shell
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost/admin
```

## Quick start

```shell
cookiecutter https://github.com/lexluter1988/cookiecutter-fastapi-dbase.git

poetry install
pre-commit install
docker-compose up -d
```

## Starting the app

```shell script
uvicorn --host 0.0.0.0 --port 5000 --reload app.main:application
```


## Example 

### Define model

```python
# app/users/models.py
from sqlalchemy import Boolean, Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.db.base import Base, DBMixin


class User(Base, DBMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Let alembic see it

```python
# alembic/env.py
from app.auth.models import User
```

### Create migrations

```shell
alembic revision --autogenerate -m "Add user model"

alembic upgrade head

```

### Define contracts
```python
# app/users/dto.py
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreateRequestDto(UserBase):
    pass


class UserResponseDto(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

```

### Define views

```python
# app/users/views.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dto import UserCreateRequestDto, UserResponseDto
from app.auth.models import User
from app.db.sessionmanager import get_db


user_router = APIRouter(prefix='/user', tags=['user'])


@user_router.post('/register', response_model=UserResponseDto)
async def create_user(user: UserCreateRequestDto, db: AsyncSession = Depends(get_db)):
    user = await User.create(
        db, **user.dict()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return user


@user_router.post('/users', response_model=List[UserResponseDto])
async def create_user(db: AsyncSession = Depends(get_db)):
    users = await User.all(db)
    return users


@user_router.post('/users/pk', response_model=List[UserResponseDto])
async def get_user__by_id(pk: int, db: AsyncSession = Depends(get_db)):
    users = await User.filter(db, id=pk)
    return users


@user_router.post('/users/email', response_model=List[UserResponseDto])
async def get_user__by_email(email: str, db: AsyncSession = Depends(get_db)):
    users = await User.filter(db, email=email)
    return users
```

### Add it to your main

```python
# app/main.py

from __future__ import annotations

from fastapi import FastAPI

from app.auth.views import user_router
from app.db.sessionmanager import sessionmanager
from app.settings import get_settings

settings = get_settings()


def get_application() -> FastAPI:
    sessionmanager.init(settings.database_url)

    app = FastAPI(
        openapi_url='/api/openapi.json',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        debug=settings.debug,
        version=settings.app_version or '0.1.0',
        title='Starter FastApi',
    )
    app.include_router(user_router, prefix='/api', tags=['user'])

    return app


application = get_application()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(application, host='0.0.0.0', port=8000)
```
