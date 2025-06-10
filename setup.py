#!/usr/bin/env python3
"""
AI Chat Service Automation - Environment Setup Script
学習・研究目的のプロトタイプ実装

このスクリプトは開発環境のセットアップを自動化します。
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_step(step_name: str):
    """ステップ名を表示"""
    print(f"\n{'='*50}")
    print(f"🔧 {step_name}")
    print(f"{'='*50}")

def check_python_version():
    """Python バージョンチェック"""
    print_step("Python バージョンチェック")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8以上が必要です")
        print(f"現在のバージョン: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_chrome_installation():
    """Chrome ブラウザの存在確認"""
    print_step("Chrome ブラウザチェック")
    
    system = platform.system()
    chrome_paths = {
        'Darwin': [  # macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chrome.app/Contents/MacOS/Chrome'
        ],
        'Windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chrome',
            '/usr/bin/chromium-browser'
        ]
    }
    
    if system not in chrome_paths:
        print(f"⚠️  {system} での Chrome パス自動検出は未対応です")
        return True  # 継続
    
    for path in chrome_paths[system]:
        if os.path.exists(path):
            print(f"✅ Chrome found: {path}")
            return True
    
    print("❌ Google Chrome が見つかりません")
    print("手動でインストールしてください: https://www.google.com/chrome/")
    return False

def create_virtual_environment():
    """仮想環境の作成"""
    print_step("仮想環境作成")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ 仮想環境は既に存在します")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ 仮想環境を作成しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 仮想環境の作成に失敗: {e}")
        return False

def get_activation_command():
    """仮想環境のアクティベーションコマンドを取得"""
    system = platform.system()
    if system == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """依存関係のインストール"""
    print_step("依存関係インストール")
    
    # 仮想環境内のpipを使用
    system = platform.system()
    pip_path = "venv/bin/pip" if system != "Windows" else "venv\\Scripts\\pip.exe"
    
    if not os.path.exists(pip_path):
        print("❌ 仮想環境のpipが見つかりません")
        return False
    
    try:
        # pipのアップデート
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # requirements.txtからインストール
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("✅ 依存関係のインストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存関係のインストールに失敗: {e}")
        return False

def setup_chromedriver():
    """ChromeDriver の自動セットアップ"""
    print_step("ChromeDriver セットアップ")
    
    system = platform.system()
    python_path = "venv/bin/python" if system != "Windows" else "venv\\Scripts\\python.exe"
    
    try:
        # webdriver-manager を使って ChromeDriver をセットアップ
        setup_code = """
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# ChromeDriver の自動ダウンロードと設定
driver_path = ChromeDriverManager().install()
print(f"ChromeDriver installed at: {driver_path}")

# 簡単な動作テスト
options = webdriver.ChromeOptions()
options.add_argument("--headless")
service = Service(driver_path)

try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.google.com")
    print("✅ ChromeDriver テスト成功")
    driver.quit()
except Exception as e:
    print(f"⚠️  ChromeDriver テスト失敗: {e}")
"""
        
        subprocess.run([python_path, "-c", setup_code], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ChromeDriver セットアップに失敗: {e}")
        return False

def create_environment_file():
    """環境変数ファイルの作成"""
    print_step("環境設定ファイル作成")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env ファイルは既に存在します")
        return True
    
    env_content = """# AI Chat Automation Environment Variables
# 必要に応じて設定を変更してください

# ログレベル (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ヘッドレスモード (True/False)
HEADLESS=False

# 自動会話保存 (True/False)
AUTO_SAVE_CONVERSATIONS=True

# 会話保存形式 (markdown/html/json)
CONVERSATION_FORMAT=markdown

# カスタムユーザーエージェント（必要に応じて）
# USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
"""
    
    try:
        env_file.write_text(env_content, encoding='utf-8')
        print("✅ .env ファイルを作成しました")
        return True
    except Exception as e:
        print(f"❌ .env ファイルの作成に失敗: {e}")
        return False

def print_next_steps():
    """次のステップを表示"""
    print_step("セットアップ完了！")
    
    activation_cmd = get_activation_command()
    
    print("🎉 環境セットアップが完了しました！")
    print("\n📋 次のステップ:")
    print(f"1. 仮想環境をアクティベート: {activation_cmd}")
    print("2. メインスクリプトを実行: python main.py")
    print("\n⚠️  重要な注意事項:")
    print("- このツールは学習・研究目的のみで使用してください")
    print("- 各サービスの利用規約を遵守してください")
    print("- レート制限を守り、適切な間隔で使用してください")
    print("- アカウント停止のリスクがあることを理解してください")

def main():
    """メイン関数"""
    print("🚀 AI Chat Service Automation - Environment Setup")
    print("学習・研究目的のプロトタイプ実装")
    
    # 各ステップを実行
    steps = [
        ("Python バージョンチェック", check_python_version),
        ("Chrome ブラウザチェック", check_chrome_installation),
        ("仮想環境作成", create_virtual_environment),
        ("依存関係インストール", install_dependencies),
        ("ChromeDriver セットアップ", setup_chromedriver),
        ("環境設定ファイル作成", create_environment_file),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ 以下のステップでエラーが発生しました:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\n手動で解決してから再度実行してください。")
        sys.exit(1)
    else:
        print_next_steps()

if __name__ == "__main__":
    main()