from app.database import SessionLocal
from app.tests.databasetest import TestingSessionLocal


def get_db():
    """
    Database dependency used as FastAPI dependency and used in almost all classes inside the app.api package. (not yet)
    """
    print("Called original get_db method")
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()


def check_sess(sess):
    '''If session is None, default session is returned, else, session is returned'''
    if sess == None:
        sess = get_db().__next__()
    return sess


def override_get_db():
    print("Called test override_get_db method")
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
