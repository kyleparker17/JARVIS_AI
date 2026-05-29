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

```powershell
cd C:\Users\user\KS\IT_Assistant
.\.venv\Scripts\Activate.ps1
npm run dev
```

또는 `start.bat` 더블클릭

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
