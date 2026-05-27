"""
베리파이 AI v5 - Maximum Multi-Agent + MCP Full Edition
(단기적 사용을 위해 최대한 강력하게 구성)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from docx import Document
import io
import os
import re

from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="베리파이 AI v5", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0c10; color: #e0e6f0; }
    .chat-bubble-user {
        background: #1f2230; border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 18px 18px 4px 18px; padding: 14px 18px; margin: 8px 0;
    }
    .chat-bubble-assistant {
        background: #14161f; border: 1px solid rgba(124, 58, 237, 0.25);
        border-radius: 18px 18px 18px 4px; padding: 14px 18px; margin: 8px 0;
    }
    h1 { background: linear-gradient(90deg, #e0e6f0 0%, #00ff9d 100%);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.title("🔎 베리파이 AI v5")
st.caption("Maximum Multi-Agent + Full MCP | SW기획·개발·AI·DB·경영기획·마케팅·인프라 전 영역")

# ================== SESSION STATE ==================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_dataframes" not in st.session_state:
    st.session_state.uploaded_dataframes = {}
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# ================== RAG (Chroma) ==================
if "vectorstore" not in st.session_state:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    st.session_state.vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

# ================== TOOLS ==================

@tool
def list_uploaded_files() -> str:
    """현재 업로드된 데이터 파일 목록을 반환합니다."""
    if not st.session_state.uploaded_dataframes:
        return "현재 업로드된 데이터 파일이 없습니다."
    return "업로드된 파일: " + ", ".join(st.session_state.uploaded_dataframes.keys())

@tool
def analyze_dataframe(file_name: str, analysis_request: str = "기본 분석") -> str:
    """업로드된 CSV/Excel 파일을 분석합니다."""
    if file_name not in st.session_state.uploaded_dataframes:
        return f"'{file_name}' 파일을 찾을 수 없습니다."
    
    df = st.session_state.uploaded_dataframes[file_name]
    result = f"[{file_name}] 분석 결과\n"
    result += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n"
    
    if "통계" in analysis_request or "기본" in analysis_request:
        numeric = df.select_dtypes(include=['number'])
        if not numeric.empty:
            result += "수치형 기본 통계:\n" + numeric.describe().to_string() + "\n\n"
    
    if "결측치" in analysis_request or "이상치" in analysis_request:
        missing = df.isnull().sum()
        result += f"결측치 현황:\n{missing[missing > 0].to_string()}\n"
    
    return result

@tool
def run_python_code(code: str) -> str:
    """업로드된 데이터를 활용하여 Python 코드를 실행합니다."""
    try:
        local_vars = {
            "pd": pd,
            "np": __import__("numpy"),
            "uploaded_dataframes": st.session_state.uploaded_dataframes,
        }
        if st.session_state.uploaded_dataframes:
            last_key = list(st.session_state.uploaded_dataframes.keys())[-1]
            local_vars["df"] = st.session_state.uploaded_dataframes[last_key]
        
        exec(code, {"__builtins__": __builtins__}, local_vars)
        return str(local_vars.get("result", "코드 실행 완료"))
    except Exception as e:
        return f"코드 실행 오류: {str(e)}"

@tool
def web_search(query: str) -> str:
    """DuckDuckGo를 사용한 웹 검색"""
    try:
        return DuckDuckGoSearchRun().run(query)
    except Exception as e:
        return f"웹 검색 실패: {e}"

@tool
def mcp_strategy(area: str) -> str:
    """MCP를 특정 영역(Sw기획, 개발, AI, DB, 경영기획, 마케팅, 인프라)에 적용한 전략을 제안합니다."""
    strategies = {
        "sw기획": "MCP로 GitHub + Jira + Notion + Figma를 하나의 Context로 연결 → 요구사항 자동 추출 → 아키텍처 초안 생성",
        "개발": "MCP로 로컬 코드베이스 + Docker + PostgreSQL + 모니터링 도구를 직접 제어하며 코드 생성",
        "ai": "Multi-Agent 간 MCP로 지식과 도구를 공유하며 협업 (Supervisor + Worker 구조)",
        "db": "PostgreSQL, MySQL, MongoDB 등에 실시간 쿼리·스키마 분석·데이터 변환 수행",
        "경영기획": "ERP + 재무 + HR + BI 도구를 MCP로 연결 → 실시간 경영 대시보드 및 보고서 자동 생성",
        "마케팅": "GA4 + Meta Ads + CRM + 이메일 마케팅 도구를 MCP로 통합 → 고객 여정 분석 및 캠페인 자동화",
        "인프라": "Kubernetes + AWS/GCP + Terraform + Prometheus를 MCP로 제어 → 인프라 코드 생성 및 장애 대응 자동화"
    }
    area_key = area.lower().replace(" ", "").replace("기획", "")
    return strategies.get(area_key, "해당 영역에 대한 MCP 적용 전략을 구체적으로 제안합니다. (sw기획/개발/ai/db/경영기획/마케팅/인프라 중 선택)")

tools = [list_uploaded_files, analyze_dataframe, run_python_code, web_search, mcp_strategy]

# ================== SKILLS ==================
SKILLS = {
    "기본": "너는 실무 중심의 IT 전문가이다.",
    "🔍 데이터 검증 전문": "데이터 품질 검증, 이상치 탐지, 통계 분석 전문가. 업로드된 데이터를 철저히 분석한다.",
    "📊 IT 전략 보고서": "2026년 최신 트렌드를 반영한 고품질 전략 컨설턴트.",
    "💻 Senior Python 개발": "Senior Python Engineer. 안전하고 실무에 바로 적용 가능한 코드를 작성한다.",
    "📑 종합 문서 분석": "RAG와 Multi-Agent를 활용한 깊이 있는 문서+데이터 분석 전문가.",
    "🚀 MCP Full Specialist": "MCP(Model Context Protocol) 전문가. SW기획·개발·AI·DB·경영기획·마케팅·인프라 7개 영역 모두에 MCP를 적용한 실무 전략을 제시한다.",
    "🧠 Multi-Agent Supervisor": "여러 전문 에이전트(Data Analyst, Code Engineer, MCP Strategist, Report Writer)를 조율하여 종합 결과를 만든다."
}

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("⚙️ 베리파이 AI v5")
    model_name = st.selectbox("모델", ["mistral-small:24b", "phi-4:14b"], index=0)
    temperature = st.slider("Temperature", 0.0, 0.7, 0.2)
    
    selected_skill = st.selectbox("Skill", list(SKILLS.keys()))
    use_tools = st.checkbox("Tool Calling 활성화", value=True)
    use_mcp = st.checkbox("MCP Full Mode (7대 영역)", value=True)

    st.divider()
    st.caption("MCP 지원 영역: SW기획 · 개발 · AI · DB · 경영기획 · 마케팅 · 인프라")

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_dataframes = {}
        st.rerun()

# ================== FILE UPLOAD ==================
uploaded_files = st.file_uploader(
    "📎 CSV / Excel 업로드 (자동 분석)", 
    accept_multiple_files=True, 
    type=['csv', 'xlsx', 'xls']
)

if uploaded_files:
    st.session_state.uploaded_dataframes = {}
    for f in uploaded_files:
        try:
            if f.name.lower().endswith('.csv'):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f)
            st.session_state.uploaded_dataframes[f.name] = df
        except Exception as e:
            st.warning(f"{f.name} 로드 실패: {e}")

# ================== CHAT UI ==================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🔎"
    with st.chat_message(msg["role"], avatar=avatar):
        css = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
        st.markdown(f'<div class="{css}">{msg["content"]}</div>', unsafe_allow_html=True)

# ================== USER INPUT ==================
if prompt := st.chat_input("MCP Multi-Agent에게 요청하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🔎"):
        placeholder = st.empty()
        full_response = ""

        try:
            llm = ChatOllama(model=model_name, temperature=temperature, num_predict=8192)

            system_prompt = f"""{SKILLS.get(selected_skill, SKILLS['기본'])}

