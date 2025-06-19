import sys, json
from pathlib import Path
from auto_exam_pdf import make_pdf

"""Usage: python regenerate_pdf.py cache/<digest>_<name>.json
Creates PDFs original2_ and answerkey2_ again without calling LLM."""

def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_pdf.py cache/<json_file>")
        sys.exit(1)
    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print("Cache JSON file not found")
        sys.exit(1)
    questions = json.loads(json_file.read_text(encoding="utf-8"))
    base = json_file.stem.split("_",1)[-1]  # original pdf stem
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    pdf_original = output_dir / f"original2_{base}.pdf"
    pdf_answer = output_dir / f"answer2_{base}.pdf"
    print("Re-creating PDFs from cache…")
    make_pdf(questions, {}, str(pdf_original), show_answer=False)
    make_pdf(questions, {}, str(pdf_answer), show_answer=True)
    print("Done →", pdf_original, pdf_answer)

if __name__ == "__main__":
    main() 