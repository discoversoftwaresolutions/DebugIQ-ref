# app/utils/parser.py

def extract_sections(trace: str) -> dict:
    """
    Parses a formatted traceback and extracts patch, explanation, and doc summary sections.
    Triggered by markers: ### PATCH, ### EXPLANATION, ### SUMMARY
    """
    sections = {
        "patch_section": "",
        "explanation_section": "",
        "doc_summary_section": ""
    }

    lines = trace.strip().splitlines()
    current = None

    for line in lines:
        if line.strip().startswith("### PATCH"):
            current = "patch_section"
            continue
        elif line.strip().startswith("### EXPLANATION"):
            current = "explanation_section"
            continue
        elif line.strip().startswith("### SUMMARY"):
            current = "doc_summary_section"
            continue

        if current:
            sections[current] += line + "\n"

    return sections
