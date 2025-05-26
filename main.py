from pathlib import Path
from dotenv import load_dotenv
import uvicorn,os,config,logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Server
from fastapi.staticfiles import StaticFiles
from app.api.v1 import v1

from contextlib import asynccontextmanager
# from app.db.database import get_database  # See [app/db/database.py](app/db/database.py)

# Load environment variables
load_dotenv() 

app = FastAPI()
lcsBaseDir = os.path.abspath(os.path.dirname(__name__))
log_file = os.path.join(lcsBaseDir, "terramo_importer.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

date_formats = ['%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d']

serverMain = Server(
    url=config.get_toml(ivsVar="server_url", ivsBase=True),
    description=config.get_toml(ivsVar="server_description", ivsBase=True),
)
version = config.get_env("REST_API_VERSION", "0.1.0")

app = FastAPI()
static = Path(__name__).resolve().parent / "static/public/"
app.mount("/static", StaticFiles(directory=static, html=True), name="static")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=config.get_toml(ivsVar="api_title", ivsBase=True),
        version=version,
        description=config.get_toml(ivsVar="api_description", ivsBase=True),
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1.router)

# @app.on_event("startup")
# async def startup():
#     print("starting api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    # Initialize DB, caches, etc.
    yield
    print("App is shutting down...")
    # Clean up stuff

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)))
