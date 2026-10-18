"""Core analysis and prompt-building functions.

The numeric scores in this module are transparent structural signals. They are
not a replacement for an editor or language model. The goal is to make a
review reproducible and portable across agent systems.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


DIMENSIONS: Tuple[str, ...] = (
    "emotional_tension",
    "reader_benefit",
    "story_or_case",
    "unique_angle",
    "author_voice",
    "format_expression",
    "specificity",
)

LABELS_ZH: Mapping[str, str] = {
    "emotional_tension": "情绪张力",
    "reader_benefit": "读者收益",
    "story_or_case": "故事／案例",
    "unique_angle": "独特角度",
    "author_voice": "作者声音",
    "format_expression": "表达形式",
    "specificity": "具体细节",
}

PROFILE_DIMENSIONS: Mapping[str, Tuple[str, ...]] = {
    "daily-briefing": ("unique_angle", "reader_benefit", "author_voice", "specificity"),
    "deep-report": ("unique_angle", "specificity", "reader_benefit", "story_or_case"),
    "product-content": ("reader_benefit", "specificity", "format_expression"),
    "case-study": ("story_or_case", "specificity", "reader_benefit", "author_voice"),
    "opinion": ("unique_angle", "author_voice", "emotional_tension"),
}


@dataclass(frozen=True)
class Signal:
    score: int
    evidence: Tuple[str, ...]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _count_patterns(text: str, patterns: Iterable[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def _cap_score(value: int, thresholds: Sequence[int] = (0, 1, 2, 4, 7)) -> int:
    return sum(value > threshold for threshold in thresholds)


def _sample_matches(text: str, patterns: Iterable[str], limit: int = 3) -> Tuple[str, ...]:
    found: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            snippet = text[max(0, match.start() - 28) : min(len(text), match.end() + 45)]
            snippet = re.sub(r"\s+", " ", snippet).strip()
            if snippet and snippet not in found:
                found.append(snippet)
            if len(found) >= limit:
                return tuple(found)
    return tuple(found)


def infer_profile(text: str) -> str:
    lower = text.lower()
    headings = len(re.findall(r"(?m)^#{1,3}\s+", text))
    news_markers = _count_patterns(lower, (r"source[s]?:", r"来源[:：]", r"[日早]报", r"briefing"))
    product_markers = _count_patterns(lower, (r"sku", r"listing", r"product", r"产品", r"买家", r"amazon"))
    case_markers = _count_patterns(lower, (r"复盘", r"case study", r"实测", r"experiment", r"before", r"after"))
    opinion_markers = _count_patterns(lower, (r"我认为", r"我的判断", r"i think", r"in my view"))
    if news_markers >= 2:
        return "daily-briefing"
    if product_markers >= 2:
        return "product-content"
    if case_markers >= 2:
        return "case-study"
    if opinion_markers >= 2 and headings < 4:
        return "opinion"
    return "deep-report"


def _signals(text: str) -> Dict[str, Signal]:
    patterns: Mapping[str, Tuple[str, ...]] = {
        "emotional_tension": (
            r"[？！!?]", r"风险", r"冲突", r"失败", r"代价", r"stakes?", r"risk", r"conflict", r"failure",
        ),
        "reader_benefit": (
            r"你可以", r"读者", r"建议", r"应该", r"如何", r"步骤", r"takeaway", r"you can", r"how to", r"recommend",
        ),
        "story_or_case": (
            r"例如", r"比如", r"案例", r"实测", r"复盘", r"for example", r"case", r"experiment", r"when ",
        ),
        "unique_angle": (
            r"关键", r"真正", r"我的判断", r"这意味着", r"更值得", r"the real", r"the harder question", r"i think", r"this means",
        ),
        "author_voice": (
            r"我认为", r"我看到", r"我的", r"在我看来", r"i think", r"i believe", r"in my view", r"my ",
        ),
        "format_expression": (
            r"(?m)^#{1,4}\s+", r"(?m)^[-*]\s+", r"(?m)^\d+[.)]\s+", r"(?m)^>\s+", r"\|[^\n]+\|",
        ),
        "specificity": (
            r"\b\d+(?:\.\d+)?%?\b", r"https?://", r"\b[A-Z][A-Za-z0-9.+-]{2,}\b", r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
        ),
    }
    result: Dict[str, Signal] = {}
    for dimension, pats in patterns.items():
        count = _count_patterns(text, pats)
        result[dimension] = Signal(_cap_score(count), _sample_matches(text, pats))
    return result


def analyze_document(text: str, profile: str = "auto") -> Dict[str, object]:
    if not text.strip():
        raise ValueError("article is empty")
    if profile == "auto":
        profile = infer_profile(text)
    if profile not in PROFILE_DIMENSIONS:
        raise ValueError(f"unknown profile: {profile}")
    signals = _signals(text)
    primary = list(PROFILE_DIMENSIONS[profile])
    secondary = [dimension for dimension in DIMENSIONS if dimension not in primary]
    return {
        "framework": "seven-dimension-content-gravity",
        "framework_version": "0.1.0",
        "source_sha256": sha256_text(text),
        "profile": profile,
        "primary_dimensions": primary,
        "secondary_dimensions": secondary,
        "dimensions": {
            key: {
                "label_zh": LABELS_ZH[key],
                "signal_score": signal.score,
                "signal_evidence": list(signal.evidence),
                "note": "Structural signal only; editorial judgment is still required.",
            }
            for key, signal in signals.items()
        },
        "baseline_requirements": [
            "Separate verified facts, reasonable inference, reported claims, and author opinion.",
            "State one defensible thesis supported by the body.",
            "Respect confidentiality, copyright, and publication boundaries.",
        ],
        "statistics": {
            "characters": len(text),
            "words_approx": len(re.findall(r"[\w'-]+", text)),
            "headings": len(re.findall(r"(?m)^#{1,6}\s+", text)),
            "links": len(re.findall(r"https?://", text)),
        },
    }


def build_prompt(text: str, report: Mapping[str, object], mode: str = "review") -> str:
    if mode not in {"review", "revise"}:
        raise ValueError("mode must be review or revise")
    primary = report["primary_dimensions"]
    dimension_lines = "\n".join(
        f"- {LABELS_ZH[str(key)]} ({key})" for key in primary  # type: ignore[arg-type]
    )
    action = (
        "只做审稿，不改写全文。输出：一句中心判断、三个最重要问题、逐段修改建议、各主维度 1–5 分与证据。"
        if mode == "review"
        else "完成全文修订。保留所有已核实事实、数字、来源与保密边界；先给出修改摘要，再输出可直接发布的完整终稿。"
    )
    return f"""你正在使用「七维内容引力模型」审阅文章。

