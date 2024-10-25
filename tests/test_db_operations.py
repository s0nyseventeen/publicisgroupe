from pytest import fixture
from sqlmodel import Session

from .conftest import engine
from app.db_operations import create_uploaded_file


@fixture
def session(setup_test_db):
    with Session(engine) as session:
        yield session


def test_create_uploaded_file(session):
    uploaded_file = create_uploaded_file('test_file', session)
    session.add(uploaded_file)
    session.commit()
    assert uploaded_file.name == 'test_file'
