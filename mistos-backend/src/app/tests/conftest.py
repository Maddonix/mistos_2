import pytest

from main import mistos
from app.api.dependencies import get_db, override_get_db
from app.tests.databasetest import Base, engine, SQLALCHEMY_DATABASE_URL
from fastapi.logger import logger as log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from starlette.testclient import TestClient

from fastapi import APIRouter, Depends

@pytest.fixture(scope="function", autouse=True)
def create_test_database():
    """
    Create a clean database on every test case.
    """
    try:
        # Create the database including tables.
        Base.metadata.create_all(bind=engine)
        yield
    finally:
        # Drop the test database.
        drop_database(SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="session")
def test_app_simple():
    """
    This fixture creates a simple test-client.
    """

    print("CREATE TEST APP SIMPLE")

    mistos.dependency_overrides[get_db] = override_get_db

    print(mistos.dependency_overrides)

    client = TestClient(mistos)

    yield client  # testing happens here
