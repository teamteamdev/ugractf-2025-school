#!/bin/bash

set -euo pipefail

TASK_DIR="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)"
APP_DIR="$TASK_DIR/app"
OUTPUT_DIR="$TASK_DIR/public"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Create a temporary directory for processing files
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Creating temporary directory: $TMP_DIR"
echo "Processing files from: $APP_DIR"

# Function to process files by removing lines ending with '// -'
# and uncommenting lines marked with '// + '
process_file() {
    local input_file="$1"
    local output_file="$2"

    # Skip if file doesn't exist
    if [ ! -f "$input_file" ]; then
        echo "Skipping non-existent file: $input_file"
        return
    fi

    # Create directory structure for output file
    mkdir -p "$(dirname "$output_file")"

    # Process the file: remove lines ending with '// -' and uncomment lines with '// + '
    sed '/\/\/ -$/d; s/\/\/ + //g' "$input_file" > "$output_file"

    echo "Processed: $input_file"
}

# Copy and process specific files
copy_and_process() {
    local file="$1"
    local target="$TMP_DIR/radikal/$file"

    process_file "$APP_DIR/$file" "$target"
}

# Copy and process the main files
copy_and_process ".eslintrc.json"
copy_and_process ".gitignore"
copy_and_process "next-env.d.ts"
copy_and_process "next.config.js"
copy_and_process "package-lock.json"
copy_and_process "package.json"
copy_and_process "tsconfig.json"
copy_and_process "public/radikal.png"

# Process the app directory contents, excluding middleware.ts

(cd "$APP_DIR"; find app -type f | while read -r file; do
    copy_and_process "$file"
done)

tar -C "$TMP_DIR" --strip-components=2 --mtime=2025-04-12 -czf "$OUTPUT_DIR/app.tar.gz" radikal

echo "Archive created: $OUTPUT_DIR/app.tar.gz"
