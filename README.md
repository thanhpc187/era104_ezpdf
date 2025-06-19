# PDF Answer Extractor
+*Viết bởi **ThanhPC***

A Python tool that extracts answers from PDF exam papers using AutoGen framework and DeepSeek LLM API.

## Features

- Extracts answers from PDF exam papers with marked answers (highlighted, bold, underlined)
- Uses DeepSeek LLM for answer detection when visual markers are unclear
- Generates two output files:
  - Original questions with all choices (no markers)
  - Answer key with correct answers
- Supports both Vietnamese and English interfaces
- Parallel processing for multiple PDFs
- Progress tracking and colorful logging

## Installation

1. Clone repository

```bash
git clone <repo-url>
cd <repo-directory>
```

2. Tạo và kích hoạt virtual environment

**Windows**
```powershell
# Tạo venv
python -m venv venv

# PowerShell
./venv/Scripts/Activate.ps1

**Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Cài đặt các thư viện phụ thuộc vào môi trường ảo
```bash
pip install -r requirements.txt
```

4. Thiết lập khóa API DeepSeek:
```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here
hoặchoặc
$env:DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"

## Usage

1. Place your PDF exam paper in the `input` directory
2. Run the script:
```bash
python auto_exam_pdf.py input/test3test3.pdf
```

Optional arguments:
- `--lang vi|en`: Set interface language (default: en)

## Output

The script generates two files in the `output` directory:
- `original_<filename>.pdf`: Questions with all choices (no markers)
- `answerkey_<filename>.pdf`: Questions with correct answers

## Example

```bash
python main.py input/sample_exam.pdf --lang vi
```

## License

MIT License 