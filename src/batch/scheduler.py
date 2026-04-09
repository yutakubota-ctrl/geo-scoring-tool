"""
スケジューラーモジュール
週1回または月2回のバッチ実行をスケジュール
"""
import logging
from datetime import datetime
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from src.batch.runner import run_batch

# ロガー設定
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_scheduler() -> BlockingScheduler:
    """スケジューラーを作成"""
    scheduler = BlockingScheduler()

    # スケジュール設定に基づいてジョブを追加
    schedule_type = settings.BATCH_SCHEDULE.lower()
    batch_day = settings.BATCH_DAY.lower()

    # 曜日のマッピング
    day_mapping = {
        "monday": "mon",
        "tuesday": "tue",
        "wednesday": "wed",
        "thursday": "thu",
        "friday": "fri",
        "saturday": "sat",
        "sunday": "sun"
    }

    day_abbr = day_mapping.get(batch_day, "mon")

    if schedule_type == "weekly":
        # 週1回（指定曜日の午前9時）
        trigger = CronTrigger(
            day_of_week=day_abbr,
            hour=9,
            minute=0
        )
        logger.info(f"週次スケジュール設定: 毎週{batch_day} 9:00")

    elif schedule_type == "bimonthly":
        # 月2回（1日と15日の午前9時）
        trigger = CronTrigger(
            day="1,15",
            hour=9,
            minute=0
        )
        logger.info("月2回スケジュール設定: 1日・15日 9:00")

    else:
        # デフォルト: 週1回（月曜）
        trigger = CronTrigger(
            day_of_week="mon",
            hour=9,
            minute=0
        )
        logger.info("デフォルトスケジュール設定: 毎週月曜 9:00")

    # ジョブを追加
    scheduler.add_job(
        run_batch,
        trigger=trigger,
        id="geo_scoring_batch",
        name="GEOスコアリングバッチ",
        replace_existing=True
    )

    return scheduler


def start_scheduler():
    """スケジューラーを開始"""
    logger.info("スケジューラーを開始します...")

    scheduler = create_scheduler()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("スケジューラーを停止します...")
        scheduler.shutdown()


def run_once():
    """1回だけバッチを実行（テスト用）"""
    logger.info("バッチを1回実行します...")
    result = run_batch()
    logger.info(f"実行結果: {result}")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GEOスコアリング スケジューラー")
    parser.add_argument(
        "--once",
        action="store_true",
        help="1回だけ実行してすぐ終了"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="デーモンとして常駐実行"
    )

    args = parser.parse_args()

    if args.once:
        run_once()
    elif args.daemon:
        start_scheduler()
    else:
        print("使い方:")
        print("  --once   : 1回だけ実行")
        print("  --daemon : スケジューラーとして常駐")
