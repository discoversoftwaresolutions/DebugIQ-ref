import subprocess
import json
import os

REPORT_FILE = os.getenv("REGRESSION_REPORT", "regression_report.json")

def run_benchmark(script_path, args=None):
    cmd = ["python", script_path]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout.strip())
    except Exception:
        return {"output": result.stdout.strip()}

def compare_metrics(before, after):
    report = {"before": before, "after": after, "regressions": {}}
    for k in before:
        if k in after and after[k] > before[k]:
            report["regressions"][k] = {"before": before[k], "after": after[k]}
    return report

def record_regression(report):
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Regression report saved to {REPORT_FILE}")

def main():
    before_script = os.getenv("BEFORE_BENCHMARK", "benchmarks/before.py")
    after_script = os.getenv("AFTER_BENCHMARK", "benchmarks/after.py")

    before_metrics = run_benchmark(before_script)
    after_metrics = run_benchmark(after_script)
    report = compare_metrics(before_metrics, after_metrics)
    record_regression(report)

if __name__ == "__main__":
    main()