너는 베리파이 AI v5 Supervisor이다.
사용자가 업로드한 데이터가 있으면 반드시 도구(list_uploaded_files, analyze_dataframe, run_python_code 등)를 사용해서 정확하게 분석하라.
MCP 관련 요청이 오면 mcp_strategy 도구를 적극 사용하라.
최종 답변은 실무에서 바로 쓸 수 있는 수준으로 Markdown으로 정리한다."""

            if use_tools:
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history", optional=True),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])
                agent = create_tool_calling_agent(llm, tools, prompt_template)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=10)
                
                response = agent_executor.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.messages[-8:]
                })["output"]
            else:
                chain = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history", optional=True),
                    ("human", "{input}")
                ]) | llm | StrOutputParser()
                
                response = chain.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.messages[-8:]
                })

            placeholder.markdown(response)
            full_response = response

        except Exception as e:
            full_response = f"오류가 발생했습니다: {str(e)}"
            placeholder.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response

        # Thinking 표시
        thinking_match = re.search(r"<thinking>(.*?)</thinking>", full_response, re.DOTALL | re.IGNORECASE)
        if thinking_match:
            with st.expander("💭 Chain of Thought"):
                st.markdown(thinking_match.group(1).strip())

# ================== EXPORT ==================
if st.session_state.last_response:
    st.divider()
    col1, col2, col3 = st.columns(3)
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    with col1:
        st.download_button("📝 Markdown", st.session_state.last_response, 
                          f"베리파이AI_v5_{ts}.md", "text/markdown", use_container_width=True)
    
    with col2:
        if st.button("📄 DOCX", use_container_width=True):
            doc = Document()
            doc.add_heading("베리파이 AI v5 Multi-Agent 보고서", 0)
            doc.add_paragraph(st.session_state.last_response)
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            st.download_button("DOCX 다운로드", bio.getvalue(), f"베리파이AI_v5_{ts}.docx", 
                              "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                              use_container_width=True)
    
    with col3:
        if st.button("📊 PPTX", use_container_width=True):
            st.info("PPTX 자동 생성은 준비 중입니다. (Markdown 변환 추천)")
