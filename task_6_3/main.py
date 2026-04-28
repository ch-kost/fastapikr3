import os
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")

if MODE not in {"DEV", "PROD"}:
    raise RuntimeError("MODE must be DEV or PROD")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
security = HTTPBasic()


def docs_auth(credentials: HTTPBasicCredentials = Depends(security)):
    username_ok = secrets.compare_digest(credentials.username, DOCS_USER)
    password_ok = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid documentation credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/ping")
def ping():
    return {"message": "pong"}


if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    def custom_docs(username: str = Depends(docs_auth)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Protected docs")

    @app.get("/openapi.json", include_in_schema=False)
    def custom_openapi(username: str = Depends(docs_auth)):
        return get_openapi(title=app.title, version=app.version, routes=app.routes)
else:
    @app.get("/docs", include_in_schema=False)
    def prod_docs():
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    @app.get("/openapi.json", include_in_schema=False)
    def prod_openapi():
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    @app.get("/redoc", include_in_schema=False)
    def prod_redoc():
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
