import google.generativeai as genai
import streamlit as st

# GitHub 아이콘 및 기타 UI 요소 숨기기
hide_github_icon = """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

# few-shot 프롬프트 구성 함수
def try_generate_content(api_key, prompt_parts):
    # API 키를 설정
    genai.configure(api_key=api_key)
    
    # 설정된 모델
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        },
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    )
    try:
        # 콘텐츠 생성 시도
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        # 예외 발생시 None 반환
        print(f"API 호출 실패: {e}")
        return None

# 스트림릿 앱 인터페이스 구성
st.title("연구계획서 작성 도우미 📝")

# 사이드바에 API 키 입력란 추가 및 안내 문구
with st.sidebar:
    user_api_key = st.text_input("API 키를 입력해주세요:", type="password")
    st.write("💡 [API 키 발급 받기](https://aistudio.google.com/app/apikey)")

# API 키 설정 함수
def configure_api(api_key):
    genai.configure(api_key=api_key)

# API 키 유효성 검사 및 설정
if user_api_key:
    configure_api(user_api_key)
else:
    st.error("API 키를 입력해주세요.")

# 연구 주제 입력 단계 관리
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.details = []

left_col, right_col = st.columns(2)

with left_col:
    if st.session_state.step == 0:
        research_topic = st.text_input("연구 주제를 입력하세요 ✏️:")
        if st.button("다음 단계", key="next_step_0"):
            if research_topic:
                st.session_state.details.append(f"연구 주제: {research_topic}")
                st.session_state.step += 1

    if st.session_state.step == 1:
        if "independent_variable_options" not in st.session_state:
            with st.spinner("독립변인 선택지를 생성 중입니다..."):
                prompt = f"연구 주제: {st.session_state.details[0]}\n독립변인에 대한 세 가지 선택지를 각각 1줄로 제공해주세요."
                try:
                    response = try_generate_content(user_api_key, [prompt])
                    st.session_state.independent_variable_options = response.split('\n')
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    st.session_state.independent_variable_options = []

        option = st.radio("독립변인 선택지", st.session_state.independent_variable_options + ["직접 입력"], key="independent_variable")
        if option == "직접 입력":
            option = st.text_input("독립변인을 입력하세요:", key="independent_variable_input")

        if st.button("다음 단계", key="next_step_1"):
            st.session_state.details.append(f"독립변인: {option}")
            st.session_state.step += 1

    if st.session_state.step == 2:
        if "dependent_variable_options" not in st.session_state:
            with st.spinner("종속변인 선택지를 생성 중입니다..."):
                prompt = f"연구 주제: {st.session_state.details[0]}\n독립변인: {st.session_state.details[1]}\n종속변인에 대한 세 가지 선택지를 각각 1줄로 제공해주세요."
                try:
                    response = try_generate_content(user_api_key, [prompt])
                    st.session_state.dependent_variable_options = response.split('\n')
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    st.session_state.dependent_variable_options = []

        option = st.radio("종속변인 선택지", st.session_state.dependent_variable_options + ["직접 입력"], key="dependent_variable")
        if option == "직접 입력":
            option = st.text_input("종속변인을 입력하세요:", key="dependent_variable_input")

        if st.button("다음 단계", key="next_step_2"):
            st.session_state.details.append(f"종속변인: {option}")
            st.session_state.step += 1

    if st.session_state.step == 3:
        if "research_subject_options" not in st.session_state:
            with st.spinner("연구대상 선택지를 생성 중입니다..."):
                prompt = f"연구 주제: {st.session_state.details[0]}\n독립변인: {st.session_state.details[1]}\n종속변인: {st.session_state.details[2]}\n연구대상에 대한 세 가지 선택지를 각각 1줄로 제공해주세요."
                try:
                    response = try_generate_content(user_api_key, [prompt])
                    st.session_state.research_subject_options = response.split('\n')
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    st.session_state.research_subject_options = []

        option = st.radio("연구대상 선택지", st.session_state.research_subject_options + ["직접 입력"], key="research_subject")
        if option == "직접 입력":
            option = st.text_input("연구대상을 입력하세요:", key="research_subject_input")

        if st.button("다음 단계", key="next_step_3"):
            st.session_state.details.append(f"연구대상: {option}")
            st.session_state.step += 1

    if st.session_state.step == 4:
        if "research_method_options" not in st.session_state:
            with st.spinner("연구방법 선택지를 생성 중입니다..."):
                prompt = f"연구 주제: {st.session_state.details[0]}\n독립변인: {st.session_state.details[1]}\n종속변인: {st.session_state.details[2]}\n연구대상: {st.session_state.details[3]}\n연구방법에 대한 세 가지 선택지를 각각 1줄로 제공해주세요."
                try:
                    response = try_generate_content(user_api_key, [prompt])
                    st.session_state.research_method_options = response.split('\n')
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    st.session_state.research_method_options = []

        option = st.radio("연구방법 선택지", st.session_state.research_method_options + ["직접 입력"], key="research_method")
        if option == "직접 입력":
            option = st.text_input("연구방법을 입력하세요:", key="research_method_input")

        if st.button("다음 단계", key="next_step_4"):
            st.session_state.details.append(f"연구방법: {option}")
            st.session_state.step += 1

    if st.session_state.step == 5:
        if "data_collection_method_options" not in st.session_state:
            with st.spinner("데이터 수집 방법 선택지를 생성 중입니다..."):
                prompt = f"연구 주제: {st.session_state.details[0]}\n독립변인: {st.session_state.details[1]}\n종속변인: {st.session_state.details[2]}\n연구대상: {st.session_state.details[3]}\n연구방법: {st.session_state.details[4]}\n데이터 수집 방법에 대한 세 가지 선택지를 각각 1줄로 제공해주세요."
                try:
                    response = try_generate_content(user_api_key, [prompt])
                    st.session_state.data_collection_method_options = response.split('\n')
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    st.session_state.data_collection_method_options = []

        option = st.radio("데이터 수집 방법 선택지", st.session_state.data_collection_method_options + ["직접 입력"], key="data_collection_method")
        if option == "직접 입력":
            option = st.text_input("데이터 수집 방법을 입력하세요:", key="data_collection_method_input")

        if st.button("다음 단계", key="next_step_5"):
            st.session_state.details.append(f"데이터 수집 방법: {option}")
            st.session_state.step += 1

with right_col:
    st.write("현재 입력 내용:")
    for detail in st.session_state.details:
        st.write(detail)

# 연구계획서 상세보기 생성 및 출력
if st.session_state.step == 6:
    if st.button("연구계획서 상세보기", key="generate_plan"):
        with st.spinner("연구계획서를 생성 중입니다. 잠시만 기다려주세요..."):
            prompt = "다음 연구계획서의 상세보기를 작성해주세요. 연구 계획의 장점을 3가지 알려주세요. 연구 수행 전 연구자가 추가로 고려야해할 점을 1가지 알려주세요.:\n\n" + "\n".join(st.session_state.details)
            try:
                response = try_generate_content(user_api_key, [prompt])
                research_plan = response if response else "생성 실패"
            except Exception as e:
                st.error(f"API 호출 실패: {e}")
                research_plan = "생성 실패"
            
            st.text_area("연구계획서 상세보기", research_plan, height=300)
            st.download_button("연구계획서 다운로드", data=research_plan, file_name="research_plan.txt", mime="text/plain")

if st.button("다시 시작하기", key="restart"):
    st.session_state.clear()
    st.rerun()
