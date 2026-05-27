"""
베리파이 AI v2 - Tool-Enhanced Version (고도화 1차)
Claude + Grok 스타일 채팅 + Tool Calling 지원
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from docx import Document
import io
import re
import tempfile
import os
from typing import List, Dict, Any

# LangChain
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="베리파이 AI v2",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CSS ==================
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
    .skill-badge {
        background: rgba(0, 255, 157, 0.12); color: #00ff9d;
        padding: 3px 10px; border-radius: 999px; font-size: 0.75rem;
        border: 1px solid rgba(0, 255, 157, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔎 베리파이 AI v2")
st.caption("Tool-Enhanced • Mistral Small 24B + Phi-4 14B | Skill + Tool 조합 시스템")

# ================== SESSION STATE ==================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_dataframes" not in st.session_state:
    st.session_state.uploaded_dataframes = {}   # filename -> DataFrame
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# ================== TOOLS ==================

@tool
def list_uploaded_files() -> str:
    """현재 업로드된 데이터 파일 목록을 반환합니다."""
    if not st.session_state.uploaded_dataframes:
        return "현재 업로드된 데이터 파일이 없습니다."
    files = list(st.session_state.uploaded_dataframes.keys())
    return f"업로드된 파일: {', '.join(files)}"

@tool
def get_dataframe_info(file_name: str) -> str:
    """특정 파일의 기본 정보(행/열, 컬럼, 결측치, 데이터 타입)를 반환합니다."""
    if file_name not in st.session_state.uploaded_dataframes:
        return f"'{file_name}' 파일을 찾을 수 없습니다. 먼저 파일을 업로드하세요."
    
    df = st.session_state.uploaded_dataframes[file_name]
    info = f"파일: {file_name}\n"
    info += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n"
    info += "컬럼 정보:\n"
    for col in df.columns:
        info += f"  - {col}: {df[col].dtype} | 결측치: {df[col].isnull().sum()}\n"
    return info

@tool
def describe_dataframe(file_name: str) -> str:
    """파일의 수치형 컬럼에 대한 상세 통계(평균, 중앙값, 분포 등)를 제공합니다."""
    if file_name not in st.session_state.uploaded_dataframes:
        return f"'{file_name}' 파일을 찾을 수 없습니다."
    
    df = st.session_state.uploaded_dataframes[file_name]
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        return "수치형 컬럼이 없습니다."
    
    return numeric.describe().to_string()

@tool
def run_python_code(code: str) -> str:
    """업로드된 데이터프레임을 활용하여 Python 코드를 실행합니다. 
    사용 가능한 변수: df (마지막으로 선택된 파일), uploaded_dataframes (dict)"""
    try:
        local_vars = {
            "pd": pd,
            "np": np,
            "uploaded_dataframes": st.session_state.uploaded_dataframes,
        }
        # 가장 최근 파일을 df로 편의 제공
        if st.session_state.uploaded_dataframes:
            last_file = list(st.session_state.uploaded_dataframes.keys())[-1]
            local_vars["df"] = st.session_state.uploaded_dataframes[last_file]
        
        exec(code, {"__builtins__": __builtins__}, local_vars)
        result = local_vars.get("result", "코드 실행 완료 (result 변수가 없음)")
        return str(result)
    except Exception as e:
        return f"코드 실행 오류: {str(e)}"

@tool
def web_search(query: str) -> str:
    """DuckDuckGo를 통해 최신 웹 정보를 검색합니다."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"웹 검색 실패: {str(e)}"

@tool
def simple_calculator(expression: str) -> str:
    """안전한 수학 계산을 수행합니다. (예: 2+3*4)"""
    try:
        allowed = {"__builtins__": None}
        result = eval(expression, allowed, {"abs": abs, "round": round, "max": max, "min": min})
        return str(result)
    except Exception as e:
        return f"계산 오류: {str(e)}"

tools = [
    list_uploaded_files,
    get_dataframe_info,
    describe_dataframe,
    run_python_code,
    web_search,
    simple_calculator
]

# ================== SKILLS ==================
SKILLS = {
    "기본": "너는 실무 중심의 IT 전문가이다.",
    "🔍 데이터 검증 전문 (Verify Analyst)": "데이터 품질 검증, 이상치 탐지, 통계 분석, Pandas 활용 전문가. 업로드된 데이터를 철저히 분석한다.",
    "📊 IT 전략 보고서": "12년차 IT 전략 컨설턴트. 2026년 트렌드를 반영한 고품질 전략 문서를 작성한다.",
    "💻 Senior Python 개발": "Senior Python Engineer. 실무 수준의 clean code와 분석 코드를 작성한다.",
    "📑 종합 문서+데이터 분석": "문서와 데이터를 함께 분석하여 인사이트를 도출한다.",
    "🚀 기술 기획 (MCP/AI Agent)": "MCP, AI Agent, Antigravity 등 최신 기술을 실무에 적용하는 기획 전문가."
}

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("⚙️ 베리파이 AI v2")
    
    models = get_local_ollama_models()
    model_name = st.selectbox("모델", models, index=0)
    temperature = st.slider("Temperature", 0.0, 0.8, 0.2)
    
    st.divider()
    st.subheader("🛠️ Skills")
    selected_skill = st.selectbox("Skill 선택", list(SKILLS.keys()))
    
    st.divider()
    use_tools = st.checkbox("🛠️ Tool Calling 활성화", value=True)
    st.caption("Mistral Small 24B에서 잘 동작합니다")
    
    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_dataframes = {}
        st.session_state.last_response = ""
        st.rerun()

