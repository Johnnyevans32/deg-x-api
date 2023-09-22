import json
from typing import Any, Generic, Optional, TypeVar
from bson.objectid import ObjectId
from fastapi import Response
from pydantic import BaseModel
from pydantic.generics import GenericModel


def get_response_model(base: object, rep: str) -> Any:
    class DynamicResponse(ResponseModelT):
        data: Optional[base]  # type: ignore
        metaData: Optional[MetaDataModel]

    return type(rep, (DynamicResponse,), {})


T = TypeVar("T")


class ResponseModelT(BaseModel):
    message: str


class MetaDataModel(BaseModel):
    page: Optional[int]
    perPage: Optional[int]
    total: Optional[int]
    pageCount: Optional[int]
    previousPage: Optional[int]
    nextPage: Optional[int]


class ResponseModel(GenericModel, Generic[T]):
    message: str
    data: T | None = None
    metaData: MetaDataModel | None = None

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda oid: str(oid),
        }


class ResponseService:
    def __init__(self) -> None:
        self.status_code_message = {
            400: "we don't allow this, go back to the docs, please",
            401: "Thou shalt not pass!",
            402: "please kindly fund your account to complete request",
            403: "you are out of bounds",
            404: "hmm, one of our engineers is responsible for this or is it you?",
            405: "wrong request method, go back to the docs, please",
            409: "this is conflicting with our resources",
            422: "unprocessable entity",
            429: "give us a break boss, too much requests sent already",
            500: "shit, we played too much, we are fixing it now",
            501: "we are working to make this implemented, give us some time please",
            503: "api maintenance undergoing",
        }

    def send_response(
        self,
        res: Response,
        status_code: int,
        message: str,
        data: T | None = None,
        meta: MetaDataModel | None = None,
        use_class_message: bool = False,
    ) -> ResponseModel[T]:
        res.status_code = status_code
        if use_class_message:
            message = self.status_code_message[status_code]
        response = ResponseModel[T](message=message, data=data)
        if meta:
            response.metaData = meta
        return response
