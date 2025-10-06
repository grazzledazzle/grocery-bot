#!/bin/bash
# Kroger API Client Script - Core Functions
# This script handles authentication, product search, and uses 'jq' for JSON parsing.

# --- 1. Configuration (Required) ---
# Your Kroger application credentials
CLIENT_ID="grocerybottest-bbc8thbr"
CLIENT_SECRET="3nQXkYLZCxsALGTbnDPffBDSnuD2fWV0hoxByxKs"

# The location ID for the store you want to use
# This is required for product search.
LOCATION_ID="09700491"

# API Endpoints
TOKEN_URL="https://api.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL="https://api.kroger.com/v1/products"

# --- 2. Core Functions ---

# Function to get a fresh Bearer access token
get_bearer_token() {
    # Combine ID and Secret, then Base64 encode them for the Basic Auth header
    local base64_credentials
    base64_credentials=$(echo -n "${CLIENT_ID}:${CLIENT_SECRET}" | base64)

    echo "Requesting new Bearer Token..." >&2

    # Make the cURL request for the token
    local response
    # Added -k flag to bypass SSL/Akamai block issues
    response=$(curl -s -k -X POST \
      "${TOKEN_URL}" \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -H "Authorization: Basic ${base64_credentials}" \
      -d 'grant_type=client_credentials')

    # Use jq to extract the access token
    local access_token
    access_token=$(echo "${response}" | jq -r '.access_token')

    if [ -z "${access_token}" ]; then
        echo "ERROR: Failed to retrieve access token. Check credentials/permissions." >&2
        echo "API Response (Raw):" >&2
        # Tries to use jq, falls back to raw output if not JSON
        echo "${response}" | jq -r '.' 2>/dev/null || echo "${response}" >&2
        exit 1
    fi

    # Return the token to the caller
    echo "${access_token}"
}

# Function to search for a specific product
search_product() {
    local item_query="$1"
    local token="$2"
    echo "Searching for product: ${item_query}..." >&2

    # Encode the search term for the URL
    local encoded_query
    encoded_query=$(echo "${item_query}" | sed 's/ /%20/g')

    local search_url="${PRODUCTS_URL}?filter.term=${encoded_query}&filter.locationId=${LOCATION_ID}&filter.limit=5"

    # Make the product search request
    # Added -k flag to bypass SSL/Akamai block issues
    curl -s -k -X GET \
      "${search_url}" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer ${token}"
}


# --- 3. Main Execution Block ---

# 1. Get the access token
ACCESS_TOKEN=$(get_bearer_token)
echo "Token successfully acquired." >&2

# 2. Test a product search
TEST_ITEM="milk"
SEARCH_RESULTS=$(search_product "${TEST_ITEM}" "${ACCESS_TOKEN}")

echo "--- JSON Search Results for ${TEST_ITEM} (Pretty-Printed by jq) ---"
# Pipe the raw response through jq for clean, readable output
echo "${SEARCH_RESULTS}" | jq

# 3. TO DO: Add cart integration logic here
# Next step: Parse the grocery list file and use the results to extract the item ID.
