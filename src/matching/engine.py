import json
import logging
import os
from datetime import datetime
from typing import List
from config import OUTPUT_PATH

logger = logging.getLogger(__name__)


def screen_candidate(
    parsed_resume: dict,
    job_description: str,
    n_chunks: int = 5
) -> dict:
    """
    Full pipeline for one candidate:
    chunk → store → search → analyze → return result
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from src.chunking.splitter import chunk_resume
    from src.embeddings.vectorstore import store_chunks, search_similar
    from src.reporting.generator import analyze_candidate

    # Step 1: chunk the resume
    chunks = chunk_resume(parsed_resume)

    # Step 2: store chunks in vector database
    store_chunks(chunks)

    # Step 3: search for relevant chunks using JD as query
    relevant_chunks = search_similar(job_description, n_results=n_chunks)

    # Step 4: analyze with LLM
    analysis = analyze_candidate(relevant_chunks, job_description)

    # Step 5: combine parsed resume info + analysis into final result
    return {
        "candidate_name": parsed_resume.get("name"),
        "email": parsed_resume.get("email"),
        "phone": parsed_resume.get("phone"),
        "github": parsed_resume.get("github"),
        "linkedin": parsed_resume.get("linkedin"),
        "skills_extracted": parsed_resume.get("skills", []),
        "education": parsed_resume.get("education", []),
        "experience": parsed_resume.get("experience", {}),
        "match_score": analysis.get("match_score", 0),
        "strengths": analysis.get("strengths", []),
        "missing_skills": analysis.get("missing_skills", []),
        "recommendation": analysis.get("recommendation", "No"),
        "summary": analysis.get("summary", ""),
    }


def screen_multiple(
    parsed_resumes: List[dict],
    job_description: str
) -> List[dict]:
    """
    Screen multiple candidates against one job description.
    Returns results sorted by match_score descending.
    """
    
    # Step 1: create empty results list
    results = []
    total = len(parsed_resumes)

    # Step 2: loop through parsed_resumes
    #         call screen_candidate() for each
    #         append result to results list
    #         log progress: "Screened X of Y candidates"
    for index, parsed_resume in enumerate(parsed_resumes):
        result = screen_candidate(parsed_resume, job_description)
        results.append(result)
        logger.info(f"Screened {index + 1} of {total} candidates.")
    

    # Step 3: sort results by match_score descending
    # Hint: sorted(results, key=lambda x: x["match_score"], reverse=True)
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    # Step 4: add rank to each result
    # Hint: enumerate starting from 1
    for i, result in enumerate(results, start=1):
        result["rank"] = i

    # Step 5: return sorted results
    return results


def save_results(results: List[dict], job_title: str = "position") -> str:
    """
    Save screening results to JSON file in outputs/ folder.
    Returns the file path.
    """
    
    # Step 1: create a timestamp string
    # Hint: datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Step 2: build filename
    # Hint: f"screening_{job_title}_{timestamp}.json"
    # clean job_title spaces: job_title.replace(" ", "_")
    filename = f"screening_{job_title.replace(' ', '_')}_{timestamp}.json"

    # Step 3: build full file path using OUTPUT_PATH from config
    file_path = os.path.join(OUTPUT_PATH, filename)

    # Step 4: write results to JSON file
    # Hint: json.dump(results, f, indent=2)
  # Step 4: write results to JSON file
    with open(file_path, "w") as f:
        json.dump(results, f, indent=2)    # ✅ uncommented, correct function

# Step 5: log and return file path
    logger.info(f"Results saved to: {file_path}")
    return file_path


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from src.ingestion.loader import load_resume
    from src.preprocessing.parser import parse_resume

    # Load and parse resume
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]

    # Job description
    jd = """
    We are looking for a Data Science Intern with:
    - Strong Python skills (Pandas, NumPy, Scikit-learn)
    - Experience with machine learning models
    - Knowledge of SQL and databases
    - Good communication skills
    - Experience with data visualization tools
    """

    # Screen single candidate
    result = screen_candidate(parsed, jd)

    print("\n── Candidate Screening Result ──")
    print(json.dumps(result, indent=2))

    # Save to file
    file_path = save_results([result], job_title="Data Science Intern")
    print(f"\n✅ Results saved to: {file_path}")