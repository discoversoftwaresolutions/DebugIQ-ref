# PR Review
review_parser = subparsers.add_parser("review-pr")
review_parser.add_argument("--pr-id", required=True)
review_parser.add_argument("--repo-url", required=True)
review_parser.add_argument("--source-branch", required=True)
review_parser.add_argument("--target-branch", required=True)
review_parser.add_argument("--pr-title", required=True)
review_parser.add_argument("--pr-description", required=True)
review_parser.add_argument("--code-diff", required=True)
case "review-pr":
    from debugiq_backend/app/api/agents import review_pr
    result = review_pr.review_pull_request(**args_dict)
