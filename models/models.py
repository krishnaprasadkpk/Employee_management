from typing import List, Optional
from pydantic import  Field, constr, field_validator
from beanie import Document



class Employee(Document):
    name: str = Field(...,title="Employee Name",min_length=1, max_length=100)
    # emp_id: int = Field(..., title="Employee ID", gt=0)
    age: int = Field(...,title="Employee Age",ge=18, le=65)
    position: str = Field(...,title="Employee Position", min_length=1)
    salary: float = Field(..., title="Employee Salary", gt=0)
    year_joined : int = Field(...,title="Year Joined", ge=2000, lt=2025)

    '''
    @field_validator("name")
    def name_validation(cls,v):
        if any(chr.isdigit() for chr in v):
            raise ValueError("Name should not contain numbers")
        return v
    '''

    class Settings:
        collection = "emp_data"

    @classmethod
    async def filter_employees(cls, name: Optional[str] = None, age: Optional[int] = None, 
                               position: Optional[str] = None, salary: Optional[float] = None, 
                               year_joined: Optional[int] = None) -> List["Employee"]:
        query = {}
        if name:
            query["name"] = name
        if age:
            query["age"] = age
        if position:
            query["position"] = position
        if salary:
            query["salary"] = salary
        if year_joined:
            query["year_joined"] = year_joined

        return await cls.find(query).to_list()

class User(Document):
    username: str
    password: str

    class Settings:
        collection = "users"

    '''
    @field_validator("password")
    def password_validation(cls, v):
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

    '''
    


class Token(Document):
    access_token: str
    token_type: str

    class Settings:
        collection = "token_data"