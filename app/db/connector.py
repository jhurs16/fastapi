import logging
from datetime import date, timedelta
from typing import List

import pandas as pd
import sqlalchemy
from pandas import DataFrame
from sqlalchemy import Connection, and_, func, insert, join, select, update

from app.api.v1.schema_polling_data import (
    FileData,
    # PollingAttributes,
)
from app.util.timeit import timeit

from .database import get_connection

"""from .metadata import (
    #PollingDataAttributeHierarchy,
)"""

logger = logging.getLogger(__name__)


# @timeit(logger)
def write_to_db(df: DataFrame, target_table: str) -> int:
    return 1


# @timeit(logger)
"""
def get_or_create_polling_data_attribute(c: Connection, attribute: str) -> int:
    with get_connection() as c:
        stmt_select = select(PollingDataAttributes.c.POLLING_DATA_ATTRIBUTE_ID).where(
            PollingDataAttributes.c.POLLING_DATA_ATTRIBUTE == attribute
        )
        result = c.execute(stmt_select).fetchone()

        if result:
            return result[0]

        stmt_insert = (
            insert(PollingDataAttributes)
            .values(POLLING_DATA_ATTRIBUTE=attribute, VALID_FROM=date.today())
            .returning(PollingDataAttributes.c.POLLING_DATA_ATTRIBUTE_ID)
        )

        try:
            insert_result = c.execute(stmt_insert)
            _commit(c)
            return insert_result.fetchone()[0]
        except sqlalchemy.exc.IntegrityError:
            _rollback(c)
            return None
"""

# @timeit(logger)
"""def db_get_files() -> FileData:
    with get_connection() as c:
        stmt_select = select(
            PollingDataFiles.c.POLLING_DATA_FILE_ID,
            PollingDataFiles.c.POLLING_DATA_FILE_NAME,
            PollingDataFiles.c.VALID_FROM,
            PollingDataFiles.c.VALID_TO,
            PollingDataFiles.c.DATA_INSERTED,
            PollingDataFiles.c.DATA_UPDATED,
        )
        results = c.execute(stmt_select).mappings().all()

        if results:
            return [FileData(**result) for result in results] if results else []
        else:
            return None
"""


def _commit(c: Connection) -> None:
    c.commit()
    logger.debug("Database changes committed successfully.")


def _rollback(c: Connection) -> None:
    c.rollback()
    logger.debug("Database changes committed successfully.")
