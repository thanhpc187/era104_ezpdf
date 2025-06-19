import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import yellow

# Đọc file text đầu vào
with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Tách bảng đáp án cuối file
answer_key = {}
answer_section = re.findall(r'(\d+-[A-D])', text)
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
        m = re.match(r'^([A-D])\.\s*(.*)', line.strip())
        if m:
            choices.append((m.group(1), m.group(2)))
        if len(choices) == 4:
            break
    questions.append({
        'question': q_text,
        'choices': choices
    })

# Tạo PDF
pdf_path = 'output/final_exam.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
story = []
styles = getSampleStyleSheet()
question_style = ParagraphStyle('Question', fontName='Helvetica', fontSize=12, leading=16, alignment=TA_LEFT)
choice_style = ParagraphStyle('Choice', fontName='Helvetica', fontSize=11, leading=14, leftIndent=20, alignment=TA_LEFT)
choice_bold = ParagraphStyle('ChoiceBold', fontName='Helvetica-Bold', fontSize=11, leading=14, leftIndent=20, alignment=TA_LEFT, backColor=yellow)

for idx, q in enumerate(questions, 1):
    story.append(Paragraph(f"<b>Câu {idx}:</b> {q['question']}", question_style))
    for letter, text_choice in q['choices']:
        if answer_key.get(idx, None) == letter:
            story.append(Paragraph(f"<b>{letter}. {text_choice}</b>", choice_bold))
        else:
            story.append(Paragraph(f"{letter}. {text_choice}", choice_style))
    story.append(Spacer(1, 8))

doc.build(story)
print(f"Đã tạo file PDF: {pdf_path}") 