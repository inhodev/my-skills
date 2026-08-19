#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="$repo_root/skills"
target_root="${CODEX_HOME:-$HOME/.codex}/skills"
backup_root="${CODEX_HOME:-$HOME/.codex}/skill-backups"
dry_run=0

usage() {
  cat <<'EOF'
사용법:
  ./scripts/install.sh all
  ./scripts/install.sh mobile-app-studio
  ./scripts/install.sh <skill-name>
  ./scripts/install.sh list
  ./scripts/install.sh --dry-run <대상>

대상:
  all                저장소의 모든 스킬 설치
  mobile-app-studio  모바일 앱 제작 묶음 설치
  <skill-name>       지정한 스킬 하나 설치
  list               설치 가능한 스킬과 묶음 표시
EOF
}

if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=1
  shift
fi

target="${1:-all}"
if (( $# > 1 )); then
  usage >&2
  exit 2
fi

list_skills() {
  echo "설치 가능한 스킬:"
  find "$source_root" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | sed 's/^/  - /'
  echo
  echo "설치 묶음:"
  echo "  - mobile-app-studio"
  echo "  - all"
}

if [[ "$target" == "list" ]]; then
  list_skills
  exit 0
fi

"$repo_root/scripts/doctor.sh"

declare -a skills=()
case "$target" in
  all)
    while IFS= read -r skill_dir; do
      skills+=("$(basename "$skill_dir")")
    done < <(find "$source_root" -mindepth 1 -maxdepth 1 -type d | sort)
    ;;
  mobile-app-studio)
    while IFS= read -r skill_name; do
      [[ -n "$skill_name" ]] && skills+=("$skill_name")
    done < "$repo_root/bundles/mobile-app-studio.txt"
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    skills+=("$target")
    ;;
esac

for skill_name in "${skills[@]}"; do
  if [[ ! -f "$source_root/$skill_name/SKILL.md" ]]; then
    echo "오류: 알 수 없는 스킬입니다: $skill_name" >&2
    exit 1
  fi
done

if (( dry_run )); then
  echo "DRY RUN: 설치 위치 $target_root"
  printf '  - %s\n' "${skills[@]}"
  exit 0
fi

mkdir -p "$target_root" "$backup_root"
timestamp="$(date '+%Y%m%d-%H%M%S')"
created_backup=0

for skill_name in "${skills[@]}"; do
  source_dir="$source_root/$skill_name"
  destination="$target_root/$skill_name"

  if [[ -d "$destination" ]] && diff -qr "$source_dir" "$destination" >/dev/null; then
    echo "유지: $skill_name (이미 최신)"
    continue
  fi

  temp_parent="$(mktemp -d "$target_root/.my-skills-install.XXXXXX")"
  trap 'rmdir "$temp_parent" 2>/dev/null || true' EXIT
  cp -R "$source_dir" "$temp_parent/$skill_name"

  if [[ -e "$destination" ]]; then
    mkdir -p "$backup_root/$timestamp"
    mv "$destination" "$backup_root/$timestamp/$skill_name"
    created_backup=1
  fi

  mv "$temp_parent/$skill_name" "$destination"
  rmdir "$temp_parent"
  trap - EXIT
  echo "설치: $skill_name"
done

if (( created_backup )); then
  echo "기존 스킬 백업: $backup_root/$timestamp"
fi

echo "설치 완료: ${#skills[@]}개 대상"
echo "Codex가 실행 중이면 새 작업을 시작하거나 앱을 다시 열어 스킬 목록을 갱신하세요."
