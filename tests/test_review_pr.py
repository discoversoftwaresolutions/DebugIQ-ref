from debugiq_agents.agents import review_pr

def test_review_pr_mock():
    result = review_pr.review_pull_request(
        pr_id="PR-123",
        repository_url="https://github.com/org/repo",
        source_branch="dev",
        target_branch="main",
        pr_title="Fix crash in processor",
        pr_description="Handles null processor keys",
        code_diff="--- a/file.py\n+++ b/file.py\n+ if not processor: return None"
    )
    assert result is not None
    assert "summary" in result
