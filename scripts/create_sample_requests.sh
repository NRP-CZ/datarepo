#!/bin/bash
# ./run.sh invenio db destroy --yes-i-know
# ./run.sh invenio index destroy --yes-i-know
# ./run.sh invenio db init
# ./run.sh invenio db create
# ./run.sh invenio index init
# ./run.sh invenio cf init
# ./run.sh invenio users create --password testtest test@test.com
# ./run.sh invenio users activate test@test.com
# ./run.sh invenio roles create admin
# ./run.sh invenio access allow superuser-access role admin
# ./run.sh invenio roles add test@test.com admin
# Create user and token
# token=$(./run.sh invenio tokens create -n demo-data -u test@test.com)
token=7bQ2N7lngE1J3rG6rBIllUFSEfdtiNMtKOozDs9KwWGWJcKc2B0FM6HVaQD0
echo "$token"

echo "Creating new datasets for requests..."

# Function to create and publish a dataset
create_dataset() {
    local title="$1"

    metadata_json=$(cat <<EOF
{
  "metadata": {
    "title": "$title",
    "resource_type": {
      "id": "c_ba08"
    }
  },
  "parent": {
    "workflow": "default"
  },
  "files": {"enabled": false}
}
EOF
)

    response=$(curl -s -k -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $token" \
      -d "$metadata_json" \
      https://127.0.0.1:5000/api/datasets)

    record_id=$(echo "$response" | jq -r '.id // empty')

    if [ -z "$record_id" ]; then
        echo "Error creating dataset: $title" >&2
        echo "$response" >&2
        return 1
    fi

    publish_link=$(echo "$response" | jq -r '.links.publish // empty')

    if [ -n "$publish_link" ]; then
        curl -s -k -X POST \
          -H "Authorization: Bearer $token" \
          "$publish_link" > /dev/null
        echo "✓ Created and published: $title (ID: $record_id)" >&2
    else
        echo "✓ Created: $title (ID: $record_id)" >&2
    fi

    # ✅ ONLY output on stdout
    echo "$record_id"
}

# Create 5 datasets
record_id_1=$(create_dataset "Dataset for Delete Request")
record_id_2=$(create_dataset "Dataset for Edit Request")
record_id_3=$(create_dataset "Dataset for Publish Draft Request")
record_id_4=$(create_dataset "Dataset for Publish New Version Request")
record_id_5=$(create_dataset "Dataset for Publish Changed Metadata Request")

if [ -z "$record_id_1" ] || [ -z "$record_id_2" ] || [ -z "$record_id_3" ] || [ -z "$record_id_4" ] || [ -z "$record_id_5" ]; then
    echo "Error: Failed to create all datasets."
    exit 1
fi

echo -e "\nUsing record IDs: $record_id_1, $record_id_2, $record_id_3, $record_id_4, $record_id_5"

echo -e "\n=== Creating Requests ==="

# Request 1: Delete Published Record
echo -e "\n1. Creating delete_published_record request..."
request_data_1='{
  "title": "Request to delete published record",
  "request_type": "delete_published_record",
  "receiver": {"user": "1"},
  "topic": {"datasets": "'$record_id_1'"},
  "payload": {
    "removal_reason": "Record contains outdated information",
    "note": "Please review and approve"
  }
}'
echo "Request Data:"
echo "$request_data_1"

req_response_1=$(curl -s -k  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$request_data_1" \
  https://127.0.0.1:5000/api/requests/)

echo "Response:"
echo "$req_response_1" | head -10

req_id_1=$(echo "$req_response_1" | jq -r '.id // empty')
if [ -z "$req_id_1" ]; then
    echo "✗ Failed to create request"
else
    echo "✓ Created request: $req_id_1"

    # Submit request
    submit_link_1=$(echo "$req_response_1" | jq -r '.links.actions.submit // empty')
    if [ -n "$submit_link_1" ]; then
        curl -s -k -X POST -H "Authorization: Bearer $token" "$submit_link_1" > /dev/null
        echo "✓ Submitted request"
    fi
fi

# Request 2: Edit Published Record
echo -e "\n2. Creating edit_published_record request..."
request_data_2='{
  "title": "Request to edit published record metadata",
  "request_type": "edit_published_record",
  "receiver": {"user": "1"},
  "topic": {"datasets": "'$record_id_2'"}
}'

