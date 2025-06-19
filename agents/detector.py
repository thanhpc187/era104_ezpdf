"""Agent for detecting correct answers in multiple choice questions."""
from typing import Dict, List
import autogen
from autogen import AssistantAgent

class AnswerDetector(AssistantAgent):
    """Agent that analyzes questions and identifies correct answers."""
    
    def __init__(self):
        """Initialize the answer detector agent."""
        # Configure LLM
        config = {
            "config_list": [{
                "model": "deepseek-chat",
                "api_key": "sk-c44ac3d56860473aadbea37581d057d6",
                "base_url": "https://api.deepseek.com/v1",
                "api_type": "openai"
            }],
            "temperature": 0.0
        }
        
        # System message
        system_message = """You are an expert at analyzing multiple-choice questions and identifying the correct answers.
        Your task is to:
        1. Read each question and its choices carefully
        2. Identify which choice is marked as correct
        3. Return the letter (A, B, C, or D) of the correct answer
        
        You must be confident in your answer (probability > 0.75) to provide it.
        If you're not confident enough, respond with 'UNCLEAR'."""
        
        super().__init__(
            name="AnswerDetector",
            llm_config=config,
            system_message=system_message
        )
    
    def detect_answer(self, question: Dict) -> str:
        """Detect the correct answer for a question.
        
        Args:
            question: Question dictionary containing text and choices
            
        Returns:
            str: Letter of correct answer (A, B, C, D) or 'UNCLEAR'
        """
        # Format question for LLM
        prompt = f"""Question: {question['question']}
        
        Choices:
        A. {question['choices'][0]['text']}
        B. {question['choices'][1]['text']}
        C. {question['choices'][2]['text']}
        D. {question['choices'][3]['text']}
        
        Which choice is marked as correct? Respond with just the letter (A, B, C, or D) or 'UNCLEAR' if you're not confident."""
        
        # Get response from LLM
        response = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        
        # Extract answer
        answer = response.strip().upper()
        if answer in ['A', 'B', 'C', 'D']:
            return answer
        return 'UNCLEAR' 