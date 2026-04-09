"""
v2.0ディレクトリ構造セットアップスクリプト

このスクリプトは、GEOスコアリングツール v2.0に必要な
すべてのディレクトリと初期ファイルを作成します。
"""

import os
from pathlib import Path

# プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 作成するディレクトリ一覧
DIRECTORIES = [
    # API層
    "src/api/external/distribution",

    # エージェント層
    "src/agents",

    # オーケストレーション層
    "src/orchestration",

    # データベース層（v2.0拡張）
    "src/database/models_v2",

    # 分析層
    "src/analytics",

    # コンテンツ層
    "src/content/templates",

    # 技術最適化層
    "src/technical",

    # ダッシュボード（v2.0追加ページ）
    "src/dashboard/pages",

    # バッチワークフロー
    "src/batch/workflows",

    # ユーティリティ
    "src/utils",

    # データ・ログ
    "data/cache",
    "logs",

    # ドキュメント
    "docs",

    # テスト
    "tests/test_agents",
    "tests/test_api",
    "tests/test_orchestration",

    # スクリプト
    "scripts",
]

# 作成する __init__.py ファイル（Pythonパッケージ化）
INIT_FILES = [
    "src/api/external/__init__.py",
    "src/api/external/distribution/__init__.py",
    "src/agents/__init__.py",
    "src/orchestration/__init__.py",
    "src/database/models_v2/__init__.py",
    "src/analytics/__init__.py",
    "src/content/__init__.py",
    "src/technical/__init__.py",
    "src/batch/workflows/__init__.py",
    "src/utils/__init__.py",
    "tests/__init__.py",
    "tests/test_agents/__init__.py",
    "tests/test_api/__init__.py",
    "tests/test_orchestration/__init__.py",
]

# .gitkeep ファイル（空ディレクトリをgitで管理）
GITKEEP_FILES = [
    "logs/.gitkeep",
    "data/cache/.gitkeep",
]


def create_directories():
    """ディレクトリを作成"""
    print("[DIR] ディレクトリを作成しています...")

    for dir_path in DIRECTORIES:
        full_path = PROJECT_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  OK {dir_path}")

    print(f"\n[OK] {len(DIRECTORIES)}個のディレクトリを作成しました。\n")


def create_init_files():
    """__init__.py ファイルを作成"""
    print("[INIT] __init__.py ファイルを作成しています...")

    for init_file in INIT_FILES:
        full_path = PROJECT_ROOT / init_file
        if not full_path.exists():
            full_path.write_text('"""このパッケージは v2.0 で追加されました。"""\n', encoding='utf-8')
            print(f"  OK {init_file}")

    print(f"\n[OK] {len(INIT_FILES)}個の __init__.py を作成しました。\n")


def create_gitkeep_files():
    """.gitkeep ファイルを作成"""
    print("[KEEP] .gitkeep ファイルを作成しています...")

    for gitkeep_file in GITKEEP_FILES:
        full_path = PROJECT_ROOT / gitkeep_file
        full_path.touch(exist_ok=True)
        print(f"  OK {gitkeep_file}")

    print(f"\n[OK] {len(GITKEEP_FILES)}個の .gitkeep を作成しました。\n")


def create_config_files():
    """設定ファイルのテンプレートを作成"""
    print("[CONFIG] 設定ファイルを作成しています...")

    # agents.yaml
    agents_yaml_path = PROJECT_ROOT / "config" / "agents.yaml"
    if not agents_yaml_path.exists():
        agents_yaml_content = """# v2.0 エージェント設定

# エージェント共通設定
common:
  model: "claude-sonnet-4-5"
  temperature: 0.1
  max_tokens: 4000

# Gem_01: GEO Intelligence Analyst
gem_01:
  enabled: true
  schedule: "weekly"
  target_queries:
    - "マーケティングツール おすすめ"
    - "営業支援ツール 比較"
  serp_api:
    engine: "google"
    num_results: 10

# Gem_02: Gap Strategist
gem_02:
  enabled: true
  priority_matrix:
    high_impact_low_effort: "P0"
    high_impact_high_effort: "P1"
    low_impact_low_effort: "P2"
    low_impact_high_effort: "P3"

# Gem_03: Content Engineer
gem_03:
  enabled: true
  distribution_channels:
    - "note"
    - "blog"
    - "press_release"
  tone_presets:
    professional: "formal_business"
    casual: "friendly_conversational"

# Gem_04: Technical Optimizer
gem_04:
  enabled: true
  schema_types:
    - "Product"
    - "FAQ"
    - "HowTo"
    - "Organization"

# Gem_05: Echo Monitor
gem_05:
  enabled: true
  monitoring_delay_hours: 72
  check_interval_hours: 24
"""
        agents_yaml_path.write_text(agents_yaml_content, encoding='utf-8')
        print(f"  OK config/agents.yaml")

    print("\n[OK] 設定ファイルを作成しました。\n")


def main():
    """メイン処理"""
    print("=" * 60)
    print("GEOスコアリングツール v2.0 セットアップ")
    print("=" * 60)
    print()

    create_directories()
    create_init_files()
    create_gitkeep_files()
    create_config_files()

    print("=" * 60)
    print("[OK] セットアップ完了！")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("1. requirements.txt を確認してパッケージをインストール")
    print("2. .env ファイルに新しいAPI情報を追加")
    print("3. scripts/setup_bigquery.py を実行してBigQueryを初期化")
    print()


if __name__ == "__main__":
    main()
