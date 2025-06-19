"""PDF generation utilities for creating output files."""
from typing import List, Dict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch
import os
import re

class PDFWriter:
    """Writer for generating output PDF files."""
    
    def __init__(self):
        """Initialize the PDF writer with necessary fonts."""
        # Use Arial Unicode MS font
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        
        # Register fonts
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        pdfmetrics.registerFont(TTFont('Arial-Bold', font_path))
        
        # Create styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Question',
            fontName='Arial',
            fontSize=12,
            leading=14
        ))
        self.styles.add(ParagraphStyle(
            name='QuestionBold',
            fontName='Arial-Bold',
            fontSize=12,
            leading=14
        ))
        self.styles.add(ParagraphStyle(
            name='Choice',
            fontName='Arial',
            fontSize=11,
            leading=13,
            leftIndent=20
        ))
        self.styles.add(ParagraphStyle(
            name='Answer',
            fontName='Arial-Bold',
            fontSize=11,
            leading=13,
            leftIndent=20
        ))
    
    def _create_question_block(self, question: Dict, style: ParagraphStyle, highlight_correct: bool = False) -> List:
        """Create a question block with its choices.
        
        Args:
            question: Question dictionary
            style: Style for the question text
            highlight_correct: If True, in đậm chữ cái đầu đáp án đúng
        Returns:
            List: List of Paragraph objects
        """
        elements = []
        
        # Add question
        elements.append(Paragraph(question['question'], style))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Add choices
        for choice in question['choices']:
            letter = choice.get('letter', '?')
            text = choice.get('text', '')
            if highlight_correct and choice.get('is_correct', False):
                elements.append(Paragraph(f"<b>{letter}</b>. {text}", self.styles['Choice']))
            else:
                elements.append(Paragraph(f"{letter}. {text}", self.styles['Choice']))
            elements.append(Spacer(1, 0.05 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        return elements
    
    def write_original(self, questions: List[Dict], output_path: str):
        """Write the original questions without answer markers.
        
        Args:
            questions: List of question dictionaries
            output_path: Path to save the output PDF
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        elements = []
        for question in questions:
            elements.extend(self._create_question_block(
                question, 
                self.styles['Question'],
                highlight_correct=False
            ))
        
        # Create PDF
        for element in elements:
            if isinstance(element, Paragraph):
                element.wrapOn(c, width - 2*inch, height)
                element.drawOn(c, inch, height - inch)
                height -= element.height + 0.1*inch
                
                # Start new page if needed
                if height < 2*inch:
                    c.showPage()
                    height = letter[1] - inch
            else:  # Spacer
                height -= element.height
        
        c.save()
    
    def write_answer_key(self, questions: List[Dict], output_path: str):
        """Write the answer key with correct answers.
        
        Args:
            questions: List of question dictionaries
            output_path: Path to save the output PDF
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        elements = []
        for question in questions:
            elements.extend(self._create_question_block(
                question,
                self.styles['QuestionBold'],
                highlight_correct=True
            ))
        
        # Create PDF
        for element in elements:
            if isinstance(element, Paragraph):
                element.wrapOn(c, width - 2*inch, height)
                element.drawOn(c, inch, height - inch)
                height -= element.height + 0.1*inch
                
                # Start new page if needed
                if height < 2*inch:
                    c.showPage()
                    height = letter[1] - inch
            else:  # Spacer
                height -= element.height
        
        c.save() 