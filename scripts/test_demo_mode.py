"""
デモモード機能のテストスクリプト

使用方法:
    DEMO_MODE=true python scripts/test_demo_mode.py
"""

import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.demo_mode import (
    is_demo_mode,
    get_demo_thought_logs,
    get_demo_citations,
    get_demo_roadmap,
    get_demo_stats
)


def test_demo_mode():
    """デモモード機能のテスト"""
    print("=" * 60)
    print("デモモード機能テスト")
    print("=" * 60)
    print()

    # デモモード確認
    print(f"デモモード有効: {is_demo_mode()}")
    print()

    # 思考ログ取得
    print("-" * 60)
    print("思考ログ取得テスト")
    print("-" * 60)
    thought_logs = get_demo_thought_logs(limit=3)
    print(f"取得件数: {len(thought_logs)}")
    if thought_logs:
        first_log = thought_logs[0]
        print(f"  クエリID: {first_log['query_id']}")
        print(f"  クエリ: {first_log['query_text']}")
        print(f"  モデル: {first_log['llm_model']}")
        print(f"  ステップ1: {first_log['thought_trace']['step_1']}")
    print()

    # 引用データ取得
    print("-" * 60)
    print("引用データ取得テスト")
    print("-" * 60)
    citations = get_demo_citations(limit=5)
    print(f"取得件数: {len(citations)}")
    if citations:
        first_citation = citations[0]
        print(f"  引用ID: {first_citation['citation_id']}")
        print(f"  企業名: {first_citation['entity_name']}")
        print(f"  センチメント: {first_citation['sentiment_score']}")
        print(f"  参照タイプ: {first_citation['reference_type']}")
    print()

    # 特定企業の引用データ取得
    print("-" * 60)
    print("特定企業の引用データ取得テスト（HubSpot）")
    print("-" * 60)
    hubspot_citations = get_demo_citations(entity_name="HubSpot")
    print(f"HubSpot引用件数: {len(hubspot_citations)}")
    print()

    # ロードマップ取得
    print("-" * 60)
    print("ロードマップ取得テスト")
    print("-" * 60)
    roadmap = get_demo_roadmap(limit=5)
    print(f"取得件数: {len(roadmap)}")
    if roadmap:
        first_task = roadmap[0]
        print(f"  タスクID: {first_task['task_id']}")
        print(f"  優先度: {first_task['priority']}")
        print(f"  説明: {first_task['description']}")
        print(f"  インパクト: {first_task['impact_score']}")
        print(f"  作業量: {first_task['effort_score']}")
        print(f"  ステータス: {first_task['status']}")
    print()

    # P0タスクのみ取得
    print("-" * 60)
    print("P0タスク取得テスト")
    print("-" * 60)
    p0_tasks = get_demo_roadmap(priority="P0")
    print(f"P0タスク件数: {len(p0_tasks)}")
    for task in p0_tasks[:3]:
        print(f"  - {task['description']} (Impact: {task['impact_score']})")
    print()

    # 統計情報取得
    print("-" * 60)
    print("統計情報取得テスト")
    print("-" * 60)
    stats = get_demo_stats()
    print(f"思考ログ総数: {stats['thought_logs_count']}")
    print(f"引用データ総数: {stats['citations_count']}")
    print(f"ロードマップ総数: {stats['roadmap_count']}")
    print()
    print("優先度別タスク数:")
    for priority, count in stats['roadmap_by_priority'].items():
        print(f"  {priority}: {count}件")
    print()
    print("ステータス別タスク数:")
    for status, count in stats['roadmap_by_status'].items():
        print(f"  {status}: {count}件")
    print()

    print("=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_demo_mode()
