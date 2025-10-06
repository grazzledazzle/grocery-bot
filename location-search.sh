curl -X GET \
  'https://api-ce.kroger.com/v1/locations&filter.zipCode.near=27713&filter.radiusInMiles=5' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {{VALID_TOKEN}}'


  # Corrected Location Search Command for ZIP 27713
curl -X GET \
  'https://api-ce.kroger.com/v1/locations?filter.zipCode.near=27713&filter.radiusInMiles=5' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLWNlLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoidnl6bG52Y3dSUUZyRzZkWDBzU1pEQT09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJncm9jZXJ5Ym90dGVzdC1iYmM4dGhiciIsImV4cCI6MTc1OTU5MjU2OSwiaWF0IjoxNzU5NTkwNzY0LCJpc3MiOiJhcGktY2Uua3JvZ2VyLmNvbSIsInN1YiI6Ijc1MDQyNGRkLWNkYzAtNTQ3Ny05MWJmLTE2N2JmMDhiMjVkZSIsInNjb3BlIjoiIiwiYXV0aEF0IjoxNzU5NTkwNzY5MzU0Njc2Njg2LCJhenAiOiJncm9jZXJ5Ym90dGVzdC1iYmM4dGhiciJ9.k9ydhNVj3yLcDI2_hwIlA6pERzMj8AuXQKNr-8Deaez1ap24o1S4xagenPfBHDZKyP7Kcq7227sH_X7P42UwWUf-q0fF070KbRyT384bb3lElbpTn7nrIXa9g3aBoVEBdgvz23Q8d6wMBKYhdrA97bDZITqgQQz4VLlyxgfiSA8qWm-PLTukgUYbLHzT588Ok47a4NVMTdZ_OjDJAyUypq1iH6Dv2Mg6-mi2RfnrFvkvs7WTJMgoTZ73nfHqVKDrFJuoJGYxbjn-ZiHVEWHHn4Vm5uJtIoZ78-GRL5nk-DDWcGXQGn33WYDfOI4jv7uUqcd3DeadVvdv4Xb6av0m2Q" \
  --output - \
  --compressed