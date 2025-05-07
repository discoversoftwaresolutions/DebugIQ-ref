# Generate a production-ready Codex CI validator script for autonomous patch QA

validator_code = '''
import os
import openai
import difflib
import subprocess

# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

# Sample files (can be replaced with dynamic path scanning)
PATCH_FILE = "tests/sample_patch.py"
SOURCE_FILE = "tests/original_file.py"

def load_file(path):
    with open(path, "r") as f:
        return f.read()

def generate_diff(original, patched):
    return "\\n".join(difflib.unified_diff(
        original.splitlines(), patched.splitlines(),
        fromfile="original.py", tofile="patched.py",
        lineterm=""
    ))

def validate_patch_with_gpt4o(diff):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You're a Python debugging QA expert."},
            {"role": "user", "content": f"Please review this code diff for logic or syntax errors:\\n\\n{diff}"}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def run_linter_on_patch(patch_code):
    with open("temp_patch.py", "w") as f:
        f.write(patch_code)
    result = subprocess.run(["flake8", "temp_patch.py"], capture_output=True, text=True)
    return result.stdout.strip()

def main():
    print("🔍 Running Codex CI Validator...")

    original = load_file(SOURCE_FILE)
    patched = load_file(PATCH_FILE)
    diff = generate_diff(original, patched)

    print("🧠 GPT-4o Review:")
    review = validate_patch_with_gpt4o(diff)
    print(review)

    print("\\n🔎 Linter Check:")
    lint_results = run_linter_on_patch(patched)
    print(lint_results or "✅ No linting issues.")

    if "error" in review.lower() or "fail" in review.lower() or lint_results:
        raise SystemExit("❌ Codex CI validation failed.")
    else:
        print("✅ Codex CI validation passed.")

if __name__ == "__main__":
    main()
'''

validator_path = "/mnt/data/DebugIQ-backend/scripts/codex_ci_validator.py"
os.makedirs(os.path.dirname(validator_path), exist_ok=True)
with open(validator_path, "w") as f:
    f.write(validator_code.strip())

validator_path
