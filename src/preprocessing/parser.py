import re
import logging
from typing import Optional
import spacy

nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger(__name__)

SKILLS_LIST = [
    # Programming Languages
    "Python", "Java", "JavaScript", "C++", "R", "SQL", "Scala",
    # Data Science
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn",
    "TensorFlow", "PyTorch", "Keras", "OpenCV",
    # ML/AI
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Data Analysis", "Data Visualization", "Feature Engineering",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Firebase",
    # Tools
    "Git", "GitHub", "Docker", "Linux", "Excel", "Power BI", "Tableau",
    # Web
    "HTML", "CSS", "React", "FastAPI", "Flask", "Django",
    # Cloud
    "AWS", "GCP", "Azure",
]


def fix_broken_words(text: str) -> str:
    """
    Fix common PDF extraction artifacts.

    Examples:
    V AJRALA -> VAJRALA
    DA T A -> DATA
    T echni cal -> Technical
    """

    # STEP 1:
    # Merge spaced uppercase sequences
    # Example:
    # D A T A -> DATA
    # DA T A -> DATA
    pattern = r'\b(?:[A-Z]{1,2}\s+){1,}[A-Z]{1,2}\b'

    def merge_uppercase(match):
        return match.group().replace(" ", "")

    text = re.sub(pattern, merge_uppercase, text)

    # STEP 2:
    # Merge:
    # T echni -> Techni
    # V AJRALA -> VAJRALA
    text = re.sub(
        r'\b([A-Z])\s+([A-Za-z]+)\b',
        r'\1\2',
        text
    )

    # STEP 3:
    # Merge:
    # Techni cal -> Technical
    # works well for resume headers but monitor on rreal data
    
    text = re.sub(
        r'\b([A-Za-z]{4,})\s+([a-z]{2,})\b',
        r'\1\2',
        text
    )

    return text


def clean_text(text: str) -> str:
    """
    Clean and normalize resume text.
    """

    # Fix broken words
    text = fix_broken_words(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove extra blank lines
    text = "\n".join(
        line.strip()
        for line in text.split("\n")
        if line.strip()
    )
    
    text = re.sub(r' +',' ', text)

    return text.strip()
def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.
    """
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    results = re.findall(pattern, text)
    if results:
         return results[0]
    else:
        logger.warning("No email found in text.")
        return None

def extract_phone(text: str) -> Optional[str]:
    #extract phone numbers from resume text
    #returns 10 digit phone number or none if not found
    patterns = [
    r'\b[6-9]\d{9}\b',   # Indian mobile — strict
    r'\b\d{10}\b',        # Any 10 digit — fallback
    ]
    for pattern in patterns:
        results = re.findall(pattern, text)
        if results:
            return results[0]

    return None

def extract_links(text: str) -> dict:
    '''
    Extract github and linkedin urls from resume text.
    returns dict with keys  github , linkedin
    
    '''
    links = {
        "github": None,
        "linkedin": None
    }
    github_pattern = r'github\.com/[\w\-]+'
    linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
    
    github = re.search(github_pattern, text)
    linkedin = re.search(linkedin_pattern, text)
    if github:
        links["github"] = github.group(0)
    else:
        logger.warning("No github link found in text.")
    if linkedin:
        links["linkedin"] = linkedin.group(0)
    else:
        logger.warning("No linkedin link found in text.")
    return {"github": links["github"],   # ✅ flat
            "linkedin": links["linkedin"]}
    
def extract_name(text: str) -> Optional[str]:
    # extract candidate name using spacy ner
    #falls back to first line of resume if ner finds nothing
    first = text.split('\n')[:3] # consider first 3 lines for name extraction
    first_line = first[0].strip()
    words = first_line.split()[:4]
    doc = nlp(" ".join(words))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    logger.warning("No name found using NER, falling back to first line.")
    return " ".join(words) if words else None


def extract_skills(text: str) -> list:
    # extract skills from resume text using case-insensitive
    # whole-word matching against skills_list
    # etruns list of matched skills
    found_skills = []
    for skill in SKILLS_LIST:
        pattern = r'(?<!\w)' + re.escape(skill)+ r'(?!\w)'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills 

def extract_experience(text: str) -> dict:
    #extracting years of experience from resume text
    # retruns dict with keys total_experience and experience_details
    pattern = r'\d+\+?\s*years?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if not matches:
    # Check if resume indicates fresher or intern
      fresher_pattern = r'\b(fresher|intern|trainee|entry.level)\b'
      if re.search(fresher_pattern, text, re.IGNORECASE):
        logger.info("Resume indicates fresher/intern profile.")
        return {"total_experience": 0, "experience_details": ["fresher"]}
    
      logger.warning("No experience details found in text.")
      return {"total_experience": 0, "experience_details": []}
    
def extract_education(text: str) -> list:
    # extract education qualifications from resume text
    # returns list of matched qualifications
   
    degree_patterns = [
    r'B\.?\s*Tech',
    r'M\.?\s*Tech',
    r'\bB\.?\s*E\b',        # \b prevents matching "be" inside words
    r'\bM\.?\s*E\b',        # \b prevents matching "me" inside words
    r'\bB\.?\s*Sc\b',
    r'\bM\.?\s*Sc\b',
    r'\bMCA\b',
    r'\bBCA\b',
    r'\bMBA\b',
    r'\bPh\.?\s*D\b',
    r"\bMaster(?:'s|s)?\s+of\b",     # "Master of Science"
    r"\bBachelor\s+of\b",             # "Bachelor of Technology"
    r'\b10th\b',
    r'\b12th\b',
    r'\bHSC\b',
    r'\bSSC\b',
    ]
    found = []
    for pattern in degree_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group() not in found:
            # TEMPORARY: show where in text the match was found
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            logger.debug(f"Pattern '{pattern}' matched at: ...{text[start:end]}...")
            found.append(match.group())
    return found
    found_degrees = []
    for pattern in degree_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches and matches.group(0).strip() not in found_degrees:
            found_degrees.append(matches.group(0))
    return found_degrees
def parse_resume(raw_text: str) -> dict:
    #takes raw resume text , returns fully structured candidate data'
    import time 
    start = time.time()
    cleaned = clean_text(raw_text)
    links = extract_links(cleaned)
    candidate = {
        "name": extract_name(cleaned),
        "email": extract_email(cleaned),
        "phone": extract_phone(cleaned),
        "github": links["github"],   
        "linkedin": links["linkedin"],
        "skills": extract_skills(cleaned),
        "experience": extract_experience(cleaned),
        "education": extract_education(cleaned),
        "raw_text": cleaned
    }
    end = time.time()
    logger.info(f"Resume parsed in {end - start:.2f} seconds.")
    return candidate

if __name__ == "__main__":
    from src.ingestion.loader import load_resume

    result = load_resume("data/samples/resume_DS_Intern.pdf")
    if result:
        parsed = parse_resume(result["raw_text"])
        import json
        print(json.dumps(parsed, indent=2))