> 리뷰 일자: 2026-07-02 · 대상 브랜치: 307c9c0 시점 스냅샷 · 읽기 전용 정적 분석 (코드 미수정)

# CLI-Anything 종합 코드리뷰

## 1. 리포 개요

| 항목 | 내용 |
|---|---|
| 목적 | GUI/데스크톱/웹 소프트웨어(Blender, GIMP, FreeCAD, Zoom, n8n 등)를 AI 에이전트가 조작할 수 있도록 소프트웨어별 CLI "하니스"를 제공하는 HKUDS 프로젝트의 포크(`dragonnite1221-lgtm/CLI-Anything`) |
| 규모 | Python 1,053개(약 258,600줄), Markdown 350개, 테스트 파일 127개 / `def test_` 4,578개 |
| 구조 | 소프트웨어별 최상위 폴더 약 60개, 각각 `agent-harness/cli_anything/<name>/`(core/ + utils/ + tests/ + setup.py)의 독립 pip 패키지. 그 외 `cli-hub/`(PyPI 패키지 매니저), `skills/`(SKILL.md 모음), `docs/`(GitHub Pages 허브), `registry.json`/`public_registry.json`(설치 레지스트리), `.github/`(CI) |
| 파일 수가 많은 이유 | 생성 코드나 벤더링이 아니라 **동일한 보일러플레이트 패턴을 60개 하니스에 복제**한 결과. 특히 `utils/repl_skin.py`(567줄)는 39개 하니스에 **바이트 단위 동일 사본**으로 존재(변형 포함 48개 + 분할된 `repl_skin/` 패키지 4개) |
| 포크 로컬 커밋 | 리팩토링 계획서(`REFACTORING_PLAN.md`), preview.py 3.10 호환 수정, 200줄 파일 크기 게이트 + pre-push 훅, repl_skin 일부 분할, Claude PR 리뷰 워크플로 |

## 2. 종합 평가: **보통** (조건부 양호)

각 하니스의 코드 위생(자격증명 0o600 저장, 파라미터화 SQL, Script-Fu 이스케이프, 타임아웃 있는 HTTP)은 준수하고, 테스트 자산도 실질적이다(로컬 샘플 실행 전수 통과). 그러나 **(a) 원격 레지스트리의 설치 명령을 검증 없이 shell 실행하는 공급망 리스크**, **(b) 4,578개 테스트를 실행하는 CI가 전무**, **(c) 567줄 파일 39중 복제 등 구조적 중복 부채**가 등급을 끌어내린다.

---

## 3. 발견 사항

### Critical

없음. (하드코딩 시크릿·SQL 인젝션·비safe yaml/pickle 로드는 전수 grep 및 해당 코드 정독 결과 미검출)

### High

**H-1. 원격 레지스트리 명령의 무검증 shell 실행 — 공급망 RCE 경로** — `cli-hub/cli_hub/installer.py:52-66`, `cli-hub/cli_hub/registry.py:9-10`
```python
_SHELL_METACHARACTERS = ("|", "&&", "||", ";", "$(", "`")
def _run_command(cmd):
    use_shell = any(c in cmd for c in _SHELL_METACHARACTERS)
    ...
    subprocess.run(cmd if use_shell else shlex.split(cmd), ..., shell=use_shell)
```
`cli-hub install <name>`은 `https://hkuds.github.io/CLI-Anything/registry.json`에서 받아온 `install_cmd` 문자열을 서명·체크섬 검증 없이 실행하며, shell 메타문자가 있으면 `shell=True`로 실행한다. 실제 레지스트리에는 `jimeng | curl -s https://jimeng.jianying.com/cli | bash` 같은 **원격 스크립트 파이프 실행 항목**이 존재한다(`public_registry.json`). `cli-hub launch`도 레지스트리의 `entry_point`를 `os.execvp(entry, ...)`로 직접 실행한다(`cli-hub/cli_hub/cli.py:264`). GitHub Pages 원본 또는 서드파티 배포 서버가 오염되면 사용자 머신에서 임의 코드가 실행된다. 주석의 "trusted registry" 가정은 서드파티 `curl|bash` 항목까지 커버하지 못한다.
**권고**: 레지스트리 항목별 SHA/서명 검증, `curl|bash`형 항목 배제 또는 명시적 사용자 확인 프롬프트, `shell=True` 경로 제거(스크립트 설치는 다운로드→검증→실행으로 분리).

