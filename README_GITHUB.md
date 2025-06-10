# 🚀 AIチャットサービス自動化システム - GitHub使用ガイド

## 📋 初心者向けGitHub実行手順

### ステップ1: GitHubリポジトリの作成

1. **GitHubアカウントでログイン**
   - https://github.com にアクセス
   - ログインまたは新規アカウント作成

2. **新しいリポジトリを作成**
   - 右上の「+」→「New repository」をクリック
   - Repository name: `ai-chat-automation`
   - Description: `AIチャットサービス自動化システム`
   - Public または Private を選択
   - 「Create repository」をクリック

### ステップ2: ローカルでGit初期化

ターミナル/コマンドプロンプトで以下を実行：

```bash
# プロジェクトディレクトリに移動
cd /Users/roudousha/Dropbox/4.AI-auto/faile/ai_chat_automation

# Gitリポジトリを初期化
git init

# GitHubリポジトリをリモートに追加（URLは自分のリポジトリに変更）
git remote add origin https://github.com/YOUR_USERNAME/ai-chat-automation.git

# 全ファイルをステージング
git add .

# 初回コミット
git commit -m "初回コミット: AIチャットサービス自動化システム基盤実装

- Loggerモジュール実装完了（utils/logger.py）
- WebDriverManagerモジュール実装完了（utils/driver_manager.py）  
- ElementFinderモジュール実装完了（utils/element_finder.py）
- メインアプリケーション（main.py）
- 設定ファイル（config/config.json）
- カスタム例外クラス（core/exceptions.py）

Phase 1の基盤実装が完了
- 詳細なログ管理機能
- Selenium WebDriver管理
- 要素検索・操作の抽象化
- 人間らしい操作パターン

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# GitHubにプッシュ
git branch -M main
git push -u origin main
```

### ステップ3: GitHub Actionsでの自動実行設定

`.github/workflows/test.yml` ファイルを作成：

```yaml
name: AI Chat Automation Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.9
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Chrome
      run: |
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    
    - name: Run logger tests
      run: |
        python utils/logger.py
    
    - name: Run basic tests
      run: |
        python -c "
        from utils.logger import get_logger
        logger = get_logger('test')
        logger.info('GitHub Actions test successful')
        print('✅ All imports working correctly')
        "
```

### ステップ4: 必要ファイルの追加

#### `.gitignore` ファイル作成：
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Logs
logs/*.log
logs/*.json

# Profiles
profiles/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Selenium
chromedriver*
geckodriver*
```

#### `requirements.txt` を更新：
```
selenium==4.21.0
undetected-chromedriver==3.5.4
webdriver-manager==4.0.1
beautifulsoup4==4.12.3
python-dotenv==1.0.1
numpy>=1.21.0
```

### ステップ5: GitHub Codespacesでの実行（推奨）

1. **GitHub Codespacesを起動**
   - リポジトリページで「Code」→「Codespaces」→「Create codespace on main」

2. **Codespacesで実行**
   ```bash
   # 依存関係インストール
   pip install -r requirements.txt
   
   # Loggerテスト実行
   python utils/logger.py
   
   # 基本動作確認
   python -c "
   from utils.logger import get_logger
   logger = get_logger('github_test')
   logger.info('GitHub Codespaces環境で正常動作中')
   logger.log_performance_summary()
   "
   ```

### ステップ6: ローカル環境での実行

他の人がプロジェクトを試す場合：

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-chat-automation.git
   cd ai-chat-automation
   ```

2. **仮想環境作成**
   ```bash
   python -m venv venv
   
   # macOS/Linux:
   source venv/bin/activate
   
   # Windows:
   venv\Scripts\activate
   ```

3. **依存関係インストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **動作確認**
   ```bash
   # Loggerモジュールテスト
   python utils/logger.py
   
   # 基本システムテスト（ブラウザ起動なし）
   python -c "
   from utils.logger import get_logger
   from utils.driver_manager import WebDriverManager
   from utils.element_finder import ElementFinder
   
   logger = get_logger('integration_test')
   logger.info('✅ All modules imported successfully')
   logger.info('✅ System ready for testing')
   "
   ```

### ステップ7: 実際のブラウザテスト

⚠️ **注意**: 実際のブラウザ自動化は自己責任で行ってください

```bash
# デモ実行（手動ログイン版）
python main.py --interactive

# または単一メッセージテスト
python main.py --message "Hello, this is a test from GitHub"
```

## 📱 スマートフォンでの確認

GitHub Mobileアプリでも以下が確認できます：
- ✅ コードの閲覧
- ✅ GitHub Actionsの実行結果
- ✅ ログファイルのダウンロード

## 🔧 トラブルシューティング

### Chrome/ChromeDriverエラー
```bash
# ChromeDriverの手動インストール
pip install webdriver-manager
python -c "
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
print('ChromeDriver installed successfully')
"
```

### 権限エラー
```bash
# ログディレクトリの権限設定
chmod 755 logs/
chmod 644 logs/*.log
```

### Importエラー
```bash
# Pythonパスの確認
python -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path[0])
"
```

## 📊 GitHub Actionsでの自動テスト

リポジトリにプッシュすると自動的に：
- ✅ Python環境のセットアップ
- ✅ 依存関係のインストール
- ✅ Loggerモジュールのテスト実行
- ✅ 基本的なImportテスト

## 🎯 次のステップ

1. **Phase 2の実装**
   - RateLimitManager の追加
   - ChatGPTBot の本格実装

2. **テストの拡充**
   - 単体テストの追加
   - 統合テストの実装

3. **ドキュメントの充実**
   - API ドキュメント
   - 使用例の追加

---

**🔒 重要な注意事項**
- このツールは学習・研究目的のみで使用してください
- 各AIサービスの利用規約を必ず遵守してください
- アカウント停止等のリスクは自己責任となります

**📞 サポート**
問題が発生した場合は、GitHubのIssuesで報告してください。