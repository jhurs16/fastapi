from fastapi import HTTPException
from app.logging import logger
from helper_fn import SQL_connection

async def esg_measure_descriptions():
    """
    Get all ESG measure descriptions.
    return: List[Dict]
    """
    try: 
        esg_measure_descriptions = SQL_connection("select * from terramo_data.esg_measure_descriptions")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_measure_descriptions is None:
        raise HTTPException(status_code=404, detail="ESG Measure Descriptions not found.")
    
    return {'response':esg_measure_descriptions}


async def esg_measure_descriptions_by_id(id: int):
    """
    Get ESG measure description by ID.
    :param id: int
    return: Dict
    """
    try: 
        query =  f"SELECT * FROM terramo_data.esg_measure_descriptions WHERE ESG_MEASURE_DESCRIPTION_ID = {id}"
        esg_measure_description = SQL_connection(query)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")
 
    if esg_measure_description is None:
        raise HTTPException(status_code=404, detail="ESG Measure Description not found.")
    return esg_measure_description[0]

