import streamlit as st
import pandas as pd
import random
import toml
import pathlib
import google.generativeai as genai

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

# 체크리스트 항목 구조화
checklist = {
    "삶과 맥락 & 수업 및 학습자 분석": [
        "학생의 삶과 연계한 학습내용을 평가하도록 설계되었는가?",
        "학습 과정 중 핵심 역량을 평가하고 있는가?",
        "평가가 실생활의 맥락과 연계되거나 적용될 수 있도록 설계되었는가?",
        "학생의 사전 지식 분석을 위한 평가가 설계되었는가?"
    ],
    "맞춤형 & 성찰 기회 제공": [
        "개인별 학습 수준에 맞는 맞춤형 평가 문항을 설계하였는가?",
        "개인 학습 과정별 맞춤형 평가 문항을 설계하였는가?",
        "융합적 사고와 창의적 문제해결력이 요구되는 평가인가?",
        "학생 개별 평가를 통한 맞춤형 피드백이 제공되는가?"
    ],
    "지식 구성 & 상호작용 협력": [
        "학생의 상호작용이 이루어지는 평가 문항을 설계하였는가?",
        "평가를 통해 협력을 위한 개별 학력 향상도가 나타나는가?",
        "학생이 능동적으로 참여하며 협력이 이루어지는 평가인가?",
        "학생 협력 활동을 돕는 맞춤형 피드백이 제공되는가?"
    ]
}

