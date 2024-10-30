from contextlib import asynccontextmanager
from typing import List, Optional
from bson import ObjectId
from models.models import *
from starlette import status
from fastapi import  APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from .auth import *
import json

router=APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


with open("status_responses.json", "r") as file:
    status_responses = json.load(file)



def get_message(status_code):
    
    return status_responses.get(str(status_code), "Unknown Status")

async def get_user(username: str):
    return await User.find_one({"username": username})

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(401),
            headers={"WWW-Authenticate":"Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(401),
            headers={"WWW-Authenticate":"Bearer"},
        )
    user = await get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(401),
            headers={"WWW-Authenticate":"Bearer"},
        )
    return user

@router.post("/register", response_model=dict)
async def register(user: User):
    if await get_user(user.username):  
        raise HTTPException(status_code=400, detail=get_message(400))

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    await user.insert()
    
    return {"status_code":201, "detail": get_message(201)}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(401),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    token = Token(
        access_token=access_token,
        token_type="bearer"
    )
    
    
    await token.insert()
    return token

# Employee Details

@router.get("/", status_code=200)
async def read_all_employees(current_user: User = Depends(get_current_user)):
    employees = await Employee.find_all().to_list()
    return employees

@router.get("/employee/{emp_id}", status_code=200)
async def read_employee_by_id(emp_id: str = Path(...), current_user: User = Depends(get_current_user)):
    emp = await Employee.get(ObjectId(emp_id))
    if emp:
        return emp.model_dump()  
    raise HTTPException(status_code=404, detail=get_message(404))

@router.get("/employee/name/{emp_name}", status_code=200)
async def read_employee_by_name(emp_name: str, current_user: User = Depends(get_current_user)):
    emp = await Employee.find_one(Employee.name == emp_name)
    if emp:
        return emp.model_dump()
    raise HTTPException(status_code=404, detail=get_message(404))

@router.get("/employees/filter", response_model=List[Employee], status_code=status.HTTP_200_OK)
async def filter_employees(
    name: str = Query(None),
    age: int = Query(None),
    position: str = Query(None),
    salary: float = Query(None),
    year_joined: int = Query(None),
    current_user: User = Depends(get_current_user)
):
    employees = await Employee.filter_employees(name, age, position, salary, year_joined)
    return [emp.model_dump() for emp in employees]


@router.post("/")
async def add_emp(new_emp: Employee, current_user: User = Depends(get_current_user)):
    try:
        await new_emp.insert()
        return {"status_code": 201, "id": str(new_emp.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=get_message(500))

@router.put("/employee/{emp_id}", status_code=200)
async def update_employee(emp_id: str, updated_emp: Employee, current_user: User = Depends(get_current_user)):
    emp_id_obj = ObjectId(emp_id)
    emp_obj = await Employee.get(emp_id_obj)  
    if not emp_obj:
        raise HTTPException(status_code=404, detail=get_message(404))
    await emp_obj.set(updated_emp.model_dump())
    return {"status_code": 200, "detail": get_message(200)}

@router.delete("/employee/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(emp_id: str, current_user: User = Depends(get_current_user)):
    emp_id_obj = ObjectId(emp_id)
    emp = await Employee.get(emp_id_obj)  
    if not emp:
        raise HTTPException(status_code=404, detail=get_message(404))
    await emp.delete()
    return {"status_code": 204, "detail": get_message(204)}





