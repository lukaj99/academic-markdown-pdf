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
    
    # Headers (order matters - do 4-level first)
    content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Abstract section (special handling)
    abstract_pattern = r'<h2>Abstract</h2>\s*\n(.*?)(?=\n<h[12]|\n---|\Z)'
    def abstract_replacer(match):
        abstract_content = match.group(1).strip()
        return f'<section class="abstract"><div class="abstract-title">Abstract</div>\n{abstract_content}\n</section>'
    
    content = re.sub(abstract_pattern, abstract_replacer, content, flags=re.DOTALL)
    
    # Keywords
    content = re.sub(
        r'\*\*Keywords:\*\*(.*?)(?=\n\n|\n---|$)',
        r'<div class="keywords"><strong>Keywords:</strong>\1</div>',
        content,
        flags=re.DOTALL
    )
    
    # Bold and italic (order matters)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', content)
    
    # Blockquotes
    content = re.sub(r'^> (.*?)$', r'<blockquote><p>\1</p></blockquote>', content, flags=re.MULTILINE)
    
    # Tables
    content = convert_tables(content)
    
    # Lists
    content = convert_lists(content)
    
    # Handle statistics highlighting
    content = re.sub(r'(\d+[\d\.,%-]*(?:\s*billion|\s*%|\s*\$))', r'<span class="statistic">\1</span>', content)
    
    # Paragraphs
    content = convert_paragraphs(content)
    
    # Section separators
    content = re.sub(r'^---$', r'<hr class="section-separator">', content, flags=re.MULTILINE)
    
    return content

def convert_tables(content):
    """Convert markdown tables to HTML"""
    table_pattern = r'(\|[^\n]+\|\n)(\|[-:\s\|]+\|\n)((?:\|[^\n]+\|\n?)*)'
    
    def table_replacer(match):
        header_line = match.group(1).strip()
        separator_line = match.group(2).strip()
        data_lines = match.group(3).strip()
        
        # Extract headers
        headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # Extract data rows
        rows = []
        if data_lines:
            for line in data_lines.split('\n'):
                if line.strip() and '|' in line:
                    row = [cell.strip() for cell in line.split('|')[1:-1]]
                    if row:  # Only add non-empty rows
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
        
        html += '</tbody>\n</table>\n</div>\n'
        return html
    
    return re.sub(table_pattern, table_replacer, content, flags=re.MULTILINE)

def convert_lists(content):
    """Convert markdown lists to HTML"""
    lines = content.split('\n')
    result = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        stripped = line.strip()
        
        # Unordered list
        if stripped.startswith('- '):
            if not in_ul and in_ol:
                result.append('</ol>')
                in_ol = False
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(f'<li>{stripped[2:]}</li>')
        
        # Ordered list
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ol and in_ul:
                result.append('</ul>')
                in_ul = False
            if not in_ol:
                result.append('<ol>')
                in_ol = True
            content_match = re.match(r'^\d+\.\s(.+)', stripped)
            if content_match:
                result.append(f'<li>{content_match.group(1)}</li>')
        
        # End lists
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            result.append(line)
    
    # Close any open lists
    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')
    
    return '\n'.join(result)

def convert_paragraphs(content):
    """Convert text blocks to paragraphs with proper spacing"""
    # Split content into blocks by double newlines or more
    blocks = re.split(r'\n\s*\n+', content)
    result = []
    in_section = False
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Check if this is a section start
        if block.startswith('<h1>') or block.startswith('<h2>'):
            in_section = True
            result.append(block)
        # Skip if already HTML or special content
        elif (block.startswith('<') or 
              block == '---' or 
              block.startswith('#') or
              '\n<' in block or
              block.startswith('|')):  # Also skip tables
            result.append(block)
        else:
            # Split block into individual lines to handle multi-line paragraphs
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            # If multiple lines, treat as separate paragraphs
            for i, line in enumerate(lines):
                if line:
                    if in_section and i == 0:
                        result.append(f'<p class="first-paragraph">{line}</p>')
                        in_section = False
                    else:
                        result.append(f'<p>{line}</p>')
    
    # Join with extra spacing to ensure proper paragraph separation
    return '\n\n\n'.join(result)

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

        /* Page Setup - Clean with no headers/footers */
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

        .article {{
            max-width: 210mm;
            margin: 0 auto;
        }}

        /* Typography Hierarchy */
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

        /* Abstract */
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

        /* Content */
        p {{
            margin-bottom: 16pt;
            text-indent: 0;
            line-height: 1.6;
        }}

        .first-paragraph {{
            text-indent: 0;
            margin-bottom: 16pt;
        }}

        section p + p {{
            text-indent: 14pt;
            margin-bottom: 16pt;
        }}
        
        /* Add extra spacing between distinct paragraphs */
        p + p {{
            margin-top: 4pt;
        }}

        /* Lists */
        ul, ol {{
            margin: 10pt 0 12pt 20pt;
            padding: 0;
        }}

        li {{
            margin-bottom: 6pt;
            line-height: 1.5;
        }}

        /* Tables */
        .table-container {{
            margin: 16pt 0;
            page-break-inside: avoid;
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

        /* Blockquotes */
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

        /* Emphasis */
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

        /* Section Separators */
        .section-separator {{
            border: none;
            height: 0.5pt;
            background: #d0d0d0;
            margin: 28pt 0;
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
        <header class="title-page">
            <h1 class="main-title">{title}</h1>'''
    
    if subtitle:
        template += f'''
            <p class="subtitle">{subtitle}</p>'''
    
    template += f'''
        </header>
        
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
    
    # Extract title
    title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Academic Paper"
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content, title)
    
    # Write HTML
    output_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Converted {input_file} → {output_file}")