#!/bin/bash

# Academic PDF Generator
# Usage: ./generate-pdf.sh input.html output.pdf

if [ $# -ne 2 ]; then
    echo "Usage: $0 input.html output.pdf"
    exit 1
fi

INPUT_HTML="$1"
OUTPUT_PDF="$2"

# Check if input exists
if [ ! -f "$INPUT_HTML" ]; then
    echo "Error: $INPUT_HTML not found"
    exit 1
fi

# Convert to absolute path
INPUT_PATH=$(realpath "$INPUT_HTML")

echo "🎨 Generating academic PDF..."
echo "📝 Input: $INPUT_PATH"
echo "📄 Output: $OUTPUT_PDF"

# Generate PDF using Chrome
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless \
    --disable-gpu \
    --print-to-pdf="$OUTPUT_PDF" \
    --print-to-pdf-no-header \
    --virtual-time-budget=5000 \
    --run-all-compositor-stages-before-draw \
    --disable-background-timer-throttling \
    --disable-extensions \
    --no-sandbox \
    "file://$INPUT_PATH"

if [ $? -eq 0 ]; then
    echo "✅ PDF generated successfully: $OUTPUT_PDF"
    # Get file size
    size=$(du -h "$OUTPUT_PDF" | cut -f1)
    echo "📄 File size: $size"
else
    echo "❌ Error generating PDF"
    exit 1
fi