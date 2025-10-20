import argparse
from crengine.main import run_full_pass, run_delta_pass

def main():
    parser = argparse.ArgumentParser("crengine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--repo", required=True)
    p_run.add_argument("--outputs", required=True)
    p_run.add_argument("--ai", choices=["none","openai","anthropic","gemini"], default=None)

    p_delta = sub.add_parser("delta")
    p_delta.add_argument("--repo", required=True)
    p_delta.add_argument("--outputs", required=True)

    args = parser.parse_args()
    if args.cmd == "run":
        run_full_pass(args.repo, args.outputs, ai_override=args.ai)
    elif args.cmd == "delta":
        run_delta_pass(args.repo, args.outputs)

if __name__ == "__main__":
    main()
