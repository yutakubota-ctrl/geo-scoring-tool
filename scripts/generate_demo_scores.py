"""
デモ用スコアデータを生成

過去90日分のスコアデータを作成
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルート
project_root = Path(__file__).parent.parent
demo_dir = project_root / "data" / "demo"

# 基準日（今日から90日前）
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

# ブランド設定（基準値 + トレンド）
brands_config = {
    1: {  # HubSpot（自社）
        "name": "HubSpot",
        "visibility_base": 7,
        "sentiment_base": 12,
        "positioning_base": 10,
        "accuracy_base": 28,
        "trend": 0.05  # 上昇トレンド
    },
    2: {  # Marketo
        "name": "Marketo",
        "visibility_base": 8,
        "sentiment_base": 15,
        "positioning_base": 12,
        "accuracy_base": 32,
        "trend": 0.0  # 横ばい
    },
    3: {  # Salesforce
        "name": "Salesforce",
        "visibility_base": 9,
        "sentiment_base": 18,
        "positioning_base": 14,
        "accuracy_base": 35,
        "trend": -0.02  # わずかに下降
    },
    4: {  # Pardot
        "name": "Pardot",
        "visibility_base": 6,
        "sentiment_base": 8,
        "positioning_base": 9,
        "accuracy_base": 24,
        "trend": 0.03  # やや上昇
    }
}

scores = []

# 各ブランド、各日付についてスコアを生成
for brand_id, config in brands_config.items():
    current_date = start_date

    for day_offset in range(91):  # 90日分 + 今日
        # 日数に応じたトレンド補正
        trend_factor = 1 + (config["trend"] * day_offset)

        # ランダムノイズ（±10%）
        noise = random.uniform(0.9, 1.1)

        # 各指標を計算
        visibility = max(0, min(10, int(config["visibility_base"] * trend_factor * noise)))
        sentiment = max(-10, min(30, int(config["sentiment_base"] * trend_factor * noise)))
        positioning = max(0, min(20, int(config["positioning_base"] * trend_factor * noise)))
        accuracy = max(0, min(40, int(config["accuracy_base"] * trend_factor * noise)))

        total_score = visibility + sentiment + positioning + accuracy

        scores.append({
            "id": len(scores) + 1,
            "brand_id": brand_id,
            "brand_name": config["name"],
            "date": (current_date + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
            "visibility": visibility,
            "sentiment": sentiment,
            "positioning": positioning,
            "accuracy": accuracy,
            "total_score": total_score,
            "created_at": (current_date + timedelta(days=day_offset)).isoformat()
        })

# JSONファイルに保存
output_file = demo_dir / "scores.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(scores, f, ensure_ascii=False, indent=2)

print(f"OK デモスコアデータを生成しました: {output_file}")
print(f"  - レコード数: {len(scores)}")
print(f"  - 期間: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print(f"  - ブランド数: {len(brands_config)}")