# 수업안 샘플
sample_lessons = [
    """1) AI 디지털교과서 기반 선수학습
진단평가 학생의 단원 출발점 진단
2) 분수 계산을 위해 원리 기반 방법의 이해 AI 디지털교과서 형성평가
3) 형성평가 결과 분석으로 성취수준 도달점 확인 AI 디지털교과서 제공 개인별 맞춤형 콘텐츠 해결 상황에서 디딤이 필요한 학습자에 대한 교사의 일대일 피드백
4) AI 디지털교과서 기반 성취도평가 일정 성취수준 도달 여부 확인
5) 도달 여부에 따른 맞춤형 수행 활동 제공 디딤 콘텐츠(느린 학습자) 및 도약 프로젝트 활동 제공 및 교사 평가/피드백
6) 단원평가 통한 배움 내용 확인""",
    
    """1) 우리 몸의 다양한 기관에 대한 주요 용어 확인 AI 챗봇 활용
2) 용어 이해하기 AI 디지털교과서 기반 인체 기관 내 주요 부분에 대한 조사 후 교사 피드백
3) 개념 공유하기 조사 내용 동료 학생과 공유하고 피드백 주고받기
4) 주제 정하기 AI 디지털교과서 데이터 기반 모둠 구성한 후 인체 기관 간 연관성이 드러나는 발표 자료 조직하고 교사 및 동료 피드백 받기
5) 발표 내용 구성하기 동영상으로 구성할 발표 내용 모둠별 구성하고 동료 피드백 주고받기
6) 발표하기 인체 내 두세 기관 간 연관성이 드러나는 인체 기관 발표하기 최종 평가""",

    """1) 한국 문화 관련 주제 선정 브레인스토밍하기 디딤 콘텐츠(느린 학습자) 및 도약 프로젝트 활동 제공 및 교사 평가/피드백
2) 세부 주제 관련 자료 조사하기 AI 챗봇 활용하기
3) 영어 대본 작성 후 피드백 받기 AI 디지털교과서로부터 쓰기 피드백 받기(영작)
4) 영어 말하기 발표 개별 연습하기 AI 디지털교과서로부터 말하기 피드백 받기(녹음 및 발음 교정, 개별 맞춤 학습 및 보충심화 과제 제시) 느린 학습자에 대한 교사 피드백
5) 영어 말하기 발표 모둠 연습하기 모둠원 피드백
6) 영어 말하기 발표하기 교사 평가 및 피드백""",

    """1) 주제 정하기 모둠원 협력 - AI 챗봇 활용하기
2) 대본 작성하기 교사가 제작한 챗봇 활용 혹은 AI 디지털교과서로부터 쓰기 피드백 받기
3) 대본 작성 후 피드백 받기 완성도가 높아 챗봇이 통과시킨 학생은 교사의 피드백 제공
4) 짝지어 발표 연습하기 짝에게 평가 받기(평가 기준을 근거로 감점 요인에 대한 동료 피드백)
5) 발표하기 교사의 채점 및 감점 요인에 대한 피드백 제공
6) 발표하기 재도전 최종 평가""",

    """1) 고대 문명의 주요 특징 조사: 인터넷을 통한 자료 검색 및 학술 논문 참조
2) 각 문명 간의 차이점과 유사점 비교 분석: 협업 도구를 사용하여 모둠별 비교 분석
3) 팀별로 문명에 대한 발표 자료 준비: 프레젠테이션 소프트웨어 활용
4) 발표 후 교사와 학생들로부터 피드백 받기: 실시간 피드백 도구 사용
5) 각 팀의 발표 내용을 바탕으로 종합 토론: 토론을 위한 온라인 게시판 활용
6) 최종 보고서 작성 및 제출: 클라우드 기반 문서 도구를 통해 개별 보고서 작성 및 제출, 교사는 개별 피드백 제공""",

    """1) 소설 속 인물 분석 및 성격 이해: 디지털 독서 플랫폼 활용하여 소설 읽기
2) 인물 간의 관계도 작성: 디지털 마인드맵 도구 사용
3) 인물의 행동 동기와 변화 분석: 학습 관리 시스템을 통해 토론 게시판에서 토론
4) 인물 분석을 바탕으로 창작 글쓰기: 워드 프로세서 사용
5) 작성한 글에 대한 동료 피드백: 협업 문서 도구의 댓글 기능을 활용한 동료 피드백
6) 최종 작품 발표 및 교사 평가: 비디오 발표 도구를 통해 발표, 교사는 루브릭을 사용해 평가 및 피드백 제공""",

    """1) 현대 미술 작품 감상 및 비평: 디지털 갤러리 및 온라인 미술관 활용
2) 감상한 작품의 특징과 기법 분석: 온라인 포트폴리오 도구 사용하여 분석 결과 공유
3) 작품에 대한 개인의 느낌과 해석 공유: 협업 도구 활용
4) 미술사적 배경과 작품의 상관관계 조사: 온라인 백과사전 및 학술 자료 활용
5) 팀별로 작품에 대한 비평서 작성: 협업 문서 도구에서 협업하여 비평서 작성
6) 비평서 발표 및 교사 피드백: 온라인 회의 도구 사용, 발표 후 교사와 동료로부터 피드백""",

    """1) 지역 사회의 환경 문제 조사: 지역 신문 및 환경 단체 웹사이트 참조
2) 문제 해결을 위한 아이디어 브레인스토밍: 디지털 화이트보드 도구 활용
3) 제안된 아이디어를 바탕으로 프로젝트 계획 수립: 프로젝트 관리 도구 사용
4) 팀별로 프로젝트 실행 및 진행 상황 공유: 협업 도구 및 진행 상황 트래킹
5) 프로젝트 결과물 발표 및 피드백: 프레젠테이션 도구 활용, 교사와 동료 피드백
6) 최종 보고서 작성 및 교사 평가: 클라우드 문서 도구를 통해 개별 보고서 작성 및 교사 피드백""",

    """1) 인공지능의 역사와 발전 과정 조사: 온라인 강의 플랫폼 활용
2) 현재 인공지능 기술의 응용 분야 탐구: 최신 학술 논문 및 기술 블로그 참조
3) 팀별로 특정 응용 분야에 대한 연구 발표: 데이터 시각화 도구 사용
4) 발표 후 교사와 학생들로부터 피드백 받기: 실시간 퀴즈 및 피드백 도구 사용
5) 인공지능 기술의 미래 전망에 대한 토론: 디지털 토론 게시판 활용
6) 최종 보고서 작성 및 제출: 협업 문서 도구를 통해 최종 보고서 작성, 개별 피드백 제공""",

    """1) 전 세계 다양한 음악 장르 탐구: 음악 스트리밍 서비스 활용
2) 각 장르의 특징과 대표 아티스트 조사: 온라인 백과사전 및 음악 블로그 참조
3) 팀별로 특정 음악 장르에 대한 발표 자료 준비: 프레젠테이션 도구 활용
4) 발표 후 교사와 학생들로부터 피드백 받기: 실시간 피드백 도구 사용
5) 각 팀의 발표 내용을 바탕으로 음악 토론: 온라인 토론 플랫폼 활용
6) 최종 보고서 작성 및 제출: 클라우드 문서 도구를 통해 최종 보고서 작성, 교사 평가 및 피드백 제공"""
]

