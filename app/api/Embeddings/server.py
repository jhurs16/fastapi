# filepath: /powerbi-fastapi-app/src/services/powerbi_service.py
import json, subprocess,asyncio
from app.api.Embeddings.config import BaseConfig as Config
from app.api.v1.routers.visuals_crcd import process_data
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


def get_access_token():
    """Fetch Access Token from Azure CLI."""
    try:
        print("🔄 Running Azure CLI Command...")
        result = subprocess.run(
            ["az", "account", "get-access-token", "--resource", "https://analysis.windows.net/powerbi/api"],
            capture_output=True, text=True, shell=True
        )
        print("📌 Return Code:", result.returncode)
        print("📌 STDOUT:", result.stdout)
        print("📌 STDERR:", result.stderr)
        
        if result.returncode != 0:
            raise Exception(f"Failed to fetch token: {result.stderr}")
        
        token_data = json.loads(result.stdout)
        access_token = token_data.get("accessToken")
        
        if not access_token:
            raise Exception("Invalid token received!")
        
        print("✅ Token Retrieved Successfully!")
        return access_token
    except Exception as ex:
        raise Exception(f"Error fetching token: {str(ex)}")


async def create_embed_info(ids : Request):

    """
    sample input json
    {
        "organization_id": 1,
        "stakeholder_id": ["5", "7", "8"],
        "esg_measure_description_id" : 1,
        "esg_measure_id" : 1,
        "esg_questionaries_id" : 1,
        "esg_questionarie_answers_id" : 1,
        "stakeholder_names_id" : 1
    }
    """
    """Create and return embed configuration using the access token."""
    try:
        
        json_body = await ids.json()        
        access_token = get_access_token()

        visuals_dict = await process_data(json_body)

        embed_url = (
            "https://app.fabric.microsoft.com/reportEmbed?"
            f"reportId={Config.REPORT_ID}&autoAuth=true&ctid={Config.TENANT_ID}"
        )


        return {
            "accessToken": access_token,
            "embedUrl": embed_url,
            "reportId": Config.REPORT_ID,
            "visuals_dict" : visuals_dict
        }
    
    except Exception as ex:
        return {"errorMsg": str(ex)}
    
