@echo off
echo Testing Invoice Generation Endpoint...
echo.

curl -X POST http://localhost:5000/gen_invoice ^
  -H "Content-Type: application/json" ^
  -d "{\"company_name\": \"Tech Solutions Inc.\", \"company_address\": \"123 Business Ave\\nSuite 456\\nNew York, NY 10001\", \"customer_name\": \"John Smith\", \"customer_email\": \"john.smith@example.com\", \"billing_address\": \"789 Customer St\\nApt 101\\nBoston, MA 02101\", \"shipping_address\": \"789 Customer St\\nApt 101\\nBoston, MA 02101\", \"items\": [{\"description\": \"Web Development Services\", \"quantity\": 40, \"unit_price\": 85.00, \"total\": 3400.00}, {\"description\": \"Domain Registration\", \"quantity\": 1, \"unit_price\": 15.99, \"total\": 15.99}, {\"description\": \"SSL Certificate\", \"quantity\": 1, \"unit_price\": 79.00, \"total\": 79.00}], \"tax_rate\": 8.25, \"notes\": \"Thank you for your business! Payment is due within 30 days.\"}"

echo.
echo Request sent! Check the response above.
pause