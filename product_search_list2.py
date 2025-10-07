#!/usr/bin/env python3
"""
Smart Kroger / Harris Teeter Grocery List Search
- Single input list
- Uses descriptive keywords per item
- Prefers Harris Teeter brand
- Picks the most relevant product
"""

import base64
import json
import sys
import requests
import os

# --- Configuration ---
CLIENT_ID = "grocerybottest-bbc8thbr".strip()
CLIENT_SECRET = "3nQXkYLZCxsALGTbnDPffBDSnuD2fWV0hoxByxKs".strip()

LOCATION_ID = "09700491"
FULFILLMENT = "csp"
CHAIN_CODE = "HART"  # Harris Teeter

TOKEN_URL = "https://api-ce.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL = "https://api-ce.kroger.com/v1/products"

# Optional: mapping item -> search keywords
SEARCH_KEYWORDS = {
    "milk": ["whole milk", "organic milk", "milk gallon"],
    "eggs": ["large eggs", "cage free eggs"],
    "cheese": ["cheddar block cheese", "shredded cheddar"],
    "bread": ["whole grain bread", "sourdough bread"],
    "ice cream": ["vanilla ice cream", "chocolate ice cream"],
}


# --- Core Functions ---

def get_bearer_token():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}",
    }
    data = {"grant_type": "client_credentials", "scope": "product.compact"}
    resp = requests.post(TOKEN_URL, headers=headers, data=data)
    if resp.status_code != 200:
        print(f"❌ Token request failed ({resp.status_code})")
        print(resp.text)
        sys.exit(1)
    return resp.json()["access_token"].strip()


def search_product(item_query, token):
    params = {
        "filter.term": item_query,
        "filter.locationId": LOCATION_ID,
        "filter.limit": 5,
        "filter.fulfillment": FULFILLMENT,
        "filter.chain": CHAIN_CODE,
    }
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    resp = requests.get(PRODUCTS_URL, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"❌ Product search failed for '{item_query}' ({resp.status_code})")
        return None
    return resp.json()


def select_best_product(item_name, results):
    """Select the most relevant product using keywords and Harris Teeter brand."""
    data = results.get("data", [])
    if not data:
        return None

    keywords = SEARCH_KEYWORDS.get(item_name.lower(), [item_name.lower()])

    # 1️⃣ First, try Harris Teeter brand with matching keywords
    for p in data:
        desc = p.get("description", "").lower()
        brand = p.get("brand", "").lower()
        if brand == "harris teeter" and any(k in desc for k in keywords):
            return p

    # 2️⃣ Next, any product matching keywords
    for p in data:
        desc = p.get("description", "").lower()
        if any(k in desc for k in keywords):
            return p

    # 3️⃣ Fallback: first product
    return data[0]


def pretty_print(product):
    description = product.get("description", "N/A")
    brand = product.get("brand", "Unknown")
    product_id = product.get("productId", "N/A")
    items = product.get("items", [])
    if items:
        price = items[0].get("price", {}).get("regular", "N/A")
    else:
        price = "N/A"
    print(f"- {description} ({brand}) — ${price} — ID: {product_id}")


def read_list(file_path):
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    items = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line)
    return items


# --- Main Execution ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python smart_grocery_search.py <grocery_list.txt>")
        sys.exit(1)

    grocery_file = sys.argv[1]
    items = read_list(grocery_file)
    print(f"Found {len(items)} items in grocery list.")

    token = get_bearer_token()

    for item in items:
        print(f"\nSearching for: {item}")
        results = search_product(item, token)
        if not results:
            print(f"No results for {item}")
            continue
        product = select_best_product(item, results)
        if not product:
            print(f"No product selected for {item}")
            continue
        pretty_print(product)


if __name__ == "__main__":
    main()
