# User Research Synthesis Report Format

Use this file for the second report produced by `video-ux-observer` after the grounded UX observation report.

This report applies the `research-users` workflow, also referred to here as the research-users workflow, to the same video-derived data, but it must stay separate from the observation report.

## Evidence Rules

- Treat one video as `N=1`; write personas, segments, journey stages, and willingness-to-pay notes as hypotheses unless multiple participants support them.
- Do not invent demographics, prevalence, user base size, market size, or intent not supported by the video.
- Use exact user quotes only when they were already verified in the observation report or transcript review.
- Use `확인 필요`, `근거 부족`, `가설`, or `단일 참가자 기준` when confidence is limited.
- Do not repeat the full transcript, detailed screen timeline, or complete UX issue list from the primary report.
- Focus on synthesis: who the user appears to be behaviorally, what needs/segments show up, how the journey feels, and what product decisions this informs.

## Output Path

Save as:

```text
reports/<participant-slug>_user_research_synthesis.md
```

## Structure

```md
# 참가자 [ID] User Research Synthesis

## 1. Research Context

- 서비스명:
- 플랫폼:
- 데이터 소스:
- 표본:
- 신뢰도:
- 주의사항:

## 2. Executive Summary

[3-5 sentences. State the core user need, strongest evidence, biggest friction, and what product decision this should inform.]

## 3. Personas

### Persona 1: [Name] — "[Verified quote]"

- **근거 수준**:
- **Who**:
- **Primary JTBD**:
- **Key pains**:
- **Key gains**:
- **Behavioral pattern**:
- **Decision relevance**:
- **Evidence**:

[If only one participant is available, create 1 primary persona and 1-2 secondary persona hypotheses only when evidence supports them.]

## 4. User Segments

| Segment | Evidence Level | Primary JTBD | Product Fit | Value Signal | Growth Signal | Notes |
|---------|----------------|--------------|-------------|--------------|---------------|-------|

## 5. Customer Journey Map

| Stage | Touchpoints | Emotion / Reaction | Pain Points | Aha Moments | Opportunities |
|-------|-------------|--------------------|-------------|-------------|---------------|

Stages:
- Awareness / First Impression
- Onboarding
- First Value
- Active Use
- Social Discovery
- Monetization / Expansion
- Advocacy / Return

## 6. Key Insights

1. [Insight with evidence]
2. [Insight with evidence]
3. [Insight with evidence]

## 7. Recommendations

1. [Actionable product recommendation tied to evidence]
2. [Actionable product recommendation tied to evidence]
3. [Actionable product recommendation tied to evidence]

## 8. Open Questions

- [What this video cannot answer]
- [Suggested follow-up research]

## 9. Decision Notes

- **Roadmap**:
- **Positioning**:
- **Onboarding**:
- **Retention**:
- **Monetization**:
```
