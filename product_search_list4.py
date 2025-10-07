#!/usr/bin/env python3
"""
Smart Kroger Grocery List Search with Brand + Type Filtering
- Single input list with optional brand hints
- Accepts em dash (—) or hyphen (-) as separator
- Selects products based on brand and description keywords
- Falls back to lowest-price if no exact match
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
        "filter.limit": 20,  # get more results to improve brand filtering
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
    Accepts either:
      <item_name> — <brand_hint>  (em dash)
      <item_name> - <brand_hint>  (hyphen)
    Returns (item_name, brand_hint) tuple. Brand hint is None if not provided.
    """
    if "—" in line:
        item_name, brand_hint = map(str.strip, line.split("—", 1))
    elif "-" in line:
        item_name, brand_hint = map(str.strip, line.split("-", 1))
    else:
        item_name = line.strip()
        brand_hint = None
    return item_name, brand_hint


def select_product(item_name, results, brand_hint=None):
    """
    Select product matching all keywords in description and optional brand.
    Falls back to lowest-price selection.
    """
    data = results.get("data", [])
    if not data:
        return None

    # Split item_name into keywords (e.g., "2% milk" -> ["2%", "milk"])
    keywords = item_name.lower().split()

    # Step 1: Brand + keyword match
    brand_filtered = []
    for p in data:
        desc = p.get("description", "").lower()
        brand = p.get("brand", "").lower()
        combined = f"{desc} {brand}"
        # Must contain all keywords
        if all(k in combined for k in keywords):
            if brand_hint:
                if brand_hint.lower() in brand or brand_hint.lower() in desc:
                    brand_filtered.append(p)
            else:
                brand_filtered.append(p)

    # Step 2: If brand_filtered not empty, pick lowest price
    candidates = brand_filtered if brand_filtered else data

    lowest = None
    lowest_price = float("inf")
    for p in candidates:
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

    # Step 3: Fallback to first candidate if no price info
    return lowest if lowest else candidates[0]


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
        print("Usage: python grocery_search.py <grocery_list.md>")
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
        product = select_product(item_name, results, brand_hint)
        if not product:
            print(f"No product selected for {item_name}")
            continue
        pretty_print(product)


if __name__ == "__main__":
    main()
