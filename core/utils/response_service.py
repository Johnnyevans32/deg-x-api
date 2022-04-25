from typing import Any, Optional

from fastapi import Response
from pydantic import BaseModel


def get_response_model(base: object, rep: str) -> Any:
    class DynamicResponse(ResponseModel):
        data: Optional[base]  # type: ignore
        metaData: Optional[MetaDataModel]

    return type(rep, (DynamicResponse,), {})


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
            429: "give us a break boss, too much requests sent already",
            500: "shit, we played too much, we are fixing it now",
            501: "we are working to make this implemented, give us some time please",
            503: "api maintenance undergoing",
        }

    def send_response(
        self,
        res: Response,
        status_code: int,
        message: str = None,
        data=None,
        meta=None,
        use_class_message: bool = False,
    ) -> Any:
        res.status_code = status_code
        if use_class_message:
            message = self.status_code_message[status_code]
        response = {"data": data, "message": message}
        if meta:
            response["metaData"] = meta
        return response


class ResponseModel(BaseModel):
    message: str


class MetaDataModel(BaseModel):
    page: Optional[int]
    perPage: Optional[int]
    total: Optional[int]
    pageCount: Optional[int]
    previousPage: Optional[int]
    nextPage: Optional[int]