**H-2. 테스트 실행 CI 부재 — "2,269 Passing" 배지 미검증** — `.github/workflows/` 전체, `README.md:22`
워크플로 7개(check-root-skills, claude, deploy-pages, file-size, pr-labeler×2, publish-cli-hub) 중 **pytest를 실행하는 워크플로가 하나도 없다.** README는 `Tests-2,269_Passing` 배지를 내걸지만 CI가 이를 보증하지 않으며, 60개 하니스 회귀가 머지 시점에 잡히지 않는다. (로컬 샘플 실행에서는 cli-hub 95개, blender 165개, obsidian 47개 전부 통과 — 테스트 자체는 실체가 있음.)
**권고**: 변경된 하니스만 선별 실행하는 path-filter 기반 pytest 매트릭스 워크플로 추가. 최소한 `cli-hub`(PyPI 배포 대상)는 publish 전 테스트 게이트 필수.

### Medium

**M-1. 텔레메트리 기본 활성 + 옵트아웃 미문서화 + 부모 프로세스 스캔** — `cli-hub/cli_hub/analytics.py:84-85, 104-135`, `cli-hub/cli_hub/cli.py:55-56`
`cli-hub`는 **모든 호출마다** PostHog로 이벤트를 전송하고(`track_visit`), `~/.cli-hub/.analytics_id`에 영구 UUID를 저장하며, `/proc/<pid>/cmdline`을 4단계 거슬러 올라가 부모 프로세스 명령줄을 읽어 어떤 AI 에이전트가 호출했는지 분류한다(`_parent_process_commands`). 옵트아웃 환경변수 `CLI_HUB_NO_ANALYTICS`는 README·SECURITY.md·CONTRIBUTING.md 어디에도 문서화되어 있지 않다(grep 무검출). 부모 프로세스 cmdline에는 파일 경로 등 민감정보가 포함될 수 있다.
**권고**: 최초 실행 시 고지 + 옵트아웃 방법 README 문서화, cmdline 원문이 아닌 매칭된 시그널 ID만 수집함을 명시(현재 코드상 시그널 ID만 전송하는 점은 확인됨 — 고지 문제가 핵심).

**M-2. Obsidian 백엔드 TLS 검증 무조건 비활성** — `obsidian/agent-harness/cli_anything/obsidian/utils/obsidian_backend.py:13, 34, 65, 96, 125, 155`
```python
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
resp = requests.get(url, headers=_headers(api_key), ..., verify=False)
```
기본값 `https://localhost:27124`(자체 서명 인증서) 사정은 이해되나, `--host`로 원격 URL을 지정해도 `verify=False`가 강제되어 Bearer API 키가 검증 없는 TLS로 전송된다. 검증을 켤 방법 자체가 없다.
**권고**: `verify` 파라미터화(기본: localhost만 False), 또는 플러그인 인증서 pinning 옵션 제공.

**M-3. 브라우저 하니스 SSRF 방어가 기본 꺼짐 + 정규식 기반 우회 여지** — `browser/agent-harness/cli_anything/browser/utils/security.py:22, 54-72`
스킴 차단(file/javascript/data 등)은 견고하지만, 사설망 차단은 **opt-in**(기본 허용)이고, 켜더라도 호스트명 정규식 매칭이라 10진수 IP(`http://2130706433/`), IPv4-mapped IPv6, DNS 리바인딩을 걸러내지 못한다. "프롬프트 인젝션된 에이전트"를 위협 모델로 명시한 프로젝트(SECURITY.md) 성격상 격차가 있다.
**권고**: `ipaddress` 모듈로 DNS 해석 후 IP 판정, 프로덕션 기본값 차단으로 전환 검토.

**M-4. Zoom OAuth 플로우에 `state` 파라미터 부재 + 콜백 오류 페이지 반사 XSS** — `zoom/agent-harness/cli_anything/zoom/utils/zoom_backend.py:96-103`, `zoom/agent-harness/cli_anything/zoom/core/auth.py:92-100`
authorize URL에 CSRF 방지용 `state`가 없어 로컬 콜백(127.0.0.1:4199)이 열려 있는 2분 동안 공격자가 유도한 인가 코드가 주입될 수 있다. 또 오류 콜백에서 `f"<h2>Authorization failed: {auth_error[0]}</h2>"`로 쿼리 파라미터를 이스케이프 없이 HTML에 삽입한다(반사 XSS, 로컬 한정이라 영향은 제한적).
**권고**: `state` 생성·검증 추가, `html.escape()` 적용.

**M-5. 567줄 파일의 39중 바이트 동일 복제 등 하니스 간 대규모 중복** — `*/agent-harness/cli_anything/*/utils/repl_skin.py`
`repl_skin.py`가 39개 하니스에 md5 동일하게 존재하고 변형 9개가 추가로 있다(총 48개 + 분할 패키지 4개). 버그 수정·기능 변경 시 60곳에 N배 반영해야 하며, 이미 변형이 갈라지기 시작한 것이 드리프트의 증거다. 이것이 py 파일 1,053개의 주된 원인이다.
**권고**: `cli-anything-core` 공용 패키지로 repl_skin/output/config 보일러플레이트를 추출하고 각 하니스가 의존하도록 전환(포크의 `REFACTORING_PLAN.md`와 동일 방향).

