"""
Gem_01 モックテスト

モックデータを使ってGem_01エージェントの動作確認を行う。
実際のAPI（OpenAI、Anthropic）を呼ばずにテストできる。

実行方法:
    py -3 tests/agents/test_gem_01_mock.py
"""

import sys
import os
import logging
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.gem_01_intelligence import Gem01Intelligence, MockGem01Intelligence

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mock_gem01_basic():
    """
    基本的なモックテスト
    """
    logger.info("=" * 60)
    logger.info("テスト1: MockGem01Intelligence 基本動作確認")
    logger.info("=" * 60)

    # モックエージェント初期化
    agent = MockGem01Intelligence()

    # テストクエリ
    query = "マーケティングツール おすすめ"

    # 分析実行
    result = agent.analyze_chatgpt_thinking(query)

    # 結果表示
    logger.info("\n--- 分析結果 ---")
    logger.info(f"クエリID: {result['query_id']}")
    logger.info(f"検索クエリ: {result['query_text']}")
    logger.info(f"使用モデル: {result['llm_model']}")
    logger.info(f"\n実行日時: {result['executed_at']}")

    logger.info("\n--- 7ステップの思考プロセス ---")
    for step, content in result['thought_trace'].items():
        logger.info(f"{step}: {content}")

    logger.info("\n--- 使用された検索クエリ ---")
    for i, search_query in enumerate(result['search_queries_used'], 1):
        logger.info(f"{i}. {search_query}")

    logger.info("\n--- 参照URL ---")
    for i, url in enumerate(result['selected_urls'], 1):
        logger.info(f"{i}. {url}")

    logger.info(f"\n--- 最終推論 ---")
    logger.info(result['final_reasoning'])

    logger.info("\n--- ブランドメンション ---")
    for mention in result['brand_mentions']:
        logger.info(f"- {mention['brand']}: {mention['sentiment']}")

    logger.info("\n✅ テスト1: 成功")
    return True


def test_gem01_with_mock_mode():
    """
    Gem01Intelligence のモックモードテスト
    """
    logger.info("\n" + "=" * 60)
    logger.info("テスト2: Gem01Intelligence（モックモード）動作確認")
    logger.info("=" * 60)

    # モックモードで初期化
    agent = Gem01Intelligence(mock_mode=True)

    # テストクエリ
    queries = [
        "CRMツール 比較",
        "メールマーケティング おすすめ",
        "営業支援ツール 日本"
    ]

    results = []

    for query in queries:
        logger.info(f"\n--- クエリ: {query} ---")
        result = agent.analyze_chatgpt_thinking(query)

        # 主要情報のみ表示
        logger.info(f"クエリID: {result['query_id']}")
        logger.info(f"Step 1: {result['thought_trace']['step_1'][:50]}...")
        logger.info(f"最終推論: {result['final_reasoning'][:80]}...")

        results.append(result)

    logger.info(f"\n✅ テスト2: 成功（{len(results)}件処理）")
    return True


def test_json_serialization():
    """
    JSON出力テスト
    """
    logger.info("\n" + "=" * 60)
    logger.info("テスト3: JSON出力確認")
    logger.info("=" * 60)

    agent = MockGem01Intelligence()
    result = agent.analyze_chatgpt_thinking("SEOツール おすすめ")

    # JSON出力
    json_output = json.dumps(result, ensure_ascii=False, indent=2)

    logger.info("\n--- JSON出力 ---")
    logger.info(json_output[:500] + "...")

    # JSON解析が正常にできるか確認
    parsed = json.loads(json_output)
    assert parsed['query_text'] == "SEOツール おすすめ"

    logger.info("\n✅ テスト3: 成功（JSON出力正常）")
    return True


def test_validation():
    """
    分析結果の検証テスト
    """
    logger.info("\n" + "=" * 60)
    logger.info("テスト4: 分析結果の検証")
    logger.info("=" * 60)

    agent = MockGem01Intelligence()
    result = agent.analyze_chatgpt_thinking("データ分析ツール おすすめ")

    # 必須フィールドの存在確認
    required_fields = [
        'query_id',
        'query_text',
        'executed_at',
        'llm_model',
        'thought_trace',
        'search_queries_used',
        'selected_urls',
        'final_reasoning',
        'brand_mentions'
    ]

    logger.info("\n--- 必須フィールド検証 ---")
    for field in required_fields:
        exists = field in result
        status = "✅" if exists else "❌"
        logger.info(f"{status} {field}: {exists}")

        if not exists:
            raise AssertionError(f"必須フィールド不足: {field}")

    # 7ステップの確認
    logger.info("\n--- 7ステップ検証 ---")
    thought_trace = result['thought_trace']
    for i in range(1, 8):
        step_key = f"step_{i}"
        exists = step_key in thought_trace
        status = "✅" if exists else "❌"
        logger.info(f"{status} {step_key}: {exists}")

        if not exists:
            raise AssertionError(f"ステップ不足: {step_key}")

    logger.info("\n✅ テスト4: 成功（すべての検証パス）")
    return True


def main():
    """
    メインテスト実行
    """
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " Gem_01 モックテスト実行開始 ".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")

    tests = [
        ("基本動作確認", test_mock_gem01_basic),
        ("モックモード動作確認", test_gem01_with_mock_mode),
        ("JSON出力確認", test_json_serialization),
        ("分析結果検証", test_validation)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"\n❌ テスト失敗: {test_name}")
            logger.error(f"エラー内容: {str(e)}", exc_info=True)
            failed += 1

    # 結果サマリー
    logger.info("\n" + "=" * 60)
    logger.info("テスト結果サマリー")
    logger.info("=" * 60)
    logger.info(f"✅ 成功: {passed}/{len(tests)}")
    logger.info(f"❌ 失敗: {failed}/{len(tests)}")

    if failed == 0:
        logger.info("\n🎉 すべてのテストが成功しました！")
        return 0
    else:
        logger.error("\n⚠️ 一部のテストが失敗しました")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
