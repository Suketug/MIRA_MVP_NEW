# auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from .auth_service import AuthService
from .token_utils import create_access_token
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, decode
from ..models.user_models import UserOut, UserLogin, RegisterUser, UserUpdate
from ..models.roles import UserRole
from datetime import timedelta
from ..db.user_db import DatabaseManager
from dotenv import load_dotenv
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from logger import get_logger


load_dotenv()

logger = get_logger(__name__)

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')  # Load this from your environment variables

router = APIRouter()
db_manager = DatabaseManager(BASE_ID, API_KEY, TABLE_NAME)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

def get_token(username: str) -> dict:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    logger.debug("Generated access token for username %s: %s", username, access_token)
    return {"access_token": access_token, "token_type": "bearer"}

# auth.py
@router.post("/register/")
async def register_user(user: RegisterUser, auth_service: AuthService = Depends(AuthService)):
    logger.debug("Received register request data: %s", user.dict())  # Print request data

    if user.password != user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    existing_user = db_manager.get_user(username=user.username)
    logger.debug("Retrieved existing user from database: %s", existing_user)  # Add this line
    if existing_user:
        logger.debug("User with username:%s already exists", user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = auth_service.get_password_hash(user.password)
    logger.debug("Password hashed successfully for username:%s", user.username)

    # Create the full_name field by combining first_name and last_name
    full_name = f"{user.first_name} {user.last_name}"

    user_data = {
                    "Username": user.username, 
                    "Password": hashed_password, 
                    "Full Name": full_name, 
                    "User Type": user.role, 
                }  

    db_manager.add_user(user_data)
    logger.debug("User with username:%s added successfully", user.username)
    
    return get_token(user.username)

@router.post("/login/", response_model=dict)
async def login(user: UserLogin, auth_service: AuthService = Depends(AuthService)):
    logger.debug("Received login request data: %s", user.dict())

    db_user = db_manager.get_user(username=user.username)
    logger.debug("Retrieved user data from database: %s", db_user)

    db_user_password = db_user.get("fields", {}).get("Password")
    if not db_user_password:
        logger.error("No password found for user: %s", user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No password found")

    if not auth_service.verify_password(user.password, db_user_password):
        logger.warning("Incorrect username or password for user: %s", user.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    logger.debug("User %s logged in successfully", user.username)
    return get_token(user.username)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token == "undefined" or token.count('.') != 2:
        logger.error("Invalid or undefined token received: %s", token)
        raise HTTPException(status_code=401, detail="Invalid token")
    logger.debug("Received token: %s", token)  # Log the received token
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        logger.debug("Decoded username from token: %s", username)  # Log the decoded username
    except PyJWTError as e:
        logger.error("Error decoding token: %s", str(e))  # Log the error
        raise credentials_exception
    return username

@router.get("/users/me/", response_model=UserOut)
async def read_users_me(request: Request, current_user: str = Depends(get_current_user)):
    auth_header = request.headers.get('Authorization')
    logger.debug("Received Authorization header: %s", auth_header)
    logger.debug("Received request to fetch profile for user: %s", current_user)
    db_user = db_manager.get_user(username=current_user)
    if db_user:
        fields = db_user.get("fields", {})
        id = db_user.get("id")
        # Debugging statement
        logger.debug("Retrieved record ID: %s", id)
        username = fields.get("Username")
        if username is None:
            logger.warning("Username is None for user: %s. Full record: %s", current_user, db_user)
        # Split the full name into first and last names
        full_name = fields.get("Full Name", "")
        first_name, last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, "")
        logger.debug("Retrieved user record: %s", db_user)
        return UserOut(
            record_id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole(fields.get("User Type", "Consumer"))  # Assuming "Consumer" is a valid UserRole
        )
    raise HTTPException(status_code=404, detail="User not found")

def get_current_user_role(token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    user = db_manager.get_user(username=username)
    if user:
        return UserRole(user["User Type"])  
    raise HTTPException(status_code=401, detail="User not found")

# auth.py
@router.patch("/users/update/{record_id}")
async def update_current_user(record_id: str, user_data: dict, current_user: str = Depends(get_current_user)):
    logger.debug("Received request to update profile for user: %s", current_user)

    # Since record_id is already available, there is no need to fetch the user again

    # Prepare the data for updating the user in Airtable
    data = {
        "records": [
            {
                "id": record_id,
                "fields": {
                    "Phone Number": user_data.get("phone_number"),
                }
            }
        ]
    }

    # Log the final data to be sent to Airtable
    logger.debug("Final data to update in Airtable: %s", data)

    # Update the user in the database
    updated_user = db_manager.update_user(record_id, data)
    if updated_user:
        logger.debug("User with username:%s updated successfully", current_user)
        return updated_user

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occurred while updating the user")

@router.get("/admin/dashboard/")
async def admin_dashboard(current_user_role: UserRole = Depends(get_current_user_role)):
    if current_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"detail": "Welcome to the admin dashboard!"}
