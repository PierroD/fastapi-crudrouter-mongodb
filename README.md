<p align="center">
  <img src="./docs/assets/img/logo-long-color.png" height="200" />
</p>
<p align="center">
  ⚡<em> Instant CRUD APIs from Pydantic Models</em> ⚡</br>
  <sub>Build a fully working FastAPI CRUD API in 10 seconds.</sub>
</p>

<div align="center">

![Monthly Downloads Shield Badge](https://img.shields.io/pypi/dm/fastapi-crudrouter-mongodb?color=50b052&style=for-the-badge) ![Weekly Downloads Shield Badge](https://img.shields.io/pypi/dw/fastapi-crudrouter-mongodb?color=50b052&style=for-the-badge) ![Python Version](https://img.shields.io/pypi/v/fastapi-crudrouter-mongodb?color=50b052&style=for-the-badge) ![Python Version](https://img.shields.io/pypi/pyversions/fastapi-crudrouter-mongodb?color=3776AB&style=for-the-badge&logo=python&logoColor=white)

</div>
---

## 🚀 Features

- Auto-generate CRUD endpoints from Pydantic models
- Works with FastAPI
- MongoDB support
- Fully extendable
- Zero boilerplate


--- 
### ⚡ Example

```py
from fastapi import FastAPI
import motor.motor_asyncio
from fastapi_crudrouter_mongodb import (
    ObjectIdType,
    MongoModel,
    CRUDRouter,
)

# Database connection using motor
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/local")

# store the database in a global variable
db = client.local

# Database Model
class UserModel(MongoModel):
    id: ObjectIdType | None = None
    name: str
    email: str

# Instantiating the CRUDRouter
users_router = CRUDRouter(
    model=UserModel,
    db=db,
    collection_name="users",
    prefix="/users",
    tags=["users"],
)

# Instantiating the FastAPI app
app = FastAPI()
app.include_router(users_router)
```

---

## ✨ What you get instantly

|HTTP Verb|Path|Description|
|------|------|------|
|`GET` | /users | `List all users` |
|`POST` | /users | `Create a new user` |
|`GET` | /users/{id} | `Get a user by id` |
|`PUT` | /users/{id} | `Update a user by id` |
|`PATCH` | /users/{id} | `Partially update a  user by id` |
|`DELETE` | /users/{id} | `Delete a user by id` |

!!!tip "No routing. No boilerplate. No repetition."
    The CRUDRouter automatically generates all the necessary routes for your models.

---

## Install

Requires Python `>=3.10`.

```
 pip install fastapi-crudrouter-mongodb
```

---

## Basic Usage

---

I will provide more examples in the future, but for now, here is a basic example of how to use the FastAPI CRUDRouter for Mongodb :seedling:.

```py linenums="1"
from typing import Annotated
from fastapi import FastAPI
from fastapi_crudrouter_mongodb import (
    ObjectId,
    MongoObjectId,
    MongoModel,
    CRUDRouter,
)
import motor.motor_asyncio

# Database connection using motor
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/local")

# store the database in a global variable
db = client.local

# Database Model
class UserModel(MongoModel):
    id: Annotated[ObjectId, MongoObjectId] | None = None
    name: str
    email: str
    password: str


# Instantiating the CRUDRouter, and a lookup for the messages
# a User is a model that contains a list of embedded addresses and related to multiple messages

users_router = CRUDRouter(
    model=UserModel,
    db=db,
    collection_name="users",
    prefix="/users",
    tags=["users"],
)

# Instantiating the FastAPI app
app = FastAPI()
app.include_router(users_router)
```

## 🧠 Why

FastAPI is amazing, but CRUD is repetitive.

This library removes boilerplate so you can focus on your product

## 📚 Documentation

👉 Full docs: [Right here](https://pierrod.github.io/fastapi-crudrouter-mongodb-doc/)


---

### Automatic OpenAPI Documentation

>By default, the CRUDRouter automatically documents all generated routes in accordance with the OpenAPI specification.


![CRUDRouter OpenAPI schema](https://pierrod.github.io/fastapi-crudrouter-mongodb-doc/assets/img/openapi-basic-example.png)


The CRUDRouter can dynamically generate comprehensive documentation based on the provided models.

![CRUDRouter OpenAPI schema details](https://pierrod.github.io/fastapi-crudrouter-mongodb-doc/assets/img/openapi-basic-example-details.png)

---

**Credits** :
- [FastAPI](https://fastapi.tiangolo.com)

- Base projet and idea : [awtkns](https://github.com/awtkns/fastapi-crudrouter)

- Convert \_id to id (for previous versions of Pydantic) : [mclate github guide](https://github.com/tiangolo/fastapi/issues/1515)

- For Pydantic v2 : [Stackoverflow](https://stackoverflow.com/questions/76686267/what-is-the-new-way-to-declare-mongo-objectid-with-pydantic-v2-0)

- [Source code on github](https://github.com/pierrod/fastapi-crudrouter-mongodb)