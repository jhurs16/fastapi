from fastapi import HTTPException
from helper_fn import SQL_connection



async def stakeholder():
    """
    Get all stakeholders.
    return: List[Dict]
    """
    try: 
        stakeholder = SQL_connection("select * from terramo_data.stakeholder")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if stakeholder is None:
        raise HTTPException(status_code=404, detail="Stakeholder not found.")
    
    return {'response':stakeholder}



async def stakeholder_by_id(id: int):
    """
    Get stakeholder by ID.
    :param id: int
    return: Dict
    """
    try: 
        stakeholder = SQL_connection(f"SELECT * FROM terramo_data.stakeholder WHERE STAKEHOLDER_ID = {id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if stakeholder is None:
        raise HTTPException(status_code=404, detail="Stakeholder not found.")
    return stakeholder[0]