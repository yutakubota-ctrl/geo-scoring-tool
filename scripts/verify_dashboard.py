"""
ダッシュボード検証スクリプト

v2.1で実装した3つの画面の動作確認を自動化
- デモデータの存在確認
- JSONファイルの妥当性チェック
- 必要なライブラリのインストール確認
"""
import os
import json
import sys
from pathlib import Path

# カラーコード
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}[OK] {message}{RESET}")

def print_error(message):
    print(f"{RED}[ERROR] {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}[WARNING] {message}{RESET}")

def check_demo_data_files():
    """デモデータファイルの存在確認"""
    print("\n[1] デモデータファイルの確認")
    print("-" * 50)

    demo_files = [
        'data/demo/thought_log_sample.json',
        'data/demo/roadmap_sample.json',
        'data/demo/echo_monitor_sample.json'
    ]

    all_exist = True

    for file_path in demo_files:
        full_path = Path(file_path)
        if full_path.exists():
            print_success(f"{file_path} が存在します")
        else:
            print_error(f"{file_path} が見つかりません")
            all_exist = False

    return all_exist

def validate_json_files():
    """JSONファイルの妥当性チェック"""
    print("\n[2] JSONファイルの妥当性チェック")
    print("-" * 50)

    demo_files = [
        'data/demo/thought_log_sample.json',
        'data/demo/roadmap_sample.json',
        'data/demo/echo_monitor_sample.json'
    ]

    all_valid = True

    for file_path in demo_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print_error(f"{file_path} が存在しないためスキップ")
            all_valid = False
            continue

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print_success(f"{file_path} は有効なJSONです")
        except json.JSONDecodeError as e:
            print_error(f"{file_path} のJSON形式が不正です: {e}")
            all_valid = False
        except Exception as e:
            print_error(f"{file_path} の読み込みエラー: {e}")
            all_valid = False

    return all_valid

def check_required_libraries():
    """必要なライブラリのインストール確認"""
    print("\n[3] 必要なライブラリの確認")
    print("-" * 50)

    required_libs = [
        'streamlit',
        'plotly',
        'pandas',
        'sqlalchemy'
    ]

    all_installed = True

    for lib in required_libs:
        try:
            __import__(lib)
            print_success(f"{lib} がインストールされています")
        except ImportError:
            print_error(f"{lib} がインストールされていません")
            all_installed = False

    return all_installed

def check_dashboard_pages():
    """ダッシュボードページファイルの存在確認"""
    print("\n[4] ダッシュボードページファイルの確認")
    print("-" * 50)

    page_files = [
        'src/dashboard/pages/4_thought_log.py',
        'src/dashboard/pages/5_roadmap.py',
        'src/dashboard/pages/6_echo_monitor.py'
    ]

    all_exist = True

    for file_path in page_files:
        full_path = Path(file_path)
        if full_path.exists():
            # ファイルサイズも確認
            file_size = full_path.stat().st_size
            print_success(f"{file_path} が存在します（{file_size:,} bytes）")
        else:
            print_error(f"{file_path} が見つかりません")
            all_exist = False

    return all_exist

def check_environment_variables():
    """環境変数の確認"""
    print("\n[5] 環境変数の確認")
    print("-" * 50)

    demo_mode = os.getenv("DEMO_MODE", "false").lower()

    if demo_mode == "true":
        print_success("DEMO_MODE=true が設定されています")
        return True
    else:
        print_warning("DEMO_MODE が設定されていません（デフォルト: false）")
        print_warning("デモモードを有効化するには: export DEMO_MODE=true")
        return False

def main():
    """メイン検証フロー"""
    print("=" * 50)
    print("GEOスコアリングツール v2.1 ダッシュボード検証")
    print("=" * 50)

    results = []

    # 各検証を実行
    results.append(("デモデータファイル", check_demo_data_files()))
    results.append(("JSON妥当性", validate_json_files()))
    results.append(("必要なライブラリ", check_required_libraries()))
    results.append(("ダッシュボードページ", check_dashboard_pages()))
    results.append(("環境変数", check_environment_variables()))

    # サマリー
    print("\n" + "=" * 50)
    print("検証結果サマリー")
    print("=" * 50)

    all_passed = True
    for check_name, result in results:
        if result:
            print_success(f"{check_name}: 合格")
        else:
            print_error(f"{check_name}: 不合格")
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print_success("すべての検証に合格しました！")
        print("\n次のコマンドでダッシュボードを起動できます:")
        print("  streamlit run src/dashboard/app.py")
        return 0
    else:
        print_error("一部の検証に失敗しました。上記のエラーを修正してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
