from fastapi import HTTPException
from app.api.v1.routers.excel_upload import read_config, connect_to_database
from app.logging import logger
from helper_fn import SQL_connection


async def esg_measures():
    """
    Get all ESG measures.
    return: List[Dict]
    """
    try : 

        esg_measures = SQL_connection("select * from terramo_data.esg_measures")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_measures is None:
        raise HTTPException(status_code=404, detail="ESG Measures not found.")
    
    return {'response':esg_measures}



async def esg_measures_by_id(id: int):
    """
    Get ESG measure by ID.
    :param id: int
    return: Dict
    """
    try: 
        esg_measure = SQL_connection(f"SELECT * FROM terramo_data.esg_measures WHERE ESG_MEASURE_ID = {id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_measure is None:
        raise HTTPException(status_code=404, detail="ESG Measure not found.")
    return esg_measure[0]
