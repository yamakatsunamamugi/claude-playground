<<<<<<< HEAD
# テスト用リポジトリ
=======
# AI Chat Service Automation

学習・研究目的のAIチャットサービス自動化システム

## ⚠️ 重要な注意事項

**このツールは学習・研究目的のプロトタイプです。以下の点を必ずお読みください：**

- ✅ **教育・研究目的のみ**で使用してください
- ✅ **各サービスの利用規約**を遵守してください  
- ✅ **レート制限**を厳格に守ってください
- ✅ **アカウント停止のリスク**を理解して使用してください
- ❌ **商用利用は推奨しません**
- ❌ **セレクタは頻繁に変更される**ため定期的なメンテナンスが必要です

## 機能

### 現在サポートされているサービス
- **ChatGPT** (最も安定) ✅
- **Google Gemini** (実験的) 🧪  
- **Claude** (実験的) 🧪

### 主要機能
- 🤖 自動メッセージ送信と応答受信
- 👤 人間らしいタイピングパターン
- 🔄 複数セレクタによるUI変更対応
- 📊 レート制限の自動検出と管理
- 💾 会話履歴の自動保存（Markdown/HTML/JSON）
- 🛡️ 基本的な検出回避機能

## セットアップ

### 1. システム要件
- Python 3.8以上
- Google Chrome ブラウザ
- macOS/Windows/Linux

### 2. 自動セットアップ
```bash
# プロジェクトディレクトリに移動
cd ai_chat_automation

# 自動セットアップ実行
python setup.py
```

### 3. 手動セットアップ（必要に応じて）
```bash
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# 依存関係インストール  
pip install -r requirements.txt
```

## 使用方法

### インタラクティブモード（推奨）
```bash
# 仮想環境をアクティベート後
python main.py --interactive
```

### 単一メッセージモード
```bash
python main.py --message "Hello, how are you?"
```

### サービス指定
```bash
python main.py --service chatgpt --interactive
python main.py --service gemini --message "Hello"
```

## 使用手順

1. **スクリプト実行**: 上記コマンドでスクリプトを実行
2. **ブラウザ起動**: Chrome ブラウザが自動で開きます
3. **手動ログイン**: 表示されたページで手動でログインしてください
4. **自動検出**: ログイン完了を自動で検出します
5. **メッセージ送信**: メッセージを入力して送信
6. **応答受信**: AIの応答を自動で抽出して表示

## 設定

### 設定ファイル: `config/config.json`

```json
{
  "chatgpt": {
    "url": "https://chat.openai.com",
    "selectors": {
      "input_fallback": [...],
      "send_button": [...],
      "response": [...]
    },
    "timeouts": {
      "page_load": 30,
      "response_wait": 60
    },
    "rate_limits": {
      "requests_per_hour": 40,
      "cooldown_seconds": 5
    }
  }
}
```

### 環境変数: `.env`

```env
# ログレベル
LOG_LEVEL=INFO

# ヘッドレスモード
HEADLESS=False

# 自動保存
AUTO_SAVE_CONVERSATIONS=True
```

## トラブルシューティング

### よくある問題

**1. セレクタが見つからない**
```
❌ SelectorNotFoundError: None of [...] found
```
**解決法**: UIが変更された可能性があります。`config.json`のセレクタを更新してください。

**2. レート制限エラー**
```
⚠️ Rate limit reached
```
**解決法**: しばらく待ってから再試行してください。

**3. ログインタイムアウト**
```
❌ Login timeout
```
**解決法**: 手動ログインを5分以内に完了してください。

**4. ChromeDriver エラー**
```
❌ Driver initialization failed
```
**解決法**: `python setup.py`を再実行してください。

### セレクタ更新方法

1. ブラウザの開発者ツール（F12）を開く
2. 目標要素を右クリック → "検証"
3. CSS セレクタをコピー
4. `config.json`の該当セレクタを更新

## ファイル構造

```
ai_chat_automation/
├── config/
│   └── config.json          # サービス設定
├── core/
│   ├── base_bot.py          # 基底クラス
│   ├── chatgpt_bot.py       # ChatGPT実装
│   └── exceptions.py        # 例外クラス
├── utils/
│   ├── driver_manager.py    # ドライバー管理
│   ├── human_behavior.py    # 人間行動シミュレート
│   └── selector_manager.py  # セレクタ管理
├── logs/                    # ログファイル
├── conversations/           # 会話履歴
├── main.py                  # メインアプリ
├── setup.py                 # セットアップスクリプト
└── requirements.txt         # 依存関係
```

## 開発者向け情報

### 新しいサービスの追加

1. `core/` に新しいボットクラスを作成
2. `BaseBot` を継承して必要なメソッドを実装
3. `config.json` にサービス設定を追加
4. `main.py` にサービス選択肢を追加

### カスタム例外の使用

```python
from ai_chat_automation import (
    ChatGPTBot, RateLimitError, SelectorNotFoundError
)

try:
    bot = ChatGPTBot()
    response = bot.send_message("Hello")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except SelectorNotFoundError as e:
    print(f"UI changed: {e}")
```

## ライセンス

このプロジェクトは**教育・研究目的のみ**で使用可能です。

## 免責事項

- 本ツールの使用によって生じるいかなる損害についても責任を負いません
- 各AIサービスの利用規約に従って使用してください
- アカウント停止等のリスクは使用者の責任です
- UIの変更により動作しなくなる可能性があります

## サポート

問題が発生した場合：
1. まず上記のトラブルシューティングをご確認ください
2. ログファイル（`logs/`）をチェックしてください
3. 設定ファイルを再確認してください

---

**🎓 This is an educational prototype. Use responsibly and ethically.**
>>>>>>> eefed81 (Add project files (excluding venv))
