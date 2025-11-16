#!/bin/bash

# Test deployment script for Nooko Interior Design AI

echo "=== Testing Nooko Deployment ==="
echo ""

# Get service URLs
WEB_URL=$(gcloud run services describe web-service --region=asia-east1 --format='value(status.url)')
API_URL=$(gcloud run services describe analysis-service --region=asia-east1 --format='value(status.url)')

echo "Web Service URL: $WEB_URL"
echo "API Service URL: $API_URL"
echo ""

# Test API endpoint
echo "=== Testing API Endpoint ==="
echo "POST $API_URL/api/projects"
RESPONSE=$(curl -s -X POST "$API_URL/api/projects" -H "Content-Type: application/json")
echo "Response: $RESPONSE"
echo ""

# Extract project_id from response
PROJECT_ID=$(echo $RESPONSE | grep -o '"project_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
  echo "❌ Failed to create project"
  exit 1
else
  echo "✓ Project created successfully with ID: $PROJECT_ID"
fi

echo ""
echo "=== Testing Web Service ==="
echo "GET $WEB_URL"
WEB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$WEB_URL")

if [ "$WEB_RESPONSE" = "200" ]; then
  echo "✓ Web service is responding (HTTP $WEB_RESPONSE)"
else
  echo "❌ Web service returned HTTP $WEB_RESPONSE"
  exit 1
fi

echo ""
echo "=== All Tests Passed! ==="
echo "You can now access the application at: $WEB_URL"
