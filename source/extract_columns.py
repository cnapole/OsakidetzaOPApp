#!/usr/bin/env python3
"""
Extract text from two-column PDF preserving column order (left col then right col per page).
Uses pdfplumber with word-level bounding boxes.
"""
import sys
import re
sys.path.insert(0, '/home/cnapole/miniconda3/lib/python3.12/site-packages')
import pdfplumber

PDF_PATH = 'pdfs/260602-OO-Legislacion.pdf'
OUT_PATH = 'legislacion_columns.txt'
COL_BOUNDARY = 300  # x0 threshold separating left and right columns

def words_to_lines(words, x_tol=10, y_tol=5):
    """Reconstruct text lines from word bboxes, sorted by y then x."""
    if not words:
        return []
    words = sorted(words, key=lambda w: (round(w['top'] / y_tol), w['x0']))
    lines = []
    current_line_y = None
    current_line = []

    for w in words:
        y = round(w['top'] / y_tol)
        if current_line_y is None or y != current_line_y:
            if current_line:
                lines.append(current_line)
            current_line = [w]
            current_line_y = y
        else:
            current_line.append(w)

    if current_line:
        lines.append(current_line)

    result = []
    prev_line_words = None
    for line_words in lines:
        # Join words in the line, preserving spacing
        text_parts = []
        for i, w in enumerate(line_words):
            if i == 0:
                text_parts.append(w['text'])
            else:
                # Add space if there's a gap between words
                gap = w['x0'] - line_words[i-1]['x1']
                if gap > 3:
                    text_parts.append(' ')
                text_parts.append(w['text'])
        result.append(''.join(text_parts))

    return result


def extract_column_text(page, col_min_x, col_max_x):
    """Extract text from a specific x-range column."""
    words = page.extract_words(x_tolerance=1, y_tolerance=3)
    col_words = [w for w in words if w['x0'] >= col_min_x and w['x0'] < col_max_x]
    return words_to_lines(col_words)


def main():
    all_text_parts = []

    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"Pages: {len(pdf.pages)}")

        for page_num, page in enumerate(pdf.pages, 1):
            # Skip first two pages (cover + copyright)
            if page_num <= 2:
                continue

            # Extract left and right columns
            left_lines = extract_column_text(page, 0, COL_BOUNDARY)
            right_lines = extract_column_text(page, COL_BOUNDARY, 9999)

            # Filter page headers from both columns
            def is_header(line):
                s = line.strip()
                return (
                    re.match(r'^PAG\.\s*\d+\s*$', s) or
                    'PREGUNTAS OSAKIDETZA' in s or
                    s == 'OSAKIDETZA' or
                    s == 'OPE' or
                    re.match(r'^ACTUALIZACIÓN', s) or
                    re.match(r'^\d{2}/\d{2}/\d{4}$', s) or
                    re.match(r'^Pregunta\s+\d+\s+-\s+respuesta', s)
                )

            left_lines = [l for l in left_lines if not is_header(l)]
            right_lines = [l for l in right_lines if not is_header(l)]

            all_text_parts.extend(left_lines)
            all_text_parts.append('')
            all_text_parts.extend(right_lines)
            all_text_parts.append('')

    result = '\n'.join(all_text_parts)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Written to {OUT_PATH}")
    print(f"Lines: {len(all_text_parts)}")


if __name__ == '__main__':
    main()
