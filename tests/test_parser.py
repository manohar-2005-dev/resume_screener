# tests/test_loader.py
from src.ingestion.loader import load_resume

test_files = [
    "data/samples/resume_DS_Intern.pdf",
    "data/samples/resume_DS_Intern.docx",
    "data/samples/resume_DS_Intern.txt",
]

for file in test_files:
    result = load_resume(file)
    if result:
        print(f"\n✅ {result['file_name']}")
        print(f"   Type   : {result['file_type']}")
        print(f"   Status : {result['status']}")
        print(f"   chars  : {len(result['raw_text'])}")
        print(f"   Preview: {result['raw_text'][:150]}")
    else:
        print(f"\n❌ Failed to load {file}")