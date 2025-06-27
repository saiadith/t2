import requests

def fetch_products():
    url = "https://fakestoreapi.com/products"
    resp = requests.get(url)
    resp.raise_for_status()
    products = resp.json()
    # Extract id, title, price, image URL, and description
    product_list = [{
        "id": p["id"],
        "title": p["title"],
        "price": p["price"],
        "image": p["image"],
        "description": p["description"]
    } for p in products]
    return product_list

if __name__ == "__main__":
    products = fetch_products()
    print(f"Fetched {len(products)} products")
    # Optionally print first product for verification
    print(products[0])
