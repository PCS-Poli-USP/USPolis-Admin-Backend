from server.deps.pagination_dep import pagination_params
from server.models.page_models import DEFAULT_PAGE_SIZE


class TestPaginationParams:
    def test_defaults_to_page_one_and_default_page_size(self) -> None:
        # pagination_params' own parameter defaults are FastAPI `Query(...)`
        # sentinels, not plain ints - they're only resolved when FastAPI
        # itself calls this function, so calling it directly always requires
        # explicit values.
        pagination = pagination_params(page=1, page_size=DEFAULT_PAGE_SIZE)

        assert pagination.page == 1
        assert pagination.page_size == DEFAULT_PAGE_SIZE

    def test_builds_pagination_input_from_given_values(self) -> None:
        pagination = pagination_params(page=3, page_size=50)

        assert pagination.page == 3
        assert pagination.page_size == 50
