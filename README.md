# 🔎 베리파이 AI v5 (Verify AI v5)

**Maximum Multi-Agent + Full MCP Edition**

SW기획 · 개발 · AI · DB · 경영기획 · 마케팅 · 인프라 전 영역 지원

---

## 설치 (v5)

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

## v5 주요 특징

- Tool Calling (데이터 분석, Python 실행, 웹 검색, MCP 전략)
- Multi-Agent Supervisor 모드
- Chroma 기반 영구 RAG
- MCP 7대 영역(SW기획~인프라) 전략 지원
- 고품질 채팅 UI

**팀 공유 시**: 각자 Ollama 모델을 직접 pull 해야 합니다. GPU 사양이 비슷해야 24B 모델이 원활합니다.

---

**고도화 1차 완료 (2026.05)**