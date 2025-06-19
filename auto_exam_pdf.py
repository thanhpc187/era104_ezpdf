import sys
import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import yellow
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from llm_parser import parse_questions_with_llm
import hashlib, json

# OCR fallback
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    convert_from_path = None
    pytesseract = None

# Đăng ký font Unicode (cả thường và bold)
font_path_regular = r"D:/hehe/fonts/dejavu-fonts-ttf-2.37/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf"
font_path_bold = r"D:/hehe/fonts/dejavu-fonts-ttf-2.37/dejavu-fonts-ttf-2.37/ttf/DejaVuSans-Bold.ttf"
if not (os.path.exists(font_path_regular) and os.path.exists(font_path_bold)):
    print("[!] Thiếu file DejaVuSans.ttf hoặc DejaVuSans-Bold.ttf. Hãy kiểm tra lại đường dẫn hoặc tải từ https://dejavu-fonts.github.io/")
    sys.exit(1)
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path_regular))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path_bold))

def extract_text_from_pdf(pdf_path):
    # Try PyMuPDF first
    if fitz is not None:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        if text.strip():
            return text
    # Fallback to OCR
    if convert_from_path is not None and pytesseract is not None:
        images = convert_from_path(pdf_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang='vie')
        return text
    raise RuntimeError("Không thể trích xuất text từ PDF. Hãy cài PyMuPDF hoặc pdf2image + pytesseract.")

def parse_questions_and_answers(text):
    # Tách bảng đáp án cuối file (tìm đoạn bắt đầu bằng số và dấu gạch ngang)
    answer_key = {}
    # Tìm đoạn đáp án cuối file (dòng liên tiếp có dạng số-đáp án)
    answer_lines = re.findall(r'^(\d+)-([A-G])$', text, re.MULTILINE)
    for num, ans in answer_lines:
        answer_key[int(num)] = ans
    # Nếu không tìm thấy, fallback về regex cũ
    if not answer_key:
        answer_section = re.findall(r'(\d+-[A-G])', text)
        for item in answer_section:
            num, ans = item.split('-')
            answer_key[int(num)] = ans
    # Tách từng câu hỏi
    question_blocks = re.split(r'\nCâu \d+:', '\n' + text)
    questions = []
    for block in question_blocks[1:]:
        lines = block.strip().split('\n')
        q_text = lines[0].strip()
        choices = []
        for line in lines[1:]:
            m = re.match(r'^([A-G])\.\s*(.*)', line.strip())
            if m:
                choices.append((m.group(1), m.group(2)))
            if len(choices) >= 7:
                break
        questions.append({
            'question': q_text,
            'choices': choices
        })
    return questions, answer_key

def make_pdf(questions, answer_key, pdf_path, show_answer=False):
    """Generate a PDF.
    
    Args:
        questions (List[dict]): list of questions parsed.
        answer_key (dict): mapping question index (1-based) -> correct letter. If empty and show_answer is True, it will be built from choices having is_correct=True.
        pdf_path (str): output file path.
        show_answer (bool): whether to highlight/bold the correct answer letter.
    """
    # Nếu answer_key rỗng và show_answer, tự xây từ is_correct
    if show_answer and not answer_key:
        answer_key = {}
        for idx, q in enumerate(questions, 1):
            for ch in q.get('choices', []):
                if ch.get('is_correct'):
                    answer_key[idx] = ch.get('letter')
                    break

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []
    question_style = ParagraphStyle('Question', fontName='DejaVuSans', fontSize=12, leading=16, alignment=TA_LEFT)
    choice_style = ParagraphStyle('Choice', fontName='DejaVuSans', fontSize=11, leading=14, leftIndent=20, alignment=TA_LEFT)

    for idx, q in enumerate(questions, 1):
        story.append(Paragraph(f"<b>Câu {idx}:</b> {q['question']}", question_style))

        # choices may be list[tuple] or list[dict]
        for ch in q['choices']:
            if isinstance(ch, tuple):
                letter, text_choice = ch
                is_correct = (answer_key.get(idx) == letter) if show_answer else False
            else:
                letter = ch.get('letter')
                text_choice = ch.get('text')
                is_correct = ch.get('is_correct', False) or (answer_key.get(idx) == letter)

            if show_answer and is_correct:
                story.append(Paragraph(f"<b><font name='DejaVuSans-Bold'>{letter}</font></b>. {text_choice}", choice_style))
            else:
                story.append(Paragraph(f"{letter}. {text_choice}", choice_style))
        story.append(Spacer(1, 8))

    doc.build(story)

def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python auto_exam_pdf.py input/ten_file.pdf")
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Không tìm thấy file: {pdf_path}")
        sys.exit(1)
    print("Đang trích xuất text từ PDF...")
    text = extract_text_from_pdf(pdf_path)
    print("Đang phân tích câu hỏi và đáp án bằng LLM...")
    questions = parse_questions_with_llm(text)
    # Debug số lượng câu hỏi và đáp án
    for idx, q in enumerate(questions, 1):
        print(f"Câu {idx}: {q['question']}")
        for c in q['choices']:
            print(f"  {c['letter']}. {c['text']}")

    # Lưu cache JSON để tái sinh PDF nhanh
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    digest = hashlib.md5(text.encode()).hexdigest()
    json_path = cache_dir / f"{digest}_{Path(pdf_path).stem}.json"
    json_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[i] Đã lưu cache câu hỏi vào {json_path}")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    base_name = Path(pdf_path).stem
    pdf_original = output_dir / f"original2_{base_name}.pdf"
    pdf_answer = output_dir / f"answer2_{base_name}.pdf"
    print(f"Đang tạo file đề gốc: {pdf_original}")
    make_pdf(questions, {}, str(pdf_original), show_answer=False)
    print(f"Đang tạo file đề có đáp án: {pdf_answer}")
    # Nếu bạn có bảng đáp án đúng, truyền vào answer_key, còn không thì để trống
    make_pdf(questions, {}, str(pdf_answer), show_answer=True)
    print("kết quả trong thư mục output/ (original2_*, answer2_*)")

if __name__ == "__main__":
    main() 