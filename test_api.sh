#!/bin/bash

set -e

cd ../"Programming Challenge Files"

for file in *; do
    if [ -f "$file" ]; then
        # Print the name of the file being processed.
        echo "Processing file: $file"

        # Send a POST request with the file to the specified API endpoint.
        response=$(curl -X POST http://localhost:4040/api/v1/extract -F "file=@$file")

        # Print the HTTP response code from the curl request.
        echo "Response code for $file: $response"
    else
        # Print a message if the current item is not a file.
        echo "Skipping $file: Not a file"
    fi
done

echo "All files processed."
