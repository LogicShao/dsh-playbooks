r"""Read one \note{...} per explicit Beamer frame and check exported page counts."""
import argparse
import re
from pathlib import Path

_TEX_COMMENT = re.compile(r"\\.|%[^\n]*")
_FRAME = re.compile(r"(?<!\\)\\begin\s*\{frame\}(.*?)(?<!\\)\\end\s*\{frame\}", re.S)
_NOTE = re.compile(r"(?<!\\)\\note\s*\{")
_GROUP_TOKEN = re.compile(r"\\.|[{}]")


def _braced_text(text, start):
    depth = 1
    for token in _GROUP_TOKEN.finditer(text, start):
        if token.group() == "{":
            depth += 1
        elif token.group() == "}":
            depth -= 1
            if depth == 0:
                return text[start:token.start()].strip()
    return ""


def parse_notes_from_tex(path):
    source = Path(path).read_text(encoding="utf-8-sig")
    source = _TEX_COMMENT.sub(lambda match: "" if match[0].startswith("%") else match[0], source)
    notes = []
    for index, frame in enumerate(_FRAME.findall(source), 1):
        matches = list(_NOTE.finditer(frame))
        if len(matches) != 1:
            raise ValueError(f"frame {index}: expected exactly one note, got {len(matches)}")
        note = _braced_text(frame, matches[0].end())
        if not note:
            raise ValueError(f"frame {index}: note is empty or has an unclosed brace")
        notes.append(note)
    if not notes:
        raise ValueError("No explicit Beamer frames found in the source file")
    return notes


def check_exports(tex, pdf, pptx):
    import pymupdf

    with pymupdf.open(pdf) as document:
        page_count = len(document)
    counts = [f"PDF pages={page_count}"]
    notes = parse_notes_from_tex(tex) if tex else None
    if notes is not None:
        counts.append(f"frames={len(notes)}")
        if len(notes) != page_count:
            raise ValueError(", ".join(counts))
    if pptx:
        from pptx import Presentation

        slides = Presentation(pptx).slides
        counts.append(f"PPTX slides={len(slides)}")
        if len(slides) != page_count:
            raise ValueError(", ".join(counts))
        if notes is not None:
            exported_notes = [
                slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
                for slide in slides
            ]
            counts.append(f"non-empty notes={sum(bool(note) for note in exported_notes)}")
            pages = [index for index, (want, got) in enumerate(zip(notes, exported_notes), 1)
                     if want != got.replace("\r\n", "\n")]
            if pages:
                raise ValueError(f"{', '.join(counts)}; note text differs on pages {pages}")
    print(", ".join(counts))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-only", action="store_true", help="Compare PDF and PPTX counts without notes.")
    parser.add_argument("files", nargs="+", metavar="FILE")
    args = parser.parse_args()
    if args.pdf_only and len(args.files) == 2:
        tex, (pdf, pptx) = None, args.files
    elif not args.pdf_only and len(args.files) in (2, 3):
        tex, pdf, *optional_pptx = args.files
        pptx = optional_pptx[0] if optional_pptx else None
    else:
        parser.error("use SOURCE.tex INPUT.pdf [OUTPUT.pptx], or --pdf-only INPUT.pdf OUTPUT.pptx")
    try:
        check_exports(tex, pdf, pptx)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
