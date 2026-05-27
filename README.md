# 🔎 베리파이 AI (Verify AI)

**데이터 분석 & 검증 특화 AI 어시스턴트**

Claude + Grok 스타일 채팅 UI | Streamlit + Ollama

---

## 프로젝트 개요

베리파이 AI는 IT 기획·개발 팀을 위한 **데이터 중심 AI 비서**입니다.

- CSV / Excel 파일을 업로드하면 자동으로 데이터 품질 분석
- 결측치, 이상치, 기본 통계, 컬럼 분석을 LLM이 바로 이해할 수 있게 변환
- "🔍 데이터 분석 & 검증" 스킬을 통해 전문적인 데이터 검증 수행
- 전략 보고서, 기획서, 아키텍처 리뷰, MCP 설계 등 다양한 IT 업무 지원

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 **데이터 분석 & 검증** | CSV/Excel 자동 분석 + 품질 검증 + 인사이트 도출 |
| 📊 IT 전략 보고서 | Executive Summary 중심의 전략 문서 작성 |
| 📝 기획서/제안서 | Problem-Solution-Benefit 구조의 설득력 있는 문서 |
| 💻 Python 개발 지원 | Senior Engineer 수준의 코드 작성 |
| 🏗️ 아키텍처 리뷰 | 보안·확장성·유지보수성 관점의 깊이 있는 리뷰 |
| 🚀 MCP Server Builder | 고품질 MCP 서버 설계 가이드 |
| ✍️ 콘텐츠 리서치 & 글쓰기 | 리서치 + 인용 + 구조화된 글쓰기 지원 |

---

## 설치 및 실행 방법 (다른 PC에서도 동일하게)

### 1. 사전 요구사항

- **Python 3.10 이상**
- **Ollama** 설치 및 실행 중
- 다음 모델이 로컬에 설치되어 있어야 함 (용량 주의)

```bash
ollama pull mistral-small:24b
ollama pull phi-4:14b
```

> **주의**: `mistral-small:24b` 모델은 약 14GB 정도의 VRAM/메모리가 필요합니다. 현재 PC와 동일하거나 비슷한 사양을 권장합니다.

### 2. 설치

```powershell
# 1. 프로젝트 클론 또는 다운로드
git clone https://github.com/kyleparker17/verifyAI.git
cd verifyAI

# 2. 가상환경 생성 (강력 권장)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. 의존성 설치
pip install -r requirements.txt
```

### 3. 실행

```powershell
python -m streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속하면 됩니다.

---

## Windows에서 쉽게 실행하는 방법 (팀원 추천)

`start.bat` 파일을 만들고 아래 내용을 넣은 후 더블클릭으로 실행할 수 있습니다:

```bat
@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
python -m streamlit run app.py
pause
```

---

## 사용 팁

- **데이터 분석**을 할 때는 반드시 **"🔍 데이터 분석 & 검증 (Verify Analyst)"** 스킬을 선택하세요.
- CSV나 Excel 파일을 여러 개 업로드해도 됩니다. 자동으로 분석 정보를 추출합니다.
- Chain of Thought(`<thinking>`)를 통해 AI의 사고 과정을 확인할 수 있습니다.
- 생성된 결과는 Markdown, DOCX, PPTX로 바로 내보낼 수 있습니다.

---

## 기술 스택

- **Frontend**: Streamlit (Claude/Grok 스타일 채팅 UI)
- **LLM Backend**: Ollama (Mistral Small 24B / Phi-4 14B)
- **Framework**: LangChain
- **Data**: pandas (자동 CSV/Excel 분석)

---

## 팀 공유 시 주의사항

- 각 PC마다 **Ollama**와 모델이 별도로 설치되어 있어야 합니다.
- `.venv` 폴더는 절대 공유하지 마세요 (gitignore 처리됨).
- 모델이 무거우므로, **동일하거나 유사한 사양**의 PC를 사용하는 것을 권장합니다.

---

## License

개인/팀 내부 사용 목적으로 제작되었습니다.

---

**Made for practical data-driven IT work • 2026**