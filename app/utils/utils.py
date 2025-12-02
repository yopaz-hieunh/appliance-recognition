import json


def get_products_local(file_path: str = 'data/products/products.json') -> list:
    """Load product data from a local JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        products = json.load(file)
    return products