**M-6. 초대형 단일 파일 CLI — 200줄 게이트 baseline 372건 동결** — `.github/scripts/file_size_baseline.txt`
`freecad/agent-harness/.../freecad_cli.py` 4,911줄, `docs/scripts/freecad_live_preview_demo.py` 4,981줄, `sbox_cli.py` 2,423줄, `cli-hub/cli_hub/preview.py` 1,891줄(HTML/CSS 문자열 혼재) 등. 게이트가 신규 위반은 막지만 기존 부채 372건이 그대로 동결되어 있다.
**권고**: baseline burndown 계획 수립(명령 그룹별 모듈 분리, preview.py는 HTML 템플릿 분리부터).

**M-7. `@claude` 트리거 워크플로의 광범위 쓰기 권한** — `.github/workflows/claude.yml`
`issue_comment`/`issues`에서 `@claude` 포함 시 `contents: write`, `pull-requests: write` 권한으로 에이전트를 실행한다. 워크플로 자체에 actor 게이팅(`author_association` 검사 등)이 없어 액션 내부 권한 검사에만 의존하며, 이슈/PR 본문(비신뢰 입력)이 에이전트 프롬프트 컨텍스트로 흘러드는 프롬프트 인젝션 표면이 있다.
**권고**: 워크플로 레벨에서 `github.event.comment.author_association`이 OWNER/MEMBER/COLLABORATOR인 경우로 제한, 권한 최소화.

### Low

**L-1. 라이선스 메타데이터 불일치** — `LICENSE`(Apache-2.0) vs `cli-hub/setup.py:20`, `blender/agent-harness/setup.py:39` 등 6개 패키지가 `license="MIT"` 선언(freecad·mailchimp만 Apache-2.0, 나머지 50여 개는 미선언). PyPI에 배포되는 `cli-anything-hub`가 저장소 라이선스와 다른 라이선스를 표방한다.
**권고**: 전 패키지 `license` 필드를 Apache-2.0으로 통일.

**L-2. 분석 토큰 소스 하드코딩** — `cli-hub/cli_hub/analytics.py:20`, `docs/hub/index.html:2812`
`POSTHOG_PROJECT_TOKEN = "phc_..."`(마스킹). PostHog 프로젝트 토큰은 공개용 write key라 비밀 유출은 아니지만, 소스에 박혀 있어 로테이션에 릴리스가 필요하고 임의 이벤트 주입(대시보드 오염)이 가능하다.
**권고**: 서버측 필터링 전제 문서화, 필요 시 빌드타임 주입.

**L-3. bare `except:` 2건** — `unimol_tools/agent-harness/cli_anything/unimol_tools/utils/weights.py:120`, 동 하니스 `tests/test_full_e2e.py:66`. `KeyboardInterrupt`/`SystemExit`까지 삼킨다. 그 외 `except Exception` 526건 중 일부는 `pass`로 무음 처리(예: `macrocli/backends/semantic_ui.py:159`).
**권고**: `except ImportError:` 등 구체 타입으로 교체.

**L-4. CI 검증 스크립트의 `exec()` 사용** — `.github/scripts/validate_root_skills.py:16`: `exec(sync_script.read_text(...), namespace)`. 자기 저장소 파일 실행이라 위험도는 낮지만 `importlib` 로드가 정석이다.

**L-5. 취약한 문자열 수술 기반 pip 명령 조립** — `cli-hub/cli_hub/installer.py:169`
```python
[sys.executable, "-m", "pip", "install"] + install_cmd.replace("pip install ", "").split()
```
`install_cmd`가 "pip install "로 시작하지 않거나 공백이 다르면 오동작하고, 레지스트리가 `--index-url` 같은 임의 pip 플래그를 주입할 수 있다(H-1과 연결). 매직 문자열 대신 패키지 스펙 필드를 구조화할 것.

**L-6. PyPI 메타데이터에 개인 CDN URL** — `cli-hub/setup.py:18`: 프로젝트 도메인이 아닌 개인 명의 DigitalOcean Spaces 버킷이 공식 패키지 메타데이터에 노출. 버킷 소유권 이전/만료 시 인계 위험.

**L-7. NSLogger 고정 인증서 비밀번호** — `nslogger/agent-harness/cli_anything/nslogger/core/listener.py:68`: 임시 자체 서명 PKCS#12에 고정 password `"nslogger-cli"`. 1일짜리 로컬 임시 키라 실위험은 낮으나 `secrets.token_hex()` 생성이 바람직.

**L-8. 텔레메트리로 인한 종료 지연 가능성** — `cli-hub/cli_hub/analytics.py:73-81`: atexit에서 대기 중 스레드를 **개별 3초 타임아웃**으로 join — 네트워크 불통 시 이벤트 수에 비례해 종료가 지연될 수 있다(데몬 스레드이므로 전체 데드라인 하나로 충분).

