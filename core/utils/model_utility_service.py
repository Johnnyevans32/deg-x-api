from functools import lru_cache, partial
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Type, TypeVar

from bson import ObjectId
from pymongo import DESCENDING
from pymongo.client_session import ClientSession
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)
from core.db import db

from core.utils.response_service import MetaDataModel


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
        genericClass: Type[T],
        query: dict,
        page_num: int,
        page_size: int,
    ) -> Tuple[List[T], MetaDataModel]:
        model = db[genericClass.__name__.lower()]

        """returns a set of documents belonging to page number `page_num`
        where size of each page is `page_size`.
        """
        # Calculate number of documents to skip
        skips = page_size * (page_num - 1)

        total_count = model.find(query).count()

        total_page = math.ceil(total_count / page_size)

        prev_page = (lambda: page_num - 1 if (page_num - 1) > 0 else None)()
        next_page = (lambda: page_num + 1 if (page_num + 1) <= total_page else None)()

        # Skip and limit
        documents = (
            model.find(query).sort("createdAt", DESCENDING).skip(skips).limit(page_size)
        )

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
        genericClass: Type[T],
        query: dict,
        fields: List[str],
        page_num: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[T], MetaDataModel]:
        model = db[genericClass.__name__.lower()]
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
        genericClass: Type[T], query: dict, fields: List[str]
    ) -> T:
        model = db[genericClass.__name__.lower()]
        pipeline: List[Dict[str, Any]] = [
            {
                "$match": query,
            },
        ]
        for field in fields:
            lookup = {
                "$lookup": {
                    "from": field,
                    "localField": field,
                    "foreignField": "_id",
                    "as": field,
                }
            }
            unwind = {"$unwind": {"path": f"${field}"}}
            pipeline += [lookup, unwind]

        limit = {"$limit": 1}
        pipeline.append(limit)
        [aggregation_result] = list(model.aggregate(pipeline))
        return genericClass(**aggregation_result)  # type: ignore [call-arg]

    @staticmethod
    def find_and_populate(
        genericClass: Type[T],
        query: dict,
        fields: List[str],
    ) -> List[T]:
        model = db[genericClass.__name__.lower()]
        pipeline = [
            {
                "$match": query,
            },
        ]

        print(pipeline)
        for field in fields:
            lookup = {
                "$lookup": {
                    "from": ModelUtilityService.__pluralize(field),
                    "localField": field,
                    "foreignField": "_id",
                    "as": field,
                }
            }
            unwind = {"$unwind": {"path": f"${field}"}}
            pipeline += [lookup, unwind]

        return list(
            map(
                partial(ModelUtilityService.to_class_object, genericClass),
                model.aggregate(pipeline),
            )
        )

    @staticmethod
    def find_one(genericClass: Type[T], query: dict) -> T:
        model = db[genericClass.__name__.lower()]

        return genericClass(**model.find_one(query))  # type: ignore [call-arg]

    @staticmethod
    def find(genericClass: Type[T], query: dict) -> List[T]:
        model = db[genericClass.__name__.lower()]

        return list(
            map(
                partial(ModelUtilityService.to_class_object, genericClass),
                model.find(query),
            )
        )

    @staticmethod
    def model_create(
        genericClass: Type[T],
        record: dict,
        session: ClientSession = None,
    ) -> T:
        model = db[genericClass.__name__.lower()]
        # Adding the SBaseModel attributes to the insertion
        record["createdAt"] = datetime.now()
        record["isDeleted"] = False
        record["updatedAt"] = datetime.now()

        created_record: InsertOneResult = model.insert_one(record, session=session)

        res = model.find_one(
            {"_id": ObjectId(created_record.inserted_id)}, session=session
        )

        return genericClass(**res)  # type: ignore

    @staticmethod
    def model_update(
        genericClass: Type[T], query: dict, record_to_update: dict
    ) -> UpdateResult:
        model = db[genericClass.__name__.lower()]
        record = {"updatedAt": datetime.now(), **record_to_update}
        updated_record: UpdateResult = model.update_one(query, {"$set": record})

        return updated_record

    @staticmethod
    def model_create_many(
        genericClass: Type[T],
        records: List[Dict[str, Any]],
        session: ClientSession = None,
    ) -> InsertManyResult:
        model = db[genericClass.__name__.lower()]
        # Adding the SBaseModel attributes to the insertion
        for record in records:
            record["createdAt"] = datetime.now()
            record["isDeleted"] = False
            record["updatedAt"] = datetime.now()

        created_records: InsertManyResult = model.insert_many(records, session=session)

        return created_records

    @staticmethod
    def model_hard_delete(genericClass: Type[T], query: dict) -> DeleteResult:
        model = db[genericClass.__name__.lower()]
        deleted_record: DeleteResult = model.delete_one(query)

        return deleted_record

    @staticmethod
    def to_class_object(
        genericClass: Type[T],
        _dict: dict,
    ) -> T:
        return genericClass(**_dict)  # type: ignore [call-arg]
