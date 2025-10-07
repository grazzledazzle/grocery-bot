#!/usr/bin/env python3
"""
Smart Kroger Grocery List Search
- Single input list with optional brand hints
- Selects the lowest price among matching products
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
CHAIN_CODE = "HART"  # Harris Teeter, optional in input

TOKEN_URL = "https://api-ce.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL = "https://api-ce.kroger.com/v1/products"


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
        "filter.limit": 10,
        "filter.fulfillment": FULFILLMENT,
        "filter.chain": CHAIN_CODE,
    }
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    resp = requests.get(PRODUCTS_URL, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"❌ Product search failed for '{item_query}' ({resp.status_code})")
        return None
    return resp.json()


def parse_item_line(line):
    """
    Parse a line in grocery_list.md.
    Format: item_name — optional_brand
    """
    if "—" in line:
        item_name, brand_hint = map(str.strip, line.split("—", 1))
    else:
        item_name = line.strip()
        brand_hint = None
    return item_name, brand_hint


def select_lowest_price_product(item_name, results, brand_hint=None):
    """
    Select the product with the lowest price.
    If brand_hint is provided, prefer products containing that brand in description or brand.
    """
    data = results.get("data", [])
    if not data:
        return None

    filtered = []
    for p in data:
        desc = p.get("description", "").lower()
        brand = p.get("brand", "").lower()
        if brand_hint and brand_hint.lower() not in desc and brand_hint.lower() not in brand:
            continue
        filtered.append(p)

    if not filtered:
        filtered = data  # fallback: use all results

    lowest = None
    lowest_price = float("inf")
    for p in filtered:
        items = p.get("items", [])
        if not items:
            continue
        price = items[0].get("price", {}).get("regular")
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue
        if price < lowest_price:
            lowest_price = price
            lowest = p

    return lowest if lowest else filtered[0]


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
        print("Usage: python smart_grocery_search.py <grocery_list.md>")
        sys.exit(1)

    grocery_file = sys.argv[1]
    items = read_list(grocery_file)
    print(f"Found {len(items)} items in grocery list.")

    token = get_bearer_token()

    for line in items:
        item_name, brand_hint = parse_item_line(line)
        print(f"\nSearching for: {item_name}" + (f" (brand hint: {brand_hint})" if brand_hint else ""))
        results = search_product(item_name, token)
        if not results:
            print(f"No results for {item_name}")
            continue
        product = select_lowest_price_product(item_name, results, brand_hint)
        if not product:
            print(f"No product selected for {item_name}")
            continue
        pretty_print(product)


if __name__ == "__main__":
    main()
