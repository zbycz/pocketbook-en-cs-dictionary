#!/usr/bin/env python3
"""Convert the GNU/FDL English-Czech source text (en-cs.txt) to XDXF.

Source format (tab separated):
    english <TAB> czech <TAB> pos/domain <TAB> note <TAB> author

Output: one <ar> entry per headword, translations grouped by part of speech.
"""

import argparse
import html
import sys
from collections import OrderedDict

POS_TOKENS = {
    "n:": "n.",
    "v:": "v.",
    "adj:": "adj.",
    "adv:": "adv.",
    "num:": "num.",
    "pron:": "pron.",
    "prep:": "prep.",
    "conj:": "conj.",
    "interj:": "interj.",
    "pl.": "pl.",
}


POS_ORDER = ["n.", "adj.", "adv.", "v.", "num.", "pron.", "prep.", "conj.", "interj.", "pl."]


def split_pos(field):
    """Split the pos/domain field into (pos, note)."""
    pos = ""
    rest = []
    for token in field.split():
        if token in POS_TOKENS and not pos:
            pos = POS_TOKENS[token]
        else:
            rest.append(token)
    return pos, " ".join(rest)


def esc(text):
    return html.escape(text, quote=False)


def split_headwords(word):
    """Expand entries like 'bbq = barbeque' into both spelling variants."""
    if " = " in word:
        return [part.strip() for part in word.split(" = ") if part.strip()]
    return [word]


def parse(src):
    raw = OrderedDict()
    skipped = 0
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            word = parts[0].strip()
            czech = parts[1].strip()
            if not word or not czech:
                skipped += 1
                continue
            pos, note = split_pos(parts[2] if len(parts) > 2 else "")
            raw.setdefault(word, []).append((pos, note, czech))

    entries = OrderedDict()
    for word, rows in raw.items():
        groups = OrderedDict()
        last_pos = ""
        for pos, note, czech in rows:
            if pos:
                last_pos = pos
            translations = groups.setdefault((pos or last_pos, note), [])
            if czech not in translations:
                translations.append(czech)
        for headword in split_headwords(word):
            target = entries.setdefault(headword, OrderedDict())
            for key, translations in groups.items():
                merged = target.setdefault(key, [])
                for czech in translations:
                    if czech not in merged:
                        merged.append(czech)
    return entries, skipped


def render(entries):
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<xdxf lang_from="eng" lang_to="cs" format="visual">',
        "<full_name>Anglicko-cesky slovnik (GNU/FDL)</full_name>",
        "<description>",
        "GNU/FDL Anglicko-cesky slovnik, https://www.svobodneslovniky.cz/",
        "Converted to PocketBook .dic with pb-dic-converter.",
        "</description>",
        "<lexicon>",
    ]
    for word, groups in entries.items():
        def order(key):
            pos, note = key
            return (
                POS_ORDER.index(pos) if pos in POS_ORDER else len(POS_ORDER),
                pos,
                note,
            )

        lines = []
        for (pos, note), translations in sorted(groups.items(), key=lambda kv: order(kv[0])):
            label = " ".join(
                part
                for part in (
                    f"<i>{esc(pos)}</i>" if pos else "",
                    f"<i>{esc(note)}</i>" if note else "",
                )
                if part
            )
            body = "; ".join(esc(t) for t in translations)
            lines.append(f"{label} \u2192 {body}" if label else f"\u2192 {body}")
        out.append(f"<ar><k>{esc(word)}</k><def>{'<br/>'.join(lines)}</def></ar>")
    out.append("</lexicon>")
    out.append("</xdxf>")
    return "\n".join(out) + "\n"


def load_additions(path):
    """Load hand-written additions: english <TAB> czech <TAB> pos."""
    entries = OrderedDict()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            word = parts[0].strip()
            czech = parts[1].strip() if len(parts) > 1 else ""
            pos = parts[2].strip() if len(parts) > 2 else ""
            if not word or not czech:
                continue
            groups = entries.setdefault(word, OrderedDict())
            translations = groups.setdefault((pos, ""), [])
            if czech not in translations:
                translations.append(czech)
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", required=True, help="en-cs.txt source file")
    parser.add_argument("-o", "--output", required=True, help="output .xdxf file")
    parser.add_argument("-a", "--additions", help="optional TSV with extra entries to merge")
    args = parser.parse_args()

    entries, skipped = parse(args.input)

    added = 0
    if args.additions:
        for word, groups in load_additions(args.additions).items():
            target = entries.setdefault(word, OrderedDict())
            for key, translations in groups.items():
                merged = target.setdefault(key, [])
                for czech in translations:
                    if czech not in merged:
                        merged.append(czech)
            added += 1

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(render(entries))

    total = sum(len(g) for g in entries.values())
    print(f"headwords: {len(entries)}", file=sys.stderr)
    print(f"  from additions: {added}", file=sys.stderr)
    print(f"translation groups: {total}", file=sys.stderr)
    print(f"skipped (no czech): {skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()
