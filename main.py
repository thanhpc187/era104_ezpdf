"""Main script for processing PDF exam papers."""
import os
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress
from dotenv import load_dotenv
from autogen import UserProxyAgent
import multiprocessing as mp

from agents.detector import AnswerDetector
from pdf_tools.parser import PDFParser
from pdf_tools.writer import PDFWriter

# Load environment variables
load_dotenv()

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()

def process_pdf(pdf_path: str, lang: str = "en") -> None:
    """Process a single PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        lang: Interface language (vi/en)
    """
    try:
        # Initialize components
        parser = PDFParser(pdf_path)
        writer = PDFWriter()
        detector = AnswerDetector()
        
        # Extract questions
        questions = parser.extract_questions()
        
        # Use LLM for questions without clear answer markers
        for question in questions:
            # Nếu không có đáp án nào được đánh dấu đúng
            if not any(choice.get('is_correct', False) for choice in question['choices']):
                # Tạo block text cho LLM hoặc logic phát hiện đáp án đúng
                block = f"{question['question']}\n"
                for choice in question['choices']:
                    block += f"{choice['letter']}. {choice['text']}\n"
                # Dùng LLM hoặc logic để xác định đáp án đúng (trả về 'A', 'B', ...)
                answer_letter = detector.detect_answer(block)
                for choice in question['choices']:
                    choice['is_correct'] = (choice['letter'] == answer_letter)
        
        # Generate output files
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = Path(pdf_path).stem
        original_path = output_dir / f"original_{filename}.pdf"
        answer_key_path = output_dir / f"answerkey_{filename}.pdf"
        
        writer.write_original(questions, str(original_path))
        writer.write_answer_key(questions, str(answer_key_path))
        
        # Cleanup
        parser.close()
        
        for idx, q in enumerate(questions, 1):
            print(f"Câu {idx}: đáp án đúng là {q.get('answer', None)}")
        
    except Exception as e:
        console.print(f"[red]Error processing {pdf_path}: {str(e)}[/red]")
        raise

@app.command()
def main(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file"),
    lang: str = typer.Option("en", help="Interface language (vi/en)"),
    parallel: bool = typer.Option(False, help="Process multiple PDFs in parallel")
):
    """Process PDF exam papers to extract questions and answers."""
    # Check DeepSeek API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]Error: DEEPSEEK_API_KEY environment variable not set[/red]")
        sys.exit(1)
    
    # Process single file
    if not parallel:
        process_pdf(pdf_path, lang)
        console.print("\n✅ Done. Check ./output for results.")
        return
    
    # Process multiple files in parallel
    pdf_dir = Path(pdf_path)
    if not pdf_dir.is_dir():
        console.print("[red]Error: When using --parallel, provide a directory path[/red]")
        sys.exit(1)
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        console.print("[yellow]No PDF files found in the specified directory[/yellow]")
        return
    
    with Progress() as progress:
        task = progress.add_task("Processing PDFs...", total=len(pdf_files))
        
        with mp.Pool() as pool:
            for _ in pool.imap_unordered(process_pdf, pdf_files):
                progress.update(task, advance=1)
    
    console.print("\n✅ Done. Check ./output for results.")

if __name__ == "__main__":
    app() 