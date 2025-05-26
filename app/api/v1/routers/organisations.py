import logging
from fastapi import HTTPException
from helper_fn import SQL_connection
logger = logging.getLogger(__name__)
async def get_organization():
    """
    Get all organizations.
    return: List[Dict]
    """
    try:

        org_dict = SQL_connection("select * from terramo_data.organisations")
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Database connection error.")

    return {'response':org_dict}



async def get_organization_by_id(org_id: int):
    """
    Get organization by ID.
    :param org_id: int
    return: Dict
    """
    try:
        QUERY = f"SELECT * FROM organisations WHERE organisation_id = {org_id}"
        org_dict = SQL_connection(QUERY)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if org_dict is None:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return org_dict[0]
