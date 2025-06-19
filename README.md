# PDF Answer Extractor

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

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your DeepSeek API key:
```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here

# Linux/Mac
export DEEPSEEK_API_KEY=your_api_key_here
```

## Usage

1. Place your PDF exam paper in the `input` directory
2. Run the script:
```bash
python main.py input/your_exam.pdf
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