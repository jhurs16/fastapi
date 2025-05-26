from fastapi import HTTPException
from app.api.v1.routers.excel_upload import read_config, connect_to_database
from helper_fn import SQL_connection


async def esg_questionaire_answers():
    """
    Get all ESG questionaire answers.
    return: List[Dict]
    """
    try: 
        esg_questionaire_answers = SQL_connection("select * from terramo_data.esg_questionaire_answers")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_questionaire_answers is None:
        raise HTTPException(status_code=404, detail="ESG Questionaire Answers not found.")
    
    return {'response':esg_questionaire_answers }



async def esg_questionaire_answers_by_id(id: int):
    """
    Get ESG questionaire answer by ID.
    :param id: int
    return: Dict
    """
    try: 
        esg_questionaire_answer =  SQL_connection(f"SELECT * FROM terramo_data.esg_questionaire_answers WHERE ESG_QUESTIONAIRE_ANSWER_ID = {id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if esg_questionaire_answer is None:
        raise HTTPException(status_code=404, detail="ESG Questionaire Answer not found.")
    return esg_questionaire_answer[0]