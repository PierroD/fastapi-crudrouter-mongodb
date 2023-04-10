The MongoModel is one of the two main classes of this package. It is a Pydantic model that inherits from the Pydantic BaseModel and adds a few extra fields to it. The MongoModel is used to define the structure of your mongo documents. It is also used to generate the OpenAPI schema for your routes.

The MongoModel is a Pydantic model, so you can use all the features of Pydantic models. You can also use the Pydantic Field class to define the fields of your model. The MongoModel adds a few extra fields to the Pydantic model.

!!! note "The MongoModel adds the following fields to the Pydantic model"
    ```py
    id: Optional[MongoObjectId] = Field()
    ```

    The id field is an optional field that is used to store the id of the document in the database. It is an instance of the MongoObjectId class, which is a subclass of the Pydantic ObjectId class. The id field is automatically generated by the database when you create a new document.

    It will be automatically translated to an "_id" in MongoDB, and returned as "id" in the response to match the RESTfull specifications.

!!! warning "Make sure to build your model like below"

    ```py
    class MyModel(MongoModel):
        id: Optional[MongoObjectId] = Field()
        my_field: str
    ```

!!! tip "More infos could be found in the following github issue"

    [https://github.com/tiangolo/fastapi/issues/1515](https://github.com/tiangolo/fastapi/issues/1515)