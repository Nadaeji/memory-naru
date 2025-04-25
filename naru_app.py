
import streamlit as st
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# 페이지 설정
st.set_page_config(page_title="기억 나루", page_icon="🌿", layout="centered")

# 키워드 데이터 로딩
keywords_df = pd.read_csv("memory_keywords.csv")
memory_keywords = defaultdict(list)
for _, row in keywords_df.iterrows():
    memory_keywords[row["category"]].append(row["keyword"])

# 회상 흐름 및 감정 목록
memory_flow = ["오늘", "이번 주", "최근 명절/행사", "청년기", "중고등학교", "초등학교", "어린 시절/유아기"]
emotions = [
    "😊 기뻤어요", "🥰 감동적이었어요", "😢 슬펐어요", "😠 화났어요",
    "😶 아무 감정이 없었어요", "🤔 복잡했어요", "😨 불안했어요",
    "🤗 편안했어요", "🔒 말하고 싶지 않아요"
]
templates = [
    "{}에 무슨 일이 있었는지 기억나?",
    "{} 때 어떤 기분이 들었는지 말해줄래?",
    "{}을 생각하면 가장 먼저 떠오르는 장면이 뭐야?",
    "{} 때 가장 기억에 남는 사람이 있었어?",
    "{}에 있었던 일을 지금 누군가에게 설명해준다면 뭐라고 말할까?"
]

# 세션 상태 초기화
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "question" not in st.session_state:
    st.session_state.question = ""
if "category" not in st.session_state:
    st.session_state.category = ""
if "emotion_stats" not in st.session_state:
    st.session_state.emotion_stats = defaultdict(int)
if "history" not in st.session_state:
    st.session_state.history = []

# 이름 입력
st.title("🌿 기억 나루")
if "username" not in st.session_state:
    name = st.text_input("너의 이름을 알려줘 🌱", "")
    if name:
        st.session_state.username = name
        st.rerun()
    st.stop()

if "started" not in st.session_state:
    with st.chat_message("나루"):
        st.markdown(f"""
안녕! 나는 **나루**야 😊  
기억을 함께 떠올리는 너의 말동무 친구야.  
처음엔 최근 기억부터 천천히 같이 걸어볼 거야.  
기억이 잘 안 나거나, 말하고 싶지 않은 건 그냥 건너뛰어도 돼.  
그럼, 시작해볼까 {st.session_state.username}아? 🌷  
""")
    if st.button("🌿 기억 산책 시작하기"):
        st.session_state.started = True
        st.rerun()
    st.stop()

# 현재 질문 구성
if st.session_state.question == "":
    category = memory_flow[st.session_state.stage]
    keyword = random.choice(memory_keywords[category])
    template = random.choice(templates)
    question = template.format(keyword)
    st.session_state.category = category
    st.session_state.question = question

st.markdown(f"#### 🔖 회상 카테고리: *{st.session_state.category}*")
st.markdown(f"### 💬 질문: {st.session_state.question}")

# 1차 분기: 기억 유무 확인
remember = st.radio("🔹 이 질문에 대해 어떻게 느꼈어?", [
    "1. 기억나!", "2. 잘 기억 안 나", "3. 말하고 싶지 않아", "4. 그만할래"
])

if remember == "4. 그만할래":
    st.success(f"{st.session_state.username}아, 오늘도 수고 많았어. 푹 쉬어! 💚")
    st.stop()

elif remember in ["2. 잘 기억 안 나", "3. 말하고 싶지 않아"]:
    st.info("다음 질문으로 넘어갈게 🌱")
    st.session_state.question = ""
    st.session_state.stage = (st.session_state.stage + 1) % len(memory_flow)
    st.rerun()

# 2차 입력: 사용자 자유 응답
user_answer = st.text_area("📝 기억이 떠오른다면 이야기해줘", "")

# 3차 선택: 감정 태그
emotion = st.radio("💛 그때 마음은 어땠어?", emotions, horizontal=True)

# 제출 처리
if st.button("➡️ 다음 질문으로 넘어가기"):
    now = datetime.now()
    log = {
        "timestamp": now.isoformat(),
        "user": st.session_state.username,
        "category": st.session_state.category,
        "question": st.session_state.question,
        "ai_answer": "",  # 향후 LLM 반영 가능
        "user_answer": user_answer,
        "emotion": emotion
    }
    st.session_state.history.append(log)
    st.session_state.emotion_stats[emotion] += 1

    # 나루 응답
    responses = [
        "음~ 그런 일이 있었구나. 이야기해줘서 고마워!",
        "그 기억, 나랑 함께 나눠줘서 참 따뜻했어.",
        "듣고 있으니까 괜히 마음이 몽글해졌어.",
        "그땐 정말 소중했겠다. 나도 미소 지어졌어."
    ]
    with st.chat_message("나루"):
        st.markdown(f"{random.choice(responses)} {st.session_state.username}이는 어땠어?")

    # 저장
    df = pd.DataFrame([log])
    try:
        df.to_csv("workspace/memory_log.csv", mode="x", index=False, encoding="utf-8")
    except FileExistsError:
        df.to_csv("workspace/memory_log.csv", mode="a", header=False, index=False, encoding="utf-8")

    st.session_state.question = ""
    st.session_state.stage = (st.session_state.stage + 1) % len(memory_flow)
    st.rerun()

# 감정 리포트 시각화
if st.button("🎁 감정 리포트 마무리 보기"):
    st.markdown("## 📊 오늘의 감정 요약")
    today = datetime.now().strftime("%Y-%m-%d")
    report_row = {"날짜": today}
    report_row.update(st.session_state.emotion_stats)

    try:
        pd.DataFrame([report_row]).to_csv("workspace/emotion_report_log.csv", mode="x", index=False, encoding="utf-8")
    except FileExistsError:
        pd.DataFrame([report_row]).to_csv("workspace/emotion_report_log.csv", mode="a", index=False, header=False, encoding="utf-8")

    fig, ax = plt.subplots()
    ax.bar(st.session_state.emotion_stats.keys(), st.session_state.emotion_stats.values(), color="mediumseagreen")
    plt.xticks(rotation=45)
    plt.title("오늘의 감정 빈도")
    st.pyplot(fig)

    st.success("💚 오늘의 감정 회상 리포트가 저장되었어요!")
