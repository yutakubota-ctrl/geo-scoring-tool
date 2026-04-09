"""
データベースモデル定義
SQLAlchemyを使用したテーブル定義
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Brand(Base):
    """ブランドマスター（自社・競合）"""
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="ブランド名")
    domain = Column(String(255), comment="公式サイトドメイン")
    keywords = Column(JSON, comment="関連キーワード（リスト）")
    is_own = Column(Boolean, default=False, comment="自社ブランドか")
    reference_facts = Column(Text, comment="正確性検証用の参照情報")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    prompts = relationship("Prompt", back_populates="brand")
    scores = relationship("Score", back_populates="brand")

    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', is_own={self.is_own})>"


class Prompt(Base):
    """監視プロンプトマスター"""
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    category = Column(String(100), comment="カテゴリ（比較・検討、課題解決など）")
    template = Column(Text, nullable=False, comment="プロンプトテンプレート")
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    brand = relationship("Brand", back_populates="prompts")
    responses = relationship("Response", back_populates="prompt")

    def __repr__(self):
        return f"<Prompt(id={self.id}, category='{self.category}')>"


class Response(Base):
    """Geminiからの回答データ"""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    batch_id = Column(String(36), comment="バッチ実行ID（UUID）")
    executed_at = Column(DateTime, default=datetime.utcnow, comment="実行日時")
    model_name = Column(String(100), comment="使用モデル名")
    raw_response = Column(Text, comment="AIの生回答")
    response_time_ms = Column(Integer, comment="応答時間（ミリ秒）")
    token_count = Column(Integer, comment="トークン数")

    # リレーション
    prompt = relationship("Prompt", back_populates="responses")
    scores = relationship("Score", back_populates="response")

    def __repr__(self):
        return f"<Response(id={self.id}, batch_id='{self.batch_id}')>"


class Score(Base):
    """スコアリング結果"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)

    # 4つのスコア指標
    visibility_score = Column(Integer, comment="認知スコア（0 or 10）")
    sentiment_score = Column(Integer, comment="推奨度スコア（-10〜30）")
    positioning_score = Column(Integer, comment="ポジションスコア（0〜20）")
    accuracy_score = Column(Integer, comment="正確性スコア（0〜40）")
    total_score = Column(Integer, comment="総合スコア")

    # 評価詳細（JSON形式）
    visibility_detail = Column(JSON, comment="認知評価詳細")
    sentiment_detail = Column(JSON, comment="推奨度評価詳細")
    positioning_detail = Column(JSON, comment="ポジション評価詳細")
    accuracy_detail = Column(JSON, comment="正確性評価詳細")

    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    response = relationship("Response", back_populates="scores")
    brand = relationship("Brand", back_populates="scores")

    def __repr__(self):
        return f"<Score(id={self.id}, total={self.total_score})>"

    def calculate_total(self) -> int:
        """総合スコアを計算"""
        return (
            (self.visibility_score or 0) +
            (self.sentiment_score or 0) +
            (self.positioning_score or 0) +
            (self.accuracy_score or 0)
        )
