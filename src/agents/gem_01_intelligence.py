"""
Gem_01: GEO Intelligence Analyst

ChatGPT o1の思考プロセスを解析し、
AIが「どう考えて、どのブランドを選んだか」を逆算するエージェント。

v2.1_design.md 第4章「Gem_01詳細設計」に基づく実装
v2.1_video_implementation_guide.md 手法#10「ChatGPT思考プロセス分析」
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic

from src.analytics.thought_parser import ThoughtParser, MockThoughtParser

logger = logging.getLogger(__name__)


class Gem01Intelligence:
    """
    GEO Intelligence Analyst

    ChatGPT o1の思考プロセスを解析する専門エージェント
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        mock_mode: bool = False
    ):
        """
        初期化

        Args:
            openai_api_key: OpenAI APIキー（省略時は環境変数から取得）
            anthropic_api_key: Anthropic APIキー（省略時は環境変数から取得）
            mock_mode: モックモード（True: 実際のAPIを呼ばずにダミーデータ使用）
        """
        self.mock_mode = mock_mode

        if not mock_mode:
            # 本番モード: 実際のAPIクライアント初期化
            self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI APIキーが設定されていません。"
                    "環境変数 OPENAI_API_KEY を設定してください。"
                )
            if not self.anthropic_api_key:
                raise ValueError(
                    "Anthropic APIキーが設定されていません。"
                    "環境変数 ANTHROPIC_API_KEY を設定してください。"
                )

            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.thought_parser = ThoughtParser(self.anthropic_api_key)
            logger.info("[Gem_01] 本番モードで初期化完了")

        else:
            # モックモード
            self.thought_parser = MockThoughtParser()
            logger.info("[Gem_01] モックモードで初期化完了")

    def analyze_chatgpt_thinking(
        self,
        query: str,
        model: str = "o1-preview"
    ) -> Dict:
        """
        ChatGPT o1の思考プロセスを解析

        Args:
            query: 検索クエリ（例: "マーケティングツール おすすめ"）
            model: 使用するモデル（o1-preview または o1-mini）

        Returns:
            思考トレース、参照URL、推論プロセスを含む辞書
        """
        logger.info(f"[Gem_01] ChatGPT思考プロセス分析開始: {query}")
        logger.info(f"[Gem_01] 使用モデル: {model}")

        if self.mock_mode:
            # モックモード: ダミーデータを返す
            return self._mock_analyze(query)

        try:
            # Step 1: ChatGPT o1に検索クエリを投げる
            chatgpt_response = self._query_chatgpt(query, model)

            # Step 2: 思考プロセス（reasoning_content）を抽出
            thinking_steps = chatgpt_response.get("thinking", "")
            final_answer = chatgpt_response.get("answer", "")

            if not thinking_steps:
                logger.warning("[Gem_01] reasoning_contentが空です")
                return {
                    "error": "reasoning_contentが取得できませんでした",
                    "query": query,
                    "answer": final_answer
                }

            logger.info(f"[Gem_01] 思考ステップ取得完了（{len(thinking_steps)} 文字）")

            # Step 3: Claudeで思考プロセスを構造化
            analysis = self.thought_parser.parse_thinking(
                thinking_steps,
                final_answer,
                query
            )

            # Step 4: 結果をまとめる
            thought_log = self._build_thought_log(query, analysis, model)

            # Step 5: データベース保存（オプション）
            # self._save_to_db(thought_log)

            logger.info("[Gem_01] 分析完了")
            return thought_log

        except Exception as e:
            logger.error(f"[Gem_01] 分析エラー: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "query": query
            }

    def _query_chatgpt(self, query: str, model: str) -> Dict:
        """
        ChatGPT o1にクエリを投げる

        Args:
            query: 検索クエリ
            model: モデル名

        Returns:
            思考プロセスと最終回答
        """
        logger.debug(f"[Gem_01] ChatGPT o1呼び出し: {query}")

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": f"""
以下の検索クエリについて、おすすめのツール・サービスを3つ挙げてください：

"{query}"

