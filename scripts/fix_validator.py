import argparse
import difflib
import subprocess
import tempfile
import openai
import os
from debugiq_agents.core.logger import get_logger

logger = get_logger("fix_validator")
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

def load_file(path):
    with open(path, "r") as f:
        return f.read()

def generate_diff(original, patched):
    return "\n".join(difflib.unified_diff(
        original.splitlines(), patched.splitlines(),
        fromfile="original.py", tofile="patched.py",
        lineterm=""
    ))

def validate_patch_with_gpt4o(diff):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You're a senior QA engineer. Flag any syntax, logic, or security issues in this patch."},
            {"role": "user", "content": f"Please analyze the following code diff:\n\n{diff}"}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def run_linter_on_patch(patch_code):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(patch_code)
        tmp_path = tmp.name
    result = subprocess.run(["flake8", tmp_path], capture_output=True, text=True)
    os.remove(tmp_path)
    return result.stdout.strip()

def run_tests():
    logger.info("Running pytest for validation...")
    result = subprocess.run(["pytest", "--maxfail=3", "--disable-warnings"], capture_output=True, text=True)
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Codex CI Validator")
    parser.add_argument("--source", required=True, help="Original source file path")
    parser.add_argument("--patch", required=True, help="Modified patch file path")
    args = parser.parse_args()

    logger.info("🧠 Validating patch...")
    original = load_file(args.source)
    patched = load_file(args.patch)
    diff = generate_diff(original, patched)

    gpt_feedback = validate_patch_with_gpt4o(diff)
    print("\n🧠 GPT Review:\n", gpt_feedback)

    print("\n🔎 Lint Results:")
    lint_output = run_linter_on_patch(patched)
    print(lint_output or "✅ No linting issues found.")

    if "error" in gpt_feedback.lower() or "fail" in gpt_feedback.lower() or lint_output:
        logger.error("❌ Codex validation failed.")
        exit(1)

    print("\n🧪 Running Tests:")
    test_output = run_tests()
    print(test_output)

    if "failed" in test_output.lower():
        logger.error("❌ Tests failed after patch.")
        exit(1)

    logger.info("✅ Patch validated successfully.")

if __name__ == "__main__":
    main()
