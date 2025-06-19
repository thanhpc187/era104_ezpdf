"""Tests for the PDF parser module."""
import pytest
from pathlib import Path
from pdf_tools.parser import PDFParser, TextSpan

def test_text_span_creation():
    """Test TextSpan dataclass creation."""
    span = TextSpan(
        text="Test",
        font_name="Arial",
        is_bold=True,
        font_size=12.0,
        color=(1.0, 1.0, 1.0),
        has_highlight=True,
        fill_color=(1.0, 0.9, 0.3)
    )
    assert span.text == "Test"
    assert span.is_bold is True
    assert span.has_highlight is True

def test_yellow_highlight_detection():
    """Test yellow highlight color detection."""
    parser = PDFParser("dummy.pdf")
    
    # Test yellow highlight
    assert parser._is_yellow_highlight((0.98, 0.9, 0.3)) is True
    
    # Test non-yellow colors
    assert parser._is_yellow_highlight((1.0, 1.0, 1.0)) is False
    assert parser._is_yellow_highlight((0.0, 0.0, 0.0)) is False

def test_answer_span_detection():
    """Test answer span detection logic."""
    parser = PDFParser("dummy.pdf")
    
    # Test highlighted span
    highlighted_span = TextSpan(
        text="Answer",
        font_name="Arial",
        is_bold=False,
        font_size=12.0,
        color=(0.0, 0.0, 0.0),
        has_highlight=True,
        fill_color=None
    )
    assert parser._is_answer_span(highlighted_span) is True
    
    # Test bold span
    bold_span = TextSpan(
        text="Answer",
        font_name="Arial-Bold",
        is_bold=True,
        font_size=12.0,
        color=(0.0, 0.0, 0.0),
        has_highlight=False,
        fill_color=None
    )
    assert parser._is_answer_span(bold_span) is True
    
    # Test regular span
    regular_span = TextSpan(
        text="Not an answer",
        font_name="Arial",
        is_bold=False,
        font_size=12.0,
        color=(0.0, 0.0, 0.0),
        has_highlight=False,
        fill_color=None
    )
    assert parser._is_answer_span(regular_span) is False 