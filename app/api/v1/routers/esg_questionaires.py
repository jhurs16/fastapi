
from fastapi import HTTPException
from helper_fn import SQL_connection

async def esg_questionaires():
    """
    Get all ESG questionaires.
    return: List[Dict]
    """
    try: 
        esg_questionaires =  SQL_connection("select * from terramo_data.esg_questionaires")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_questionaires is None:
        raise HTTPException(status_code=404, detail="ESG Questionaires not found.")
    
    return {'response' :esg_questionaires}



async def esg_questionaires_by_id(id: int):
    """
    Get ESG questionaire by ID.
    :param id: int
    return: Dict
    """
    try: 
        esg_questionaire = SQL_connection(f"SELECT * FROM terramo_data.esg_questionaires WHERE ESG_QUESTIONAIRE_ID = {id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_questionaire is None:
        raise HTTPException(status_code=404, detail="ESG Questionaire not found.")
    return esg_questionaire[0]
