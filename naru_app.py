
import pandas as pd
import random
from collections import defaultdict
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="기억 나루", page_icon="🌿", layout="centered")

keywords_df = pd.read_csv("memory_keywords.csv")
memory_keywords = defaultdict(list)
for _, row in keywords_df.iterrows():
    memory_keywords[row["category"]].append(row["keyword"])

memory_flow = [
    "오늘", "이번 주", "최근 명절/행사",
    "청년기", "중고등학교", "초등학교", "어린 시절/유아기"
]

emotions = [
    "😊 기뻤어요", "🥰 감동적이었어요", "😢 슬펐어요", "😠 화났어요",
    "😶 아무 감정이 없었어요", "🤔 복잡했어요", "😨 불안했어요",
    "🤗 편안했어요", "🔒 말하고 싶지 않아요"
]

if "emotion_stats" not in st.session_state:
    st.session_state.emotion_stats = defaultdict(int)
if "stage_index" not in st.session_state:
    st.session_state.stage_index = 0
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🌿 기억 나루")
st.markdown("###### 감성 회상 기반 인지 자극 친구, 나루와 함께해요")

if "username" not in st.session_state:
    user_name = st.text_input("당신의 이름을 알려주세요 ✨", "")
    if user_name:
        st.session_state.username = user_name
        st.rerun()
    st.stop()

if "started" not in st.session_state:
    with st.chat_message("나루"):
        st.markdown(f'''
안녕! 나는 **나루**야 😊  
기억을 함께 떠올리고, 마음을 같이 나눌 수 있는 너의 말동무 친구야.  
처음엔 최근 기억부터 천천히 같이 걸어볼 거야.  
기억이 잘 안 나거나, 말하고 싶지 않은 건 그냥 건너뛰어도 괜찮아.  
그럼, 시작해볼까 {st.session_state.username}아? 🌷  
''')
    if st.button("🌿 기억 산책 시작하기"):
        st.session_state.started = True
        st.rerun()
    st.stop()

stage = memory_flow[st.session_state.stage_index]
keywords = memory_keywords[stage]
question = random.choice(keywords)

st.markdown(f"#### 💭 회상 카테고리: *{stage}*")
st.markdown(f"### 🩷 질문: {question}")

user_answer = st.text_area("✍️ 이 기억에 대해 떠오르는 걸 자유롭게 적어줘", "")

emotion_selected = st.radio("💛 이 기억은 어떤 감정이었어?", emotions, horizontal=True)

if st.button("다음으로 넘어가기 ➡️"):
    log = {
        "timestamp": datetime.now().isoformat(),
        "user": st.session_state.username,
        "category": stage,
        "question": question,
        "user_answer": user_answer,
        "emotion": emotion_selected
    }
    st.session_state.history.append(log)
    st.session_state.emotion_stats[emotion_selected] += 1

    st.session_state.stage_index = (st.session_state.stage_index + 1) % len(memory_flow)
    st.rerun()
