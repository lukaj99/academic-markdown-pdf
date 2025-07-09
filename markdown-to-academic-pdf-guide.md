# Markdown to Academic PDF Masterpiece Guide

## Overview

This guide provides a complete, reproducible system for converting academic markdown documents into publication-quality PDFs using professional typography and layout standards.

## Prerequisites

### Required Tools
- **Google Chrome** (for PDF generation)
- **Gulliver Elsevier Fonts** (located at `/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/`)
- **Text editor** for HTML template modification

### Font Files Needed
```
Gulliver-Elsevier-Regular-Text.otf
Gulliver-Elsevier-Bold-Text.otf  
Gulliver-Elsevier-Italic-Text.otf
Gulliver-Elsevier-Bold-Italic-Text.otf
Gulliver-Elsevier-Regular-Display.otf
Gulliver-Elsevier-Bold-Display.otf
Gulliver-Elsevier-Regular-Caption.otf
Gulliver-Elsevier-Bold-Caption.otf
Gulliver-Elsevier-Mono-Regular.otf
```

## Step 1: Prepare Your Markdown

### Required Structure
Your markdown should follow this structure:
```markdown
# Main Title

*Subtitle (optional)*

## Abstract

**Background:** ...
**Objective:** ...
**Methods:** ...
**Results:** ...
**Conclusions:** ...

**Keywords:** keyword1, keyword2, keyword3

---

## 1. Introduction

Content here...

---

## 2. Section Name

### 2.1 Subsection

#### 2.1.1 Sub-subsection

Content with **bold** and *italic* emphasis.

> Blockquotes for important statements

### Tables
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

### Lists
- Bullet point 1
- Bullet point 2

1. Numbered item 1
2. Numbered item 2

---

## References

Reference list...

---

## Disclosures

**Conflict of Interest:** ...
**Funding:** ...
```

## Step 2: Convert Markdown to HTML

The primary script for this conversion is `convert-markdown.py`. It now utilizes the `python-markdown` library for robust Markdown parsing and supports a range of academic features.

### Key Features of `convert-markdown.py`:
-   Uses `python-markdown` with extensions like `extra` (for tables, footnotes, fenced code), `codehilite` (for syntax highlighting), `toc` (for table of contents), and more.
-   Extracts title, subtitle, abstract, and keywords to structure the HTML appropriately.
-   Links to an external CSS file (`academic_style.css` by default) for styling.
-   Allows specifying a custom CSS file via the command line.
-   Includes a placeholder for easy MathJax integration for LaTeX-style math rendering.

You do not need to recreate this script; it is provided in the repository.

## Step 3: Generate PDF

Create this PDF generation script:

### `generate-pdf.sh`
```bash
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

echo "Generating academic PDF..."
echo "Input: $INPUT_PATH"
echo "Output: $OUTPUT_PDF"

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
```

## Step 4: Complete Automation Script

### `markdown-to-pdf.sh`
```bash
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
TEMP_HTML="${INPUT_MD%.md}.html"

# Check if input exists
if [ ! -f "$INPUT_MD" ]; then
    echo "Error: $INPUT_MD not found"
    exit 1
fi

echo "🚀 Academic PDF Generation Pipeline"
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

# Step 2: Generate PDF
echo "Step 2: Generating PDF..."
./generate-pdf.sh "$TEMP_HTML" "$OUTPUT_PDF"

if [ $? -ne 0 ]; then
    echo "❌ Error generating PDF"
    rm -f "$TEMP_HTML"
    exit 1
fi

# Step 3: Cleanup
echo "Step 3: Cleaning up..."
rm -f "$TEMP_HTML"

echo ""
echo "✅ Academic PDF generation complete!"
echo "📄 Output: $OUTPUT_PDF"

# Optional: Open the PDF
read -p "Open PDF? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$OUTPUT_PDF"
fi
```

## Step 5: Usage Instructions

### Quick Start
1. **Make scripts executable:**
   ```bash
   chmod +x convert-markdown.py generate-pdf.sh markdown-to-pdf.sh
   ```

2. **Convert your markdown:**
   ```bash
   ./markdown-to-pdf.sh your-paper.md
   ```

### Advanced Usage

#### Convert specific file:
```bash
./markdown-to-pdf.sh research-paper.md beautiful-paper.pdf
```

#### Step-by-step conversion:
```bash
# Step 1: Markdown to HTML (using default academic_style.css)
python3 convert-markdown.py paper.md paper.html

# Or, with a custom CSS file:
python3 convert-markdown.py paper.md paper.html --css my_custom_style.css

# Step 2: HTML to PDF
./generate-pdf.sh paper.html paper.pdf
```

#### Customize Styling and Fonts:
-   **Edit `academic_style.css`:** This is the primary way to change the appearance. You can modify font families, sizes, colors, margins, etc., directly in this file.
    The Gulliver Elsevier font paths are defined in `academic_style.css` (e.g., `src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Text.otf')`). Adjust these paths if your fonts are stored elsewhere or if you want to use different fonts.
-   **Provide your own CSS:** Use the `--css` option as shown above.

## Step 6: Quality Control Checklist

### Before Generation
- ✅ Markdown follows proper structure
- ✅ Headers use correct hierarchy (# ## ### ####)
- ✅ Tables are properly formatted
- ✅ Abstract has required sections
- ✅ References are included

### After Generation
- ✅ Typography looks professional
- ✅ Page breaks are appropriate
- ✅ Tables fit properly
- ✅ No orphaned headings
- ✅ Consistent spacing throughout

## Step 7: Troubleshooting

### Common Issues

#### Fonts not loading:
- Check font file paths in `academic_style.css` (or your custom CSS).
- Ensure Gulliver Elsevier fonts (or your chosen fonts) are installed and accessible at the specified paths.
- Verify file permissions for font files.

#### PDF generation fails:
- Check Chrome installation path
- Ensure sufficient disk space
- Try increasing virtual-time-budget

#### Poor formatting:
- Review markdown structure
- Check for proper header hierarchy
- Ensure tables have proper syntax

### Performance Tips
- Use shorter virtual-time-budget for simple documents
- Remove unused font variants to reduce load time
- Optimize images before including in markdown

## Example Output

The system generates publication-quality PDFs with:
- **Professional typography** using Gulliver Elsevier fonts
- **Academic layout standards** following Nature/Science conventions
- **Proper spacing** and visual hierarchy
- **Print-ready formatting** at 300 DPI equivalent
- **Consistent styling** throughout the document

## File Structure
```
project/
├── convert-markdown.py      # Markdown to HTML converter
├── academic_style.css       # Default CSS for styling HTML
├── generate-pdf.sh         # HTML to PDF generator  
├── markdown-to-pdf.sh      # Complete pipeline
├── your-paper.md          # Input markdown
└── your-paper.pdf         # Output PDF
```

This system transforms any well-structured academic markdown into a beautiful, publication-ready PDF (via HTML) that rivals professionally typeset documents.