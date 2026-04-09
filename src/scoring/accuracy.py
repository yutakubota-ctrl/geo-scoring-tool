"""
情報正確性スコアラー（Accuracy Scorer）
テキスト内の情報の正確性を参照情報と比較して評価
"""
import logging
from typing import Optional

from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.scoring.base_scorer import BaseScorer, ScoringResult, ScoringError

# ログ設定
logger = logging.getLogger(__name__)


class AccuracyScorer(BaseScorer):
    """
    情報正確性スコアを計算するクラス

    評価基準（各10点、合計40点）:
    1. 製品情報の正確性（10点）
    2. 機能・特徴の正確性（10点）
    3. 価格情報の正確性（10点）
    4. 企業情報の正確性（10点）

    参照情報との比較により、誤情報の有無を判定
    """

    # 評価プロンプトテンプレート
    EVALUATION_PROMPT = """
あなたは「情報検証」の専門家です。
以下のテキストを分析し、指定されたブランドに関する情報の正確性を評価してください。

## 評価対象ブランド
{brand_name}

## 参照情報（正確な事実）
{reference_info}

## 評価カテゴリ（各10点満点、合計40点）

### 1. 製品情報の正確性（0〜10点）
- 製品名、型番、バージョンなどが正確か
- 10点: 完全に正確
- 7-9点: ほぼ正確（軽微な誤りのみ）
- 4-6点: 一部不正確
- 1-3点: 多くの誤り
- 0点: 重大な誤情報、または該当情報なし

### 2. 機能・特徴の正確性（0〜10点）
- 製品やサービスの機能説明が正確か
- スペック、性能値などが正確か

### 3. 価格情報の正確性（0〜10点）
- 価格、料金プランが正確か
- キャンペーン情報などが正確か
- 価格情報がない場合は参照情報と照合して判断

### 4. 企業情報の正確性（0〜10点）
- 会社名、本社所在地、設立年などが正確か
- サービス提供地域、対応言語などが正確か

## 出力形式（JSON）
{{
    "product_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した製品情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "feature_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した機能情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "price_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した価格情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "company_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した企業情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "total_score": 合計スコア（0〜40）,
    "overall_reasoning": "総合評価の説明",
    "critical_errors": ["重大な誤情報のリスト（あれば）"]
}}

注意:
- 参照情報に記載のない項目については、一般的な事実と照合してください
- 明らかな誤情報がある場合は厳しく評価してください
- 該当カテゴリの情報がテキストにない場合は0点としてください
"""

    # 参照情報がない場合のデフォルトプロンプト
    NO_REFERENCE_PROMPT = """
あなたは「情報検証」の専門家です。
以下のテキストを分析し、指定されたブランドに関する情報の正確性を評価してください。

## 評価対象ブランド
{brand_name}

## 注意
参照情報が提供されていません。
一般的に知られている事実やあなたの知識に基づいて評価してください。
明らかな誤りのみを指摘し、確認できない情報は「検証不可」として扱ってください。

## 評価カテゴリ（各10点満点、合計40点）

### 1. 製品情報の正確性（0〜10点）
### 2. 機能・特徴の正確性（0〜10点）
### 3. 価格情報の正確性（0〜10点）
### 4. 企業情報の正確性（0〜10点）

## 出力形式（JSON）
{{
    "product_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した製品情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "feature_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した機能情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "price_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した価格情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "company_accuracy": {{
        "score": 0〜10,
        "found_info": ["テキストから抽出した企業情報"],
        "errors": ["発見された誤り"],
        "reasoning": "評価理由"
    }},
    "total_score": 合計スコア（0〜40）,
    "overall_reasoning": "総合評価の説明",
    "critical_errors": ["重大な誤情報のリスト（あれば）"]
}}
"""

    def __init__(self, client: Optional[GeminiClient] = None):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
        """
        super().__init__(
            client=client,
            max_score=settings.MAX_ACCURACY_SCORE,
            min_score=0
        )

    @property
    def scorer_name(self) -> str:
        """スコアラー名"""
        return "情報正確性スコアラー"

    def score(
        self,
        text: str,
        brand_name: str,
        reference_info: Optional[str] = None,
        **kwargs
    ) -> ScoringResult:
        """
        情報正確性スコアを計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名
            reference_info: 正確性検証用の参照情報（オプション）

        戻り値:
            ScoringResult: スコア（0〜40）と評価詳細
        """
        # 評価プロンプトを構築
        if reference_info:
            prompt = self.EVALUATION_PROMPT.format(
                brand_name=brand_name,
                reference_info=reference_info
            )
        else:
            prompt = self.NO_REFERENCE_PROMPT.format(brand_name=brand_name)

        try:
            # Gemini APIで評価を実行
            context = {"ブランド名": brand_name}
            if reference_info:
                context["参照情報あり"] = "はい"

            result = self.client.evaluate_with_prompt(
                evaluation_prompt=prompt,
                text=text,
                context=context
            )

            # 各カテゴリのスコアを抽出
            product = result.get("product_accuracy", {})
            feature = result.get("feature_accuracy", {})
            price = result.get("price_accuracy", {})
            company = result.get("company_accuracy", {})

            product_score = product.get("score", 0)
            feature_score = feature.get("score", 0)
            price_score = price.get("score", 0)
            company_score = company.get("score", 0)

            # 合計スコアを計算
            total_score = result.get("total_score")
            if total_score is None:
                total_score = product_score + feature_score + price_score + company_score

            overall_reasoning = result.get("overall_reasoning", "評価理由が取得できませんでした")
            critical_errors = result.get("critical_errors", [])

            # 詳細な評価理由を構築
            detail_parts = [
                overall_reasoning,
                "",
                f"製品情報: {product_score}/10点 - {product.get('reasoning', '')}",
                f"機能・特徴: {feature_score}/10点 - {feature.get('reasoning', '')}",
                f"価格情報: {price_score}/10点 - {price.get('reasoning', '')}",
                f"企業情報: {company_score}/10点 - {company.get('reasoning', '')}"
            ]

            if critical_errors:
                detail_parts.append("")
                detail_parts.append(f"重大な誤情報: {', '.join(critical_errors)}")

            return ScoringResult(
                score=total_score,
                reasoning="\n".join(detail_parts),
                raw_response=result
            )

        except Exception as e:
            logger.error(f"正確性スコア評価エラー: {e}")
            raise ScoringError(f"正確性スコアの評価に失敗しました: {e}") from e

    def get_category_scores(self, raw_response: dict) -> dict[str, int]:
        """
        生のレスポンスから各カテゴリのスコアを抽出

        引数:
            raw_response: APIからの生のレスポンス

        戻り値:
            カテゴリ名とスコアの辞書
        """
        return {
            "product": raw_response.get("product_accuracy", {}).get("score", 0),
            "feature": raw_response.get("feature_accuracy", {}).get("score", 0),
            "price": raw_response.get("price_accuracy", {}).get("score", 0),
            "company": raw_response.get("company_accuracy", {}).get("score", 0)
        }

    def get_accuracy_label(self, score: int) -> str:
        """
        スコアから正確性ラベルを取得

        引数:
            score: 正確性スコア（0〜40）

        戻り値:
            正確性ラベル（日本語）
        """
        percentage = (score / self.max_score) * 100

        if percentage >= 90:
            return "非常に正確"
        elif percentage >= 70:
            return "概ね正確"
        elif percentage >= 50:
            return "一部不正確"
        elif percentage >= 30:
            return "多くの誤り"
        else:
            return "重大な誤情報あり"
