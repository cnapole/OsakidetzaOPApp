#!/usr/bin/env python3
"""
Parser for the Salusplay Legislación PDF (260602-OO-Legislacion.pdf).
Generates legislacion_preguntas.json with 200 questions.
Then combines with preguntas_enfermero.json into 202606preguntas_enfermero.json.
"""
import json
import re
import sys

# Corrections from the ACTUALIZACIÓN section of the PDF
CORRECTIONS = {
    33: 'b',
    171: 'a',
    192: 'c',
    4: 'a',
    26: 'd',
    113: 'c',
    145: 'c',
}

HEADER_PATTERNS = [
    re.compile(r'^PAG\.\s*\d+\s*$'),
    re.compile(r'PREGUNTAS OSAKIDETZA.*LEGISLACI[OÓ]N'),
    re.compile(r'^OSAKIDETZA\s*$'),
]

def is_header_line(line):
    s = line.strip()
    return any(p.search(s) for p in HEADER_PATTERNS)

def clean_text(text):
    """Normalize whitespace and join hyphenated line breaks."""
    # Join hyphenated word breaks: word-\n  continuation → wordcontinuation
    text = re.sub(r'([a-záéíóúüñA-ZÁÉÍÓÚÜÑ])-[\s\n]+([a-záéíóúüñA-ZÁÉÍÓÚÜÑ])', r'\1\2', text)
    return ' '.join(text.split())

def sentence_case(text):
    """Convert ALL-CAPS text to sentence case (lowercase + capitalize first letter)."""
    lowered = text.lower()
    return lowered[0].upper() + lowered[1:] if lowered else lowered

def parse_questions(raw_text):
    # Strip known header lines
    lines = [l for l in raw_text.split('\n') if not is_header_line(l)]
    text = '\n'.join(lines)

    # Find where actual questions start
    first_q = re.search(r'^\s*PREGUNTA\s+1\b', text, re.MULTILINE)
    if not first_q:
        print("ERROR: Could not find PREGUNTA 1", file=sys.stderr)
        return []
    text = text[first_q.start():]

    # Split into question blocks by PREGUNTA N header (allow leading whitespace)
    blocks = re.split(r'(?=^\s*PREGUNTA\s+\d+\b)', text, flags=re.MULTILINE)
    blocks = [b.strip() for b in blocks if b.strip()]

    questions = []
    problems = []

    for block in blocks:
        m = re.match(r'^\s*PREGUNTA\s+(\d+)\s*$', block, re.MULTILINE)
        if not m:
            continue
        q_num = int(m.group(1))
        rest = block[m.end():].strip()

        # Locate "Respuesta correcta: X" — require letter to be at end of line (not "...CORRECTA:\n A.")
        ans_m = re.search(r'Respuesta\s+correcta\s*:\s*([A-D])\s*$', rest, re.IGNORECASE | re.MULTILINE)
        if not ans_m:
            problems.append(q_num)
            continue

        pre = rest[:ans_m.start()].strip()

        # Separate question text from options: first line matching "^[space]A. " is option start
        opt_start = re.search(r'(?m)^\s*A\.\s', pre)
        if not opt_start:
            problems.append(q_num)
            continue

        question_text = clean_text(pre[:opt_start.start()])
        # Convert ALL CAPS question to sentence case
        if question_text == question_text.upper():
            question_text = sentence_case(question_text)

        opts_raw = pre[opt_start.start():]

        # Parse options: lines starting with A./B./C./D. begin a new option
        options = []
        current_letter = None
        current_parts = []

        for line in opts_raw.split('\n'):
            s = line.strip()
            lm = re.match(r'^([A-D])\.\s*(.*)', s)
            if lm:
                if current_letter:
                    options.append((current_letter, ' '.join(current_parts)))
                current_letter = lm.group(1).lower()
                current_parts = [lm.group(2).strip()] if lm.group(2).strip() else []
            elif current_letter and s:
                current_parts.append(s)

        if current_letter:
            options.append((current_letter, ' '.join(current_parts)))

        if len(options) < 2:
            problems.append(q_num)
            continue

        # Determine correct answer, applying any corrections
        correct_letter = ans_m.group(1).lower()
        if q_num in CORRECTIONS:
            correct_letter = CORRECTIONS[q_num]

        # Build options list
        opts_list = []
        for letter, text_val in options:
            opts_list.append({
                'letter': letter,
                'text': clean_text(text_val),
                'correct': letter == correct_letter
            })

        # Verify exactly one correct (for now just note if not)
        n_correct = sum(1 for o in opts_list if o['correct'])
        if n_correct == 0:
            # Correct letter not found in options — keep as-is and flag
            problems.append(q_num)

        # Extract solution note (Comentario section)
        comment_m = re.search(r'Comentario\s*:', rest[ans_m.end():])
        solution_note = None
        if comment_m:
            comment_start = ans_m.end() + comment_m.end()
            comment_raw = rest[comment_start:].strip()
            solution_note = clean_text(comment_raw) or None

        questions.append({
            '_src_num': q_num,
            'question': question_text,
            'options': opts_list,
            'impugnable': False,
            'solution_note': solution_note,
        })

    return questions, problems


def main():
    # Parse the column-sequential text (properly ordered two-column layout)
    with open('legislacion_sequential.txt', encoding='utf-8') as f:
        raw = f.read()

    questions, problems = parse_questions(raw)

    # Sort by original question number
    questions.sort(key=lambda q: q['_src_num'])

    print(f"Parsed: {len(questions)} questions")
    if problems:
        print(f"Problems with question numbers: {sorted(problems)}")

    # Check for duplicates
    nums = [q['_src_num'] for q in questions]
    dupes = [n for n in nums if nums.count(n) > 1]
    if dupes:
        print(f"Duplicate question numbers: {sorted(set(dupes))}")

    # Verify corrections were applied
    print("\nVerifying corrections:")
    for q_num, expected_letter in CORRECTIONS.items():
        match = next((q for q in questions if q['_src_num'] == q_num), None)
        if match:
            corrects = [o['letter'] for o in match['options'] if o['correct']]
            ok = expected_letter in corrects
            print(f"  Q{q_num}: expected={expected_letter}, got={corrects}, {'OK' if ok else 'MISMATCH'}")
        else:
            print(f"  Q{q_num}: not found!")

    # Save the 200-question legislacion JSON (with original src numbers)
    slim_leq = []
    for q in questions:
        slim_leq.append({
            'src_id': q['_src_num'],
            'question': q['question'],
            'options': q['options'],
            'impugnable': q['impugnable'],
            'solution_note': q['solution_note'],
        })
    with open('legislacion_preguntas.json', 'w', encoding='utf-8') as f:
        json.dump(slim_leq, f, ensure_ascii=False, indent=1)
    print(f"\nWrote legislacion_preguntas.json ({len(slim_leq)} questions)")

    # Load existing enfermero questions
    with open('preguntas_enfermero.json', encoding='utf-8') as f:
        existing = json.load(f)
    print(f"Loaded preguntas_enfermero.json ({len(existing)} questions)")

    # Build combined dataset, assigning new IDs starting from 501
    combined = list(existing)
    last_id = max(q['id'] for q in existing)
    for i, q in enumerate(questions, start=1):
        combined.append({
            'id': last_id + i,
            'question': q['question'],
            'options': q['options'],
            'impugnable': q['impugnable'],
            'solution_note': q['solution_note'],
        })

    print(f"Combined total: {len(combined)} questions")

    with open('202606preguntas_enfermero.json', 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=1)
    print(f"Wrote 202606preguntas_enfermero.json")


if __name__ == '__main__':
    main()
