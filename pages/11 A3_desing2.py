import streamlit as st
import toml
import pathlib
import json
from openai import OpenAI

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

# secrets.toml 파일 경로 설정 및 파일 읽기
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = toml.load(f)

# 여러 API 키 값 가져오기
api_keys = [secrets.get(f"api_key{i}") for i in range(1, 13) if secrets.get(f"api_key{i}")]

# 인공지능 설정
selected_api_key = api_keys[0]
client = OpenAI(api_key=selected_api_key)

# 성취기준 JSON 파일 경로 설정 및 파일 읽기
achievement_standards_path = pathlib.Path(__file__).parent.parent / "achievement_standards.json"
with open(achievement_standards_path, "r", encoding="utf-8") as f:
    achievement_standards = json.load(f)

# Streamlit 인터페이스
st.title("개념기반 탐구모형수업 설계하기")

# 주의 문구
st.warning("""
본 페이지는 서울특별시교육청 에듀테크선도교사 활동비용으로 운영되고 있습니다.
""")

# 초기 세션 상태 설정
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.details = []
    st.session_state.ai_recommendation = ""
    st.session_state.user_input = ""

def call_openai(prompt, model="gpt-4o-mini", max_tokens=500):
    try:
        with st.spinner("AI 의 대답을 기다리는 중입니다..."):
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return completion.choices[0].message.content
    except Exception as e:
        st.error(f"API 호출 실패: {e}")
        return ""

def show_previous_inputs():
    st.subheader("이전 단계에서 입력한 내용")
    for detail in st.session_state.details:
        st.write(detail)

# Step 1: 과목 선택
if st.session_state.step == 0:
    st.header("Step 1: 과목 선택")
    subject = st.selectbox("과목을 선택하세요:", ["사회", "과학"], key="subject")
    if st.button("다음 단계", key="next_step_0"):
        if subject:
            st.session_state.details.append(f"과목: {subject}")
            st.session_state.step += 1
            st.rerun()
        else:
            st.warning("과목을 선택하세요.")

# Step 2: 학년군 선택
elif st.session_state.step == 1:
    st.header("Step 2: 학년군 선택")
    show_previous_inputs()
    grade_group = st.selectbox("학년군을 선택하세요:", ["3~4학년", "5~6학년"], key="grade_group")
    if st.button("다음 단계", key="next_step_1"):
        if grade_group:
            st.session_state.details.append(f"학년군: {grade_group}")
            st.session_state.step += 1
            st.rerun()
        else:
            st.warning("학년군을 선택하세요.")

# Step 3: 성취기준 선택
elif st.session_state.step == 2:
    st.header("Step 3: 성취기준 선택")
    show_previous_inputs()
    grade_group = st.session_state.details[1].split(": ")[1]
    subject = st.session_state.details[0].split(": ")[1]
    topics = achievement_standards[grade_group][subject].keys()
    selected_topic = st.selectbox("주제를 선택하세요:", list(topics), key="selected_topic")

    standards = achievement_standards[grade_group][subject][selected_topic]
    selected_standard = st.selectbox("성취기준을 선택하세요:", standards, key="selected_standard")

    if st.button("다음 단계", key="next_step_2"):
        if selected_topic and selected_standard:
            st.session_state.details.append(f"주제: {selected_topic}")
            st.session_state.details.append(f"성취기준: {selected_standard}")
            st.session_state.step += 1
            st.rerun()
        else:
            st.warning("주제와 성취기준을 선택하세요.")

