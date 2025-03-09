# AI大喜利ゲーム

複数のAIモデルと対話できるStreamlitアプリケーションです。各AIモデルの回答にポイントを付与し、ゲーム形式で楽しむことができます。

## 機能

- 複数のAIモデルとの対話
  - Claude (Anthropic)
  - ChatGPT (OpenAI)
  - Gemini (Google)
  - DeepSeek (DeepSeek) (未確認)
- リアルタイムストリーミング応答
- ポイントシステム
- カスタマイズ可能なシステムプロンプト
- チャットUI形式のインターフェース

## セットアップ

1. 必要なAPIキーを取得
   - Anthropic API Key
   - OpenAI API Key
   - Google API Key
   - DeepSeek API Key (オプション)

2. 環境設定
   ```bash
   # 仮想環境の作成と有効化
   python -m venv .venv
   source .venv/bin/activate  # Unix系
   # または
   .venv\Scripts\activate     # Windows

   # 依存関係のインストール
   uv pip install -e .
   ```

3. 環境変数の設定
   - `.env.sample`を`.env`にコピー
   - 各APIキーを設定
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

## 使い方

1. アプリケーションの起動
   ```bash
   streamlit run app.py
   ```

2. サイドバーの設定
   - システムプロンプトのカスタマイズ
   - 使用するAIモデルの選択

3. チャット
   - お題を入力
   - AIモデルがランダムな順序で回答
   - 各回答にポイントを付与可能
   - 3ラウンドで終了

4. スコア
   - サイドバーでリアルタイムのスコアを確認
   - ゲーム終了時に最終結果を表示

## カスタマイズ

`config.yaml`でAIモデルの設定を変更できます：
- モデル名
- 温度（ランダム性）
- 最大トークン数
- 表示名

## 開発環境

- Python 3.13
- Streamlit 1.27.0
- Anthropic Claude API
- OpenAI API
- Google Gemini API
- DeepSeek API (オプション)
