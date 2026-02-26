#!/bin/bash
# Auto-upload marine_corps_news.json to WordPress server
# Run this script after the aggregator updates the JSON file

JSON_FILE="/Users/canadytw/PycharmProjects/Jarheads.net/data/marine_corps_news.json"
REMOTE_HOST="jarheads@162.241.218.175"
REMOTE_PATH="~/public_html/data/marine_corps_news.json"

# Check if JSON file exists
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file not found at $JSON_FILE"
    exit 1
fi

# Upload to server
echo "Uploading marine_corps_news.json to WordPress server..."
scp "$JSON_FILE" "$REMOTE_HOST:$REMOTE_PATH"

if [ $? -eq 0 ]; then
    echo "✓ Upload successful!"
    echo "WordPress will automatically import new articles within the hour."
else
    echo "✗ Upload failed!"
    exit 1
fi
