import math
import re
from datetime import datetime
from functools import lru_cache, partial
from typing import Any, Dict, Tuple, Type, TypeVar

from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from core.db import db
from core.utils.custom_exceptions import UnicornException
from core.utils.response_service import MetaDataModel
from core.utils.utils_service import Utils


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
    def paginate_data(
        generic_class: Type[T],
        query: dict,
        page_num: int,
        page_size: int,
    ) -> Tuple[list[T], MetaDataModel]:
        model = db[generic_class.__name__.lower()]

        """returns a set of documents belonging to page number `page_num`
        where size of each page is `page_size`.
        """
        # Calculate number of documents to skip
        skips = page_size * (page_num - 1)

        total_count = model.count_documents(query)

        print("total_count", total_count)

        total_page = math.ceil(total_count / page_size)

        prev_page = (lambda: page_num - 1 if (page_num - 1) > 0 else None)()
        next_page = (lambda: page_num + 1 if (page_num + 1) <= total_page else None)()

        documents = (
            model.find(query).sort("createdAt", DESCENDING).skip(skips).limit(page_size)
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
        return result, MetaDataModel(**meta_data)

    @staticmethod
    def populate_and_paginate_data(
        generic_class: Type[T],
        query: dict,
        fields: list[str],
        page_num: int = 1,
        page_size: int = 10,
    ) -> Tuple[list[T], MetaDataModel]:
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
                        {"$sort": {"createdAt": DESCENDING}},
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
                        "from": field,
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {"$unwind": {"path": f"${field}"}},
            ]
            pipeline[0]["$facet"]["pipelineData"].insert(1, *lookup)

        aggregation_result = list(model.aggregate(pipeline))

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
        return result, MetaDataModel(**meta_data)

    @staticmethod
    def find_one_and_populate(
        generic_class: Type[T],
        query: dict,
        fields: list[str],
        throw_error_if_none=False,
    ) -> T:
        model = db[generic_class.__name__.lower()]
        pipeline: list[Dict[str, Any]] = [
            {
                "$match": query,
            },
        ]
        for field in fields:
            lookup = [
                {
                    "$lookup": {
                        "from": field,
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {"$unwind": {"path": f"${field}"}},
            ]
            pipeline += lookup

        pipeline += [{"$limit": 1}]
        [aggregation_result] = list(model.aggregate(pipeline))

        if throw_error_if_none and aggregation_result is None:
            raise UnicornException(f"{generic_class.__name__.lower()} record not found")
        return generic_class(**aggregation_result)  # type: ignore [call-arg]

    @staticmethod
    def find_and_populate(
        generic_class: Type[T],
        query: dict,
        fields: list[str],
    ) -> list[T]:
        model = db[generic_class.__name__.lower()]
        pipeline = [
            {
                "$match": query,
            },
        ]

        for field in fields:
            lookup = [
                {
                    "$lookup": {
                        "from": field,
                        "localField": field,
                        "foreignField": "_id",
                        "as": field,
                    }
                },
                {"$unwind": {"path": f"${field}"}},
            ]
            pipeline += lookup

        return list(
            map(
                partial(Utils.to_class_object, generic_class),
                model.aggregate(pipeline),
            )
        )

    @staticmethod
    def find_one(generic_class: Type[T], query: dict, throw_error_if_none=False) -> T:
        model = db[generic_class.__name__.lower()]
        result = model.find_one(query)
        if throw_error_if_none and result is None:
            raise UnicornException(f"{generic_class.__name__.lower()} record not found")

        return generic_class(**result)  # type: ignore [call-arg]

    @staticmethod
    def find(generic_class: Type[T], query: dict) -> list[T]:
        model = db[generic_class.__name__.lower()]

        return list(
            map(
                partial(Utils.to_class_object, generic_class),
                model.find(query),
            )
        )

    @staticmethod
    def model_create(
        generic_class: Type[T],
        record: dict,
        session: ClientSession = None,
    ) -> T:
        model = db[generic_class.__name__.lower()]

        # record.pop("_id", None)
        created_record: InsertOneResult = model.insert_one(record, session=session)

        # return created_record
        res = model.find_one(
            {"_id": ObjectId(created_record.inserted_id)}, session=session
        )

        return generic_class(**res)  # type: ignore

    @staticmethod
    def model_update(generic_class: Type[T], query: dict, record: dict) -> UpdateResult:
        model = db[generic_class.__name__.lower()]
        record["updatedAt"] = datetime.now()
        updated_record: UpdateResult = model.update_one(query, {"$set": record})

        return updated_record

    @staticmethod
    def model_find_one_and_update(
        generic_class: Type[T], query: dict, record: dict, upsert=False
    ) -> Any:
        model = db[generic_class.__name__.lower()]
        record["updatedAt"] = datetime.now()
        updated_record = model.find_one_and_update(
            query, {"$set": record}, upsert=upsert, return_document=ReturnDocument.AFTER
        )

        return updated_record

    @staticmethod
    def model_find_or_create(generic_class: Type[T], query: dict, record: dict) -> T:
        model = db[generic_class.__name__.lower()]
        result = model.find_one(query)
        if result is None:
            result = ModelUtilityService.model_create(generic_class, record)
        return result

    @staticmethod
    def model_create_many(
        generic_class: Type[T],
        records: list[Any],
        session: ClientSession = None,
    ) -> InsertManyResult:
        try:
            model = db[generic_class.__name__.lower()]

            created_records: InsertManyResult = model.insert_many(
                records, False, session=session
            )

            return created_records
        except Exception as e:
            print(e)

    @staticmethod
    def model_hard_delete(generic_class: Type[T], query: dict) -> DeleteResult:
        model = db[generic_class.__name__.lower()]
        deleted_record: DeleteResult = model.delete_one(query)

        return deleted_record
