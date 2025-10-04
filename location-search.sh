curl -X GET \
  'https://api.kroger.com/v1/locations&filter.zipCode.near=27713&filter.radiusInMiles=5' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {{VALID_TOKEN}}'

  # NN: working location search but the token expired