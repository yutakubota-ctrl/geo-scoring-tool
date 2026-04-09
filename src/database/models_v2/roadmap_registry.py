"""
ロードマップレジストリテーブルモデル

Gap_Strategistが生成した優先順位付きタスクを管理するテーブル
Impact × Effort マトリクスに基づく優先度付け
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, Date
from sqlalchemy.sql import func
from .base import Base


class RoadmapRegistry(Base):
    """ロードマップレジストリテーブル"""

    __tablename__ = 'roadmap_registry'

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True)

    # タスク識別子（一意制約付き）
    task_id = Column(String(36), unique=True, nullable=False)

    # 作成日時
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    # 優先度（'P0', 'P1', 'P2', 'P3'）
    priority = Column(String(10), nullable=False, index=True)

    # タスクタイプ（'Technical', 'Content', 'Analytics'）
    task_type = Column(String(50))

    # タスク説明
    description = Column(Text, nullable=False)

    # 担当者（'Gem_02', 'Human'等）
    assigned_to = Column(String(50))

    # ステータス（'Pending', 'In_Progress', 'Done'）
    status = Column(String(20), default='Pending', index=True)

    # 期限日
    due_date = Column(Date)

    # インパクトスコア（1-10）
    impact_score = Column(Integer)

    # 実装難易度スコア（1-10）
    effort_score = Column(Integer)

    # 親ギャップID（どの分析結果から生成されたか）
    parent_gap_id = Column(String(36))

    # 承認ステータス（'Draft', 'Approved', 'Rejected'）
    approval_status = Column(String(20), default='Draft')

    def __repr__(self):
        return f"<RoadmapRegistry(task_id='{self.task_id}', priority='{self.priority}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'priority': self.priority,
            'task_type': self.task_type,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'impact_score': self.impact_score,
            'effort_score': self.effort_score,
            'parent_gap_id': self.parent_gap_id,
            'approval_status': self.approval_status
        }
