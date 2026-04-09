"""
データベースモデルの基底クラス

全モデルで共有するBase定義
"""

from sqlalchemy.ext.declarative import declarative_base

# 共通のBaseを作成
Base = declarative_base()
