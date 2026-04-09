"""
デモモード機能

環境変数 DEMO_MODE=true で自動的にデモデータを使用するヘルパー機能

使用例:
    from src.utils.demo_mode import is_demo_mode, load_demo_data

    if is_demo_mode():
        thought_logs = load_demo_data("thought_logs")
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path


# デモデータのディレクトリパス
DEMO_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "demo"


def is_demo_mode() -> bool:
    """
    デモモードが有効かどうかを判定

    環境変数 DEMO_MODE=true または DEMO_MODE=1 の場合に True を返す

    Returns:
        デモモードが有効な場合 True
    """
    demo_mode_value = os.getenv("DEMO_MODE", "false").lower()
    return demo_mode_value in ["true", "1", "yes", "on"]


def load_demo_data(data_type: str) -> Optional[List[Dict]]:
    """
    デモデータをロード

    Args:
        data_type: データタイプ（"thought_logs", "citations", "roadmap"）

    Returns:
        デモデータのリスト。ファイルが存在しない場合は None

    Raises:
        ValueError: 不正なdata_typeが指定された場合
    """
    valid_types = ["thought_logs", "citations", "roadmap"]

    if data_type not in valid_types:
        raise ValueError(
            f"不正なdata_typeです: {data_type}. "
            f"有効な値: {', '.join(valid_types)}"
        )

    filename = f"{data_type}.json"
    filepath = DEMO_DATA_DIR / filename

    if not filepath.exists():
        print(f"警告: デモデータファイルが見つかりません: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"デモデータをロードしました: {filename} ({len(data)}件)")
        return data
    except json.JSONDecodeError as e:
        print(f"エラー: デモデータの読み込みに失敗しました: {e}")
        return None


def get_demo_thought_logs(limit: Optional[int] = None) -> List[Dict]:
    """
    デモ思考ログを取得

    Args:
        limit: 取得件数の上限（指定しない場合は全件）

    Returns:
        思考ログのリスト
    """
    data = load_demo_data("thought_logs") or []

    if limit is not None and limit > 0:
        return data[:limit]

    return data


def get_demo_citations(
    entity_name: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    デモ引用データを取得

    Args:
        entity_name: フィルタする企業名（指定しない場合は全件）
        limit: 取得件数の上限（指定しない場合は全件）

    Returns:
        引用データのリスト
    """
    data = load_demo_data("citations") or []

    # 企業名でフィルタ
    if entity_name:
        data = [
            citation for citation in data
            if citation.get("entity_name") == entity_name
        ]

    # 件数制限
    if limit is not None and limit > 0:
        return data[:limit]

    return data


def get_demo_roadmap(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    デモロードマップを取得

    Args:
        priority: フィルタする優先度（"P0", "P1", "P2"）
        status: フィルタするステータス（"pending", "in_progress", "completed"）
        limit: 取得件数の上限（指定しない場合は全件）

    Returns:
        ロードマップタスクのリスト
    """
    data = load_demo_data("roadmap") or []

    # 優先度でフィルタ
    if priority:
        data = [
            task for task in data
            if task.get("priority") == priority
        ]

    # ステータスでフィルタ
    if status:
        data = [
            task for task in data
            if task.get("status") == status
        ]

    # 件数制限
    if limit is not None and limit > 0:
        return data[:limit]

    return data


def get_demo_stats() -> Dict:
    """
    デモデータの統計情報を取得

    Returns:
        統計情報の辞書
    """
    thought_logs = load_demo_data("thought_logs") or []
    citations = load_demo_data("citations") or []
    roadmap = load_demo_data("roadmap") or []

    return {
        "thought_logs_count": len(thought_logs),
        "citations_count": len(citations),
        "roadmap_count": len(roadmap),
        "roadmap_by_priority": {
            "P0": len([t for t in roadmap if t.get("priority") == "P0"]),
            "P1": len([t for t in roadmap if t.get("priority") == "P1"]),
            "P2": len([t for t in roadmap if t.get("priority") == "P2"])
        },
        "roadmap_by_status": {
            "pending": len([t for t in roadmap if t.get("status") == "pending"]),
            "in_progress": len([t for t in roadmap if t.get("status") == "in_progress"]),
            "completed": len([t for t in roadmap if t.get("status") == "completed"])
        }
    }


def print_demo_mode_banner():
    """
    デモモード有効時にバナーを表示
    """
    if is_demo_mode():
        print("=" * 60)
        print("  デモモードが有効です")
        print("  サンプルデータを使用して動作を確認できます")
        print("=" * 60)
        print()


# モジュールロード時にバナー表示
if __name__ != "__main__":
    print_demo_mode_banner()
