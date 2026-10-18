---
name: seven-dimension-content-gravity
description: Review or revise articles with the Seven-Dimension Content Gravity model. Select 2-4 article-fit dimensions from emotional tension, reader benefit, story/case, unique angle, author voice, format, and specificity; preserve facts and avoid formulaic writing. Use for article reviews, rewrites, daily briefings, deep reports, product content, case studies, and opinion pieces.
---

# Seven-Dimension Content Gravity

Use this skill to make content more compelling without forcing every article into the same template.

## Core principle

Treat the seven dimensions as optional editorial lenses, not seven simultaneous gates:

1. Emotional tension
2. Reader benefit
3. Story or case
4. Unique angle
5. Author voice
6. Format and expression
7. Specificity

Select only 2-4 primary dimensions for the current article. Mark the rest as secondary or not applicable. Never add emotion, story, personality, or novelty merely to satisfy the framework.

## Baseline requirements

Always enforce these before optimizing engagement:

- Separate verified facts, reasonable inference, reported claims, and author opinion.
- Require one defensible thesis supported by the body.
- Preserve citations, numbers, qualifications, confidentiality, copyright, and publication boundaries.
- Do not invent examples, quotes, tests, results, or sources.

## Choose a profile

- `daily-briefing`: unique angle, reader benefit, author voice, specificity
- `deep-report`: unique angle, specificity, reader benefit, story/case
- `product-content`: reader benefit, specificity, format/expression
- `case-study`: story/case, specificity, reader benefit, author voice
- `opinion`: unique angle, author voice, emotional tension

Override a profile when the article clearly needs a different combination, but keep 2-4 primary dimensions.

## Workflow

1. Read the full article and identify its type, audience, intended action, factual claims, and publication boundary.
2. Select 2-4 primary dimensions and explain why they fit.
3. State the article's thesis in one sentence. If the body cannot support it, stop and request evidence or narrow the thesis.
4. Review the primary dimensions with specific textual evidence. Do not score from keywords alone.
5. Identify the three changes with the highest editorial leverage.
6. When revision is requested, preserve facts and sources, revise the complete article, and remove formulaic AI patterns.
7. Re-review the final text. A changed file invalidates any hash-bound prior approval.

## Required review output

Return:

- Article profile and selected primary dimensions
- One-sentence thesis
- Decision: `approved`, `revise`, or `blocked`
- Scores from 1-5 for primary dimensions, each with evidence
- Three highest-priority problems
- Concrete cuts, additions, or rewrites
- Risks: factual, legal, confidentiality, tone, or unsupported claims

## CLI companion

When the repository CLI is available:

```bash
content-gravity review article.md --profile deep-report
content-gravity prompt article.md --profile deep-report --mode review
content-gravity prompt article.md --profile deep-report --mode revise > revision-prompt.md
content-gravity revise article.md --profile deep-report --output revision-prompt.md
content-gravity packet article.md --profile product-content --mode revise --output packet.json
```

The CLI's numeric signal scores are diagnostics only. Apply editorial judgment before approving or rewriting.

Read `references/framework.md` for the dimension definitions and `references/original-seven-points.md` for the original source summary when a user asks about the method's origin.
