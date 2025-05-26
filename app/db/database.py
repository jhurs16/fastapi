import logging
import sys
from contextlib import contextmanager
from typing import Iterator, Optional, Tuple

from sqlalchemy import Connection, Engine, create_engine, text

from app import config as myconfig
from app.config import get_config, scramble_secret

from .metadata import get_metadata

logger = logging.getLogger(__name__)

ORACLE_DIALECT_CX = "oracledb"


class Database:
    _engine: Engine

    def __init__(self, url: str) -> None:
        logger.info("Connecting to database... not mysql")
        logger.info(url)
        self._engine = create_engine(
            url,
            future=True,
        )
        

    def get_engine(self) -> Engine:
        return self._engine

    @contextmanager
    def get_connection(self) -> Iterator[Connection]:
        with self._engine.connect() as conn:
            yield conn

    def dispose(self) -> None:
        self._engine.dispose()


class SqliteDatabase(Database):
    def populate_tables(self) -> None:
        meta = get_metadata()
        meta.create_all(self._engine)


class OracleDatabase(Database):
    def __init__(self, url: str) -> None:
        logger.info("Connecting to Oracle database...")
        self._engine = create_engine(
            url,
            future=True,
            thick_mode=None,
        )

    def populate_tables(self) -> None:
        logger.warning(
            "Tables will not be created in Oracle database, they are expected to exist."
        )
        with self.get_connection() as conn:
            _ = conn.execute(text("SELECT 1 FROM dual")).one()


class MySQLDatabase(Database):
    logger.info("Connecting... mYSQL")
    def populate_tables(self) -> None:
        meta = get_metadata()
        meta.create_all(self._engine)


_database: Optional[Database] = None


def init_database() -> None:
    _ = get_database()


def get_database() -> Database:
    global _database
    if _database:
        return _database

    config = get_config()
    assert config.database.dsn is not None, "Missing data source name for database"

    logger.debug(
        f"DB: engine {config.database.engine}"
        f" dsn {config.database.dsn}" 
        f" username {config.database.username}"
        f" password {scramble_secret(config.database.password)}"
    )
    url, scrambled_url = get_url(
        config.database.engine,
        config.database.dsn,
        config.database.username,
        config.database.password,
    )
    logger.info(f"DB url {url}")
    logger.info(f"DB scrambled_url {scrambled_url}")

    if config.database.engine == myconfig.Engine.oracle:
        _database = OracleDatabase(url)
    elif config.database.engine == myconfig.Engine.mysql:
        logger.info(f"########## MYSQL #########")
        _database = MySQLDatabase(url)
    else:
        _database = SqliteDatabase(url)

    _database.populate_tables()

    return _database


@contextmanager
def get_connection() -> Iterator[Connection]:
    db = get_database()
    if db is None:
        logger.error("No database available, no connection possible!")
        sys.exit(-1)
    assert db is not None
    with db.get_connection() as conn:
        yield conn


def get_url(
    engine: str, dsn: str, username: str | None, password: str | None
) -> Tuple[str, str]:
    assert dsn is not None, "No data source name specified for the database!"
    match engine:
        case myconfig.Engine.sqlite:
            url = f"{engine}:///{dsn}"
            scrambled = url
        case myconfig.Engine.oracle:
            assert username is not None, "Oracle database connection requires username!"
            assert password is not None, "Oracle database connection requires password!"
            prefix = f"{engine}"
            url = f"{prefix}+{ORACLE_DIALECT_CX}://{username}:{password}@{dsn}"
            scrambled = f"{prefix}://{username}:{scramble_secret(password)}@{dsn}"
        case myconfig.Engine.mysql:
            assert username is not None, "MySQL database connection requires username!"
            assert password is not None, "MySQL database connection requires password!"
            logger.info(f"database.... is mysql!")
            url = f"mysql+pymysql://{username}:{password}@{dsn}"
            scrambled = f"mysql+pymysql://{username}:{scramble_secret(password)}@{dsn}"
        case _:
            assert (
                False
            ), "Only sqlite, Oracle, and MySQL are supported as database engines!"
    return url, scrambled
