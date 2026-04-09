"""
データベースリポジトリ
CRUD操作を提供
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.database.models import Brand, Prompt, Response, Score
from src.database.connection import db


class BrandRepository:
    """ブランドのCRUD操作"""

    @staticmethod
    def create(session: Session, name: str, domain: str = None,
               keywords: list = None, is_own: bool = False,
               reference_facts: str = None) -> Brand:
        """ブランドを作成"""
        brand = Brand(
            name=name,
            domain=domain,
            keywords=keywords or [],
            is_own=is_own,
            reference_facts=reference_facts
        )
        session.add(brand)
        session.flush()
        return brand

    @staticmethod
    def get_by_id(session: Session, brand_id: int) -> Optional[Brand]:
        """IDでブランドを取得"""
        return session.query(Brand).filter(Brand.id == brand_id).first()

    @staticmethod
    def get_own_brand(session: Session) -> Optional[Brand]:
        """自社ブランドを取得"""
        return session.query(Brand).filter(Brand.is_own == True).first()

    @staticmethod
    def get_competitors(session: Session) -> list[Brand]:
        """競合ブランドを取得"""
        return session.query(Brand).filter(Brand.is_own == False).all()

    @staticmethod
    def get_all(session: Session) -> list[Brand]:
        """全ブランドを取得"""
        return session.query(Brand).all()


class PromptRepository:
    """プロンプトのCRUD操作"""

    @staticmethod
    def create(session: Session, brand_id: int, category: str,
               template: str, is_active: bool = True) -> Prompt:
        """プロンプトを作成"""
        prompt = Prompt(
            brand_id=brand_id,
            category=category,
            template=template,
            is_active=is_active
        )
        session.add(prompt)
        session.flush()
        return prompt

    @staticmethod
    def get_active_prompts(session: Session, brand_id: int = None) -> list[Prompt]:
        """有効なプロンプトを取得"""
        query = session.query(Prompt).filter(Prompt.is_active == True)
        if brand_id:
            query = query.filter(Prompt.brand_id == brand_id)
        return query.all()

    @staticmethod
    def get_by_category(session: Session, category: str) -> list[Prompt]:
        """カテゴリでプロンプトを取得"""
        return session.query(Prompt).filter(Prompt.category == category).all()


class ResponseRepository:
    """回答のCRUD操作"""

    @staticmethod
    def create(session: Session, prompt_id: int, batch_id: str,
               model_name: str, raw_response: str,
               response_time_ms: int = None, token_count: int = None) -> Response:
        """回答を作成"""
        response = Response(
            prompt_id=prompt_id,
            batch_id=batch_id,
            model_name=model_name,
            raw_response=raw_response,
            response_time_ms=response_time_ms,
            token_count=token_count
        )
        session.add(response)
        session.flush()
        return response

    @staticmethod
    def get_by_batch(session: Session, batch_id: str) -> list[Response]:
        """バッチIDで回答を取得"""
        return session.query(Response).filter(Response.batch_id == batch_id).all()

    @staticmethod
    def get_latest(session: Session, limit: int = 100) -> list[Response]:
        """最新の回答を取得"""
        return session.query(Response).order_by(
            desc(Response.executed_at)
        ).limit(limit).all()


class ScoreRepository:
    """スコアのCRUD操作"""

    @staticmethod
    def create(session: Session, response_id: int, brand_id: int,
               visibility_score: int, sentiment_score: int,
               positioning_score: int, accuracy_score: int,
               visibility_detail: dict = None, sentiment_detail: dict = None,
               positioning_detail: dict = None, accuracy_detail: dict = None) -> Score:
        """スコアを作成"""
        total_score = visibility_score + sentiment_score + positioning_score + accuracy_score
        score = Score(
            response_id=response_id,
            brand_id=brand_id,
            visibility_score=visibility_score,
            sentiment_score=sentiment_score,
            positioning_score=positioning_score,
            accuracy_score=accuracy_score,
            total_score=total_score,
            visibility_detail=visibility_detail,
            sentiment_detail=sentiment_detail,
            positioning_detail=positioning_detail,
            accuracy_detail=accuracy_detail
        )
        session.add(score)
        session.flush()
        return score

    @staticmethod
    def get_by_brand(session: Session, brand_id: int,
                     start_date: datetime = None, end_date: datetime = None) -> list[Score]:
        """ブランドのスコアを取得"""
        query = session.query(Score).filter(Score.brand_id == brand_id)
        if start_date:
            query = query.filter(Score.created_at >= start_date)
        if end_date:
            query = query.filter(Score.created_at <= end_date)
        return query.order_by(desc(Score.created_at)).all()

    @staticmethod
    def get_latest_by_brand(session: Session, brand_id: int) -> Optional[Score]:
        """ブランドの最新スコアを取得"""
        return session.query(Score).filter(
            Score.brand_id == brand_id
        ).order_by(desc(Score.created_at)).first()

    @staticmethod
    def get_average_scores(session: Session, brand_id: int,
                           days: int = 30) -> dict:
        """指定期間の平均スコアを取得"""
        start_date = datetime.utcnow() - timedelta(days=days)
        result = session.query(
            func.avg(Score.visibility_score).label("avg_visibility"),
            func.avg(Score.sentiment_score).label("avg_sentiment"),
            func.avg(Score.positioning_score).label("avg_positioning"),
            func.avg(Score.accuracy_score).label("avg_accuracy"),
            func.avg(Score.total_score).label("avg_total")
        ).filter(
            Score.brand_id == brand_id,
            Score.created_at >= start_date
        ).first()

        return {
            "visibility": round(result.avg_visibility or 0, 1),
            "sentiment": round(result.avg_sentiment or 0, 1),
            "positioning": round(result.avg_positioning or 0, 1),
            "accuracy": round(result.avg_accuracy or 0, 1),
            "total": round(result.avg_total or 0, 1)
        }

    @staticmethod
    def get_score_trend(session: Session, brand_id: int,
                        days: int = 90) -> list[dict]:
        """スコアのトレンドデータを取得"""
        start_date = datetime.utcnow() - timedelta(days=days)
        scores = session.query(Score).filter(
            Score.brand_id == brand_id,
            Score.created_at >= start_date
        ).order_by(Score.created_at).all()

        return [
            {
                "date": score.created_at.strftime("%Y-%m-%d"),
                "total": score.total_score,
                "visibility": score.visibility_score,
                "sentiment": score.sentiment_score,
                "positioning": score.positioning_score,
                "accuracy": score.accuracy_score
            }
            for score in scores
        ]

    @staticmethod
    def get_comparison_data(session: Session, brand_ids: list[int],
                            days: int = 30) -> dict:
        """複数ブランドの比較データを取得"""
        result = {}
        for brand_id in brand_ids:
            result[brand_id] = ScoreRepository.get_average_scores(
                session, brand_id, days
            )
        return result
