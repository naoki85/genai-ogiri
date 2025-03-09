import streamlit as st
from dotenv import load_dotenv
import random
from models.claude_model import ClaudeModel
from models.gpt_model import GPTModel
from models.gemini_model import GeminiModel
# from models.deepseek_model import DeepSeekModel
from utils.config import get_system_prompt, get_model_config
import time

load_dotenv()

MAX_ROUNDS = 3

# AIモデルの設定
AI_MODELS = {
    "claude": {
        "class": ClaudeModel,
        "name": "Claude",
        "avatar": "🟣"
    },
    "chatgpt": {
        "class": GPTModel,
        "name": "ChatGPT",
        "avatar": "🟢"
    },
    "gemini": {
        "class": GeminiModel,
        "name": "Gemini",
        "avatar": "🔵"
    },
    # "deepseek": {
    #     "class": DeepSeekModel,
    #     "name": "DeepSeek",
    #     "avatar": "🟡"
    # }
}

AVATARS = {
    model_id: (config["avatar"], config["name"])
    for model_id, config in AI_MODELS.items()
}
AVATARS["user"] = ("👤", "司会")

def initialize_ai_models(system_prompt):
    return {
        model_id: config["class"](system_prompt, config["name"])
        for model_id, config in AI_MODELS.items()
    }

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "theme" not in st.session_state:
        st.session_state.theme = ""
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = get_system_prompt()
    if "current_round" not in st.session_state:
        st.session_state.current_round = 1
    if "scores" not in st.session_state:
        st.session_state.scores = {model_id: 0 for model_id in AI_MODELS.keys()}
    if "round_completed" not in st.session_state:
        st.session_state.round_completed = False
    if "waiting_for_score" not in st.session_state:
        st.session_state.waiting_for_score = False
    if "current_answer" not in st.session_state:
        st.session_state.current_answer = None
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

def display_message(role: str, content: str, model: str = None):
    avatar, name = AVATARS.get(model, AVATARS["user"])
    with st.chat_message(role, avatar=avatar):
        st.markdown(f"**{name}**: {content}")

def display_scores():
    st.sidebar.subheader("現在のスコア")
    for model_id, score in st.session_state.scores.items():
        avatar, name = AVATARS[model_id]
        st.sidebar.text(f"{avatar} {name}: {score}点")

def display_final_scores():
    st.header("🏆 最終結果 🏆")
    sorted_scores = sorted(
        st.session_state.scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for rank, (model_id, score) in enumerate(sorted_scores, 1):
        avatar, name = AVATARS[model_id]
        st.markdown(f"**第{rank}位**: {avatar} {name} - {score}点")

def main():
    st.title("AI大喜利")
    initialize_session_state()
    
    # サイドバーの設定
    with st.sidebar:
        st.header("設定")
        
        # システムプロンプトの編集
        st.subheader("システムプロンプト")
        system_prompt = st.text_area(
            "プロンプトを編集",
            value=st.session_state.system_prompt,
            height=200
        )
        
        # AIモデルの選択
        st.subheader("AIモデル選択")
        model_options = list(AI_MODELS.keys())
        selected_models = st.multiselect(
            "参加するAIを選択",
            model_options,
            default=model_options
        )
        
        # スコア表示
        display_scores()
        
        # クリアボタン
        if st.button("ゲームをリセット"):
            for key in ["messages", "theme", "current_round", "scores", 
                       "round_completed", "waiting_for_score", "current_answer", "game_over"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ゲーム終了時は結果のみ表示
    if st.session_state.game_over:
        display_final_scores()
        return

    # チャットUIのメインエリア
    if not st.session_state.waiting_for_score:
        if theme := st.chat_input("お題を入力してください"):
            st.session_state.theme = theme
            st.session_state.messages.append({"role": "user", "content": f"お題: {theme}"})
    
    # メッセージ履歴の表示
    for message in st.session_state.messages:
        if message["role"] == "user":
            display_message("user", message["content"], "user")
        else:
            display_message("assistant", message["content"], message["model"])
    
    # 採点待ち状態の処理
    if st.session_state.waiting_for_score and st.session_state.current_answer:
        answer = st.session_state.current_answer
        avatar, name = AVATARS[answer.model]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍 ポイント付与", key="give_point"):
                st.session_state.scores[answer.model] += 1
                st.session_state.waiting_for_score = False
                st.rerun()
        with col2:
            if st.button("👎 スキップ", key="skip_point"):
                st.session_state.waiting_for_score = False
                st.rerun()
        with col3:
            if st.button("🔚 ゲーム終了", key="end_game"):
                st.session_state.game_over = True
                st.rerun()
    
    # 新しい回答の生成
    if (st.session_state.theme and not st.session_state.waiting_for_score and 
            st.session_state.current_round <= MAX_ROUNDS):
        # ランダムにモデルを選択
        available_models = [
            model for model in selected_models
            if model in AI_MODELS
        ]
        if available_models:
            model_name = random.choice(available_models)
            avatar, name = AVATARS[model_name]
            
            with st.chat_message("assistant", avatar=avatar):
                message_placeholder = st.empty()
                try:
                    ai_models = initialize_ai_models(system_prompt)
                    model = ai_models[model_name]
                    answer = model.stream_response(st.session_state.theme, message_placeholder)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer.content,
                        "model": model_name
                    })
                    st.session_state.current_answer = answer
                    st.session_state.waiting_for_score = True
                    
                    # 全てのモデルが回答し終えたら次のラウンドへ
                    if len(st.session_state.messages) % len(selected_models) == 0:
                        st.session_state.current_round += 1
                        if st.session_state.current_round > MAX_ROUNDS:
                            st.session_state.game_over = True
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"{name}からの回答生成中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main() 