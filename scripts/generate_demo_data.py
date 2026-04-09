"""
デモモード用のサンプルデータ生成スクリプト

使用方法:
    python scripts/generate_demo_data.py

生成されるファイル:
    - data/demo/thought_logs.json: 思考ログサンプル（10件）
    - data/demo/citations.json: 引用サンプル（30件）
    - data/demo/roadmap.json: ロードマップサンプル（20件）
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import random


class DemoDataGenerator:
    """デモデータ生成クラス"""

    def __init__(self, output_dir: str = "data/demo"):
        """
        初期化

        Args:
            output_dir: 出力先ディレクトリ
        """
        self.output_dir = output_dir
        self.brands = [
            "HubSpot", "Marketo", "Salesforce", "Pardot", "ActiveCampaign",
            "Mailchimp", "Constant Contact", "GetResponse", "Sendinblue", "ConvertKit"
        ]
        self.queries = [
            "マーケティングツール おすすめ",
            "CRM 比較",
            "メールマーケティング ツール",
            "マーケティングオートメーション 選び方",
            "営業支援ツール ランキング",
            "顧客管理システム 中小企業",
            "BtoB マーケティングツール",
            "リードナーチャリング ツール",
            "メルマガ配信 サービス",
            "マーケティング 分析ツール"
        ]

    def ensure_output_directory(self):
        """出力ディレクトリを作成"""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"出力ディレクトリを作成しました: {self.output_dir}")

    def generate_thought_logs(self, count: int = 10) -> List[Dict]:
        """
        思考ログサンプルを生成

        Args:
            count: 生成件数

        Returns:
            思考ログのリスト
        """
        thought_logs = []

        for i in range(count):
            query = self.queries[i % len(self.queries)]
            brand_subset = random.sample(self.brands, 3)  # ランダムに3つのブランドを選択

            thought_log = {
                "query_id": f"q_demo_{i:03d}",
                "query_text": query,
                "executed_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "llm_model": "ChatGPT o1-preview",
                "thought_trace": {
                    "step_1": f"候補ブランドを列挙: {', '.join(brand_subset)}",
                    "step_2": f"{brand_subset[0]}の公式サイト（{brand_subset[0].lower()}.com）を確認",
                    "step_3": f"G2レビュー（g2.com/products/{brand_subset[0].lower()}）を参照",
                    "step_4": "特に公的機関の情報は見つからず",
                    "step_5": f"{brand_subset[0]}と{brand_subset[1]}の料金・機能を比較",
                    "step_6": f"口コミサイトで{brand_subset[0]}の評判を確認",
                    "step_7": f"{brand_subset[0]}は中小企業向け、{brand_subset[1]}は大企業向けと判断"
                },
                "search_queries_used": [
                    f"{query.split()[0]} tools comparison",
                    f"{brand_subset[0]} pricing 2026",
                    f"{brand_subset[0]} vs {brand_subset[1]}"
                ],
                "selected_urls": [
                    f"https://www.{brand_subset[0].lower()}.com/",
                    f"https://www.g2.com/products/{brand_subset[0].lower()}",
                    f"https://www.capterra.com/p/{random.randint(100000, 999999)}/{brand_subset[0].lower()}/"
                ],
                "final_reasoning": f"{brand_subset[0]}は使いやすさとコスパの観点から中小企業に最適と判断",
                "brand_mentions": {
                    brand_subset[0]: {
                        "rank": 1,
                        "score": round(random.uniform(7.5, 9.5), 1)
                    },
                    brand_subset[1]: {
                        "rank": 2,
                        "score": round(random.uniform(6.5, 8.5), 1)
                    },
                    brand_subset[2]: {
                        "rank": 3,
                        "score": round(random.uniform(5.5, 7.5), 1)
                    }
                }
            }

            thought_logs.append(thought_log)

        return thought_logs

    def generate_citations(self, count: int = 30) -> List[Dict]:
        """
        引用データサンプルを生成

        Args:
            count: 生成件数

        Returns:
            引用データのリスト
        """
        citations = []

        for i in range(count):
            brand = self.brands[i % len(self.brands)]
            query = self.queries[random.randint(0, len(self.queries) - 1)]
            reference_types = ["AI_Overview", "ChatGPT", "Gemini", "Perplexity"]

            citation = {
                "citation_id": f"cite_demo_{i:03d}",
                "query_id": f"q_demo_{random.randint(0, 9):03d}",
                "entity_name": brand,
                "mention_count": random.randint(1, 5),
                "sentiment_score": round(random.uniform(6.0, 9.5), 2),
                "reference_type": reference_types[i % len(reference_types)],
                "source_url": f"https://www.{brand.lower().replace(' ', '')}.com/",
                "source_domain": f"{brand.lower().replace(' ', '')}.com",
                "position_in_response": random.randint(50, 500),
                "reference_rank": random.randint(1, 5) if random.random() > 0.3 else None,
                "context_snippet": f"{brand}は{query.split()[0]}において優れた選択肢の一つです。特に使いやすさと機能の充実度で評価されています。",
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }

            citations.append(citation)

        return citations

    def generate_roadmap(self, count: int = 20) -> List[Dict]:
        """
        ロードマップタスクサンプルを生成

        Args:
            count: 生成件数

        Returns:
            ロードマップタスクのリスト
        """
        task_templates = [
            {
                "type": "Technical",
                "description": "サイトのページ速度を改善（Core Web Vitals最適化）",
                "impact": 8,
                "effort": 6
            },
            {
                "type": "Content",
                "description": "製品比較ページに導入実績セクションを追加",
                "impact": 7,
                "effort": 3
            },
            {
                "type": "Content",
                "description": "FAQページを拡充（よくある質問30項目追加）",
                "impact": 6,
                "effort": 4
            },
            {
                "type": "Technical",
                "description": "構造化データ（Schema.org）の実装",
                "impact": 7,
                "effort": 5
            },
            {
                "type": "Content",
                "description": "お客様の声（導入事例）ページを作成",
                "impact": 9,
                "effort": 7
            },
            {
                "type": "Analytics",
                "description": "GRC順位データの定期取得・分析の自動化",
                "impact": 5,
                "effort": 4
            },
            {
                "type": "Content",
                "description": "料金ページに詳細な機能比較表を追加",
                "impact": 8,
                "effort": 5
            },
            {
                "type": "Technical",
                "description": "404エラーページの修正（25件）",
                "impact": 6,
                "effort": 3
            },
            {
                "type": "Content",
                "description": "製品デモ動画の制作と埋め込み",
                "impact": 7,
                "effort": 8
            },
            {
                "type": "Analytics",
                "description": "競合被リンク分析の実施とリンク獲得戦略立案",
                "impact": 6,
                "effort": 5
            },
            {
                "type": "Content",
                "description": "ブログ記事「マーケティングツール選び方ガイド」作成",
                "impact": 7,
                "effort": 6
            },
            {
                "type": "Technical",
                "description": "モバイル対応の改善（レスポンシブデザイン最適化）",
                "impact": 8,
                "effort": 7
            },
            {
                "type": "Content",
                "description": "無料トライアル申込フォームのCTA強化",
                "impact": 9,
                "effort": 4
            },
            {
                "type": "Analytics",
                "description": "ChatGPT思考プロセス分析の定期実行",
                "impact": 9,
                "effort": 5
            },
            {
                "type": "Technical",
                "description": "内部リンク構造の最適化",
                "impact": 6,
                "effort": 5
            },
            {
                "type": "Content",
                "description": "製品機能ページに使用シーン別の活用例を追加",
                "impact": 7,
                "effort": 5
            },
            {
                "type": "Analytics",
                "description": "AI Overviewsメンション状況の週次レポート自動化",
                "impact": 8,
                "effort": 4
            },
            {
                "type": "Content",
                "description": "ホワイトペーパー「BtoBマーケティング完全ガイド」作成",
                "impact": 8,
                "effort": 9
            },
            {
                "type": "Technical",
                "description": "サイトマップXMLの最適化と再送信",
                "impact": 5,
                "effort": 2
            },
            {
                "type": "Content",
                "description": "製品ページにインタラクティブなデモを追加",
                "impact": 8,
                "effort": 8
            }
        ]

        roadmap = []

        for i in range(min(count, len(task_templates))):
            template = task_templates[i]

            # Impact/Effortから優先度を決定
            if template["impact"] >= 8 and template["effort"] <= 5:
                priority = "P0"
            elif template["impact"] >= 7 and template["effort"] <= 6:
                priority = "P1"
            else:
                priority = "P2"

            # ステータスをランダムに決定（重み付け）
            status_weights = [("pending", 0.5), ("in_progress", 0.3), ("completed", 0.2)]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]

            task = {
                "task_id": f"task_demo_{i:03d}",
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
                "priority": priority,
                "task_type": template["type"],
                "description": template["description"],
                "assigned_to": "Gem_02" if template["type"] in ["Analytics", "Technical"] else "Human",
                "status": status,
                "due_date": (datetime.now() + timedelta(days=random.randint(7, 90))).date().isoformat(),
                "impact_score": template["impact"],
                "effort_score": template["effort"],
                "parent_gap_id": f"gap_demo_{random.randint(0, 9):03d}",
                "approval_status": "Approved" if status in ["in_progress", "completed"] else "Draft"
            }

            roadmap.append(task)

        # 優先度とインパクトスコアでソート
        roadmap.sort(key=lambda x: (
            {"P0": 0, "P1": 1, "P2": 2}[x["priority"]],
            -x["impact_score"]
        ))

        return roadmap

    def save_to_json(self, data: List[Dict], filename: str):
        """
        データをJSONファイルとして保存

        Args:
            data: 保存するデータ
            filename: ファイル名
        """
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"保存しました: {filepath} ({len(data)}件)")

    def generate_all(self):
        """すべてのデモデータを生成"""
        print("デモデータ生成を開始します...")
        print("=" * 60)

        # 出力ディレクトリ作成
        self.ensure_output_directory()
        print()

        # 思考ログ生成
        print("思考ログを生成中...")
        thought_logs = self.generate_thought_logs(10)
        self.save_to_json(thought_logs, "thought_logs.json")
        print()

        # 引用データ生成
        print("引用データを生成中...")
        citations = self.generate_citations(30)
        self.save_to_json(citations, "citations.json")
        print()

        # ロードマップ生成
        print("ロードマップを生成中...")
        roadmap = self.generate_roadmap(20)
        self.save_to_json(roadmap, "roadmap.json")
        print()

        print("=" * 60)
        print("デモデータ生成が完了しました")
        print()
        print("生成されたファイル:")
        print(f"  - {os.path.join(self.output_dir, 'thought_logs.json')} (10件)")
        print(f"  - {os.path.join(self.output_dir, 'citations.json')} (30件)")
        print(f"  - {os.path.join(self.output_dir, 'roadmap.json')} (20件)")


def main():
    """メイン処理"""
    generator = DemoDataGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()
