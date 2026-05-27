# 🔎 베리파이 AI v5 (Verify AI v5)

**Maximum Multi-Agent + Full MCP Edition**

SW기획 · 개발 · AI · DB · 경영기획 · 마케팅 · 인프라 전 영역 지원

---

## v5 주요 특징

- **Tool Calling** (데이터 분석, Python 실행, 웹 검색, MCP 전략)
- **Multi-Agent Supervisor** 모드
- **Chroma 기반 영구 RAG**
- **MCP Full Mode** — 7대 영역(Sw기획~인프라) 전문 전략 도구
- Claude + Grok 스타일 채팅 UI

---

## 설치

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Ollama 모델
ollama pull mistral-small:24b
ollama pull phi-4:14b
ollama pull nomic-embed-text
```

## 실행

```powershell
python -m streamlit run app.py
```

또는 `start.bat` 더블클릭.

---

## 팀 공유

- 각자 Ollama 모델 직접 pull 필요
- GPU 12GB 이상 권장 (24B 모델 사용 시)
- `.venv`는 공유 금지

**고도화 1차 (v5) 완료 • 2026.05**