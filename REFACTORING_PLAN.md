# CLI-Anything 리팩토링 계획

작성일: 2026-06-11

## 1. 현황 요약

- HKUDS/CLI-Anything의 **포크 미러** — `origin/main..HEAD` 차이 없음, 로컬 고유 커밋 없음 (현재는 순수 업스트림 추종 상태)
- Python 약 258,000줄, 60여 개 소프트웨어별 CLI 하니스(freecad, blender, n8n, mailchimp 등) + `cli-hub`(허브 CLI) + `docs/`
- 비밀 하드코딩 패턴 전수 grep 미검출, bare `except:` 2건 수준 — 전반적 코드 위생은 양호
- 대형 자산은 데모 GIF(최대 4.8MB)로 README용

## 2. 발견된 문제점

### High

- **Python 3.10/3.11에서 구문 오류로 import 불가** — `cli-hub/cli_hub/preview.py:725`: f-string 표현식 내 백슬래시 사용. 이 문법은 Python 3.12+에서만 허용되는데 README/배지는 `python>=3.10`을 표방한다. 3.10/3.11 사용자는 `cli-hub` preview 기능이 SyntaxError로 즉사한다. (전체 .py `py_compile` 일괄 검사에서 이 1건만 실패 — Python 3.11.15 기준)

### Medium

- **거대 파일 다수** — `docs/scripts/freecad_live_preview_demo.py` 4,981줄, `freecad/.../freecad_cli.py` 4,911줄, `sbox_cli.py` 2,423줄, `mubu_probe.py` 2,265줄 등. 단일 파일 CLI 패턴이 한계를 넘은 하니스들은 명령 그룹별 모듈 분리가 필요하다.
- **하니스 간 구조 중복** — 각 하니스가 `agent-harness/cli_anything/<name>/` 보일러플레이트(설정 로딩, JSON 출력, 테스트 골격)를 복제. 공통 스캐폴드/베이스 라이브러리 부재로 수정 사항이 60여 곳에 N배 반영되어야 한다.
- **포크 운영 전략 부재** — 이 포크에 로컬 변경을 쌓기 시작하면 업스트림(활발히 머지 중)과의 충돌 비용이 급증한다. 추종/기여 정책이 정해져 있지 않다.

### Low

- bare `except:` 2건 (예외 삼킴 가능성)
- README 데모 GIF 합계 약 15MB가 git 직접 추적 (포크에서는 수정 불가 영역이므로 기록만)

## 3. 단계적 개선 계획

> 이 리포는 포크이므로, **코드 수정은 업스트림 PR로 보내는 것**을 원칙으로 하고 포크에는 로컬 패치를 쌓지 않는다.

### Phase 1 — 즉시 (업스트림 기여 후보)

| 작업 | 내용 | 규모 | 리스크 | 검증 |
|---|---|---|---|---|
| preview.py 3.10/3.11 호환 수정 | f-string 내 백슬래시를 사전 변수로 추출 → 업스트림 PR | S | 없음 | `python3.11 -m py_compile` 통과 + 해당 테스트 |
| bare except 2건 구체화 | 예외 타입 명시 → 업스트림 PR | S | 없음 | pytest |

### Phase 2 — 포크 운영 체계

| 작업 | 내용 | 규모 | 리스크 | 검증 |
|---|---|---|---|---|
| 추종 전략 문서화 | "포크는 미러로만 유지, 로컬 변경 금지, 수정은 upstream PR" 정책을 본 문서 또는 FORK_POLICY.md로 명문화 | S | 없음 | — |
| 동기화 자동화 | 주기적 `git fetch upstream && git merge`(또는 GitHub Sync fork) 절차 수립 | S | 로컬 커밋이 생기면 충돌 | `git log origin/main..HEAD` 0건 유지 |

### Phase 3 — 장기 (자체 하니스를 만들 경우)

- 자체 CLI 하니스가 필요해지면 이 포크 안이 아니라 **별도 리포**에서 `cli-anything`를 의존성으로 사용 — 업스트림 보일러플레이트 중복 문제를 자체 코드로 들여오지 않는다
- 업스트림에 공통 스캐폴드(베이스 클래스/코드젠) 제안 이슈 등록 검토

## 4. 검증 체크리스트

- [ ] `git ls-files '*.py' | xargs -n50 python3 -m py_compile` 실패 0건 (3.11 기준)
- [ ] `git log origin/main..HEAD` → 로컬 고유 커밋 0건 유지 (본 계획서 브랜치 제외)
- [ ] 업스트림 PR 제출 시 upstream CI 통과
