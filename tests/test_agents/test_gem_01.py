"""
Gem_01: GEO Intelligence Analyst のユニットテスト

v2.1設計書 第4章に基づく ChatGPT o1 思考プロセス解析のテスト
動画手法 #10「ChatGPT思考プロセス分析」の実装検証
"""
import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch


class MockGem01Intelligence:
    """
    Gem_01の実装プロトタイプ（テスト用）

    実際の実装は src/agents/gem_01_intelligence.py に配置予定
    このモッククラスは期待される動作を定義
    """

    def __init__(self, openai_client=None, claude_client=None):
        self.openai_client = openai_client
        self.claude_client = claude_client

    def analyze_chatgpt_thinking(self, query: str) -> dict:
        """
        ChatGPT o1の思考プロセスを解析

        Args:
            query: 検索クエリ

        Returns:
            思考トレース、参照URL、推論プロセス
        """
        # Step 1: ChatGPT o1 に検索クエリを投げる
        chatgpt_response = self.openai_client.chat.completions.create(
            model="o1-preview",
            messages=[{
                "role": "user",
                "content": f"以下のクエリについておすすめを教えて: {query}"
            }]
        )

        # Step 2: 思考プロセスを抽出
        thinking_steps = chatgpt_response.choices[0].message.reasoning_content
        final_answer = chatgpt_response.choices[0].message.content

        # Step 3: Claudeで構造化
        analysis = self.analyze_with_claude(thinking_steps, final_answer, query)

        # Step 4: 結果を返す
        return {
            "query_id": self.generate_query_id(),
            "query_text": query,
            "llm_model": "ChatGPT o1-preview",
            "thought_trace": analysis.get("7ステップの分解", {}),
            "search_queries_used": analysis.get("検索クエリ候補", []),
            "selected_urls": analysis.get("参照URL", []),
            "final_reasoning": analysis.get("最終推論", "")
        }

    def analyze_with_claude(self, thinking: str, answer: str, query: str) -> dict:
        """Claudeで思考プロセスを構造化"""
        prompt = f"""
        以下はChatGPT o1の推論プロセスです。
        7ステップを抽出し、JSON形式で返してください。

        【検索クエリ】{query}
        【思考プロセス】{thinking}
        【最終回答】{answer}
        """

        response = self.claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis_text = response.content[0].text

        # JSONブロック抽出
        if "```json" in analysis_text:
            json_start = analysis_text.find("```json") + 7
            json_end = analysis_text.find("```", json_start)
            json_str = analysis_text[json_start:json_end].strip()
        else:
            json_str = analysis_text

        return json.loads(json_str)

    def generate_query_id(self) -> str:
        """クエリID生成（例: q_20260409_120000）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"q_{timestamp}"

    def extract_7_steps(self, thought_trace: dict) -> list:
        """7ステップを抽出"""
        steps = []
        for i in range(1, 8):
            step_key = f"step_{i}"
            if step_key in thought_trace:
                steps.append(thought_trace[step_key])
        return steps

    def identify_missing_brand_reason(self, thought_trace: dict, brand_name: str) -> str:
        """自社ブランドが言及されなかった理由を特定"""
        # 7ステップ全体からブランド名を検索
        all_steps = " ".join([str(v) for v in thought_trace.values()])

        if brand_name.lower() in all_steps.lower():
            return f"{brand_name}は候補に挙がったが最終選考で落選"
        else:
            return f"{brand_name}は候補にも挙がらなかった（認知不足）"


class TestGem01BasicFunctionality:
    """Gem_01の基本機能テスト"""

    def test_analyze_chatgpt_thinking_returns_valid_structure(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """ChatGPT思考分析が正しい構造を返すか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")

        # 必須キーが含まれているか
        assert "query_id" in result
        assert "query_text" in result
        assert "llm_model" in result
        assert "thought_trace" in result
        assert "search_queries_used" in result
        assert "selected_urls" in result
        assert "final_reasoning" in result

        # 値の型チェック
        assert isinstance(result["thought_trace"], dict)
        assert isinstance(result["search_queries_used"], list)
        assert isinstance(result["selected_urls"], list)
        assert isinstance(result["final_reasoning"], str)

    def test_query_id_format(self, mock_openai_client, mock_claude_client, assert_valid_query_id):
        """クエリIDのフォーマットテスト"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("テストクエリ")
        assert_valid_query_id(result["query_id"])

    def test_llm_model_name_recorded(self, mock_openai_client, mock_claude_client):
        """使用したLLMモデル名が記録されるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("テストクエリ")
        assert result["llm_model"] == "ChatGPT o1-preview"


class TestGem01ThoughtTraceExtraction:
    """思考トレース抽出のテスト"""

    def test_extract_7_steps(self, mock_openai_client, mock_claude_client):
        """7ステップを正しく抽出できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        steps = gem_01.extract_7_steps(result["thought_trace"])

        # 7ステップが抽出されているか
        assert len(steps) == 7, f"期待: 7ステップ, 実際: {len(steps)}ステップ"

        # 各ステップが空でないか
        for i, step in enumerate(steps, 1):
            assert step, f"ステップ{i}が空です"

    def test_thought_trace_contains_expected_keywords(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """思考トレースに期待されるキーワードが含まれているか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        thought_trace = result["thought_trace"]

        # 期待されるキーワード（v2.1設計書 4.2に基づく）
        expected_keywords = [
            "候補",
            "公式",
            "レビュー",
            "比較",
            "判断"
        ]

        all_steps_text = " ".join([str(v) for v in thought_trace.values()])

        for keyword in expected_keywords:
            assert keyword in all_steps_text, f"キーワード '{keyword}' が思考トレースに含まれていません"