req_response_2=$(curl -s -k  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$request_data_2" \
  https://127.0.0.1:5000/api/requests/)

req_id_2=$(echo "$req_response_2" | jq -r '.id // empty')
if [ -z "$req_id_2" ]; then
    echo "✗ Failed to create request"
else
    echo "✓ Created request: $req_id_2"
    submit_link_2=$(echo "$req_response_2" | jq -r '.links.actions.submit // empty')
    if [ -n "$submit_link_2" ]; then
        curl -s -k -X POST -H "Authorization: Bearer $token" "$submit_link_2" > /dev/null
        echo "✓ Submitted request"
    fi
fi

# Request 3: Publish Draft
echo -e "\n3. Creating publish_draft request..."
request_data_3='{
  "title": "Request to publish draft",
  "request_type": "publish_draft",
  "receiver": {"user": "1"},
  "topic": {"datasets": "'$record_id_3'"},
  "payload": {
    "version": "v1.0"
  }
}'

req_response_3=$(curl -s -k  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$request_data_3" \
  https://127.0.0.1:5000/api/requests/)

req_id_3=$(echo "$req_response_3" | jq -r '.id // empty')
if [ -z "$req_id_3" ]; then
    echo "✗ Failed to create request"
else
    echo "✓ Created request: $req_id_3"
    submit_link_3=$(echo "$req_response_3" | jq -r '.links.actions.submit // empty')
    if [ -n "$submit_link_3" ]; then
        curl -s -k -X POST -H "Authorization: Bearer $token" "$submit_link_3" > /dev/null
        echo "✓ Submitted request"
    fi
fi

# Request 4: Publish New Version
echo -e "\n4. Creating publish_new_version request..."
request_data_4='{
  "title": "Request to publish new version",
  "request_type": "publish_new_version",
  "receiver": {"user": "1"},
  "topic": {"datasets": "'$record_id_4'"},
  "payload": {
    "version": "v2.0"
  }
}'

req_response_4=$(curl -s -k  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$request_data_4" \
  https://127.0.0.1:5000/api/requests/)

req_id_4=$(echo "$req_response_4" | jq -r '.id // empty')
if [ -z "$req_id_4" ]; then
    echo "✗ Failed to create request"
else
    echo "✓ Created request: $req_id_4"
    submit_link_4=$(echo "$req_response_4" | jq -r '.links.actions.submit // empty')
    if [ -n "$submit_link_4" ]; then
        curl -s -k -X POST -H "Authorization: Bearer $token" "$submit_link_4" > /dev/null
        echo "✓ Submitted request"
    fi
fi

# Request 5: Publish Changed Metadata
echo -e "\n5. Creating publish_changed_metadata request..."
request_data_5='{
  "title": "Request to publish changed metadata",
  "request_type": "publish_changed_metadata",
  "receiver": {"user": "1"},
  "topic": {"datasets": "'$record_id_5'"}
}'

req_response_5=$(curl -s -k  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token" \
  -d "$request_data_5" \
  https://127.0.0.1:5000/api/requests/)

req_id_5=$(echo "$req_response_5" | jq -r '.id // empty')
if [ -z "$req_id_5" ]; then
    echo "✗ Failed to create request"
else
    echo "✓ Created request: $req_id_5"
    submit_link_5=$(echo "$req_response_5" | jq -r '.links.actions.submit // empty')
    if [ -n "$submit_link_5" ]; then
        curl -s -k -X POST -H "Authorization: Bearer $token" "$submit_link_5" > /dev/null
        echo "✓ Submitted request"
    fi
fi

echo -e "\n=== Done! ==="
echo "Created 5 requests of different types"
