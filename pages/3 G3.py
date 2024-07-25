import streamlit as st
import google.generativeai as genai
import toml
import pathlib

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

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기 (UTF-8 인코딩으로)
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = toml.load(f)

# 여러 API 키 값 가져오기
api_keys = [secrets.get(f"gemini_api_key{i}") for i in range(1, 13) if secrets.get(f"gemini_api_key{i}")]

# 인공지능 설정
selected_api_key = api_keys[0]
genai.configure(api_key=selected_api_key)

# Streamlit 인터페이스
st.title("연구계획서 작성 도우미 📝")

# 주의 문구
st.warning("""
⚠️ **주의:** 본 페이지는 개인의 API 키를 사용하고 있으므로 API 한도 초과에 따라 작동이 일정 기간 멈출 수 있습니다.
계속 사용을 원하시는 분은 [G3 (API 입력) 페이지](https://aidt-seondo-2nd.streamlit.app/G3_(API%EC%9E%85%EB%A0%A5))를 참고해주세요.
""")

# 연구 주제 입력
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
                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config={
                                                  "temperature": 0.7,
                                                  "max_output_tokens": 150,
                                              })
                try:
                    response = model.generate_content([prompt])
                    st.session_state.independent_variable_options = response.text.split('\n')
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
                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config={
                                                  "temperature": 0.7,
                                                  "max_output_tokens": 150,
                                              })
                try:
                    response = model.generate_content([prompt])
                    st.session_state.dependent_variable_options = response.text.split('\n')
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
                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config={
                                                  "temperature": 0.7,
                                                  "max_output_tokens": 150,
                                              })
                try:
                    response = model.generate_content([prompt])
                    st.session_state.research_subject_options = response.text.split('\n')
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
                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config={
                                                  "temperature": 0.7,
                                                  "max_output_tokens": 150,
                                              })
                try:
                    response = model.generate_content([prompt])
                    st.session_state.research_method_options = response.text.split('\n')
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
                model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                              generation_config={
                                                  "temperature": 0.7,
                                                  "max_output_tokens": 150,
                                              })
                try:
                    response = model.generate_content([prompt])
                    st.session_state.data_collection_method_options = response.text.split('\n')
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
        with st.spinner("연구계획서를 생성 중입니다..."):
            prompt = "다음 연구계획서의 상세보기를 작성해주세요. 연구 계획의 장점을 3가지 알려주세요. 연구 수행 전 연구자가 추가로 고려해야 할 점을 1가지 알려주세요.:\n\n" + "\n".join(st.session_state.details)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                          generation_config={
                                              "temperature": 0.7,
                                              "max_output_tokens": 3000,
                                          })
            try:
                response = model.generate_content([prompt])
                research_plan = response.text
            except Exception as e:
                st.error(f"API 호출 실패: {e}")
                research_plan = "생성 실패"
            
            st.text_area("연구계획서 상세보기", research_plan, height=300)
            st.download_button("연구계획서 다운로드", data=research_plan, file_name="research_plan.txt", mime="text/plain")

if st.button("다시 시작하기", key="restart"):
    st.session_state.clear()
    st.rerun()
