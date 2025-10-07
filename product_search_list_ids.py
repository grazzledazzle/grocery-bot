#!/usr/bin/env python3
"""
Kroger / Harris Teeter CE Grocery List Search with Product IDs
-------------------------------------------------------------
Reads a grocery list file and searches each item using Kroger CE API.
Collects the product IDs for each item.
"""

import base64
import json
import sys
import requests
import os

# --- 1. Configuration ---

CLIENT_ID = "grocerybottest-bbc8thbr".strip()
CLIENT_SECRET = "3nQXkYLZCxsALGTbnDPffBDSnuD2fWV0hoxByxKs".strip()

# Store location ID
LOCATION_ID = "09700491"

# Optional filters
FULFILLMENT = "csp"
CHAIN_CODE = "HART"

# CE endpoints
TOKEN_URL = "https://api-ce.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL = "https://api-ce.kroger.com/v1/products"


# --- 2. Core Functions ---

def get_bearer_token():
    """Request a new OAuth2 Bearer token with product.compact scope."""
    print("Requesting new Bearer token...", file=sys.stderr)

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code != 200:
        print("❌ Failed to retrieve access token", file=sys.stderr)
        print(f"Status: {response.status_code}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        sys.exit(1)

    token = response.json().get("access_token")
    if not token:
        print("❌ No access token in response", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)

    token = token.strip()
    print("✅ Token successfully acquired.", file=sys.stderr)
    return token


def search_product(item_query, token):
    """Search for a product by term (e.g., 'milk')."""
    print(f"\nSearching for product: {item_query}...", file=sys.stderr)

    params = {
        "filter.term": item_query,
        "filter.locationId": LOCATION_ID,
        "filter.limit": 5,
        "filter.fulfillment": FULFILLMENT,
        "filter.chain": CHAIN_CODE,
    }

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(PRODUCTS_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"❌ Product search failed for '{item_query}'", file=sys.stderr)
        print(f"Status: {response.status_code}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        return None

    return response.json()


def extract_product_ids(results):
    """Extract the Kroger product IDs from search results."""
    product_ids = []
    if not results:
        return product_ids

    for product in results.get("data", []):
        product_id = product.get("productId")
        if product_id:
            product_ids.append(product_id)

    return product_ids


def pretty_print_results(item_name, results):
    """Print the top product results in a readable format."""
    if not results:
        print(f"No results for {item_name}.")
        return

    data = results.get("data", [])
    if not data:
        print(f"No results found for {item_name}.")
        return

    print(f"\n--- Top Results for '{item_name}' ---")
    for product in data:
        description = product.get("description", "N/A")
        brand = product.get("brand", "Unknown")
        product_id = product.get("productId", "N/A")
        items = product.get("items", [])
        if items:
            price_info = items[0].get("price", {})
            price = price_info.get("regular", "N/A")
        else:
            price = "N/A"
        print(f"- {description} ({brand}) — ${price} — ID: {product_id}")


def read_grocery_list(file_path):
    """Read grocery items from a text or markdown file."""
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    items = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line)
    return items


# --- 3. Main Execution ---

def main():
    print("🚀 Grocery List Product Search Script Started.")

    # Check command line argument
    if len(sys.argv) < 2:
        print("Usage: python product_search_list.py <grocery_list_file.txt>")
        sys.exit(1)

    grocery_file = sys.argv[1]
    items = read_grocery_list(grocery_file)
    print(f"Found {len(items)} items in grocery list.")

    # Get token
    token = get_bearer_token()

    # Dictionary to store item -> product IDs
    grocery_product_ids = {}

    # Search each item
    for item in items:
        results = search_product(item, token)
        pretty_print_results(item, results)
        ids = extract_product_ids(results)
        grocery_product_ids[item] = ids

    print("\n✅ Collected Product IDs for Grocery List:")
    for item, ids in grocery_product_ids.items():
        print(f"{item}: {ids}")


if __name__ == "__main__":
    main()
