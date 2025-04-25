
import gradio as gr
import pandas as pd
import random
from datetime import datetime
from collections import defaultdict
import os
import csv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama

# 모델 세팅
llm = ChatOllama(model="EEVE-Korean-10.8B", temperature=0.7)

# 디렉토리 생성
os.makedirs("workspace", exist_ok=True)

# 데이터 로딩
keywords_df = pd.read_csv("workspace/memory_keywords.csv")
memory_keywords = defaultdict(list)
for _, row in keywords_df.iterrows():
    memory_keywords[row["category"]].append(row["keyword"])

memory_flow = ["오늘", "이번 주", "최근 명절", "청년기", "중고등학교", "초등학교", "유아기"]
templates = [
    "{} 때 누구랑 보냈어?",
    "{}에는 주로 어떤 걸 했어?",
    "{}하면 어떤 풍경이나 냄새가 떠올라?",
    "{} 때 특별한 기억이 있어?"
]
emotions = [
    "😊 기뻤어", "🥰 감동적이었어", "😢 슬펐어", "😠 화났어",
    "😶 아무 감정이 없었어", "🤔 복잡했어", "😨 불안했어",
    "🤗 편안했어", "🤔 잘 기억이 안 나"
]

# 세션
session = {
    "username": "",
    "stage": 0,
    "emotion_stats": defaultdict(int),
    "history": [],
    "question": "",
    "category": ""
}

def generate_initial_question():
    category = memory_flow[session["stage"]]
    session["category"] = category
    keyword = random.choice(memory_keywords[category])
    template = random.choice(templates)
    session["question"] = template.format(keyword)
    return session["question"]

def generate_naru_reply(user_answer, emotion):
    base = f"너의 대답: '{user_answer}'"
    if "기뻤" in emotion or "감동" in emotion:
        style = "정말 좋았던 기억이구나. 들으니까 나도 미소 지어져."
    elif "슬펐" in emotion:
        style = "마음이 좀 아팠겠다... 그 기억, 나랑 나눠줘서 고마워."
    elif "화났" in emotion:
        style = "화날 수밖에 없는 순간이었겠다. 이해돼."
    elif "복잡" in emotion:
        style = "감정이 얽혀 있었나 보네. 그때 참 많은 생각 들었겠다."
    elif "불안" in emotion:
        style = "불안했구나... 그런 감정도 소중한 기억이야."
    elif "편안" in emotion:
        style = "편안했던 그 순간, 들으니까 나도 마음이 놓인다."
    elif "없었" in emotion:
        style = "무덤덤했던 그 순간도 분명 의미 있었을 거야."
    else:
        style = "응, 그래도 나눠줘서 고마워!"
    return f"🌿 {style} {session['username']}이는 어땠어?"

def generate_next_question():
    session["stage"] = (session["stage"] + 1) % len(memory_flow)
    return generate_initial_question()

def start_conversation(name):
    session["username"] = name
    q = generate_initial_question()
    return [(f"나루", f"🩷 질문: {q}")]

def continue_chat(choice, user_answer, emotion):
    logs = []

    if choice == "잘 기억 안 나":
        logs.append(("나루", "🤔 괜찮아! 흐릿한 기억도 있지!"))
        q = generate_next_question()
        logs.append(("나루", f"🩷 다음 질문: {q}"))
        return logs

    elif choice == "말하고 싶지 않아":
        logs.append(("나루", "🔒 물론! 편할 때 말해도 돼!"))
        q = generate_next_question()
        logs.append(("나루", f"🩷 다음 질문: {q}"))
        return logs

    elif choice == "그만할래":
        return [("나루", f"💚 {session['username']}아, 오늘도 수고 많았어. 푹 쉬어!")]

    elif choice == "기억나":
        reply = generate_naru_reply(user_answer, emotion)
        session["emotion_stats"][emotion] += 1

        log = {
            "timestamp": datetime.now().isoformat(),
            "user": session["username"],
            "category": session["category"],
            "question": session["question"],
            "ai_answer": reply,
            "user_answer": user_answer,
            "emotion": emotion
        }

        df = pd.DataFrame([log])
        try:
            df.to_csv("workspace/memory_log.csv", mode="x", index=False)
        except FileExistsError:
            df.to_csv("workspace/memory_log.csv", mode="a", header=False, index=False)

        logs.append((session["username"], f"💬 {user_answer}"))
        logs.append(("나루", f"🌿 {reply}"))
        q = generate_next_question()
        logs.append(("나루", f"🩷 다음 질문: {q}"))
        return logs

    return [("나루", "⚠️ 선택을 정확히 해줘!")]

# Gradio 인터페이스
with gr.Blocks() as demo:
    gr.Markdown("## 🌿 기억 나루처럼 감성적으로 함께 기억을 떠올려보자 😊")

    with gr.Row():
        user_name = gr.Textbox(label="너의 이름은?", placeholder="예: 지윤")
        start_btn = gr.Button("기억 산책 시작하기")

    memory_choice = gr.Radio(["기억나", "잘 기억 안 나", "말하고 싶지 않아", "그만할래"], label="이 기억 어땠어?")
    user_answer = gr.Textbox(label="📝 기억을 말해줘")
    emotion = gr.Radio(emotions, label="그때 감정은 어땠어?")
    chatbot = gr.Chatbot(label="나루와의 대화")
    send_btn = gr.Button("대화하기")

    start_btn.click(fn=start_conversation, inputs=user_name, outputs=chatbot)
    send_btn.click(fn=continue_chat, inputs=[memory_choice, user_answer, emotion], outputs=chatbot)

demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
