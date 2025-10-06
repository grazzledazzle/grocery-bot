# kroger_api_client.sh
# This script automatically gets a fresh access token and runs a location search.
# Use: source kroger_api_client.sh

# Exit immediately if any command fails. This helps debug failures.
set -e

# --- 1. Sourcing Credentials ---
# Load CLIENT_ID and CLIENT_SECRET from the separate credentials file.
source credentials_v1.sh

# Check if credentials were loaded
if [ -z "$KROGER_CLIENT_ID" ] || [ -z "$KROGER_CLIENT_SECRET" ]; then
    echo "ERROR: Credentials not found. Please ensure credentials_v1.sh is in this directory and correctly filled."
    read -p "Press Enter to exit..." # Pause on error
    exit 1
fi

# --- 2. Dynamic Token Generation ---

# 2a. Combine ID and Secret and Base64 encode it.
# The '-n' ensures no trailing newline is included in the string to be encoded.
CREDENTIALS_BASE64=$(echo -n "$KROGER_CLIENT_ID:$KROGER_CLIENT_SECRET" | base64)

echo "Requesting new Access Token..."

# 2b. Make the POST request to get the token.
# '-s' suppresses the progress meter. 'tr' removes line breaks from the JSON response.
TOKEN_RESPONSE=$(curl -s -X POST \
  'https://api-ce.kroger.com/v1/connect/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H "Authorization: Basic $CREDENTIALS_BASE64" \
  -d 'grant_type=client_credentials' \
  --compressed | tr -d '\n\r')

# 2c. Check for success (look for 'access_token' key)
if ! echo "$TOKEN_RESPONSE" | grep -q '"access_token"'; then
    echo "------------------------------------------------------------"
    echo "🚨 TOKEN REQUEST FAILED! The script will now pause. Read the error below."
    echo "Raw response from API (Error message):"
    echo "$TOKEN_RESPONSE" | jq || echo "$TOKEN_RESPONSE" # Use jq or print raw
    echo "------------------------------------------------------------"
    read -p "Press Enter to exit and close the terminal..." # PAUSE ON FAILURE
    exit 1
fi

# 2d. Extract the clean token using 'sed' or string manipulation (assuming 'jq' might not be installed).
# This extracts the value following "access_token": and strips the surrounding quotes and comma.
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//;s/"//')

echo "Token successfully generated (Valid for 30 minutes)."

# --- 3. Location Search API Call ---

ZIP_CODE="27713"
RADIUS="5"

echo "Searching for locations near ZIP $ZIP_CODE (Radius: $RADIUS miles)..."

# 3a. Use the freshly generated ACCESS_TOKEN to search for locations.
LOCATION_RESPONSE=$(curl -s \
  "https://api-ce.kroger.com/v1/locations?filter.zipCode.near=$ZIP_CODE&filter.radiusInMiles=$RADIUS" \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --compressed)

echo "--------------------------------------------------------"
echo "✅ Location Search Results (JSON):"
echo "--------------------------------------------------------"
# Print the results, using 'jq' to pretty-print if available, otherwise print raw.
echo "$LOCATION_RESPONSE" | jq || echo "$LOCATION_RESPONSE"

# Note: The ACCESS_TOKEN is now available as a variable in your shell if you use 'source'.
export KROGER_ACCESS_TOKEN="$ACCESS_TOKEN"
echo ""
echo "HINT: The clean token is now available in your terminal as: \$KROGER_ACCESS_TOKEN"

# --- 4. Pause for Troubleshooting (New Line) ---
read -p "Press Enter to finish and clear the screen..."
