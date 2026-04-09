"""
引用マスターテーブルモデル

AI Overviews、ChatGPT、Gemini等での引用状況を追跡するテーブル
ブランド名ごとのメンション数、感情スコア、参照順位を記録
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class CitationMaster(Base):
    """引用マスターテーブル"""

    __tablename__ = 'citation_master'

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 引用識別子（一意制約付き）
    citation_id = Column(String(36), unique=True, nullable=False)

    # クエリID（外部キー）
    query_id = Column(
        String(36),
        ForeignKey('llm_thought_log.query_id'),
        index=True
    )

    # ブランド名・エンティティ名
    entity_name = Column(String(255), nullable=False, index=True)

    # メンション数
    mention_count = Column(Integer, default=0)

    # 感情スコア（-1.00 〜 1.00）
    sentiment_score = Column(DECIMAL(3, 2))

    # 参照タイプ（'AI_Overview', 'ChatGPT', 'Gemini'等）
    reference_type = Column(String(50))

    # 参照元URL
    source_url = Column(Text)

    # 参照元ドメイン
    source_domain = Column(String(255))

    # 回答内での出現位置（文字位置）
    position_in_response = Column(Integer)

    # 参照元リンクでの順位（1位、2位等）
    reference_rank = Column(Integer)

    # 引用文脈スニペット
    context_snippet = Column(Text)

    # 作成日時
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    def __repr__(self):
        return f"<CitationMaster(entity='{self.entity_name}', type='{self.reference_type}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'citation_id': self.citation_id,
            'query_id': self.query_id,
            'entity_name': self.entity_name,
            'mention_count': self.mention_count,
            'sentiment_score': float(self.sentiment_score) if self.sentiment_score else None,
            'reference_type': self.reference_type,
            'source_url': self.source_url,
            'source_domain': self.source_domain,
            'position_in_response': self.position_in_response,
            'reference_rank': self.reference_rank,
            'context_snippet': self.context_snippet,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
