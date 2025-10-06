#!/usr/bin/env python3
"""
Kroger / Harris Teeter API Client - Core Functions
-------------------------------------------------
Performs authentication (client_credentials flow) and basic product search.
Replaces the Bash version with a structured, Pythonic implementation.
"""

import base64
import json
import sys
import requests

# --- 1. Configuration (Required) ---

# Kroger developer credentials
CLIENT_ID = "grocerybottest-bbc8thbr"
CLIENT_SECRET = "3nQXkYLZCxsALGTbnDPffBDSnuD2fWV0hoxByxKs"

# Store location ID (required for product search)
LOCATION_ID = "09700491"

# API endpoints
TOKEN_URL = "https://api.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL = "https://api.kroger.com/v1/products"

# --- 2. Core Functions ---

def get_bearer_token():
    """Request a new OAuth2 Bearer token using client_credentials grant."""
    print("Requesting new Bearer token...", file=sys.stderr)

    # Build Basic Auth header (Base64 encoded client_id:client_secret)
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }
    data = {"grant_type": "client_credentials"}

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

    print("✅ Token successfully acquired.", file=sys.stderr)
    return token


def search_product(item_query, token):
    """Search for a product by term (e.g., 'milk')."""
    print(f"Searching for product: {item_query}...", file=sys.stderr)
    params = {
        "filter.term": item_query,
        "filter.locationId": LOCATION_ID,
        "filter.limit": 5,
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(PRODUCTS_URL, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Product search failed", file=sys.stderr)
        print(f"Status: {response.status_code}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        sys.exit(1)

    return response.json()