class TestGem01URLExtraction:
    """参照URL抽出のテスト"""

    def test_selected_urls_extraction(self, mock_openai_client, mock_claude_client):
        """参照URLが抽出されるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        selected_urls = result["selected_urls"]

        # 最低3件のURLが抽出されるか（v2.1設計書 4.5の成功基準）
        assert len(selected_urls) >= 3, f"URLが3件未満です: {len(selected_urls)}件"

        # URLが有効な形式か
        for url in selected_urls:
            assert url.startswith("http"), f"無効なURL: {url}"

    def test_urls_are_unique(self, mock_openai_client, mock_claude_client):
        """抽出されたURLが重複していないか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        selected_urls = result["selected_urls"]

        # 重複チェック
        unique_urls = set(selected_urls)
        assert len(selected_urls) == len(unique_urls), "URLに重複があります"


class TestGem01SearchQueryInference:
    """検索クエリ推測のテスト"""

    def test_search_queries_inference(self, mock_openai_client, mock_claude_client):
        """ChatGPTが使用した検索クエリを推測できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        search_queries = result["search_queries_used"]

        # 検索クエリが抽出されているか
        assert len(search_queries) > 0, "検索クエリが抽出されていません"

        # クエリが文字列のリストか
        assert all(isinstance(q, str) for q in search_queries), "検索クエリがすべて文字列ではありません"


class TestGem01BrandMentionAnalysis:
    """ブランド言及分析のテスト"""

    def test_identify_missing_brand_reason(self, mock_openai_client, mock_claude_client):
        """自社ブランドが言及されなかった理由を特定できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")

        # 言及されなかったブランドの理由を分析
        reason = gem_01.identify_missing_brand_reason(
            result["thought_trace"],
            "自社ツール"
        )

        # 理由が返されるか
        assert reason, "ブランド不言及の理由が特定できません"
        assert isinstance(reason, str), "理由が文字列ではありません"
        assert len(reason) > 10, "理由の説明が短すぎます"

    def test_brand_mentioned_in_steps(self, mock_openai_client, mock_claude_client):
        """特定ブランドが7ステップのどこで言及されたかを検出"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        thought_trace = result["thought_trace"]

        # HubSpotが言及されているか（モックデータに含まれる）
        mentioned_steps = []
        for step_key, step_text in thought_trace.items():
            if "HubSpot" in str(step_text):
                mentioned_steps.append(step_key)

        assert len(mentioned_steps) > 0, "HubSpotが7ステップのどこにも言及されていません"


class TestGem01SuccessCriteria:
    """
    v2.1設計書 4.5の成功基準テスト

    - [x] ChatGPT o1から思考プロセスを取得できる
    - [x] 7ステップのうち最低5ステップを抽出できる
    - [x] 参照URLを最低3件特定できる
    - [x] 自社ブランドが言及されなかった理由を1文で説明できる
    """

    def test_acceptance_criteria_reasoning_content_retrieval(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """成功基準1: reasoning_contentを取得できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")

        # thought_traceが存在し、空でないか
        assert result["thought_trace"], "思考プロセスが取得できていません"
        assert len(result["thought_trace"]) > 0, "思考プロセスが空です"

    def test_acceptance_criteria_5_steps_extraction(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """成功基準2: 7ステップのうち最低5ステップを抽出できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        steps = gem_01.extract_7_steps(result["thought_trace"])

        # 最低5ステップが抽出されているか
        assert len(steps) >= 5, f"5ステップ未満しか抽出できていません: {len(steps)}ステップ"

    def test_acceptance_criteria_3_urls_identification(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """成功基準3: 参照URLを最低3件特定できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")

        # 最低3件のURLが特定されているか
        assert len(result["selected_urls"]) >= 3, \
            f"URLが3件未満です: {len(result['selected_urls'])}件"

    def test_acceptance_criteria_missing_reason_explanation(
        self,
        mock_openai_client,
        mock_claude_client
    ):
        """成功基準4: 自社ブランドが言及されなかった理由を1文で説明できるか"""
        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude_client
        )

        result = gem_01.analyze_chatgpt_thinking("マーケティングツール おすすめ")
        reason = gem_01.identify_missing_brand_reason(
            result["thought_trace"],
            "自社ツール"
        )

        # 理由が1文（100文字以内）で説明されているか
        assert len(reason) > 0, "理由が空です"
        assert len(reason) <= 100, "理由が長すぎます（1文を超えています）"


class TestGem01ErrorHandling:
    """エラーハンドリングのテスト"""

    def test_handles_empty_reasoning_content(self, mock_claude_client):
        """reasoning_contentが空の場合のエラーハンドリング"""
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.reasoning_content = ""  # 空
        mock_response.choices[0].message.content = "回答のみ"
        mock_openai.chat.completions.create.return_value = mock_response

        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai,
            claude_client=mock_claude_client
        )

        # エラーが発生せず、デフォルト値が返されるか
        try:
            result = gem_01.analyze_chatgpt_thinking("テストクエリ")
            # reasoning_contentが空でもエラーにならないことを確認
            assert True
        except Exception as e:
            pytest.fail(f"reasoning_contentが空でエラーが発生: {e}")

    def test_handles_invalid_json_from_claude(self, mock_openai_client):
        """ClaudeがJSON以外を返した場合のエラーハンドリング"""
        mock_claude = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "これはJSONではありません"  # 無効なJSON
        mock_claude.messages.create.return_value = mock_response

        gem_01 = MockGem01Intelligence(
            openai_client=mock_openai_client,
            claude_client=mock_claude
        )

        # JSONパースエラーが適切にハンドリングされるか
        with pytest.raises(json.JSONDecodeError):
            gem_01.analyze_chatgpt_thinking("テストクエリ")
