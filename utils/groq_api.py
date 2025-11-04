"""
Groq API integration for generating quiz questions
"""
import random
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_questions(category="general", num_questions=10, question_type="financial"):
    """
    Generate quiz questions using Groq API
    
    Args:
        category: Topic category for questions
        num_questions: Number of questions to generate
    
    Returns:
        List of question dictionaries with options and effects
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Use random library to ensure different questions each time
    seed = random.randint(100000, 9999999)
    
    # Build prompt based on question type
    if question_type == "would_you_rather":
        question_instruction = f"""Generate UNIQUE and THOUGHT-PROVOKING 'Would you rather' questions.
        
RULES:
- Each question MUST be COMPLETELY DIFFERENT from others
- NO REPETITION of themes or scenarios
- Make them engaging for ADULTS, not childish
- Challenging moral dilemmas or interesting trade-offs
- Creative superpowers with limitations
- Career/lifestyle choices with consequences
- Time travel or reality-bending scenarios
- Social situations with humor

EXAMPLES:
- "Would you rather know the date of your death or the cause of your death?"
- "Would you rather have the ability to read minds but never turn it off, or be able to teleport but arrive naked?"
- "Would you rather live in a world where everyone can hear your thoughts, or you can hear everyone's?"

Each question must be UNIQUE - no repeating patterns!"""
    else:
        question_instruction = f"""Generate IMMERSIVE and FUN questions about {category}.
        
IMPORTANT RULES:
- Questions should be about the WORLD/UNIVERSE of {category}, NOT about money or financial decisions
- Make questions like "If YOU were in this world/scenario, what would you do?"
- Focus on choices, dilemmas, and situations from {category}
- Be creative and engaging
- Each question should be UNIQUE and DIFFERENT
-there should not be why in question eg. If you were a chess piece, which one would you be and why?

EXAMPLES (if category was Harry Potter):
- "If you were a student at Hogwarts and discovered a classmate cheating using magic, what would you do?"
- "You're facing a Dementor. Which memory would you use for your Patronus charm?"
- "If you could master only one branch of magic, which would you choose and why?"
- "You discovered a dangerous creature in the Forbidden Forest. What's your approach?"

NO FINANCIAL QUESTIONS - make it about the world of {category}!"""
    
    # Prompt for Groq to generate questions
    prompt = f"""[Session ID: {seed}]

Generate exactly {num_questions} COMPLETELY UNIQUE quiz questions that you have NEVER generated before.

CRITICAL RULES:
- These MUST be entirely NEW questions
- DO NOT repeat any patterns from previous generations
- Think of FRESH scenarios and situations
- Be CREATIVE and ORIGINAL
- Each question should explore DIFFERENT themes

{question_instruction}

For each question, provide:
- 4 options (A, B, C, D)
- IMPORTANT MONEY RULES:
  * ONLY ONE option should have POSITIVE money (+10 to +30) - the best/correct answer
  * The other 3 options should have NEGATIVE money
  * Option close to correct: -10 to -20 money
  * Option somewhat wrong: -30 to -50 money  
  * Option very wrong: -60 to -90 money
- Add occasional multipliers (1.5x, 2x, 2.5x, 3x) to about 20% of options
- Make sure each question is DIFFERENT from the others

Return ONLY a valid JSON array:
[
  {{
    "question": "Question text?",
    "options": [
      {{"text": "Best option", "money_change": 10, "multiplier": 2.0}},
      {{"text": "Good option", "money_change": 5}},
      {{"text": "Poor option", "money_change": -20}},
      {{"text": "Worst option", "money_change": -70}}
    ]
  }}
]

Make questions creative, engaging, and avoid concatenated words like 'creditcarddebtorinvest'. 
Use proper spacing and punctuation. Questions should be clear and interesting."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a quiz generator. Return ONLY valid JSON, no explanations,and not same question generate in the session."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 1.0,
        "max_tokens": 4000,
        "top_p": 0.95,
        "presence_penalty": 0.6,
        "frequency_penalty": 0.6
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith("json"):
                content = content[4:].strip()
        
        # Parse JSON
        questions = json.loads(content)
        
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("Invalid questions format")
        
        return questions[:num_questions]
        
    except Exception as e:
        print(f"Error with Groq API: {e}")
        raise