# 사이드바에 API 키 입력란 추가 및 안내 문구
with st.sidebar:
    user_api_key = st.text_input("API 키를 입력해주세요:", type="password")
    st.write("""
    💡 [API 키 발급 받기](https://aistudio.google.com/app/apikey)
    """)

# API 키 설정 함수
def configure_api(api_key):
    genai.configure(api_key=api_key)

# 앱 제목
st.title("개별 및 협력학습 설계 시 과정중심평가와 성찰계획 수립을 위한 체크리스트")

if user_api_key:
    configure_api(user_api_key)
else:
    st.error("API 키를 입력해주세요.")

# 수업안 랜덤 선택 버튼
if st.button("랜덤 뽑기"):
    selected_lesson = random.choice(sample_lessons)
    st.session_state.selected_lesson = selected_lesson

# 선택된 수업안 표시
if "selected_lesson" in st.session_state:
    st.header("평가할 수업안")
    st.write(st.session_state.selected_lesson)

    # 체크리스트 생성
    st.header("체크리스트")
    checklist_responses = {}

    for category, items in checklist.items():
        st.subheader(category)
        for item in items:
            checklist_responses[item] = st.slider(item, 1, 5)

    # 모든 체크리스트 항목을 선택하지 않으면 다음 단계로 진행할 수 없음
    if all(value > 0 for value in checklist_responses.values()):
        if st.button("결과 저장"):
            results_df = pd.DataFrame.from_dict(checklist_responses, orient='index', columns=['평가'])
            st.write("평가 결과:")
            st.dataframe(results_df)
            st.success("평가 결과가 저장되었습니다.")

        if st.button("AI 검토"):
            with st.spinner("AI 검토 중입니다. 잠시만 기다려주세요..."):
                prompt = (
                    f"수업안:\n{st.session_state.selected_lesson}\n\n"
                    "체크리스트 평가 결과:\n" +
                    "\n".join([f"{item}: {response}" for item, response in checklist_responses.items()]) +
                    "\n\n확정된 수업안에 대해 교사가 체크리스트로 평가한 결과입니다. 각 체크리스트는 1점부터 5점까지 이루어져 있으며, 1점은 가장 낮은 점수입니다. "
                    "교사가 실시한 평가 결과를 수업안과 비교하여 비판적으로 인공지능으로 검토해주세요. 교사가 준 점수가 옳지 않다고 여기면 점검해 주고 이유를 꼭 이야기해 주세요. 예를 들어 낮은 점수를 주었는데, 수업안에 반영되어 있는 항목이라면 어느 부분을 살펴본 후 교사가 부여한 점수를 수정하라고 말해주세요."
                )
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 3000,
                    }
                )
                try:
                    response = model.generate_content([prompt])
                    ai_feedback = response.text
                except Exception as e:
                    st.error(f"API 호출 실패: {e}")
                    ai_feedback = "생성 실패"

                st.text_area("AI 검토 피드백", ai_feedback, height=300)

        if st.button("다시 시작하기", key="restart"):
            st.session_state.clear()
            st.experimental_rerun()
    else:
        st.warning("모든 체크리스트 항목을 선택해야 합니다.")
else:
    st.write("랜덤 뽑기를 눌러 수업안을 선택하세요.")
