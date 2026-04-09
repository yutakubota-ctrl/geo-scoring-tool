"""
バッチ処理実行モジュール
定期的なスコアリング実行を管理
"""
import uuid
import logging
from datetime import datetime
from typing import Optional
import yaml
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.database.connection import db
from src.database.models import Brand, Prompt, Response, Score
from src.database.repository import (
    BrandRepository, PromptRepository, ResponseRepository, ScoreRepository
)

# ロガー設定
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchRunner:
    """バッチ処理を実行するクラス"""

    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        self.results = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

    def load_config(self) -> dict:
        """設定ファイルを読み込む"""
        config_path = project_root / "config" / "brands.yaml"
        prompts_path = project_root / "config" / "prompts.yaml"

        config = {}

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config["brands"] = yaml.safe_load(f)

        if prompts_path.exists():
            with open(prompts_path, "r", encoding="utf-8") as f:
                config["prompts"] = yaml.safe_load(f)

        return config

    def setup_brands(self, session, config: dict) -> tuple[Brand, list[Brand]]:
        """ブランドをセットアップ"""
        brands_config = config.get("brands", {})

        # 自社ブランド
        own_brand = BrandRepository.get_own_brand(session)
        if not own_brand and "own_brand" in brands_config:
            own_config = brands_config["own_brand"]
            own_brand = BrandRepository.create(
                session,
                name=own_config.get("name", "自社ブランド"),
                domain=own_config.get("domain"),
                keywords=own_config.get("keywords", []),
                is_own=True,
                reference_facts=own_config.get("reference_facts")
            )
            logger.info(f"自社ブランドを作成: {own_brand.name}")

        # 競合ブランド
        competitors = BrandRepository.get_competitors(session)
        if not competitors and "competitors" in brands_config:
            for comp_config in brands_config["competitors"]:
                comp = BrandRepository.create(
                    session,
                    name=comp_config.get("name"),
                    domain=comp_config.get("domain"),
                    keywords=comp_config.get("keywords", []),
                    is_own=False
                )
                competitors.append(comp)
                logger.info(f"競合ブランドを作成: {comp.name}")

        return own_brand, competitors

    def setup_prompts(self, session, config: dict, brand: Brand) -> list[Prompt]:
        """プロンプトをセットアップ"""
        existing_prompts = PromptRepository.get_active_prompts(session, brand.id)
        if existing_prompts:
            return existing_prompts

        brands_config = config.get("brands", {})
        custom_prompts = brands_config.get("custom_prompts", [])

        prompts = []
        for prompt_config in custom_prompts:
            if prompt_config.get("is_active", True):
                prompt = PromptRepository.create(
                    session,
                    brand_id=brand.id,
                    category=prompt_config.get("category", "general"),
                    template=prompt_config.get("template", ""),
                    is_active=True
                )
                prompts.append(prompt)
                logger.info(f"プロンプトを作成: {prompt.category}")

        return prompts

    def execute_prompt(self, prompt: Prompt, brand: Brand) -> Optional[dict]:
        """
        プロンプトを実行してスコアリング

        注: このメソッドは src/api/gemini_client.py と
            src/scoring/aggregator.py が実装されたら完成します
        """
        try:
            # プロンプトテンプレートを展開
            expanded_prompt = prompt.template.format(
                brand_name=brand.name,
                category="マーケティングツール"  # デフォルトカテゴリ
            )

            logger.info(f"プロンプト実行: {expanded_prompt[:50]}...")

            # TODO: Gemini API呼び出し
            # from src.api.gemini_client import GeminiClient
            # client = GeminiClient()
            # response = client.generate_content(expanded_prompt)

            # 仮のレスポンス（実装後に置き換え）
            response_text = f"[仮の回答] {brand.name}についての情報..."
            response_time = 1000  # ミリ秒

            # TODO: スコアリング実行
            # from src.scoring.aggregator import ScoreAggregator
            # aggregator = ScoreAggregator()
            # scores = aggregator.score_all(response_text, brand)

            # 仮のスコア（実装後に置き換え）
            scores = {
                "visibility": {"score": 10, "detail": {"mentioned": True}},
                "sentiment": {"score": 15, "detail": {"sentiment_type": "positive"}},
                "positioning": {"score": 10, "detail": {"position_ratio": 0.3}},
                "accuracy": {"score": 30, "detail": {"total_score": 30}}
            }

            return {
                "response_text": response_text,
                "response_time_ms": response_time,
                "scores": scores
            }

        except Exception as e:
            logger.error(f"プロンプト実行エラー: {e}")
            return None

    def run(self) -> dict:
        """バッチ処理を実行"""
        logger.info(f"バッチ処理開始: {self.batch_id}")
        start_time = datetime.utcnow()

        try:
            # 設定読み込み
            config = self.load_config()

            with db.get_session() as session:
                # ブランドセットアップ
                own_brand, competitors = self.setup_brands(session, config)

                if not own_brand:
                    raise ValueError("自社ブランドが設定されていません")

                # プロンプトセットアップ
                prompts = self.setup_prompts(session, config, own_brand)

                if not prompts:
                    raise ValueError("プロンプトが設定されていません")

                # 全ブランドに対してスコアリング実行
                all_brands = [own_brand] + competitors

                for prompt in prompts:
                    for brand in all_brands:
                        result = self.execute_prompt(prompt, brand)

                        if result:
                            # 回答を保存
                            response = ResponseRepository.create(
                                session,
                                prompt_id=prompt.id,
                                batch_id=self.batch_id,
                                model_name=settings.GEMINI_MODEL,
                                raw_response=result["response_text"],
                                response_time_ms=result["response_time_ms"]
                            )

                            # スコアを保存
                            scores = result["scores"]
                            ScoreRepository.create(
                                session,
                                response_id=response.id,
                                brand_id=brand.id,
                                visibility_score=scores["visibility"]["score"],
                                sentiment_score=scores["sentiment"]["score"],
                                positioning_score=scores["positioning"]["score"],
                                accuracy_score=scores["accuracy"]["score"],
                                visibility_detail=scores["visibility"]["detail"],
                                sentiment_detail=scores["sentiment"]["detail"],
                                positioning_detail=scores["positioning"]["detail"],
                                accuracy_detail=scores["accuracy"]["detail"]
                            )

                            self.results["success"] += 1
                            logger.info(f"スコアリング完了: {brand.name}")
                        else:
                            self.results["failed"] += 1

                session.commit()

        except Exception as e:
            logger.error(f"バッチ処理エラー: {e}")
            self.results["errors"].append(str(e))

        # 結果サマリー
        end_time = datetime.utcnow()
        self.results["batch_id"] = self.batch_id
        self.results["duration_seconds"] = (end_time - start_time).total_seconds()
        self.results["completed_at"] = end_time.isoformat()

        logger.info(f"バッチ処理完了: 成功={self.results['success']}, 失敗={self.results['failed']}")

        return self.results


def run_batch():
    """バッチ処理を実行するエントリーポイント"""
    runner = BatchRunner()
    return runner.run()


if __name__ == "__main__":
    result = run_batch()
    print(f"バッチ処理結果: {result}")
