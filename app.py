import streamlit as st
import pypdf
import google.generativeai as genai

# ---------------------------------------------------------
# 1. 페이지 레이아웃 및 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI PDF 요약 & 키워드 추출기",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI PDF 핵심 요약 & 키워드 추출기")
st.write("PDF 문서(전공 서적, 논문, 강의록 등)를 업로드하면 AI가 핵심 내용과 주요 키워드를 정리해 드립니다.")

# ---------------------------------------------------------
# 2. 사이드바 - API Key 입력 및 설정 옵션
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown("[👉 Gemini API Key 무료 발급받기](https://aistudio.google.com/)")
    
    st.divider()
    summary_length = st.select_slider(
        "요약 상세도 선택",
        options=["간단히 (3줄)", "보통 (5줄)", "상세히 (상세 요약)"],
        value="보통 (5줄)"
    )

# ---------------------------------------------------------
# 3. PDF에서 텍스트 추출하는 함수
# ---------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# ---------------------------------------------------------
# 4. 메인 화면 UI 및 분석 로직
# ---------------------------------------------------------
uploaded_file = st.file_uploader("요약할 PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    st.success(f"파일명: **{uploaded_file.name}** 업로드 성공!")
    
    # PDF 텍스트 추출
    with st.spinner("PDF에서 텍스트를 추출하는 중..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
    
    if not pdf_text.strip():
        st.error("PDF에서 텍스트를 추출하지 못했습니다. (이미지만 스캔된 PDF일 수 있습니다.)")
    else:
        st.info(f"문서 읽기 완료: 총 **{len(pdf_text):,}** 자의 글자를 추출했습니다.")
        
        # 추출한 텍스트 미리보기
        with st.expander("📄 추출된 원문 미리보기"):
            st.text_area("원문 텍스트", pdf_text, height=200)
            
        # AI 분석 버튼
        if st.button("🚀 AI 분석 시작하기", type="primary"):
            if not api_key:
                st.warning("⚠️ 왼쪽 사이드바에 Gemini API Key를 먼저 입력해주세요!")
            else:
                try:
                    # Gemini API 설정
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
너는 대학생의 학습을 돕는 전문 문서 분석 AI야. 
아래 제시된 문서 내용에서 핵심 내용을 요약하고 주요 키워드를 추출해줘.

[요약 조건]
- 요약 상세도: {summary_length}
- 핵심 내용 요약: 중요한 포인트를 명확하게 불렛 포인트(•)로 정리할 것.
- 주요 키워드: 문서를 대표하는 핵심 단어 5~8개를 '#키워드' 태그 형태로 목록화해줄 것.
- 핵심 한 줄 인사이트: 문서 전체의 주요 결론이나 핵심 메시지를 한 줄로 요약해줄 것.

[문서 내용]
{pdf_text[:12000]}
"""
                    
                    with st.spinner("AI가 문서를 읽고 요약/키워드를 분석하고 있습니다..."):
                        response = model.generate_content(prompt)
                        
                        st.markdown("---")
                        st.subheader("💡 분석 결과")
                        st.markdown(response.text)
                        
                        # 요약 결과 TXT 저장 기능
                        st.download_button(
                            label="📥 요약 결과 파일(.txt)로 저장하기",
                            data=response.text,
                            file_name=f"Summary_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
