from fastapi import HTTPException
from helper_fn import SQL_connection


async def stakeholder_names():
    """
    Get all stakeholder names.
    return: List[Dict]
    """
    try: 
        stakeholder_names = SQL_connection("select * from terramo_data.stakeholder_names")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")
    
    if stakeholder_names is None:
        raise HTTPException(status_code=404, detail="Stakeholder Names not found.")
    
    return {'response':stakeholder_names}


async def stakeholder_names_by_id(id: int):
    """
    Get stakeholder name by ID.
    :param id: int
    return: Dict
    """
    try: 

        stakeholder_name = SQL_connection(f"SELECT * FROM terramo_data.stakeholder_names WHERE STAKEHOLDER_NAME_ID = {id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if stakeholder_name is None:
        raise HTTPException(status_code=404, detail="Stakeholder Name not found.")
    return stakeholder_name[0]
