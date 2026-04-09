"""
LLM思考ログテーブルモデル

ChatGPT o1等のLLMの思考プロセスを記録するテーブル
7ステップの推論過程、参照URL、最終判断を保存
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, JSON
from sqlalchemy.sql import func
from .base import Base


class LLMThoughtLog(Base):
    """LLM思考ログテーブル"""

    __tablename__ = 'llm_thought_log'

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True)

    # クエリ識別子（一意制約付き）
    query_id = Column(String(36), unique=True, nullable=False, index=True)

    # クエリテキスト
    query_text = Column(Text, nullable=False)

    # 実行日時
    executed_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        index=True
    )

    # 使用したLLMモデル（'chatgpt-o1', 'gemini-1.5-pro'等）
    llm_model = Column(String(50), nullable=False)

    # 7ステップの推論プロセス（JSON形式）
    # 例: {"step_1": "候補ブランド列挙", "step_2": "公式サイト確認", ...}
    thought_trace = Column(JSON)

    # 使用された検索クエリ群（JSON配列として保存）
    search_queries_used = Column(JSON)

    # 参照されたURL（JSON配列として保存）
    selected_urls = Column(JSON)

    # 最終判断の根拠
    final_reasoning = Column(Text)

    # 各ブランドの言及状況（JSON形式）
    # 例: {"HubSpot": {"mentioned": true, "position": 1}, ...}
    brand_mentions = Column(JSON)

    def __repr__(self):
        return f"<LLMThoughtLog(query_id='{self.query_id}', model='{self.llm_model}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'query_id': self.query_id,
            'query_text': self.query_text,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'llm_model': self.llm_model,
            'thought_trace': self.thought_trace,
            'search_queries_used': self.search_queries_used,
            'selected_urls': self.selected_urls,
            'final_reasoning': self.final_reasoning,
            'brand_mentions': self.brand_mentions
        }
