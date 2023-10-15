from typing import Any, Generic, Literal, Optional, TypeVar

import certifi
from bson.timestamp import Timestamp
from pydantic import BaseModel, Field, ConfigDict
from pymongo import MongoClient
from pymongo.change_stream import DatabaseChangeStream
from pymongo.database import Database

from core.config import settings
from core.depends.get_object_id import PyObjectId


def get_db() -> tuple[MongoClient[Any], Database[Any], DatabaseChangeStream[Any]]:
    db_name = settings.DATABASE_NAME
    uri = settings.DATABASE_URI
    client = MongoClient[Any](uri, tlsCAFile=certifi.where(), appname="deg-x")
    db = client[db_name]
    cursor = db.watch()
    return client, db, cursor


client, db, cursor = get_db()

T = TypeVar("T")


class Ns(BaseModel):
    db: str
    coll: str


class UpdateDesc(BaseModel):
    updatedFields: dict[str, Any]
    removedFields: Optional[list[str]] = None
    truncatedArrays: Optional[list[str]] = None


class CursorModel(BaseModel, Generic[T]):
    id: dict[str, str] = Field(alias="_id")
    operationType: Literal["insert", "delete", "update"]
    clusterTime: Timestamp
    fullDocument: Optional[T] = None
    ns: Ns
    documentKey: dict[str, PyObjectId]
    updateDescription: Optional[UpdateDesc] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)


def mongo_data_streaming() -> None:
    from apps.wallet.interfaces.walletasset_interface import WalletAssetOut

    doc = next(cursor)
    document = CursorModel[WalletAssetOut](**doc)

    print("document", document, doc)
