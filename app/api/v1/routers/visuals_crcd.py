import asyncio
from fastapi import Request
from app.api.v1.routers.organisations import get_organization_by_id
from app.api.v1.routers.stakeholder import stakeholder_by_id
from app.api.v1.routers.esg_measure_descriptions import esg_measure_descriptions_by_id
from app.api.v1.routers.esg_measures import esg_measures_by_id
from app.api.v1.routers.esg_questionaires import esg_questionaires_by_id
from app.api.v1.routers.esg_questionaire_answers import esg_questionaire_answers_by_id
from app.api.v1.routers.stakeholder_names import stakeholder_names_by_id
from app.api.v1.routers.persons import persons_by_id


endpoint_dict = {
    "organization_id": get_organization_by_id,
    "stakeholder_id": stakeholder_by_id,
    "esg_measure_description_id": esg_measure_descriptions_by_id,
    "esg_measure_id": esg_measures_by_id,
    "esg_questionaries_id": esg_questionaires_by_id,
    "esg_questionarie_answers_id": esg_questionaire_answers_by_id,
    "stakeholder_names_id": stakeholder_names_by_id,
    "persons_id": persons_by_id
}

async def process_data(json_body):

    response = {}
    for key, value in json_body.items():
        if key in endpoint_dict:
            func = endpoint_dict[key]
            if isinstance(value, list):
                try:
                    int_values = [int(id_str) for id_str in value]
                except ValueError:
                    response[key] = "Invalid ID in list"
                    continue
                tasks = [func(id_int) for id_int in int_values]
                try:
                    results = await asyncio.gather(*tasks)
                    response[key] = [result for result in results if result]
                except Exception as e:
                    response[key] = f"Error: {str(e)}"
            else:
                try:
                    value_int = int(value)
                except ValueError:
                    response[key] = "Invalid ID"
                    continue
                try:
                    response[key] = await func(value_int)
                except Exception as e:
                    response[key] = f"Error: {str(e)}"
        else:
            response[key] = "Invalid key"
            
    return response


async def visuals_crcd(request: Request):
    """
    Sample request 

    json_body = {
        "organization_id": 1,
        "stakeholder_id": ["5", "7", "8"],
        "esg_measure_description_id" : 1,
        "esg_measure_id" : 1,
        "esg_questionaries_id" : 1,
        "esg_questionarie_answers_id" : 1,
        "stakeholder_names_id" : 1        
        }

    """
    json_body = await request.json()

    response = process_data(json_body)

    return response