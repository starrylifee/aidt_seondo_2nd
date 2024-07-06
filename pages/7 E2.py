import streamlit as st
import random
import toml
import pathlib
from openai import OpenAI

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# 여러 API 키 값 가져오기
api_keys = [secrets.get(f"api_key{i}") for i in range(1, 13)]

# 랜덤하게 API 키를 선택하여 OpenAI 클라이언트 초기화
selected_api_key = random.choice(api_keys)
client = OpenAI(api_key=selected_api_key)

# 페르소나 특성 정의
persona_traits = ["집중력", "기기친숙도", "구두언어 사용 빈도", "과제집착력", "학업스트레스", "자기조절", "가정환경", "학업성취도", "메타인지"]

# Streamlit 앱 인터페이스 구성
st.title("학생 페르소나 하이터치 게임 🎨")
st.write("학생의 페르소나가 무작위로 생성됩니다. 가지고 있느냐 AIDT 카드를 이용해 하이터치를 시도해보세요.")

# 입력 값 검증 및 이미지 생성
if st.button("이미지 생성하기"):
    # 무작위로 3개의 페르소나 특성 선택
    selected_traits = random.sample(persona_traits, 3)
    selected_gauges = {trait: random.choice([1, 2, 3, 4, 5]) for trait in selected_traits}

    st.write("선택된 페르소나 특성 및 게이지:")
    for trait, gauge in selected_gauges.items():
        st.write(f"{trait}: {gauge}")

    # 프롬프트 구성
    final_description = ", ".join([f"{trait} {gauge} out of 5" for trait, gauge in selected_gauges.items()])
    prompt = f"Caricature of an elementary school student with the following traits: {final_description}"

    # DALL-E API 호출 시도
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # 생성된 이미지 출력
        st.image(image_url, caption="생성된 학생 페르소나 이미지")

        # 이미지 다운로드 링크 제공
        st.markdown(f"[이미지 다운로드]({image_url})")

    except Exception as e:
        st.error(f"이미지 생성에 실패했습니다: {e}")

# 세션 초기화 버튼
if st.button("다시 시작하기"):
    st.experimental_rerun()
