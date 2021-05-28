test:
	poetry run pytest

test_dev:
	poetry run pytest portfolio/tests/test_asset_admin.py --quiet --disable-warnings