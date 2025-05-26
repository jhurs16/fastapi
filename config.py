from os import environ, path

import toml
from dotenv import load_dotenv

lcsBasedir = path.abspath(path.dirname(__file__))


def get_toml(
    ivsVar: str, ivsBase: bool = False, ivsDefault: str = None, ivsTable: str = None
):
    lsoConfig = toml.load(path.join(lcsBasedir, "config.toml"))
    if ivsBase:
        ovsValue = lsoConfig["base"][ivsVar]
    else:
        environment = get_env("REST_API_ENVIRONMENT")
        if environment is None:
            environment = "testing"
        ovsValue = lsoConfig[ivsTable][environment][ivsVar]
    return ovsValue or ivsDefault


def get_env(ivsVar: str, ivsDefault: str = None):
    load_dotenv(path.join(lcsBasedir, ".env"))
    return environ.get(ivsVar) or ivsDefault
