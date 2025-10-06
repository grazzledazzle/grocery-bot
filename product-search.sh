# product-search.sh
# This script automatically gets a fresh access token and executes a Product Search
# for a specific item at a known location ID.
# Use: source product-search.sh

# Exit immediately if any command fails. This helps debug failures.
set -e

# Define a temporary file name for the authorization header
AUTH_HEADER_FILE=".kroger_auth_header.tmp"

# Function to safely print JSON output (handles missing 'jq')
print_json_output() {
    local json_response="$1"
    if command -v jq &> /dev/null; then
        echo "$json_response" | jq
    else
        # Fallback to pure echo if jq is not found
        echo "$json_response"
    fi
}

# --- 1. Sourcing Credentials & Cleaning ---
# Load CLIENT_ID and CLIENT_SECRET from the separate credentials file.
source credentials_v1.sh

# Check if credentials were loaded
if [ -z "$KROGER_CLIENT_ID" ] || [ -z "$KROGER_CLIENT_SECRET" ]; then
    echo "ERROR: Credentials not found. Please ensure credentials_v1.sh is in this directory and correctly filled."
    read -p "Press Enter to exit..." # Pause on error
    exit 1
fi

# CRITICAL FIX: Clean up credentials to remove any trailing spaces or hidden characters
CLEAN_ID=$(echo "$KROGER_CLIENT_ID" | tr -d '[:space:]')
CLEAN_SECRET=$(echo "$KROGER_CLIENT_SECRET" | tr -d '[:space:]')

# --- 2. Dynamic Token Generation ---

echo "Requesting new Access Token (with 'product.compact' scope)..."

# 2a. Combine clean ID and Secret and Base64 encode it.
CREDENTIALS_BASE64=$(echo -n "$CLEAN_ID:$CLEAN_SECRET" | base64 | tr -d '\n\r')
    
# 2b. Make the POST request to get the token.
TOKEN_RESPONSE=$(curl -s -X POST \
  'https://api-ce.kroger.com/v1/connect/oauth2/token' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --header "Authorization: Basic $CREDENTIALS_BASE64" \
  -d 'grant_type=client_credentials&scope=product.compact' \
  --compressed | tr -d '\n\r')

# 2c. Check for success (look for 'access_token' key)
if ! echo "$TOKEN_RESPONSE" | grep -q '"access_token"'; then
    echo "------------------------------------------------------------"
    echo "🚨 TOKEN REQUEST FAILED! The script will now pause. Read the error below."
    echo "Raw response from API (Error message):"
    print_json_output "$TOKEN_RESPONSE"
    echo "------------------------------------------------------------"
    read -p "Press Enter to exit and close the terminal..." # PAUSE ON FAILURE
    exit 1
fi

# 2d. Use pure shell parameter expansion for reliable token extraction.
TOKEN_SEGMENT=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"')
ACCESS_TOKEN=${TOKEN_SEGMENT#*\"access_token\":\"}
ACCESS_TOKEN=${ACCESS_TOKEN%\"}

# 2e. CRITICAL FIX: Create an absolutely clean token variable stripped of all ambient space.
CLEAN_ACCESS_TOKEN=$(echo "$ACCESS_TOKEN" | tr -d '[:space:]')

echo "Token successfully generated (Valid for 30 minutes) with required scope."

# Create the Authorization header file once using the temporary file method for reliability
printf "Authorization: Bearer %s" "$CLEAN_ACCESS_TOKEN" > "$AUTH_HEADER_FILE"


# --- 3. Product Search API Call ---

LOCATION_ID="09700491" # Harris Teeter - Southpoint Crossing
PRODUCT_TERM="cheese" 
CHAIN_CODE="HART" # Chain code for Harris Teeter

echo ""
echo "--------------------------------------------------------"
echo "🧀 Executing Product Search: '$PRODUCT_TERM' at store $LOCATION_ID (w/ CSP, CHAIN filters)..."
echo "--------------------------------------------------------"

# Reverting to the consistent API-CE domain.
PRODUCT_RESPONSE=$(curl -s \
  "https://api-ce.kroger.com/v1/products?filter.term=$PRODUCT_TERM&filter.locationId=$LOCATION_ID&filter.fulfillment=csp&filter.chain=$CHAIN_CODE" \
  --header 'Accept: application/json' \
  --header "@$AUTH_HEADER_FILE" \
  --compressed)

# Print the results.
echo "✅ Product Search Results (JSON):"
print_json_output "$PRODUCT_RESPONSE"


# --- 4. Clean Up and Finish ---
# Clean up the temporary file
rm -f "$AUTH_HEADER_FILE"

export KROGER_ACCESS_TOKEN="$CLEAN_ACCESS_TOKEN"
echo ""
echo "Script finished."
echo "HINT: The clean token is now available in your terminal as: \$KROGER_ACCESS_TOKEN"

read -p "Press Enter to finish and clear the screen..."
