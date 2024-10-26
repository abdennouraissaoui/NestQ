from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import app_config


engine = create_engine(
    app_config.SQLALCHEMY_DATABASE_URI,
    pool_size=1,
    max_overflow=5,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    from app.models.database import Client

    db = get_db()

    # Get a session
    session = next(db)

    # Count the number of clients
    client_count = session.query(Client).count()

    print(f"Total number of clients: {client_count}")

    # Close the session
    session.close()
