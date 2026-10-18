import json

from content_gravity.core import analyze_document, build_prompt, sha256_text, validate_editorial_report


ARTICLE = """# AI 热点早报

今天最值得关注的不是模型更快，而是团队如何检查并行 Agent 的冲突。

## 一个具体案例

2026 年 10 月 18 日，我们测试了 3 个 Agent。完成时间下降 28%，但复核时间增加 12%。

读者可以先记录任务拆分、冲突率和人工接管时间。

来源：https://example.com/report
"""


def test_auto_profile_daily_briefing():
    report = analyze_document(ARTICLE)
    assert report["profile"] == "daily-briefing"
    assert report["primary_dimensions"] == [
        "unique_angle",
        "reader_benefit",
        "author_voice",
        "specificity",
    ]


def test_selects_two_to_four_dimensions():
    for profile in ("daily-briefing", "deep-report", "product-content", "case-study", "opinion"):
        report = analyze_document(ARTICLE, profile)
        assert 2 <= len(report["primary_dimensions"]) <= 4


def test_report_is_hash_bound():
    report = analyze_document(ARTICLE)
    assert report["source_sha256"] == sha256_text(ARTICLE)


def test_prompt_explains_dimensions_are_optional():
    report = analyze_document(ARTICLE)
    prompt = build_prompt(ARTICLE, report, "revise")
    assert "不是七项同时达标" in prompt
    assert "不得补造事实" in prompt
    assert ARTICLE.strip() in prompt


def test_validate_editorial_report():
    review = {
        "source_sha256": sha256_text(ARTICLE),
        "primary_dimensions": ["unique_angle", "specificity"],
        "decision": "approved",
        "scores": {"unique_angle": 4, "specificity": 5},
    }
    ok, errors = validate_editorial_report(review, ARTICLE)
    assert ok
    assert errors == []


def test_rejects_stale_review():
    review = {
        "source_sha256": "stale",
        "primary_dimensions": ["unique_angle", "specificity"],
        "decision": "approved",
        "scores": {"unique_angle": 4, "specificity": 5},
    }
    ok, errors = validate_editorial_report(review, ARTICLE)
    assert not ok
    assert any("source_sha256" in error for error in errors)


def test_json_serializable():
    json.dumps(analyze_document(ARTICLE), ensure_ascii=False)
