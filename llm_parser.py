import os
import requests
from dotenv import load_dotenv
import json
import re

# Tự động load biến môi trường từ file .env nếu có
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

PROMPT_TEMPLATE = '''Bạn là chuyên gia xử lý đề thi trắc nghiệm. Hãy phân tích đoạn văn bản sau và trích xuất các câu hỏi trắc nghiệm.
Với mỗi câu hỏi, hãy trả về một object JSON có cấu trúc:
  "question": (chuỗi) nội dung câu hỏi không bao gồm tiền tố "Câu n:"
  "choices":  danh sách các đáp án, mỗi đáp án là object {{"letter": "A", "text": "..."}}
  "answer":   (chuỗi) ký tự A/B/C/... thể hiện đáp án đúng.
Chỉ trả về MỘT mảng JSON hợp lệ, không kèm giải thích.

Ví dụ:
Đầu vào:
Câu 1: Thủ đô của Việt Nam là gì?
A. Hà Nội
B. TP. Hồ Chí Minh
C. Đà Nẵng
D. Hải Phòng

Đầu ra:
[
  {{"question": "Thủ đô của Việt Nam là gì?", "choices": [{{"letter": "A", "text": "Hà Nội"}}, {{"letter": "B", "text": "TP. Hồ Chí Minh"}}, {{"letter": "C", "text": "Đà Nẵng"}}, {{"letter": "D", "text": "Hải Phòng"}}], "answer": "A"}}
]

Văn bản cần phân tích:
{text}
'''

def split_text_into_chunks(text: str, max_chunk_size: int = 2000) -> list[str]:
    """Chia text thành các phần nhỏ hơn dựa trên số lượng câu hỏi."""
    # Tìm các câu hỏi bằng cách tìm số thứ tự câu hỏi (ví dụ: "Câu 1:", "1.", etc)
    question_markers = re.finditer(r'(?:^|\n)(?:\d+[\.\)]|Câu\s+\d+[:\.])', text)
    question_positions = [m.start() for m in question_markers]
    
    if not question_positions:
        # Nếu không tìm thấy marker, chia đều text
        return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    chunks = []
    current_chunk = text[:question_positions[0]]
    
    for i in range(len(question_positions)):
        start = question_positions[i]
        end = question_positions[i + 1] if i + 1 < len(question_positions) else len(text)
        question_text = text[start:end]
        
        if len(current_chunk) + len(question_text) <= max_chunk_size:
            current_chunk += question_text
        else:
            chunks.append(current_chunk)
            current_chunk = question_text
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def parse_questions_with_llm(text: str, model: str = "deepseek-chat"):
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("Chưa thiết lập DEEPSEEK_API_KEY trong biến môi trường hoặc file .env!")
    
    # Chia text thành các phần nhỏ
    chunks = split_text_into_chunks(text)
    all_questions = []
    
    for chunk in chunks:
        prompt = PROMPT_TEMPLATE.format(text=chunk)
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"DeepSeek API error: {response.status_code} {response.text}")
        
        try:
            content = response.json()["choices"][0]["message"]["content"]
            # Ưu tiên lấy JSON trong code block ```json ... ```
            code_block_match = re.search(r"```json\s*([\s\S]+?)```", content)
            if code_block_match:
                json_str = code_block_match.group(1)
            else:
                # Fallback: tìm đoạn JSON trong content (nếu LLM trả về kèm giải thích)
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                json_str = content[json_start:json_end]
            
            try:
                questions = json.loads(json_str)
                # Nếu LLM trả về trường 'answer', chuyển thành is_correct cho choices
                for q in questions:
                    ans_letter = None
                    if isinstance(q, dict):
                        ans_letter = q.pop('answer', None)
                    if ans_letter:
                        for ch in q.get('choices', []):
                            ch['is_correct'] = (ch.get('letter') == ans_letter)
                all_questions.extend(questions)
            except json.JSONDecodeError as je:
                # Nếu lỗi do JSON bị cắt (thường là thiếu dấu ] hoặc ,)
                if 'Unterminated string' in str(je) or 'Expecting' in str(je) or 'EOF' in str(je):
                    raise RuntimeError(
                        f"Kết quả trả về từ DeepSeek bị cắt giữa chừng (do quá dài). Hãy thử chia nhỏ đề hoặc gửi ít câu hỏi hơn mỗi lần.\nLỗi: {je}\nNội dung JSON: {json_str[:500]}..."
                    )
                else:
                    raise
        except Exception as e:
            raise RuntimeError(f"Không parse được JSON từ DeepSeek: {e}\nNội dung trả về: {response.text}")
    
    return all_questions 