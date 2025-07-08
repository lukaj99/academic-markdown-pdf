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

Create this conversion script:

### `convert-markdown.py`
```python
#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def markdown_to_html(markdown_content, title="Academic Paper"):
    """Convert markdown to academic HTML with proper structure"""
    
    # Extract title and subtitle
    lines = markdown_content.split('\n')
    main_title = ""
    subtitle = ""
    
    for i, line in enumerate(lines):
        if line.startswith('# ') and not main_title:
            main_title = line[2:].strip()
            lines[i] = ""
            # Check if next non-empty line is italic (subtitle)
            for j in range(i+1, min(i+3, len(lines))):
                if lines[j].strip() and lines[j].strip().startswith('*') and lines[j].strip().endswith('*'):
                    subtitle = lines[j].strip()[1:-1]
                    lines[j] = ""
                    break
            break
    
    content = '\n'.join(lines)
    
    # Convert markdown elements
    content = convert_markdown_elements(content)
    
    # Generate HTML with template
    html = generate_html_template(main_title, subtitle, content)
    return html

def convert_markdown_elements(content):
    """Convert markdown syntax to HTML"""
    
    # Headers
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Handle four-level headers
    content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Abstract section (special handling)
    content = re.sub(
        r'<h2>Abstract</h2>\s*\n(.*?)\n(?=<h[12]|---)', 
        r'<section class="abstract"><div class="abstract-title">Abstract</div>\1</section>',
        content, 
        flags=re.DOTALL
    )
    
    # Keywords
    content = re.sub(
        r'\*\*Keywords:\*\*(.*?)(?=\n\n|\n---|$)',
        r'<div class="keywords"><strong>Keywords:</strong>\1</div>',
        content,
        flags=re.DOTALL
    )
    
    # Bold and italic
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    
    # Blockquotes
    content = re.sub(r'^> (.*?)$', r'<blockquote><p>\1</p></blockquote>', content, flags=re.MULTILINE)
    
    # Tables
    content = convert_tables(content)
    
    # Lists
    content = convert_lists(content)
    
    # Paragraphs
    content = convert_paragraphs(content)
    
    # Section separators
    content = re.sub(r'^---$', r'<hr class="section-separator">', content, flags=re.MULTILINE)
    
    return content

def convert_tables(content):
    """Convert markdown tables to HTML"""
    table_pattern = r'(\|.*?\|.*?\n)+(\|.*?\|.*?\n)+'
    
    def table_replacer(match):
        table_text = match.group(0).strip()
        lines = table_text.split('\n')
        
        # Extract headers and rows
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        rows = []
        
        for line in lines[2:]:  # Skip separator line
            if line.strip():
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(row)
        
        # Generate HTML table
        html = '<div class="table-container">\n<table>\n<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for row in rows:
            html += '<tr>\n'
            for cell in row:
                html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
        
        html += '</tbody>\n</table>\n</div>'
        return html
    
    return re.sub(table_pattern, table_replacer, content, flags=re.MULTILINE)

def convert_lists(content):
    """Convert markdown lists to HTML"""
    # Unordered lists
    content = re.sub(r'^- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>(?:\n<li>.*?</li>)*)', r'<ul>\n\1\n</ul>', content, flags=re.DOTALL)
    
    # Ordered lists
    content = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>(?:\n<li>.*?</li>)*)', r'<ol>\n\1\n</ol>', content, flags=re.DOTALL)
    
    return content

def convert_paragraphs(content):
    """Convert text blocks to paragraphs"""
    # Split content into blocks
    blocks = re.split(r'\n\s*\n', content)
    result = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Skip if already HTML
        if block.startswith('<') or block in ['', '---']:
            result.append(block)
        else:
            # Check if first paragraph in section
            if any(tag in block for tag in ['<h1>', '<h2>', '<section>']):
                result.append(block)
            else:
                result.append(f'<p>{block}</p>')
    
    return '\n\n'.join(result)

def generate_html_template(title, subtitle, content):
    """Generate complete HTML document with academic styling"""
    
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Load Gulliver Elsevier Fonts */
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Text.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Text.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Italic-Text.otf') format('opentype');
            font-weight: 400;
            font-style: italic;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Italic-Text.otf') format('opentype');
            font-weight: 700;
            font-style: italic;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Display';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Display.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Display';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Display.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Caption';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Caption.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Caption';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Caption.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Mono';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Mono-Regular.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}

        /* Page Setup - Clean academic layout */
        @page {{
            size: A4;
            margin: 25mm 20mm;
        }}

        /* Reset and Base Typography */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Gulliver Elsevier', Times, serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #000000;
            background: #ffffff;
            text-align: justify;
            hyphens: auto;
            orphans: 2;
            widows: 2;
            word-spacing: 0.02em;
            letter-spacing: 0.01em;
        }}

        /* Article Structure */
        .article {{
            max-width: 210mm;
            margin: 0 auto;
        }}

        /* Typography Hierarchy - Optimized Academic Standards */
        h1 {{
            font-family: 'Gulliver Elsevier Display', serif;
            font-size: 14pt;
            font-weight: 700;
            line-height: 1.3;
            color: #000000;
            margin: 24pt 0 16pt 0;
            text-align: left;
            page-break-after: avoid;
            letter-spacing: -0.01em;
        }}

        h2 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 12pt;
            font-weight: 700;
            color: #1a365d;
            margin: 20pt 0 10pt 0;
            text-align: left;
            page-break-after: avoid;
            letter-spacing: 0;
        }}

        h3 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 11pt;
            font-weight: 700;
            color: #2d3748;
            margin: 16pt 0 8pt 0;
            text-align: left;
            page-break-after: avoid;
        }}

        h4 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 10pt;
            font-weight: 700;
            color: #4a5568;
            margin: 14pt 0 6pt 0;
            text-align: left;
            page-break-after: avoid;
            font-style: italic;
        }}

        /* Title Page */
        .title-page {{
            text-align: center;
            margin-bottom: 32pt;
            page-break-after: avoid;
        }}

        .main-title {{
            font-family: 'Gulliver Elsevier Display', serif;
            font-size: 16pt;
            font-weight: 700;
            line-height: 1.4;
            color: #000000;
            margin-bottom: 20pt;
            letter-spacing: -0.02em;
            max-width: 80%;
            margin-left: auto;
            margin-right: auto;
        }}

        .subtitle {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 11pt;
            font-weight: 400;
            color: #4a5568;
            font-style: italic;
            margin-bottom: 32pt;
            line-height: 1.5;
        }}

        /* Abstract - Refined Academic Style */
        .abstract {{
            background: #f8f9fa;
            border-left: 2pt solid #1a365d;
            padding: 16pt 20pt;
            margin: 20pt 0 28pt 0;
            font-size: 10pt;
            line-height: 1.5;
            page-break-inside: avoid;
        }}

        .abstract-title {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 9pt;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 12pt;
            text-transform: uppercase;
            letter-spacing: 1pt;
        }}

        .keywords {{
            margin-top: 12pt;
            font-size: 9pt;
            color: #666;
        }}

        .keywords strong {{
            font-weight: 700;
            color: #333;
        }}

        /* Content Styling - Optimized Academic Spacing */
        p {{
            margin-bottom: 12pt;
            text-indent: 0;
        }}

        .first-paragraph {{
            text-indent: 0;
        }}

        /* Following paragraphs in sections get indentation */
        section p + p {{
            text-indent: 14pt;
            margin-bottom: 12pt;
        }}

        /* Lists - Optimized Academic Style */
        ul, ol {{
            margin: 10pt 0 12pt 20pt;
            padding: 0;
        }}

        li {{
            margin-bottom: 6pt;
            line-height: 1.5;
        }}

        /* Tables - Following Nature Standards */
        .table-container {{
            margin: 16pt 0;
            page-break-inside: avoid;
        }}

        .table-title {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 9pt;
            font-weight: 700;
            color: #000;
            margin-bottom: 6pt;
            text-align: left;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
            line-height: 1.3;
        }}

        th {{
            background: #f0f0f0;
            font-weight: 700;
            padding: 6pt 8pt;
            border: 1pt solid #ccc;
            text-align: left;
            vertical-align: top;
        }}

        td {{
            padding: 6pt 8pt;
            border: 1pt solid #ddd;
            vertical-align: top;
        }}

        /* Blockquotes - Academic Style */
        blockquote {{
            margin: 12pt 0;
            padding: 8pt 16pt;
            border-left: 2pt solid #ddd;
            font-style: italic;
            background: #fafafa;
            page-break-inside: avoid;
        }}

        blockquote p {{
            margin-bottom: 6pt;
        }}

        /* Emphasis and Special Elements */
        strong, b {{
            font-weight: 700;
        }}

        em, i {{
            font-style: italic;
        }}

        .statistic {{
            font-weight: 700;
            color: #d63384;
        }}

        /* Case Studies - Subtle Academic Treatment */
        .case-study {{
            border: 1pt solid #e0e0e0;
            padding: 12pt;
            margin: 16pt 0;
            background: #fbfbfb;
            page-break-inside: avoid;
        }}

        .case-study-title {{
            font-weight: 700;
            color: #2c5aa0;
            margin-bottom: 8pt;
            font-size: 11pt;
        }}

        /* Highlight Boxes - Minimal Academic Style */
        .highlight-box {{
            background: #f0f4f8;
            border: 1pt solid #b8d4ea;
            padding: 10pt;
            margin: 12pt 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }}

        /* Section Separators */
        .section-separator {{
            border: none;
            height: 0.5pt;
            background: #d0d0d0;
            margin: 28pt 0;
        }}

        /* Captions and Small Text */
        .caption, .small-text {{
            font-family: 'Gulliver Elsevier Caption', serif;
            font-size: 8pt;
            color: #666;
            line-height: 1.3;
        }}

        /* Page Breaks */
        .page-break {{
            page-break-before: always;
        }}

        .avoid-break {{
            page-break-inside: avoid;
        }}

        /* Print Optimizations */
        @media print {{
            body {{
                font-size: 10.5pt;
                line-height: 1.5;
            }}
            
            .main-title {{
                font-size: 15pt;
            }}
            
            h1 {{ font-size: 13pt; }}
            h2 {{ font-size: 11.5pt; }}
            h3 {{ font-size: 10.5pt; }}
            h4 {{ font-size: 9.5pt; }}
            
            .abstract {{
                font-size: 9.5pt;
            }}
            
            table {{
                font-size: 8.5pt;
            }}
            
            p {{
                margin-bottom: 11pt;
            }}
            
            section p + p {{
                text-indent: 13pt;
            }}
        }}
    </style>
</head>
<body>
    <article class="article">
        <!-- Title Page -->
        <header class="title-page">
            <h1 class="main-title">{title}</h1>'''
    
    if subtitle:
        template += f'''
            <p class="subtitle">{subtitle}</p>'''
    
    template += f'''
        </header>

        <!-- Content -->
        {content}
    </article>
</body>
</html>'''
    
    return template

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert-markdown.py input.md output.html")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    # Read markdown
    markdown_content = input_file.read_text(encoding='utf-8')
    
    # Extract title for HTML title tag
    title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Academic Paper"
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content, title)
    
    # Write HTML
    output_file.write_text(html_content, encoding='utf-8')
    print(f"Converted {input_file} → {output_file}")
```

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
# Step 1: Markdown to HTML
python3 convert-markdown.py paper.md paper.html

# Step 2: HTML to PDF
./generate-pdf.sh paper.html paper.pdf
```

#### Customize fonts path:
Edit the font paths in `convert-markdown.py`:
```python
src: url('/path/to/your/fonts/Gulliver-Elsevier-Regular-Text.otf')
```

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
- Check font file paths in HTML template
- Ensure Gulliver Elsevier fonts are installed
- Verify file permissions

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
├── generate-pdf.sh         # HTML to PDF generator  
├── markdown-to-pdf.sh      # Complete pipeline
├── your-paper.md          # Input markdown
└── your-paper.pdf         # Output PDF
```

This system transforms any well-structured academic markdown into a beautiful, publication-ready PDF that rivals professionally typeset documents.