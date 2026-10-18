"""Command-line interface for Seven-Dimension Content Gravity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .core import LABELS_ZH, PROFILE_DIMENSIONS, analyze_document, build_prompt, dumps_json, validate_editorial_report


def _read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write(value: str, output: Optional[str]) -> None:
    if output:
        Path(output).write_text(value, encoding="utf-8")
    else:
        sys.stdout.write(value)


def _render_text(report: Dict[str, Any]) -> str:
    lines = [
        "七维内容引力模型 / Seven-Dimension Content Gravity",
        f"Profile: {report['profile']}",
        f"SHA256: {report['source_sha256']}",
        "",
        "Primary dimensions:",
    ]
    for dimension in report["primary_dimensions"]:
        item = report["dimensions"][dimension]
        lines.append(f"- {item['label_zh']} ({dimension}): structural signal {item['signal_score']}/5")
    lines.extend(["", "Secondary lenses:"])
    for dimension in report["secondary_dimensions"]:
        lines.append(f"- {LABELS_ZH[dimension]} ({dimension})")
    lines.extend(
        [
            "",
            "Important: signal scores are diagnostics, not editorial approval.",
            "Use `content-gravity prompt ARTICLE --mode review|revise` for a model-ready instruction.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="content-gravity", description="Review content through 2-4 article-fit editorial dimensions.")
    parser.add_argument("--version", action="version", version="content-gravity 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    profiles = ["auto", *PROFILE_DIMENSIONS.keys()]

    review = sub.add_parser("review", help="Generate a transparent structural review report.")
    review.add_argument("article", help="Markdown/text file, or - for stdin")
    review.add_argument("--profile", choices=profiles, default="auto")
    review.add_argument("--format", choices=("text", "json"), default="text")
    review.add_argument("--output")

    prompt = sub.add_parser("prompt", help="Generate a model-ready review or revision prompt.")
    prompt.add_argument("article", help="Markdown/text file, or - for stdin")
    prompt.add_argument("--profile", choices=profiles, default="auto")
    prompt.add_argument("--mode", choices=("review", "revise"), default="review")
    prompt.add_argument("--output")

    revise = sub.add_parser("revise", help="Generate a complete revision instruction for a downstream model or agent.")
    revise.add_argument("article", help="Markdown/text file, or - for stdin")
    revise.add_argument("--profile", choices=profiles, default="auto")
    revise.add_argument("--output")

    packet = sub.add_parser("packet", help="Emit a JSON integration packet for another agent or CLI.")
    packet.add_argument("article", help="Markdown/text file, or - for stdin")
    packet.add_argument("--profile", choices=profiles, default="auto")
    packet.add_argument("--mode", choices=("review", "revise"), default="review")
    packet.add_argument("--output")

    validate = sub.add_parser("validate-report", help="Validate a model/editor report against the current article hash.")
    validate.add_argument("article")
    validate.add_argument("report")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in {"review", "prompt", "revise", "packet"}:
            text = _read_text(args.article)
            report = analyze_document(text, args.profile)
            if args.command == "review":
                output = dumps_json(report) if args.format == "json" else _render_text(report)
            elif args.command == "prompt":
                output = build_prompt(text, report, args.mode)
            elif args.command == "revise":
                output = build_prompt(text, report, "revise")
            else:
                output = dumps_json({"review": report, "mode": args.mode, "prompt": build_prompt(text, report, args.mode)})
            _write(output, args.output)
            return 0

        article = _read_text(args.article)
        payload = json.loads(Path(args.report).read_text(encoding="utf-8"))
        ok, errors = validate_editorial_report(payload, article)
        if ok:
            print("valid")
            return 0
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"content-gravity: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