七个维度是可选镜头，不是七项同时达标的清单。本篇只把以下 {len(primary)} 项设为主维度：
{dimension_lines}

基础硬要求：
1. 区分事实、推断、转述和作者观点；不得补造事实。
2. 正文必须支撑一个明确中心判断。
3. 遵守保密、版权和发布边界。
4. 不为追求传播强塞情绪、故事、人设或夸张结论。
5. 消除模板化 AI 表达、重复对照句和口号式结尾。

任务：{action}

文章类型：{report['profile']}
源文件 SHA256：{report['source_sha256']}

--- 原文开始 ---
{text.rstrip()}
--- 原文结束 ---
"""


def validate_editorial_report(payload: Mapping[str, object], source_text: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if payload.get("source_sha256") != sha256_text(source_text):
        errors.append("source_sha256 does not match the current article")
    primary = payload.get("primary_dimensions")
    if not isinstance(primary, list) or not 2 <= len(primary) <= 4:
        errors.append("primary_dimensions must contain 2-4 items")
    elif any(item not in DIMENSIONS for item in primary):
        errors.append("primary_dimensions contains an unknown dimension")
    if payload.get("decision") not in {"approved", "revise", "blocked"}:
        errors.append("decision must be approved, revise, or blocked")
    scores = payload.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores must be an object")
    elif isinstance(primary, list):
        for dimension in primary:
            value = scores.get(dimension)
            if not isinstance(value, int) or not 1 <= value <= 5:
                errors.append(f"score for {dimension} must be an integer from 1 to 5")
    return not errors, errors


def dumps_json(data: Mapping[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