各ツールについて、以下を明記してください：
- なぜそのツールを選んだか
- どの情報源を参考にしたか
- どのような基準で評価したか
"""
                }]
            )

            # reasoning_content を取得
            message = response.choices[0].message

            # o1モデルの場合、reasoning_contentが含まれる可能性がある
            thinking = getattr(message, "reasoning_content", None) or ""
            final_answer = message.content or ""

            return {
                "thinking": thinking,
                "answer": final_answer
            }

        except Exception as e:
            logger.error(f"[Gem_01] ChatGPT呼び出しエラー: {str(e)}")
            raise

    def _build_thought_log(
        self,
        query: str,
        analysis: Dict,
        model: str
    ) -> Dict:
        """
        思考ログを構築

        Args:
            query: 検索クエリ
            analysis: 分析結果
            model: 使用モデル

        Returns:
            思考ログ辞書
        """
        query_id = self._generate_query_id()

        return {
            "query_id": query_id,
            "query_text": query,
            "executed_at": datetime.now().isoformat(),
            "llm_model": model,
            "thought_trace": analysis.get("7ステップの分解", {}),
            "search_queries_used": analysis.get("検索クエリ候補", []),
            "selected_urls": analysis.get("参照URL", []),
            "final_reasoning": analysis.get("最終推論", ""),
            "brand_mentions": analysis.get("ブランドメンション", [])
        }

    def _generate_query_id(self) -> str:
        """
        クエリIDを生成

        Returns:
            クエリID（例: q_20260409_120530）
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"q_{timestamp}"

    def _mock_analyze(self, query: str) -> Dict:
        """
        モック分析（ダミーデータ）

        Args:
            query: 検索クエリ

        Returns:
            ダミーの思考ログ
        """
        logger.info(f"[Gem_01] モック分析実行: {query}")

        # モックパーサーで分析
        mock_analysis = self.thought_parser.parse_thinking("", "", query)

        # 思考ログを構築
        return self._build_thought_log(query, mock_analysis, "o1-preview (mock)")

    def _save_to_db(self, thought_log: Dict) -> None:
        """
        PostgreSQLのllm_thought_logテーブルに保存

        Args:
            thought_log: 思考ログ辞書

        注意:
            現時点では未実装。将来的にRepositoryクラスを通じて保存する。
        """
        # TODO: データベース保存を実装
        # from src.database.repository import ThoughtLogRepository
        # repo = ThoughtLogRepository()
        # repo.save(thought_log)

        logger.debug("[Gem_01] データベース保存は未実装（スキップ）")


class MockGem01Intelligence:
    """
    完全モックエージェント（テスト用）

    OpenAI/Anthropic APIを一切呼ばずに固定データを返す
    """

    def __init__(self):
        """初期化（何もしない）"""
        logger.info("[MockGem01Intelligence] モックエージェント初期化")

    def analyze_chatgpt_thinking(
        self,
        query: str,
        model: str = "o1-preview"
    ) -> Dict:
        """
        固定のモックデータを返す

        Args:
            query: 検索クエリ
            model: モデル名（未使用）

        Returns:
            ダミー思考ログ
        """
        logger.info(f"[MockGem01Intelligence] モック分析: {query}")

        return {
            "query_id": f"q_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "query_text": query,
            "executed_at": datetime.now().isoformat(),
            "llm_model": f"{model} (mock)",
            "thought_trace": {
                "step_1": "HubSpot, Marketo, Salesforce等を候補として列挙",
                "step_2": "HubSpot公式サイト（hubspot.com）を確認し、機能概要を把握",
                "step_3": "G2.com、Capterra等のレビューサイトで評価を参照",
                "step_4": "該当なし",
                "step_5": "各ツールの料金プランを比較し、中小企業向けかエンタープライズ向けかを判断",
                "step_6": "Twitter、Redditでの口コミを確認",
                "step_7": "HubSpotは中小企業向け、Marketoは大企業向けと判断し、推奨順位を決定"
            },
            "search_queries_used": [
                "marketing automation tools comparison",
                "HubSpot pricing 2026",
                "Marketo vs HubSpot",
                "Salesforce Marketing Cloud review",
                "best marketing tools for small business"
            ],
            "selected_urls": [
                "hubspot.com",
                "g2.com",
                "capterra.com",
                "salesforce.com",
                "marketo.com"
            ],
            "final_reasoning": "HubSpotは中小企業向けで使いやすく、Marketoはエンタープライズ向けで高機能だが複雑と判断",
            "brand_mentions": [
                {"brand": "HubSpot", "sentiment": "positive"},
                {"brand": "Marketo", "sentiment": "neutral"},
                {"brand": "Salesforce", "sentiment": "positive"}
            ]
        }
