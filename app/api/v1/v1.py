from fastapi import APIRouter
from fastapi.applications import FastAPI
from fastapi.routing import APIRoute
from app.api.v1.routers import default
from app.api.v1.schema import HttpError
from app.api.v1.routers import (organisations,excel_upload,esg_measures,
                                esg_measure_descriptions,esg_questionaires,esg_questionaire_answers,
                                persons,stakeholder,stakeholder_names,visuals_crcd, customers)

from app.api.v1.auth.schema import (GetOrganizationsResponse, Organization, GetEsgMeasuresResponse,Esg_measures,
                                    Esg_Measure_Description,GetEsgMeasureDescriptionsResponse,Esg_questionaires, Stakeholder,
                                    getEsgQuestionairesResponse,Esg_Questionaires_answers,getEsg_Questionaires_answers,
                                    getPerson,Person, getStakeholder,Stakeholder,Stakeholder_names,getStakeholder_names,Customer, GetCustomersResponse
                                   
                                    )
from app.api.Embeddings import server

router = APIRouter(
    prefix="/v1",
    responses={
        201: {"description": "Resource created"},
        301: {"description": "Resource moved"},
        400: {"model": HttpError, "description": "Error: Malformed request"},
        401: {"description": "Unauthorized"},
        403: {"model": HttpError, "description": "Error: Access forbidden"},
        404: {"model": HttpError, "description": "Error: Not found"},
        409: {"model": HttpError, "description": "Conflict - Data validation failed"},
        422: {"description": "Error: Unprocessable entity"},
        500: {"description": "Error: Unexpected error"},
        503: {"description": "Error: Service unavailable"},
        "default": {"description": "Error: Unexpected error"},
    },
)

router.include_router(default.router)
# router.include_router(customers.router, prefix="/customers", tags=["Customers"])


@router.get("/")
async def root():
    return {"message": "REST API"}


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute) and route.operation_id is None:
            route.operation_id = route.name


use_route_names_as_operation_ids(router)


router.post("/upload")(excel_upload.upload_excel)
router.get("/organisation", response_model= GetOrganizationsResponse)(organisations.get_organization)
router.get("/organisation/{org_id}", response_model= Organization)(organisations.get_organization_by_id)
router.get("/esg_measures", response_model= GetEsgMeasuresResponse)(esg_measures.esg_measures)
router.get("/esg_measures/{id}", response_model= Esg_measures)(esg_measures.esg_measures_by_id)
router.get("/esg_measure_descriptions", response_model=GetEsgMeasureDescriptionsResponse)(esg_measure_descriptions.esg_measure_descriptions)
router.get("/esg_measure_descriptions/{id}", response_model=Esg_Measure_Description )(esg_measure_descriptions.esg_measure_descriptions_by_id)
router.get("/esg_questionaires",response_model=getEsgQuestionairesResponse )(esg_questionaires.esg_questionaires)
router.get("/esg_questionaires/{id}", response_model= Esg_questionaires)(esg_questionaires.esg_questionaires_by_id)
router.get("/esg_questionaire_answers", response_model=getEsg_Questionaires_answers)(esg_questionaire_answers.esg_questionaire_answers)
router.get("/esg_questionaire_answers/{id}", response_model=Esg_Questionaires_answers)(esg_questionaire_answers.esg_questionaire_answers_by_id)
router.get("/persons", response_model= getPerson)(persons.persons)
router.get("/persons/{id}", response_model=Person)(persons.persons_by_id)
router.get("/stakeholder", response_model=getStakeholder)(stakeholder.stakeholder)
router.get("/stakeholder/{id}", response_model=Stakeholder)(stakeholder.stakeholder_by_id)
router.get("/stakeholder_names", response_model=getStakeholder_names)(stakeholder_names.stakeholder_names)
router.get("/stakeholder_names/{id}", response_model=Stakeholder_names)(stakeholder_names.stakeholder_names_by_id)
# router.post("/visuals/crcd")(visuals_crcd.visuals_crcd)
router.post("/visuals/crcd")(server.create_embed_info)
# customers
router.get("/customers", response_model= GetCustomersResponse)(customers.customers)

