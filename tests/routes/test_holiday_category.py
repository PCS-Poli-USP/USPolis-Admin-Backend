# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from json import loads

# from server.models.database.user_db_model import User
# from server.models.database.holiday_category_db_model import HolidayCategory
# from tests.utils.holiday_category_test_utils import add_holiday_category, make_holiday_category_register, make_holiday_category_update
# from tests.utils.default_values.test_holiday_category_default_values import HolidayCategoryDefaultValues

# MAX_HOLIDAY_CATEGORY_COUNT = 5


# @pytest.mark.asyncio
# async def test_holiday_category_get_all(client: AsyncClient, user: User) -> None:
#     for i in range(MAX_HOLIDAY_CATEGORY_COUNT):
#         await add_holiday_category(f"Category {i}", user)

#     response = await client.get("/holidays_categories")
#     assert response.status_code == status.HTTP_200_OK

#     data = response.json()
#     assert len(data) == MAX_HOLIDAY_CATEGORY_COUNT


# @pytest.mark.asyncio
# async def test_holiday_category_get(client: AsyncClient, user: User) -> None:
#     holiday_category_id = await add_holiday_category(HolidayCategoryDefaultValues.NAME, user)

#     response = await client.get(f"/holidays_categories/{holiday_category_id}")
#     assert response.status_code == status.HTTP_200_OK

#     data = response.json()
#     assert data["name"] == HolidayCategoryDefaultValues.NAME


# @pytest.mark.asyncio
# async def test_holiday_category_create(client: AsyncClient, user: User) -> None:
#     register = make_holiday_category_register(
#         HolidayCategoryDefaultValues.NAME)
#     input = register.model_dump_json()

#     response = await client.post("/holidays_categories", json=loads(input))
#     assert response.status_code == status.HTTP_200_OK

#     holiday_category_id = response.json()
#     assert isinstance(holiday_category_id, str)
#     assert await HolidayCategory.check_name_exists(HolidayCategoryDefaultValues.NAME)


# @pytest.mark.asyncio
# async def test_holiday_category_update(client: AsyncClient, user: User) -> None:
#     holiday_category_id = await add_holiday_category(HolidayCategoryDefaultValues.NAME, user)
#     new_category = f"{HolidayCategoryDefaultValues.NAME} Updated"
#     update = make_holiday_category_update(new_category)
#     input = update.model_dump_json()

#     response = await client.post("/holidays_categories", json=loads(input))
#     assert response.status_code == status.HTTP_200_OK

#     holiday_category_id = response.json()
#     assert isinstance(holiday_category_id, str)
#     assert await HolidayCategory.check_name_exists(new_category)


# @pytest.mark.asyncio
# async def test_holiday_category_delete(client: AsyncClient, user: User) -> None:
#     holiday_category_id = await add_holiday_category(HolidayCategoryDefaultValues.NAME, user)

#     response = await client.delete(f"/holidays_categories/{holiday_category_id}")
#     assert response.status_code == status.HTTP_200_OK

#     data = response.json()
#     assert isinstance(data, int)

#     assert not await HolidayCategory.check_name_exists(HolidayCategoryDefaultValues.NAME)
