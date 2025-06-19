"""PDF parsing utilities for extracting questions and answers."""
import re
from typing import List, Dict, Tuple, Optional
import fitz  # PyMuPDF
from dataclasses import dataclass

@dataclass
class TextSpan:
    """Represents a span of text with its metadata."""
    text: str
    font_name: str
    is_bold: bool
    font_size: float
    color: Tuple[float, float, float]
    has_highlight: bool
    fill_color: Optional[Tuple[float, float, float]]

class PDFParser:
    """Parser for extracting questions and answers from PDF files."""
    
    def __init__(self, pdf_path: str):
        """Initialize the PDF parser.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def _is_yellow_highlight(self, color: Tuple[float, float, float]) -> bool:
        """Check if a color is within the yellow highlight range.
        
        Args:
            color: RGB tuple
            
        Returns:
            bool: True if color is in yellow range
        """
        r, g, b = color
        # Check if color is close to #FCE94F (yellow)
        return (0.95 <= r <= 1.0 and 
                0.85 <= g <= 0.95 and 
                0.25 <= b <= 0.35)
    
    def _is_answer_span(self, span: TextSpan) -> bool:
        """Check if a text span represents a marked answer.
        
        Args:
            span: TextSpan object
            
        Returns:
            bool: True if span is marked as answer (bold)
        """
        return span.is_bold
    
    def _extract_spans(self, page: fitz.Page) -> List[TextSpan]:
        """Extract text spans with metadata from a page.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List[TextSpan]: List of text spans with metadata
        """
        spans = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    # Get highlight annotation if exists
                    has_highlight = False
                    fill_color = None
                    for annot in page.annots():
                        if annot.type[0] == 8:  # Highlight annotation
                            rect = annot.rect
                            if rect.intersects(fitz.Rect(span["bbox"])):
                                has_highlight = True
                                fill_color = annot.colors.get("stroke", None)
                                break
                    
                    spans.append(TextSpan(
                        text=span["text"],
                        font_name=span["font"],
                        is_bold="bold" in span["font"].lower(),
                        font_size=span["size"],
                        color=span["color"],
                        has_highlight=has_highlight,
                        fill_color=fill_color
                    ))
        return spans
    
    def _group_into_questions(self, spans: List[TextSpan]) -> List[Dict]:
        """Group text spans into questions and choices.
        
        Args:
            spans: List of TextSpan objects
            
        Returns:
            List[Dict]: List of questions with their choices
        """
        questions = []
        current_question = None
        current_choices = []
        
        for span in spans:
            text = span.text.strip()
            
            # Check for question number
            if re.match(r'^\d+[\.\)]\s', text):
                if current_question is not None:
                    questions.append({
                        'question': current_question,
                        'choices': current_choices
                    })
                current_question = text
                current_choices = []
                continue
            
            # Check for choice
            choice_match = re.match(r'^([A-G])[\.\)]\s*(.*)', text)
            if choice_match:
                letter = choice_match.group(1)
                answer_text = choice_match.group(2).strip()
                current_choices.append({
                    'letter': letter,
                    'text': answer_text,
                    'is_correct': self._is_answer_span(span) or span.has_highlight
                })
                continue
            
            # Append to current question or choice
            if current_question is not None:
                if current_choices:
                    # Nối dòng mới vào đáp án gần nhất
                    current_choices[-1]['text'] += ' ' + text
                else:
                    current_question += ' ' + text
        
        # Add last question
        if current_question is not None:
            questions.append({
                'question': current_question,
                'choices': current_choices
            })
        
        return questions
    
    def extract_questions(self) -> List[Dict]:
        """Extract all questions and their choices from the PDF.
        
        Returns:
            List[Dict]: List of questions with choices and answers
        """
        all_spans = []
        for page in self.doc:
            all_spans.extend(self._extract_spans(page))
        
        questions = self._group_into_questions(all_spans)
        
        return questions
    
    def close(self):
        """Close the PDF document."""
        self.doc.close() 