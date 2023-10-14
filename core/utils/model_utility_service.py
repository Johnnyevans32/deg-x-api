import asyncio
import math
import re
from datetime import datetime
from enum import Enum
from functools import lru_cache, partial
from typing import Any, Type, TypeVar
from bson.objectid import ObjectId
from pymongo import DESCENDING, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    UpdateResult,
)

from core.db import db
from core.utils.loggly import logger
from core.utils.response_service import MetaDataModel
from core.utils.utils_service import Utils


class UpdateAction(str, Enum):
    SET = "$set"
    PUSH = "$push"
    PULL = "$pull"


class ModelUtilityService:
    T = TypeVar("T")

    @lru_cache(16)
    @staticmethod
    def __pluralize(noun: str) -> str:
        if re.search("[xz]$", noun):
            return re.sub("$", "es", noun)
        elif re.search("[s]$", noun):
            return re.sub("$", "", noun)
        elif re.search("[y]$", noun):
            return re.sub("$", "", noun)
        elif re.search("[^aeioudgkprt]h$", noun):
            return re.sub("$", "es", noun)
        elif re.search("[aeiou]$", noun):
            return re.sub("$", "ies", noun)
        else:
            return noun + "s"

    @staticmethod
    async def paginate_data(
        generic_class: Type[T],
        query: dict[str, Any],
        page_num: int,
        page_size: int,
        sort_field: str = "createdAt",
    ) -> tuple[list[T], MetaDataModel]:
        loop = asyncio.get_event_loop()
        model = db[generic_class.__name__.lower()]

        """returns a set of documents belonging to page number `page_num`
        where size of each page is `page_size`.
        """
        # Calculate number of documents to skip
        skips = page_size * (page_num - 1)

        total_count = await loop.run_in_executor(None, model.count_documents, query)

        total_page = math.ceil(total_count / page_size)

        prev_page = (lambda: page_num - 1 if (page_num - 1) > 0 else None)()
        next_page = (lambda: page_num + 1 if (page_num + 1) <= total_page else None)()

        documents = (
            (await loop.run_in_executor(None, model.find, query))
            .sort(sort_field, DESCENDING)
            .skip(skips)
            .limit(page_size)
        )

        # Skip and limit

        result = list(documents)
        result_count = len(result)

        meta_data = {
            "page": page_num,
            "perPage": page_size,
            "total": total_count,
            "pageCount": result_count,
            "previousPage": prev_page,
            "nextPage": next_page,
        }

        # Return documents
        return (
            list(
                map(
                    partial(Utils.to_class_object, generic_class),
                    result,
                )
            )
            if result
            else result,
            MetaDataModel(**meta_data),
        )

    @staticmethod
    async def populate_and_paginate_data(
        generic_class: Type[T],
        query: dict[str, Any],
        fields: list[str],
        page_num: int = 1,
        page_size: int = 10,
        sort_field: str = "createdAt",
    ) -> tuple[list[T], MetaDataModel]:
        model = db[generic_class.__name__.lower()]
        # Calculate number of documents to skip
        skips = page_size * (page_num - 1)

        pipeline = [
            {
                "$facet": {
                    "pipelineData": [
                        {
                            "$match": query,
                        },
                        {"$sort": {sort_field: DESCENDING}},
                        {"$skip": skips},
                        {"$limit": page_size},
                    ],
                    "pipelineCount": [
                        {
                            "$match": query,
                        },
                        {"$skip": skips},
                        {"$limit": page_size},
                        {"$count": "pageCount"},
                    ],
                    "totalCount": [
                        {
                            "$match": query,
                        },
                        {"$count": "count"},
                    ],
                }
            }
        ]

        for field in fields:
            lookup = [
                {
                    "$lookup": {
                        "from": field.split(".")[-1].lower(),
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {
                    "$unwind": {
                        "path": f"${field}",
                        "includeArrayIndex": "arrayIndex",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
            ]
            for i, pl in enumerate(lookup):
                pipeline[0]["$facet"]["pipelineData"].insert(1 + i, pl)
        loop = asyncio.get_event_loop()
        aggregation_result = list(
            await loop.run_in_executor(None, model.aggregate, pipeline)
        )

        result = aggregation_result[0]["pipelineData"]
        pipeline_count = aggregation_result[0]["pipelineCount"]
        pipeline_total_count = aggregation_result[0]["totalCount"]

        result_count = pipeline_count[0]["pageCount"] if len(pipeline_count) > 0 else 0
        total_count = (
            pipeline_total_count[0]["count"] if len(pipeline_total_count) > 0 else 0
        )

        total_page = math.ceil(total_count / page_size)

        prev_page = (lambda: page_num - 1 if (page_num - 1) > 0 else None)()
        next_page = (lambda: page_num + 1 if (page_num + 1) <= total_page else None)()

        meta_data = {
            "page": page_num,
            "perPage": page_size,
            "total": total_count,
            "pageCount": result_count,
            "previousPage": prev_page,
            "nextPage": next_page,
        }
        # And there goes the populate function just as mongoose populate works 🚀🕺🏽
        return (
            list(
                map(
                    partial(Utils.to_class_object, generic_class),
                    result,
                )
            )
            if result
            else result,
            MetaDataModel(**meta_data),
        )

    @staticmethod
    async def find_one_and_populate(
        generic_class: Type[T],
        query: dict[str, Any],
        fields: list[str],
    ) -> T | None:
        model = db[generic_class.__name__.lower()]
        pipeline: list[dict[str, Any]] = [
            {
                "$match": query,
            },
        ]
        for field in fields:
            lookup: list[dict[str, Any]] = [
                {
                    "$lookup": {
                        "from": field.split(".")[-1].lower(),
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {
                    "$unwind": {
                        "path": f"${field}",
                        "includeArrayIndex": "arrayIndex",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
            ]
            pipeline += lookup

        pipeline += [{"$limit": 1}]
        loop = asyncio.get_event_loop()
        result = list(await loop.run_in_executor(None, model.aggregate, pipeline))

        aggregation_result = None
        if result:
            [aggregation_result] = result

        return generic_class(**aggregation_result) if aggregation_result else None

    @staticmethod
    async def find_and_populate(
        generic_class: Type[T],
        query: dict[str, Any],
        fields: list[str],
    ) -> list[T]:
        model = db[generic_class.__name__.lower()]
        loop = asyncio.get_event_loop()
        pipeline = [
            {
                "$match": query,
            },
        ]

        for field in fields:
            lookup = [
                {
                    "$lookup": {
                        "from": field.split(".")[-1].lower(),
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {"$unwind": {"path": f"${field}"}},
            ]
            pipeline += lookup
        results = await loop.run_in_executor(None, model.aggregate, pipeline)

        if not results:
            return []

        return list(
            map(
                partial(Utils.to_class_object, generic_class),
                results,
            )
        )

    @staticmethod
    async def find_one(generic_class: Type[T], query: dict[str, Any]) -> T | None:
        model = db[generic_class.__name__.lower()]
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, model.find_one, query)

        return generic_class(**result) if result else None

    @staticmethod
    def non_async_find_one(generic_class: Type[T], query: dict[str, Any]) -> T | None:
        model = db[generic_class.__name__.lower()]
        result = model.find_one(query)

        return generic_class(**result) if result else None

    @staticmethod
    async def find(generic_class: Type[T], query: dict[str, Any]) -> list[T]:
        loop = asyncio.get_event_loop()
        model = db[generic_class.__name__.lower()]

        results = await loop.run_in_executor(None, model.find, query)
        if not results:
            return []

        return list(
            map(
                partial(Utils.to_class_object, generic_class),
                results,
            )
        )

    @staticmethod
    async def model_create(
        generic_class: Type[T],
        record: dict[str, Any],
        session: ClientSession | None = None,
    ) -> T:
        model = db[generic_class.__name__.lower()]
        loop = asyncio.get_event_loop()

        created_record = await loop.run_in_executor(
            None, model.insert_one, record, False, session
        )

        def find_one() -> Any | None:
            return model.find_one(
                {"_id": ObjectId(created_record.inserted_id)}, session=session
            )

        res = await loop.run_in_executor(None, find_one)

        return generic_class(**res)

    @staticmethod
    async def model_update(
        generic_class: Type[T],
        query: dict[str, Any],
        record: dict[str, Any],
        session: ClientSession | None = None,
    ) -> UpdateResult:
        model = db[generic_class.__name__.lower()]
        record["updatedAt"] = datetime.now()
        loop = asyncio.get_event_loop()

        def update_one() -> UpdateResult:
            return model.update_one(query, {"$set": record}, session=session)

        updated_record = await loop.run_in_executor(None, update_one)

        return updated_record

    @staticmethod
    async def model_find_one_and_update(
        generic_class: Type[T],
        query: dict[str, Any],
        record: dict[str, Any],
        upsert: bool = False,
        session: ClientSession | None = None,
        updateAction: UpdateAction = UpdateAction.SET,
    ) -> T | None:
        loop = asyncio.get_event_loop()
        model = db[generic_class.__name__.lower()]
        update_payload = {"$set": {"updatedAt": datetime.now()}}
        if updateAction == UpdateAction.SET:
            update_payload["$set"] = {**record, **update_payload["$set"]}
        else:
            update_payload[updateAction.value] = record

        def find_one_and_update() -> Any:
            return model.find_one_and_update(
                query,
                update_payload,
                upsert=upsert,
                return_document=ReturnDocument.AFTER,
                session=session,
            )

        updated_record = await loop.run_in_executor(None, find_one_and_update)

        return generic_class(**updated_record) if updated_record else None

    @staticmethod
    async def model_find_one_or_create(
        generic_class: Type[T], query: dict[str, Any], record: dict[str, Any]
    ) -> T:
        loop = asyncio.get_event_loop()
        model = db[generic_class.__name__.lower()]

        def find_one_and_update() -> Any:
            return model.find_one_and_update(
                query,
                {"$setOnInsert": record},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

        result = await loop.run_in_executor(None, find_one_and_update)

        return generic_class(**result)

    @staticmethod
    async def model_create_many(
        generic_class: Type[T],
        records: list[Any],
        session: ClientSession | None = None,
    ) -> InsertManyResult | None:
        try:
            loop = asyncio.get_event_loop()
            model = db[generic_class.__name__.lower()]
            created_records = await loop.run_in_executor(
                None,
                model.insert_many,
                records,
                False,
                False,
                session,
            )

            return created_records
        except Exception as e:
            logger.error(f"Error inserting many records - {str(e)}")
            raise e

    @staticmethod
    async def model_hard_delete(
        generic_class: Type[T], query: dict[str, Any]
    ) -> DeleteResult:
        loop = asyncio.get_event_loop()
        model = db[generic_class.__name__.lower()]
        deleted_record = await loop.run_in_executor(None, model.delete_one, query)

        return deleted_record
