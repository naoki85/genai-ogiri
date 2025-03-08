import sys
import argparse
from typing import Literal
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
import os
from dotenv import load_dotenv
import traceback
import random
from collections import defaultdict
from typing import List
from models.answer import Answer

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_TYPE = Literal["gemini", "chatgpt", "claude"]

SYSTEM_PROMPT = """
これから大喜利をします。あなたは大喜利の回答者です。大喜利のルールは以下の通りです。
1. 大喜利の回答は100文字以内で回答してください。
2. 大喜利の回答は日本語で回答してください。
3. 大喜利の回答はスマートで楽しいものを回答してください。
4. 他の参加者の回答も会話に含めます。前の回答も考慮して回答をしてください。
"""

def setup_gemini():
    return genai.Client(api_key=GOOGLE_API_KEY)

def setup_claude():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def setup_chatgpt():
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_response(model_type: MODEL_TYPE, prompt: str, conversation_history: list) -> str:
    if model_type == "gemini":
        client = setup_gemini()
        previous_messages = "\n".join([h['content'] for h in conversation_history])
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT + "\n" + previous_messages,
                temperature=0.9,
            ),
        )
        result = ""
        for chunk in response:
            content = chunk.text
            print(content, end='', flush=True)
            result += content
        return result
    
    elif model_type == "claude":
        client = setup_claude()
        with client.messages.stream(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.9,
            system=SYSTEM_PROMPT,
            messages=[
                *conversation_history,
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            result = ""
            for text in stream.text_stream:
                print(text, end='', flush=True)
                result += text
            return result
    
    elif model_type == "chatgpt":
        client = setup_chatgpt()
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.9,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history,
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        result = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                result += content
        return result

def get_point_input() -> int:
    while True:
        try:
            response = input("\nこの回答にポイントを付与しますか？ (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return 1
            elif response in ['n', 'no']:
                return 0
        except EOFError:
            return 0
        print("'y' または 'n' で回答してください。")

def display_results(answers: List[Answer]):
    print("\n=== 大喜利の結果発表 ===")

    model_points = defaultdict(int)
    for answer in answers:
        model_points[answer.model] += answer.points    

    print("\n【総合順位】")
    for rank, (model, points) in enumerate(
        sorted(model_points.items(), key=lambda x: x[1], reverse=True), 1
    ):
        print(f"{rank}位: {model.upper()} ({points}ポイント)")

    print("\n【ポイントを獲得した回答】")
    point_answers = [a for a in answers if a.points > 0]
    if point_answers:
        for answer in point_answers:
            print(f"\nラウンド{answer.round}: {answer.model.upper()}")
            print(f"回答: {answer.content}")
    else:
        print("ポイントを獲得した回答はありませんでした。")

def main():
    parser = argparse.ArgumentParser(description='AI生成ツール')
    args = parser.parse_args()

    conversation_history = []
    answers = []
    
    try:
        print("問題を入力してください（終了するには Ctrl+D）:")
        prompt = sys.stdin.read().strip()
    
        models = ["gemini", "claude", "chatgpt"] * 3
        random.shuffle(models)

        for i, model in enumerate(models, 1):
            print(f"\n=== ラウンド{i}: {model.upper()} の回答 ===")
            response = generate_response(model, prompt, conversation_history)

            points = get_point_input()
            
            # 回答を保存
            answer = Answer(round=i, model=model, content=response, points=points)
            answers.append(answer)

            conversation_history.append({
                "role": "assistant", 
                "content": f"[{model}の回答] {response} (獲得ポイント: {points})"
            })
            
            print()

        display_results(answers)
        
    except KeyboardInterrupt:
        print("\n\nプログラムが中断されました。これまでの結果を表示します。")
        display_results(answers)
        sys.exit(0)
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}", file=sys.stderr)
        print("スタックトレース:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
