#!/usr/bin/env python3
"""
Convert a two-column pdftotext -layout file into single-column sequential text.
Reads left column then right column per page (correct reading order).
"""
import re
import sys

IN_PATH = 'legislacion_out.txt'
OUT_PATH = 'legislacion_sequential.txt'

# Regex patterns to filter page headers
HEADER_RE = [
    re.compile(r'^PAG\.\s*\d+\s*$'),
    re.compile(r'PREGUNTAS OSAKIDETZA.*LEGISLACI[OÓ]N'),
    re.compile(r'^OSAKIDETZA\s*$'),
    re.compile(r'^OPE\s*$'),
    re.compile(r'^ACTUALIZACIÓN\s*$'),
    re.compile(r'^\d{2}/\d{2}/\d{4}\s*$'),
    re.compile(r'^Pregunta\s+\d+\s+-\s+respuesta'),
    re.compile(r'^•\s+Pregunta\s+\d+'),
    re.compile(r'^Bateria\s+de\s+\d+\s+preguntas'),
    re.compile(r'^PREGUNTAS COMENTADAS'),
    re.compile(r'^OPES ENFERMERÍA'),
    re.compile(r'^LEGISLACIÓN\s*$'),
    re.compile(r'^ASIGNATURA\s*$'),
    re.compile(r'^de Legislación'),
    re.compile(r'^SALUSPLAY'),
    re.compile(r'^CARRETERA'),
    re.compile(r'^48950 ERANDIO'),
    re.compile(r'^TEL\.:'),
    re.compile(r'^FECHA Y LUGAR'),
    re.compile(r'^Todos los derechos'),
    re.compile(r'^grabación\)'),
    re.compile(r'^del editor\. No'),
    re.compile(r'^automática,'),
    re.compile(r'^\-$'),
    re.compile(r'^\-ÚLTIMA'),
]

def is_header(line):
    s = line.strip()
    if not s:
        return False
    return any(p.search(s) for p in HEADER_RE)


def split_line(line, min_gap_chars=4, min_left_content_end=30):
    """
    Split a layout line into (left, right) columns.
    A column separator is a run of min_gap_chars+ spaces after position min_left_content_end.
    Right-only lines start with 55+ leading spaces.
    """
    stripped_right = line.rstrip('\n')

    # Lines shorter than 30 chars → left only
    if len(stripped_right) <= min_left_content_end:
        return stripped_right, ''

    # Check for right-column-only: line starts with 55+ spaces
    content_start = len(stripped_right) - len(stripped_right.lstrip())
    if content_start >= 55:
        return '', stripped_right.strip()

    # Find column separator: first run of 8+ consecutive spaces after position 30
    m = re.search(r' {4,}', stripped_right[min_left_content_end:])
    if m:
        split_pos = min_left_content_end + m.start()
        left = stripped_right[:split_pos].rstrip()
        right = stripped_right[split_pos:].lstrip()
        return left, right

    # No separator found → left only
    return stripped_right.rstrip(), ''


def process_layout_file(text):
    pages = text.split('\x0c')
    result_lines = []

    for page_idx, page in enumerate(pages):
        if not page.strip():
            continue

        raw_lines = page.split('\n')
        left_lines = []
        right_lines = []

        for raw_line in raw_lines:
            left, right = split_line(raw_line)
            if not is_header(left):
                left_lines.append(left)
            if not is_header(right):
                right_lines.append(right)

        # Emit left column then right column for this page
        # (correct reading order for a two-column layout)
        result_lines.extend(left_lines)
        result_lines.append('')  # blank line between columns
        result_lines.extend(right_lines)
        result_lines.append('')  # blank line between pages

    return '\n'.join(result_lines)


def main():
    with open(IN_PATH, encoding='utf-8') as f:
        raw = f.read()

    seq = process_layout_file(raw)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(seq)

    lines = seq.split('\n')
    print(f"Output lines: {len(lines)}")

    # Quick check: count PREGUNTA headers
    q_nums = [int(m.group(1)) for line in lines
              if (m := re.match(r'^PREGUNTA\s+(\d+)\s*$', line.strip()))]
    q_nums.sort()
    print(f"Questions found: {len(q_nums)}")
    if q_nums:
        missing = [n for n in range(1, max(q_nums)+1) if n not in q_nums]
        print(f"Missing: {missing[:20]}")
        dupes = [n for n in set(q_nums) if q_nums.count(n) > 1]
        print(f"Duplicates: {dupes[:20]}")


if __name__ == '__main__':
    main()
