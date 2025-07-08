#!/bin/bash

# Complete Markdown to Academic PDF Pipeline
# Usage: ./markdown-to-pdf.sh input.md [output.pdf]

if [ $# -lt 1 ]; then
    echo "Usage: $0 input.md [output.pdf]"
    echo "Example: $0 paper.md paper.pdf"
    exit 1
fi

INPUT_MD="$1"
OUTPUT_PDF="${2:-${INPUT_MD%.md}.pdf}"
TEMP_HTML="${INPUT_MD%.md}_temp.html"

# Check if input exists
if [ ! -f "$INPUT_MD" ]; then
    echo "Error: $INPUT_MD not found"
    exit 1
fi

echo "🚀 Academic PDF Generation Pipeline"
echo "=================================="
echo "📝 Input: $INPUT_MD"
echo "📄 Output: $OUTPUT_PDF"
echo ""

# Step 1: Convert Markdown to HTML
echo "Step 1: Converting Markdown to HTML..."
python3 convert-markdown.py "$INPUT_MD" "$TEMP_HTML"

if [ $? -ne 0 ]; then
    echo "❌ Error converting markdown to HTML"
    exit 1
fi

echo "✅ HTML generated: $TEMP_HTML"

# Step 2: Generate PDF
echo ""
echo "Step 2: Generating PDF..."
./generate-pdf.sh "$TEMP_HTML" "$OUTPUT_PDF"

if [ $? -ne 0 ]; then
    echo "❌ Error generating PDF"
    rm -f "$TEMP_HTML"
    exit 1
fi

# Step 3: Cleanup
echo ""
echo "Step 3: Cleaning up temporary files..."
rm -f "$TEMP_HTML"

echo ""
echo "🎉 Academic PDF generation complete!"
echo "📄 Beautiful PDF created: $OUTPUT_PDF"
echo ""

# Optional: Open the PDF
read -p "Open PDF? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$OUTPUT_PDF"
fi