# Step 4: 개념 입력
elif st.session_state.step == 3:
    st.header("Step 4: 개념 입력")
    show_previous_inputs()
    grade_group = st.session_state.details[1].split(": ")[1]
    subject = st.session_state.details[0].split(": ")[1]
    selected_topic = st.session_state.details[2].split(": ")[1]
    selected_standard = st.session_state.details[3].split(": ")[1]

    if not st.session_state.ai_recommendation:
        st.session_state.user_input = st.text_input("개념을 입력하세요:", key="concept")
        if st.button("다음 단계", key="check_concept"):
            if st.session_state.user_input:
                prompt = f"주제: {selected_topic}\n성취기준: {selected_standard}\n이 주제와 성취기준에 맞는 관련된 개념 단어를 1개 제공해주세요. 목표 단어만 제공 서술어 및 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt)
                st.rerun()
            else:
                st.warning("개념을 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_input("개념을 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_concept"):
            st.session_state.details.append(f"개념: {st.session_state.user_input}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# Step 5: 단원 가르칠 내용 생성
elif st.session_state.step == 4:
    st.header("Step 5: 단원 가르칠 내용 생성")
    show_previous_inputs()
    unit_title = st.text_input("교과서 단원명을 입력하세요:", key="unit_title")
    concepts = st.text_input("대주제를 입력하세요 (3~4개 쉼표로 구분):", key="unit_concepts")
    
    selected_standard = st.session_state.details[3].split(": ")[1]
    ai_concept = st.session_state.details[4].split(": ")[1]

    if not st.session_state.ai_recommendation:
        if st.button("다음 단계", key="generate_unit"):
            if unit_title and concepts:
                prompt = f"성취기준: {selected_standard}\n개념: {ai_concept}\n이 성취기준과 개념에 맞는 가르쳐야 할 4개의 대주제를 제공해주세요. 4개의 대주제만 생성하고 별도의 서술어나 내용 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt, max_tokens=300)
                st.session_state.user_input = f"{concepts}"
                st.rerun()
            else:
                st.warning("단원 제목과 대주제를 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_input("대주제를 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_unit"):
            st.session_state.details.append(f"단원 제목: {unit_title}")
            st.session_state.details.append(f"단원 대주제: {st.session_state.user_input}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# Step 6: 단원 전체 일반화
elif st.session_state.step == 5:
    st.header("Step 6: 단원 전체 일반화")
    show_previous_inputs()
    selected_standard = st.session_state.details[3].split(": ")[1]
    ai_concept = st.session_state.details[4].split(": ")[1]

    if not st.session_state.ai_recommendation:
        st.session_state.user_input = st.text_area("단원을 통해 배우는 일반화 문장을 입력하세요:", key="generalization")
        if st.button("다음 단계", key="generate_generalization"):
            if st.session_state.user_input:
                prompt = f"성취기준: {selected_standard}\n개념: {ai_concept}\n이 성취기준과 개념에 맞는 일반화 문장을 제공해주세요. 서술어 및 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt, max_tokens=200)
                st.rerun()
            else:
                st.warning("일반화 문장을 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_area("일반화 문장을 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_generalization"):
            st.session_state.details.append(f"일반화 문장: {st.session_state.user_input}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# Step 7: 탐구 질문 만들기
elif st.session_state.step == 6:
    st.header("Step 7: 탐구 질문 만들기")
    show_previous_inputs()
    selected_standard = st.session_state.details[3].split(": ")[1]
    ai_concept = st.session_state.details[4].split(": ")[1]

    if not st.session_state.ai_recommendation:
        factual_question = st.text_input("사실적 질문을 입력하세요:", key="factual_question")
        conceptual_question = st.text_input("개념적 질문을 입력하세요:", key="conceptual_question")
        debatable_question = st.text_input("논쟁적 질문을 입력하세요:", key="debatable_question")
        if st.button("다음 단계", key="generate_questions"):
            if factual_question and conceptual_question and debatable_question:
                prompt = f"성취기준: {selected_standard}\n개념: {ai_concept}\n이 성취기준과 개념에 맞는 사실적 질문, 개념적 질문, 논쟁적 질문을 각각 1개씩 제공해주세요. 서술어 및 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt, max_tokens=300)
                st.session_state.user_input = f"사실적 질문: {factual_question}\n개념적 질문: {conceptual_question}\n논쟁적 질문: {debatable_question}"
                st.rerun()
            else:
                st.warning("모든 질문을 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_area("질문을 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_questions"):
            questions = st.session_state.user_input.split('\n')
            st.session_state.details.append(f"사실적 질문: {questions[0].split(': ')[1]}")
            st.session_state.details.append(f"개념적 질문: {questions[1].split(': ')[1]}")
            st.session_state.details.append(f"논쟁적 질문: {questions[2].split(': ')[1]}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# Step 8: 학생들이 배울 지식과 기능 작성
elif st.session_state.step == 7:
    st.header("Step 8: 학생들이 배울 지식과 기능 작성")
    show_previous_inputs()
    selected_standard = st.session_state.details[3].split(": ")[1]
    ai_concept = st.session_state.details[4].split(": ")[1]

    if not st.session_state.ai_recommendation:
        st.session_state.user_input = st.text_area("대목차 별 지식과 기능을 입력하세요:", key="knowledge")
        if st.button("다음 단계", key="generate_knowledge"):
            if st.session_state.user_input:
                prompt = f"성취기준: {selected_standard}\n개념: {ai_concept}\n이 성취기준과 개념에 맞는 지식과 기능을 4가지 제공해주세요. 서술어 및 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt, max_tokens=300)
                st.rerun()
            else:
                st.warning("대목차 별 지식과 기능을 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_area("지식과 기능을 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_knowledge"):
            st.session_state.details.append(f"지식과 기능: {st.session_state.user_input}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# Step 9: 평가 루브릭 GRASP 작성
elif st.session_state.step == 8:
    st.header("Step 9: 평가 루브릭 GRASP 작성")
    show_previous_inputs()
    selected_standard = st.session_state.details[3].split(": ")[1]
    ai_concept = st.session_state.details[4].split(": ")[1]

    if not st.session_state.ai_recommendation:
        st.session_state.user_input = st.text_area("평가 루브릭 GRASP를 입력하세요:", key="rubric")
        if st.button("다음 단계", key="generate_rubric"):
            if st.session_state.user_input:
                prompt = f"성취기준: {selected_standard}\n개념: {ai_concept}\n이 성취기준과 개념에 맞는 평가 루브릭 GRASP를 제공해주세요. 서술어 및 설명 금지."
                st.session_state.ai_recommendation = call_openai(prompt, max_tokens=500)
                st.rerun()
            else:
                st.warning("평가 루브릭 GRASP를 입력하세요.")
    else:
        st.write(f"AI의 추천: {st.session_state.ai_recommendation}")
        st.session_state.user_input = st.text_area("평가 루브릭을 수정하거나 그대로 사용하세요:", st.session_state.user_input)
        if st.button("확인하고 다음 단계로", key="confirm_rubric"):
            st.session_state.details.append(f"평가 루브릭: {st.session_state.user_input}")
            st.session_state.ai_recommendation = ""
            st.session_state.user_input = ""
            st.session_state.step += 1
            st.rerun()

# 마지막 단계: 결과 다운로드
if st.session_state.step == 9:
    st.header("최종 결과")
    combined_results = "\n\n".join(st.session_state.details)
    final_result = f"최종 결과:\n\n{combined_results}"
    st.text_area("최종 결과", final_result, height=300)
    st.download_button("결과 다운로드", data=final_result, file_name="results.txt", mime="text/plain")

if st.button("다시 시작하기", key="restart"):
    st.session_state.clear()
    st.rerun()

st.markdown("제작자: 서울특별시교육청융합과학교육원 정용석")