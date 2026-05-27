"""
베리파이 AI (Verify AI) - 최종 버전
Claude + Grok 스타일 채팅 UI
데이터 분석 & 검증 특화 | IT Planning & Development
"""

import streamlit as st
import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import ollama

from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

import io
import re
from datetime import datetime
from typing import List

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="베리파이 AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== FUTURISTIC CHAT CSS (Verify AI 테마) ==================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #e0e6f0;
    }
    
    .chat-bubble-user {
        background: #1f2230;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 18px 18px 4px 18px;
        padding: 14px 18px;
        margin: 8px 0;
        display: inline-block;
        max-width: 80%;
    }
    
    .chat-bubble-assistant {
        background: #14161f;
        border: 1px solid rgba(124, 58, 237, 0.25);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        display: inline-block;
        max-width: 80%;
    }
    
    .stChatInput textarea {
        background-color: #14161f !important;
        border: 1px solid rgba(0, 229, 255, 0.25) !important;
        color: #e0e6f0 !important;
    }
    
    h1 {
        background: linear-gradient(90deg, #e0e6f0 0%, #00ff9d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.95rem !important;
        font-weight: 600;
    }
    
    .skill-badge {
        background: rgba(0, 255, 157, 0.12);
        color: #00ff9d;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        border: 1px solid rgba(0, 255, 157, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔎 베리파이 AI")
st.caption("Verify AI • 데이터 분석 & 검증 특화 | Mistral Small 24B + Phi-4 14B")

# ================== SKILLS LIBRARY (데이터 분석 강화) ==================
SKILLS = {
    "기본": "너는 실무 중심의 IT 전문가이다. 명확하고 구체적인 답변을 제공한다.",
    
    "📊 IT 전략 보고서 작성": "너는 12년차 IT 전략 컨설턴트이다. 2025~2026 최신 트렌드를 반영하고, Executive Summary → 분석 → 제안 → Roadmap 구조로 작성한다.",
    
    "📝 기획서/제안서 전문": "너는 전문 기획서 작가이다. Problem → Solution → Benefit 구조로 설득력 있게 작성한다.",
    
    "💻 Senior Python 개발": "너는 Senior Python Engineer이다. clean code, 타입 안전성, 실무 적용성을 최우선으로 한다.",
    
    "🏗️ 아키텍처 리뷰": "너는 시니어 아키텍트이다. 확장성, 보안, 유지보수성 관점에서 깊이 있게 분석하고 대안을 제시한다.",
    
    "🚀 MCP Server Builder": "너는 MCP 서버 설계 전문가이다. Workflow 중심 도구 설계와 Agent 친화적인 에러 처리를 중시한다.",
    
    "✍️ 콘텐츠 리서치 & 글쓰기": "너는 Content Research Writer이다. 리서치, 인용, 강력한 Hook, 섹션별 피드백을 체계적으로 제공한다.",
    
    # === 데이터 분석 특화 Skill (강화) ===
    "🔍 데이터 분석 & 검증 (Verify Analyst)": """너는 데이터 분석 및 검증 전문가(Verify Analyst)이다.
주요 역할:
- 업로드된 CSV/Excel 파일의 데이터 품질을 철저히 검증
- 결측치, 이상치, 중복, 타입 불일치 등을 자동으로 찾아내고 보고
- 기본 통계(평균, 중앙값, 표준편차, 최솟값/최댓값)와 분포 특성을 분석
- 사용자 질문에 따라 요약, 인사이트 도출, 시각화 제안, 자동 분석 코드 생성, 문제점 리포팅 등을 수행
- 항상 정확성과 신뢰성을 최우선으로 하며, "데이터가 말하는 것"만 근거로 답변한다.
- 분석 결과는 Markdown 테이블과 bullet point로 명확하게 정리한다."""
}

# ================== HELPERS ==================
def get_local_ollama_models() -> List[str]:
    try:
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

def analyze_uploaded_files(files) -> str:
    """CSV/Excel 파일을 분석해서 LLM에게 넘길 컨텍스트 생성"""
    if not files:
        return ""
    
    context = "\n\n=== 업로드된 데이터 파일 분석 결과 ===\n"
    
    for file in files:
        try:
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                context += f"- {file.name}: 문서 파일 (텍스트 분석 모드)\n"
                continue
            
            # 기본 정보
            context += f"\n### {file.name}\n"
            context += f"- 행 수: {len(df):,} | 열 수: {len(df.columns)}\n"
            
            # 컬럼 정보
            context += "- 컬럼 목록:\n"
            for col in df.columns[:12]:
                dtype = str(df[col].dtype)
                nulls = df[col].isnull().sum()
                context += f"  - {col} ({dtype}) | 결측치: {nulls:,}\n"
            if len(df.columns) > 12:
                context += f"  - ... 외 {len(df.columns)-12}개 컬럼\n"
            
            # 수치형 컬럼 기본 통계
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                context += "- 수치형 변수 기본 통계:\n"
                desc = df[num_cols[:6]].describe().T
                for col in desc.index:
                    context += f"  - {col}: 평균={desc.loc[col, 'mean']:.2f}, 중앙값={desc.loc[col, '50%']:.2f}, 최소={desc.loc[col, 'min']:.2f}, 최대={desc.loc[col, 'max']:.2f}\n"
            
            # 결측치 요약
            total_missing = df.isnull().sum().sum()
            if total_missing > 0:
                context += f"- 전체 결측치: {total_missing:,}개\n"
            
        except Exception as e:
            context += f"- {file.name}: 분석 실패 ({str(e)})\n"
    
    context += "\n위 데이터를 기반으로 사용자의 질문에 정확하게 답변하라.\n"
    return context

def create_pptx_from_text(md_text: str, title: str = "베리파이 AI 분석 결과") -> bytes:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    DARK = RGBColor(0x0b, 0x0c, 0x10)
    CYAN = RGBColor(0x00, 0xe5, 0xff)
    GREEN = RGBColor(0x00, 0xff, 0x9d)
    WHITE = RGBColor(0xe0, 0xe6, 0xf0)

    def add_dark_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK
        bg.line.fill.background()
        spTree = slide.shapes._spTree
        sp = bg._element
        spTree.remove(sp)
        spTree.insert(2, sp)

    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_dark_bg(slide)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = GREEN
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(1.2))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Content
    lines = md_text.strip().split("\n")
    current_title = "분석 결과"
    bullets = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            if bullets:
                _add_content_slide(prs, current_title, bullets, DARK, GREEN, WHITE)
            current_title = line[2:].strip()
            bullets = []
        elif line.startswith("## "):
            if bullets:
                _add_content_slide(prs, current_title, bullets, DARK, GREEN, WHITE)
            current_title = line[3:].strip()
            bullets = []
        elif line.startswith(("- ", "* ")):
            bullets.append(line[2:])

    if bullets:
        _add_content_slide(prs, current_title, bullets, DARK, GREEN, WHITE)

    bio = io.BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio.getvalue()

def _add_content_slide(prs, title, bullets, DARK, GREEN, WHITE):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK
    bg.line.fill.background()
    spTree = slide.shapes._spTree
    sp = bg._element
    spTree.remove(sp)
    spTree.insert(2, sp)

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.06), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = GREEN
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.7), Inches(0.5), Inches(12), Inches(0.8))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = WHITE

    content = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(12), Inches(5.5))
    tf = content.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets[:8]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "•  " + b
        p.font.size = Pt(16)
        p.font.color.rgb = WHITE
        p.space_after = Pt(10)

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("⚙️ 설정")

    models = get_local_ollama_models()
    model_name = st.selectbox("모델", models, index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.25, 0.05)

    st.divider()
    st.subheader("🛠️ Skills Library")
    selected_skill = st.selectbox("Skill 선택", list(SKILLS.keys()))

    if selected_skill != "기본":
        st.markdown(f'<span class="skill-badge">{selected_skill}</span>', unsafe_allow_html=True)

    st.divider()
    uploaded_files = st.file_uploader(
        "📎 CSV / Excel / 문서 업로드", 
        accept_multiple_files=True, 
        type=['csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt', 'md']
    )

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_response = ""
        st.rerun()

    # Export
    if "last_response" in st.session_state and st.session_state.last_response:
        st.divider()
        st.subheader("📥 마지막 응답 Export")
        ts = datetime.now().strftime("%Y%m%d_%H%M")

        st.download_button("Markdown", st.session_state.last_response, 
                          f"VerifyAI_{ts}.md", "text/markdown", use_container_width=True)

        if st.button("DOCX 변환", use_container_width=True):
            doc = Document()
            doc.add_heading("베리파이 AI 분석 결과", 0)
            doc.add_paragraph(st.session_state.last_response)
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            st.download_button("DOCX 다운로드", bio.getvalue(), 
                              f"VerifyAI_Report_{ts}.docx", 
                              "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                              use_container_width=True)

        if st.button("PPTX 자동 생성", use_container_width=True):
            try:
                pptx_bytes = create_pptx_from_text(st.session_state.last_response, "베리파이 AI 분석 결과")
                st.download_button("PPTX 다운로드", pptx_bytes, f"VerifyAI_{ts}.pptx", 
                                  "application/vnd.openxmlformats-officedocument.presentationml.presentation", 
                                  use_container_width=True)
            except Exception as e:
                st.error(f"PPTX 오류: {e}")

# ================== SESSION ==================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# ================== CHAT UI ==================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🔎"
    with st.chat_message(msg["role"], avatar=avatar):
        css = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
        st.markdown(f'<div class="{css}">{msg["content"]}</div>', unsafe_allow_html=True)

# ================== INPUT ==================
if prompt := st.chat_input("분석 요청이나 질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🔎"):
        placeholder = st.empty()
        full_response = ""

        try:
            llm = ChatOllama(model=model_name, temperature=temperature, num_predict=8192)

            # 데이터 분석 강화: 실제 파일 분석 결과 주입
            file_context = analyze_uploaded_files(uploaded_files) if uploaded_files else ""

            skill_prompt = SKILLS.get(selected_skill, "")
            system_prompt = f"""{skill_prompt}

{file_context}

사용자가 요청한 분석을 정확하고 신뢰성 있게 수행한다.
결과는 Markdown으로 구조화해서 제시하며, <thinking> 태그로 사고 과정을 먼저 작성한다."""

            chat_history = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                chat_history.append({"role": m["role"], "content": m["content"]})

            chain = ChatPromptTemplate.from_messages(chat_history) | llm | StrOutputParser()
            response = chain.invoke({})

            placeholder.markdown(response)
            full_response = response

        except Exception as e:
            full_response = f"오류가 발생했습니다: {e}"
            placeholder.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response

        thinking, _ = extract_thinking(full_response)
        if thinking:
            with st.expander("💭 Chain of Thought"):
                st.markdown(thinking)
