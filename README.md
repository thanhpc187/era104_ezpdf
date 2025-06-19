# PDF Answer Extractor

*Author: **ThanhPC***

A Python tool that extracts multiple-choice questions from a PDF exam, detects the correct answers with the help of the DeepSeek LLM, and produces two clean PDF files: one without markings and one with the correct options highlighted.

---

## Features

- Supports PDF files that contain either selectable text or scanned images (OCR fallback).
- Uses the DeepSeek Chat API to robustly parse questions when visual cues are unreliable.
- Generates two outputs per input file:
  - **original_&lt;filename&gt;.pdf** – untouched questions and choices.
  - **answer2_&lt;filename&gt;.pdf** – the same questions but with the correct option letter in bold.
- Works with both Vietnamese and English content.
- Simple caching layer to avoid repeated LLM calls for the same file.

---

## Requirements

- Python 3.9 or newer
- A free or paid **DeepSeek** API key ([sign up here](https://deepseek.com/))

---

## Installation

### 1 · Clone the repository

```bash
git clone <repo-url>
cd <repo-directory>
```

### 2 · Create and activate a virtual environment (recommended)

**Windows (PowerShell)**
```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3 · Install dependencies inside the venv

```bash
pip install -r requirements.txt
```

### 4 · Set your DeepSeek API key

**PowerShell / Command Prompt**
```powershell
$env:DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

**Bash / zsh**
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```
---

## Usage

1. Place one or more PDF files in the `input` directory.
2. Run the script:

```bash
python auto_exam_pdf.py input/your_exam.pdf
```

Optional flags (see `main.py` for full CLI):

| Flag          | Description                              | Default |
| ------------- | ---------------------------------------- | ------- |
| `--lang vi|en`| UI language of console logs              | `en`    |

---

## Output

The program creates two files in the `output` directory:

| File pattern                 | Description                               |
| ---------------------------- | ----------------------------------------- |
| `original2_<name>.pdf`       | Questions with all choices (no highlight) |
| `answer2_<name>.pdf`         | Questions with the correct option bolded |

---

## Example

```bash
python auto_exam_pdf.py input/sample_exam.pdf --lang vi
```

---

## License

This project is licensed under the MIT License. 