---

## 4. 확인했으나 문제없음 (긍정 사항)

- **하드코딩 시크릿 없음**: `ghp_`/`sk-`/`xox`/`AKIA` 및 `key=value` 패턴 전수 grep 결과 실제 비밀 미검출. API 키는 전부 env var 또는 0o600 설정 파일(`anygen_backend.py:60`, `novita_backend.py:41`, zoom `_restrict_path(…, 0o600)`) 경유.
- **SQL 인젝션 없음**: `zotero/utils/zotero_sqlite.py:440-495`의 f-string은 구조 조각(WHERE 골격)만이고 모든 값은 `?` 파라미터 바인딩. n8n `versions.py`의 placeholder 조립도 동일하게 안전.
- **SECURITY.md의 위협 모델이 실코드와 일치**: 문서가 주장하는 `_script_fu_escape()`(`gimp/utils/gimp_backend.py:15-22`) 실재·적용 확인.
- **`pull_request_target` 워크플로 안전 구현**: `pr-labeler.yml`이 base ref만 체크아웃 + `persist-credentials: false`.
- **프리뷰 서버 127.0.0.1 바인딩**: `cli-hub/cli_hub/preview.py:1852`.
- **테스트 실체 확인**: cli-hub 95개, blender 165개, obsidian 47개 로컬 실행 전부 통과. 레지스트리는 네트워크 실패 시 캐시 폴백(`registry.py:44-52`).
- **문법 건전성**: 1,053개 py 전체 `compileall` 통과(Python 3.11 — 포크 커밋이 3.10 호환 이슈를 이미 수정).
- **의존성 선언 정합**: `requests` 사용 하니스들의 setup.py에 모두 선언됨. 표준 라이브러리 위주의 얕은 의존성.
- **200줄 게이트 인프라**(포크 추가): CI + pre-push 훅 + baseline 신규 위반 차단 동작 구조 확인.

## 5. 관점별 평가표

| 관점 | 점수 | 근거 |
|---|---|---|
| 보안성 | 5/10 | 하니스 레벨 위생(이스케이프·0o600·파라미터화 SQL)은 우수하나, 원격 레지스트리 명령 shell 실행(H-1)·verify=False·SSRF 기본 허용이 큰 감점 |
| 안정성 | 7/10 | HTTP 타임아웃·예외 래핑·캐시 폴백이 일관적이고 테스트 통과율 실증됨. bare except 2건과 광범위 `except Exception` 다수 |
| 효율성 | 7/10 | 레지스트리 1시간 캐시, 비동기 텔레메트리, 프리뷰 스레드 서버 등 적절. atexit 개별 3초 join과 초대형 단일 파일의 로드 비용은 사소한 감점 |
| 보수 용이성 | 4/10 | 567줄 파일 39중 복제 + 4,900줄 단일 파일 + baseline 372건 + 라이선스 메타 불일치 — 수정 비용이 하니스 수에 비례해 폭증 |
| 확장성 | 6/10 | "하니스 1개 = 폴더 1개 + 레지스트리 1항목" 패턴은 기여 확장에 강함(60개 실증). 다만 공용 코어 부재로 횡단 변경이 60배 비용 |
| 체계성 | 6/10 | 패키지별 setup.py·테스트·SKILL.md·레지스트리·파일 크기 게이트는 갖췄으나, **테스트 CI 부재**(H-2)·린트 CI 부재·메타데이터 드리프트 |

## 6. 개선 우선순위 Top 5

1. **설치 파이프라인 공급망 방어** (H-1, L-5): `curl|bash` 항목 격리·사용자 확인, `shell=True` 제거, 레지스트리 항목 무결성 검증 — cli-hub는 PyPI로 배포되는 실사용 진입점이라 파급이 가장 큼.
2. **pytest CI 도입** (H-2): path-filter 매트릭스로 변경 하니스만 실행 + cli-hub는 publish 게이트화. "2,269 Passing" 배지를 실제 CI가 보증하게.
3. **공용 코어 패키지 추출** (M-5): repl_skin/output/config 보일러플레이트를 `cli-anything-core`로 통합 — 파일 수·중복·드리프트를 구조적으로 해소.
4. **텔레메트리 고지·옵트아웃 문서화** (M-1): README/SECURITY.md에 수집 항목과 `CLI_HUB_NO_ANALYTICS` 명시, 최초 실행 시 1회 고지.
5. **네트워크 경계 보강** (M-2, M-3, M-4): Obsidian `verify` 파라미터화, 브라우저 사설망 차단의 IP 해석 기반 전환, Zoom OAuth `state` + HTML 이스케이프.
