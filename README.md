# 🔎 베리파이 AI (Verify AI)

**데이터 분석 & IT 기획·개발 전용 Ollama UI**  
Tool-Enhanced | Multi-Agent + RAG 지원 | Claude + Grok 스타일 채팅

---

## 팀 공유용 설치 가이드

이 프로젝트는 각 팀원이 **로컬 PC**에서 독립적으로 실행하는 형태입니다.  
GPU 사양이 비슷해야 24B 모델을 원활하게 사용할 수 있습니다.

### 필수 사양 (권장)
- NVIDIA GPU 12GB VRAM 이상 (RTX 4070 12GB 이상 추천)
- RAM 32GB 이상
- Python 3.10+
- Ollama 설치

### 1. Ollama + 모델 설치 (가장 중요)

```powershell
# Ollama 공식 사이트에서 설치 후 아래 명령 실행

# 문서/전략 작성용 (메인 추천)
ollama pull mistral-small:24b

# Python 개발/분석용
ollama pull phi-4:14b

# 설치 확인
ollama list
```

> **주의**: `mistral-small:24b` 모델은 약 14GB 정도 필요합니다. 12GB VRAM GPU에서는 CPU offloading이 발생해 다소 느릴 수 있습니다.

### 2. 프로젝트 설치

```powershell
# 1. 저장소 클론
git clone https://github.com/kyleparker17/verifyAI.git
cd verifyAI

# 2. 가상환경 생성
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. 의존성 설치
pip install -r requirements.txt
```

### 3. 실행

```powershell
python -m streamlit run app.py
```

또는 Windows 사용자는 `start.bat` 더블클릭으로 실행 가능.

---

## 주요 기능 (v2 기준)

- Tool Calling 지원 (데이터 분석, 웹 검색, Python 코드 실행 등)
- Skills Library (awesome-claude-skills 스타일)
- CSV/Excel 자동 분석 + Pandas 기반 검증
- Chain of Thought 표시
- Markdown / DOCX / PPTX Export
- RAG (문서 업로드 분석)

---

## 팀원 주의사항

- `.venv` 폴더는 절대 커밋하지 마세요 (gitignore 처리됨)
- 각자 Ollama 모델을 직접 pull 해야 합니다.
- GPU 사양이 크게 차이 나면 24B 모델 사용이 어려울 수 있습니다.
- 필요시 `start.bat`을 사용하면 편합니다.

---

## 개발자용

- Skills 추가: `app.py` 상단 `SKILLS` 딕셔너리 수정
- Tool 추가: LangChain `@tool` 데코레이터 사용
- 고도화 방향: Multi-Agent, LangGraph, MCP Server 연동 등

**Made for practical IT & Data work • 2026**