# ================== FILE UPLOAD (자동 로드) ==================
uploaded_files = st.file_uploader(
    "📎 CSV / Excel 파일 업로드 (자동 분석됨)", 
    accept_multiple_files=True, 
    type=['csv', 'xlsx', 'xls']
)

# 업로드된 파일을 pandas DataFrame으로 로드
if uploaded_files:
    st.session_state.uploaded_dataframes = {}
    for file in uploaded_files:
        try:
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            st.session_state.uploaded_dataframes[file.name] = df
        except Exception as e:
            st.warning(f"{file.name} 로드 실패: {e}")

# ================== HELPER ==================
def get_local_ollama_models() -> List[str]:
    try:
        import ollama
        models = ollama.list()
        names = [m.get("name", "") for m in models.get("models", []) if m.get("name")]
        return sorted(names) if names else ["mistral-small:24b", "phi4:14b"]
    except:
        return ["mistral-small:24b", "phi4:14b"]

def extract_thinking(text: str):
    match = re.search(r"<thinking>(.*?)</thinking>", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip(), re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    return "", text

# ================== CHAT HISTORY ==================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🔎"
    with st.chat_message(msg["role"], avatar=avatar):
        css = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
        st.markdown(f'<div class="{css}">{msg["content"]}</div>', unsafe_allow_html=True)

# ================== USER INPUT ==================
if prompt := st.chat_input("분석 요청, 코드 생성, 전략 수립 등을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🔎"):
        placeholder = st.empty()
        full_response = ""

        try:
            llm = ChatOllama(
                model=model_name,
                temperature=temperature,
                num_predict=8192,
            )

            skill_prompt = SKILLS.get(selected_skill, SKILLS["기본"])

            system_prompt = f"""{skill_prompt}

너는 베리파이 AI v2로서, 사용자가 제공한 도구(list_uploaded_files, get_dataframe_info, describe_dataframe, run_python_code, web_search, simple_calculator)를 적극적으로 활용해야 한다.

업로드된 데이터가 있으면 반드시 도구를 사용해서 정확한 분석을 수행하라.
답변은 항상 Markdown으로 구조화하고, <thinking> 태그로 사고 과정을 먼저 작성하라."""

            if use_tools:
                # Tool Calling Agent
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history", optional=True),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])

                agent = create_tool_calling_agent(llm, tools, prompt_template)
                agent_executor = AgentExecutor(
                    agent=agent, 
                    tools=tools, 
                    verbose=False,
                    handle_parsing_errors=True,
                    max_iterations=8
                )

                # 최근 대화 6개만 전달
                chat_history = []
                for m in st.session_state.messages[-6:]:
                    chat_history.append((m["role"], m["content"]))

                response = agent_executor.invoke({
                    "input": prompt,
                    "chat_history": chat_history
                })["output"]

            else:
                # 일반 모드 (Tool 없이)
                chat_history = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages[-8:]:
                    chat_history.append({"role": m["role"], "content": m["content"]})

                chain = ChatPromptTemplate.from_messages(chat_history) | llm | StrOutputParser()
                response = chain.invoke({})

            placeholder.markdown(response)
            full_response = response

        except Exception as e:
            full_response = f"오류가 발생했습니다: {str(e)}"
            placeholder.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response

        # Thinking 표시
        thinking, _ = extract_thinking(full_response)
        if thinking:
            with st.expander("💭 Chain of Thought"):
                st.markdown(thinking)

# ================== EXPORT ==================
if st.session_state.last_response:
    st.divider()
    col1, col2, col3 = st.columns(3)
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    with col1:
        st.download_button("📝 Markdown", st.session_state.last_response, 
                          f"VerifyAI_{ts}.md", "text/markdown", use_container_width=True)
    
    with col2:
        if st.button("📄 DOCX", use_container_width=True):
            doc = Document()
            doc.add_heading("베리파이 AI v2 분석 결과", 0)
            doc.add_paragraph(st.session_state.last_response)
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            st.download_button("DOCX 다운로드", bio.getvalue(), f"VerifyAI_Report_{ts}.docx", 
                              "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                              use_container_width=True, key="docx_dl")
    
    with col3:
        if st.button("📊 PPTX", use_container_width=True):
            try:
                # 간단 PPTX 생성 (이전 버전 재사용)
                prs = Presentation()
                slide = prs.slides.add_slide(prs.slide_layouts[6])
                # ... (간단 버전)
                st.success("PPTX 생성 완료 (추후 고도화)")
            except Exception as e:
                st.error(str(e))
