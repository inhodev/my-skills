#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_root="$repo_root/skills"
failures=0

if [[ ! -d "$skills_root" ]]; then
  echo "오류: skills 디렉터리를 찾을 수 없습니다: $skills_root" >&2
  exit 1
fi

while IFS= read -r skill_dir; do
  skill_name="$(basename "$skill_dir")"
  skill_file="$skill_dir/SKILL.md"
  agent_file="$skill_dir/agents/openai.yaml"

  if [[ ! -f "$skill_file" ]]; then
    echo "실패: $skill_name/SKILL.md가 없습니다." >&2
    failures=$((failures + 1))
    continue
  fi

  declared_name="$(awk '
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" { exit }
    in_frontmatter && /^name:[[:space:]]*/ {
      sub(/^name:[[:space:]]*/, "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$skill_file")"

  if [[ "$declared_name" != "$skill_name" ]]; then
    echo "실패: $skill_name 폴더와 frontmatter name($declared_name)이 다릅니다." >&2
    failures=$((failures + 1))
  fi

  if [[ ! -f "$agent_file" ]]; then
    echo "실패: $skill_name/agents/openai.yaml이 없습니다." >&2
    failures=$((failures + 1))
  elif ! grep -Fq "\$$skill_name" "$agent_file"; then
    echo "실패: $skill_name의 default_prompt에 \$$skill_name 호출 예시가 없습니다." >&2
    failures=$((failures + 1))
  fi
done < <(find "$skills_root" -mindepth 1 -maxdepth 1 -type d | sort)

if find "$skills_root" -type d -name __pycache__ -print -quit | grep -q . \
  || find "$skills_root" -type f -name '*.pyc' -print -quit | grep -q .; then
  echo "실패: Python 캐시 파일이 포함되어 있습니다." >&2
  failures=$((failures + 1))
fi

if grep -RInE --exclude-dir=.git --exclude='doctor.sh' \
  '(/Users/[^/]+|gho_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)' \
  "$repo_root" >/dev/null; then
  echo "실패: 개인 절대경로나 비밀정보로 의심되는 문자열이 있습니다." >&2
  failures=$((failures + 1))
fi

if (( failures > 0 )); then
  echo "검증 실패: $failures개 문제" >&2
  exit 1
fi

skill_count="$(find "$skills_root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
echo "검증 통과: ${skill_count}개 스킬"
