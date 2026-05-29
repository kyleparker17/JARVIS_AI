# 🔎 JARVIS v7

**Multi-Agent System** — 완전 로컬 Ollama 기반

Main Orchestrator (24B) + Specialized Agents (8B/9B)

---

## 🧠 Multi-Agent 구조 (v7)

| 역할                  | 모델                | 담당 영역                          | 비고 |
|-----------------------|---------------------|------------------------------------|------|
| **Main Orchestrator** | mistral-small:24b   | 전체 지휘, 복잡한 추론, 최종 판단   | 기본 |
| **2nd Orchestrator**  | phi-4:14b           | 빠른 응답용 대체 지휘자             | 수동 전환 |
| **Document/RAG Agent**| llama3.1:8b         | 문서 분석, Watch Folder, RAG       | Orchestrator가 호출 지시 |
| **Code/Analysis Agent**| gemma2:9b          | 코드, 데이터 분석, Reasoning       | Orchestrator가 호출 지시 |

> **중요**: 24B와 14B는 **절대 동시에 로드되지 않습니다**. (VRAM 보호)

---

## ✨ v7 주요 특징

- **자동 Orchestrator 선택** (Smart Routing)
- 수동 전환 지원
- **다중 채팅** 지원 (여러 주제별 독립 세션)
- **채팅창 내 파일 업로드** (PDF, DOCX, XLSX, CSV, TXT 등) — 사이드바가 아닌 채팅 영역에 배치
- **추론 과정 표시** (🧠 추론 과정 보기 expander)
- 사이드바 최소화 (Agent Pool 제거)
- Watch Folder 자동 로드 + Persistent Config
- 사이드바에서 실시간 Agent 상태 시각화
- Persistent Watch Folder (`config.json`)
- Streaming 응답
- 완전 로컬 (외부 API 없음)

---

## 🚀 실행 방법

### 처음 설치하는 경우 (최초 1회)

> **사전 준비**: [Python 3.11+](https://python.org), [Node.js 18+](https://nodejs.org), [Ollama](https://ollama.com) 설치 필요

```powershell
# 1. 프로젝트 폴더로 이동
cd C:\Users\사용자이름\KS\IT_Assistant   # 본인 경로로 수정

# 2. Python 가상환경 생성
python -m venv .venv

# 3. PowerShell 실행 권한 허용 (최초 1회, 관리자 불필요)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 4. 패키지 설치
.\.venv\Scripts\pip install -r requirements.txt

# 5. Ollama 모델 다운로드 (용량 큼 — 처음에만)
ollama pull mistral-small:24b   # ~14GB, 메인 모델
ollama pull phi-4:14b           # ~8GB,  보조 모델
```

### 이후 실행 (매번)

```powershell
npm run dev
```

> `npm run dev`는 `.venv` 안의 Python을 직접 사용합니다. 가상환경 활성화 불필요.  
> 또는 `start.bat` 더블클릭으로도 실행 가능.

### 설치가 잘 안 될 때

```powershell
# pip 업그레이드 후 재시도
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

---

## 📌 사용 팁

- **기본**: Main Orchestrator (24B) 사용 추천
- 복잡하거나 느릴 때 → 사이드바에서 **Orchestrator 전환** 버튼 클릭
- 빠른 테스트 → Multi-Agent Mode를 OFF로 전환
- Watch Folder는 연결 후 `config.json`에 자동 저장됩니다

---

## 📁 파일 구조

- `config.json` — Watch Folder 경로 저장
- `chroma_db_v7/` — RAG용 벡터 DB (준비)
- 다운로드 파일: `JARVIS_v7_*.md`, `JARVIS_v7_*.docx`

---

**JARVIS v7 Multi-Agent Edition**  
팀 공유를 위한 실용적 Multi-Agent 아키텍처

Made with ❤️ by 츠키토
