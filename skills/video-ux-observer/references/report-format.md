# UX Observation Report Format

Use this exact top-level structure unless the user asks for a different output.

```md
# 참가자 [ID] 사용자 테스트 영상 분석

## 입력 정보

- 서비스명:
- 플랫폼:
- 테스트일:
- 참가자 ID:
- 참가자 정보:
- 서비스 소개:
- 주요 타겟:
- 이번 테스트에서 특히 확인하고 싶은 점:

## 1. 전체 음성 대사 텍스트화

[00:12]
"발언"
★ 인용 후보: 맥락

## 2. 화면 변화 타임라인

[00:00-00:20] 화면/행동

## 3. 화면별 반응 연결

### [화면명]

시간:

본 것:

말한 것:

행동:

멈칫한 지점:

반응:

해석:

리포트용 메모:

## 4. UX 문제점

문제 제목:

발생 시간:

관찰된 행동:

사용자 발언:

문제 원인:

왜 문제인가:

심각도:

근거:

## 5. 긍정 포인트

긍정 포인트:

발생 시간:

사용자 발언:

긍정적으로 본 이유:

서비스에 주는 의미:

## 6. 핵심 검증 질문 분석

핵심 검증 질문:

1. 언제 이해했는가?
2. 어떤 화면/문구/결과가 이해를 도왔는가?
3. 끝까지 헷갈린 부분은 무엇인가?
4. 경쟁 서비스 또는 기존 습관과 어떻게 비교했는가?
5. 핵심 가치가 전달됐는가?

## 7. 이탈 가능성 높은 구간

1. [구간 제목]

시간:

원인:

사용자 발언:

이탈 가능성이 높은 이유:

개선 방향:

## 8. 리포트용 핵심 발언 모음

1. "발언"

- 시간:
- 맥락:
- 사용할 수 있는 보고서 페이지:

## 9. 한 페이지 요약

첫인상:

핵심 강점 3개:

1.
2.
3.

핵심 문제 3개:

1.
2.
3.

실제 사용 의향:

판단 근거:

개선 우선순위:

1.
2.
3.

최종 한 줄:
```

## Evidence Discipline

- Record only what is visible or audible.
- Do not combine multiple separate utterances into one quote.
- Do not rewrite speech into polished copy.
- Use `확인 필요`, `음성 불명확`, `화면상 정확한 문구 확인 어려움`, or `추정:` when evidence is incomplete.
- If STT quality is poor, preserve the artifact but do not quote it as user speech.

## Common Observations To Watch

- first screen comprehension
- first CTA discovery
- onboarding length and clarity
- tab/navigation confusion
- long forms/question fatigue
- unexpected scroll position
- missing save/success feedback
- payment/subscription exposure
- external app/page exits
- comparison with existing habits or AI tools
