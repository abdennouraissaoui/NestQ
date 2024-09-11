from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import app_config


class DBConnectionManager:
    def __init__(self, pool_size=1, max_overflow=5):
        self.engine = create_engine(
            app_config.SQLALCHEMY_DATABASE_URI,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self._connections = []

    def get_connection(self):
        """
        Get A DBAPI. When done, please close by calling method .close()
        :return: DBAPI
        """
        connection = self.engine.connect()
        self._connections.append(connection)
        return connection

    def close_all_connections(self):
        for connection in self._connections:
            connection.close()

    def get_session(self):
        return Session(bind=self.engine)

    def __del__(self):
        """
        Closes the DB automatically when the program ends
        """
        self.close_all_connections()


if __name__ == "__main__":
    dbcm = DBConnectionManager()
    conn = dbcm.get_connection()
    print(conn.exec_driver_sql("SELECT count(*) FROM clients").fetchall())
    print("Done")
    dbcm.close_all_connections()
