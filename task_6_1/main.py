import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

VALID_USERNAME = "admin"
VALID_PASSWORD = "secret"


def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    username_ok = secrets.compare_digest(credentials.username, VALID_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/login")
def login(username: str = Depends(check_credentials)):
    return {"message": "You got my secret, welcome"}
