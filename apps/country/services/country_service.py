from apps.country.interfaces.country_interface import Country
from core.utils.model_utility_service import ModelUtilityService
from core.utils.response_service import MetaDataModel


class CountryService:
    async def get_country(
        self, page_num: int, page_size: int
    ) -> tuple[list[Country], MetaDataModel]:
        query = {"isDeleted": False}
        res, meta_data = await ModelUtilityService.paginate_data(
            Country, query, page_num, page_size
        )

        return res, meta_data

    async def search_country(
        self, name: str, page_num: int, page_size: int
    ) -> tuple[list[Country], MetaDataModel]:
        query = {
            "isDeleted": False,
            "$or": [
                {"name": {"$regex": name, "$options": "i"}},
                {"code": {"$regex": name, "$options": "i"}},
                {"callingCode": {"$regex": name, "$options": "i"}},
            ],
        }
        res, meta_data = await ModelUtilityService.paginate_data(
            Country, query, page_num, page_size
        )

        return res, meta_data
