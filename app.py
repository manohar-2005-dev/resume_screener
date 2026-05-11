import streamlit as st
#import json
import sys
import os
from config import OUTPUT_PATH, RAW_DATA_PATH, VECTOR_STORE_PATH
import tempfile


sys.path.append(os.path.dirname(__file__))

from src.ingestion.loader import load_resume
from src.preprocessing.parser import parse_resume
from src.matching.engine import screen_multiple, save_results
from src.embeddings.vectorstore import clear_vectorstore

for path in [OUTPUT_PATH, RAW_DATA_PATH, VECTOR_STORE_PATH]:
    os.makedirs(path, exist_ok=True)
# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🤖",
    layout="wide"
)

# ── HEADER ───────────────────────────────────────────
st.title("🤖 AI Resume Screening System")
st.markdown("Upload resumes and enter a job description to rank candidates.")
st.divider()

# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    n_results = st.slider(
        "Chunks to retrieve per candidate",
        min_value=3, max_value=10, value=5
    )
    job_title = st.text_input("Job Title", value="Software Engineer")
    st.divider()
    if st.button("🗑️ Clear Vector Store"):
        clear_vectorstore()
        st.success("Vector store cleared.")

# ── MAIN LAYOUT ──────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=300,
        placeholder="We are looking for a Python developer with..."
    )

with col2:
    st.subheader("📄 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

st.divider()

# ── SCREEN BUTTON ─────────────────────────────────────
if st.button("🚀 Screen Candidates", type="primary"):

    # YOUR TASK — fill in this block:

    # Step 1: validate inputs
    # if not job_description → st.error("Please enter a job description")
    # if not uploaded_files  → st.error("Please upload at least one resume")
    if not job_description:
        st.error("Please enter a job description.")
        st.stop()

    if not uploaded_files:
        st.error("Please upload at least one resume.")
        st.stop()

    # Step 2: process each uploaded file
    # uploaded files are not real files — save to tempfile first:
    
    #
    # parsed_resumes = []
    # for uploaded_file in uploaded_files:
    #     suffix = "." + uploaded_file.name.split(".")[-1]
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    #         tmp.write(uploaded_file.read())
    #         tmp_path = tmp.name
    #     loaded = load_resume(tmp_path)
    #     if loaded:
    #         parsed = parse_resume(loaded["raw_text"])
    #         parsed["file_name"] = uploaded_file.name
    #         parsed_resumes.append(parsed)
    temp_dir = tempfile.mkdtemp()
    parsed_resumes = []
    for uploaded_file in uploaded_files:
        suffix = "." + uploaded_file.name.split(".")[-1]
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        loaded = load_resume(temp_path)
        if loaded:
            parsed = parse_resume(loaded["raw_text"])
            parsed["file_name"] = uploaded_file.name
            parsed_resumes.append(parsed)

    # Step 3: screen all candidates
    # use st.spinner("Analyzing candidates..."):
    # call screen_multiple(parsed_resumes, job_description)
    # store in st.session_state["results"]
    with st.spinner("Analyzing candidates..."):
        results = screen_multiple(parsed_resumes, job_description)
        st.session_state["results"] = results
        

    # Step 4: save results to JSON
    # call save_results()
    # store file path in st.session_state["file_path"]
    file_path = save_results(results, job_title)
    st.session_state["file_path"] = file_path

# TEMPORARY DEBUG
    st.write(f"DEBUG file_path: {file_path}")
    st.write(f"DEBUG file exists: {os.path.exists(file_path)}")
    st.write(f"DEBUG OUTPUT_PATH: {OUTPUT_PATH}")
    st.session_state["file_path"] = file_path
    # Step 5: display success message
    st.success("Candidates screened successfully! See results below.")

    pass

# ── RESULTS DISPLAY ───────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]

    st.subheader(f"🏆 Ranked Candidates ({len(results)} total)")

    # YOUR TASK — display results:

    # For each result, show:
    # - Rank and name (st.subheader)
    # - Match score as metric (st.metric)
    # - Recommendation with color (st.success/warning/error)
    # - Skills as comma-joined string
    # - Strengths as bullet list
    # - Missing skills as bullet list
    # - Summary text
    # - Divider between candidates

    # HINT for recommendation color:
    # rec = result["recommendation"]
    # if rec == "Strong Yes": st.success(f"✅ {rec}")
    # elif rec == "Yes":       st.info(f"👍 {rec}")
    # elif rec == "Maybe":     st.warning(f"🤔 {rec}")
    # else:                    st.error(f"❌ {rec}")
    for result in results:
        st.subheader(f"{result['rank']}. {result['candidate_name']}")
        st.metric("Match Score", f"{result['match_score']}%")
        rec = result["recommendation"]
        if rec == "Strong Yes":
            st.success(f"✅ {rec}")
        elif rec == "Yes":
            st.info(f"👍 {rec}")
        elif rec == "Maybe":
            st.warning(f"🤔 {rec}")
        else:
            st.error(f"❌ {rec}")

        skills = ", ".join(result.get("skills_extracted", []))
        st.write(f"**Skills:** {skills}")

        strengths = result.get("strengths", [])
        if strengths:
            st.write("**Strengths:**")
            for s in strengths:
                st.write(f"- {s}")

        missing_skills = result.get("missing_skills", [])
        if missing_skills:
            st.write("**Missing Skills:**")
            for ms in missing_skills:
                st.write(f"- {ms}")

        summary = result.get("summary", "")
        if summary:
            st.write(f"**Summary:** {summary}")

        st.divider()

    # Download button at bottom:
    if "file_path" in st.session_state:
       file_path = st.session_state["file_path"]
    
    # Check file actually exists before trying to open
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=f.read(),
                file_name="screening_results.json",
                mime="application/json"
            )
    else:
        st.warning("Results file not found. Please screen candidates again.")