#!/usr/bin/env bash
set -euo pipefail
# There is a chance, you might need to tweak some permissions such as can_manage_files for individual workflow
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_JSON="$SCRIPT_DIR/sample_record_full.json"

./run.sh invenio users create --password testtest test@test.com || echo "User test@test.com already exists; continuing."
./run.sh invenio users activate test@test.com
./run.sh invenio roles create admin || echo "Role 'admin' already exists; continuing."
./run.sh invenio access allow superuser-access role admin || echo "Access rule for 'admin' may already exist; continuing."
./run.sh invenio roles add test@test.com admin || echo "User test@test.com may already have role 'admin'; continuing."
token=$(./run.sh invenio tokens create -n demo-data -u test@test.com)
echo "API token created for demo-data user (test@test.com)."

echo "Creating new datasets from template..."

# Read the template JSON and add files: {enabled: false}
metadata_json=$(jq '. + {"files": {"enabled": false}} + {"parent": {"workflow": "individual", "communities":{"default":"e79bd1b6-2441-42c5-818f-72c899b4a351"}}}' "$TEMPLATE_JSON")


echo "Payload being sent:"
echo "$metadata_json" | jq .

# Function to create and publish a dataset
create_dataset() {
    response=$(curl -s -k -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $token" \
      -d "$metadata_json" \
      https://127.0.0.1:5000/api/datasets) 

    echo "Create response:"
    echo "$response" | jq .

    record_id=$(echo "$response" | jq -r '.id // empty')

    if [ -z "$record_id" ]; then
        echo "Error creating dataset" >&2
        echo "$response" >&2
        return 1
    fi

    publish_link=$(echo "$response" | jq -r '.links.publish // empty')
    if [ -n "$publish_link" ]; then
        publish_response=$(curl -s -k -X POST \
          -H "Authorization: Bearer $token" \
          "$publish_link")
        publish_status=$(echo "$publish_response" | jq -r '.status // empty')
        if [ "$publish_status" = "400" ]; then
            echo "✗ Created but publish FAILED (ID: $record_id)"
            echo "Publish error: $publish_response"
        else
            echo "✓ Created and published (ID: $record_id)"
        fi
    else
        echo "✓ Created (ID: $record_id)"
    fi

    echo "$record_id"
}

# Create 3 datasets
echo "Creating record 1..."
create_dataset
echo "Creating record 2..."
create_dataset
echo "Creating record 3..."
create_dataset

