import os
import json
import logging
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

# Initialize Groq client once at module level
client = Groq(api_key=GROQ_API_KEY)


def build_prompt(candidate_chunks: list, job_description: str) -> str:
    """
    Build a structured prompt for the LLM.
    Combines retrieved chunks + job description into one context block.
    """
    # Step 1: join chunk texts with labels
    context = ""
    for i, chunk in enumerate(candidate_chunks):
        context += f"\n--- Section {i+1} ---\n{chunk['text']}\n"

    # Step 2: build and return full prompt string
    prompt = f"""
You are an expert technical recruiter with 10 years of experience.

Analyze the following candidate resume sections against the job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME SECTIONS:
{context}

Your task:
1. Calculate a match score from 0 to 100
2. List the candidate's key strengths relevant to this role
3. List important skills or experience missing from the resume
4. Give a hiring recommendation: Strong Yes / Yes / Maybe / No

IMPORTANT: Respond ONLY in this exact JSON format, nothing else:
{{
    "match_score": <integer 0-100>,
    "strengths": ["strength1", "strength2", "strength3"],
    "missing_skills": ["skill1", "skill2"],
    "recommendation": "<Strong Yes / Yes / Maybe / No>",
    "summary": "<2-3 sentence recruiter summary>"
}}
"""
    return prompt


def analyze_candidate(candidate_chunks: list, job_description: str) -> dict:
    """
    Send prompt to Groq LLM and parse structured JSON response.
    Returns analysis dict or error dict on failure.
    """
    # YOUR TASK:
    # Step 1: call build_prompt() to get the prompt string
    prompt = build_prompt(candidate_chunks, job_description)

    # Step 2: call client.chat.completions.create() with:
    #         model = LLM_MODEL
    #         messages = [{"role": "user", "content": prompt}]
    #         temperature = 0.2  (low = more consistent, less creative)
    #         max_tokens = 1000
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000
    )

    # Step 3: extract response text
    # Hint: response.choices[0].message.content
    response_text = response.choices[0].message.content
    # Clean markdown code blocks if present
    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    # Step 4: parse JSON from response text
    # Hint: json.loads(response_text)
    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return {"match_score": 0, "error": "Invalid JSON response from LLM."}
    # Wrap in try/except — LLM sometimes adds extra text around JSON

    # Step 5: return parsed dict
    # On failure: log error, return {"match_score": 0, "error": str(e)}
    return analysis


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from src.embeddings.vectorstore import search_similar

    # Test job description
    jd = """
    We are looking for a Data Science Intern with:
    - Strong Python skills (Pandas, NumPy, Scikit-learn)
    - Experience with machine learning models
    - Knowledge of SQL and databases
    - Good communication skills
    - Experience with data visualization tools
    """

    # Search for relevant chunks
    chunks = search_similar(jd, n_results=5)

    # Analyze
    result = analyze_candidate(chunks, jd)

    print("\n── AI Analysis Result ──")
    print(json.dumps(result, indent=2))