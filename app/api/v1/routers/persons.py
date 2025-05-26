import logging
from fastapi import HTTPException
from app.api.v1.routers.excel_upload import read_config, connect_to_database
from helper_fn import SQL_connection

logger = logging.getLogger(__name__)
async def persons():
    """
    Get all persons.
    return: List[Dict]
    """
    try: 

        persons = SQL_connection("select * from terramo_data.persons")
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Database connection error.")

    if persons is None:
            raise HTTPException(status_code=404, detail="Not found.")
    return {'response':persons}



async def persons_by_id(id: int):
    """
    Get person by ID.
    :param id: int
    return: Dict
    """
    try: 

        person = SQL_connection(f"SELECT * FROM terramo_data.persons WHERE PERSON_ID = {id}")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if person is None:
        raise HTTPException(status_code=404, detail="Person not found.")
    return person[0]

