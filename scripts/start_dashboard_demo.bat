@echo off
REM GEOスコアリングツール v2.1 ダッシュボード起動スクリプト（デモモード）

echo ================================================
echo GEOスコアリングツール v2.1 ダッシュボード
echo ================================================
echo.

REM デモモードを有効化
set DEMO_MODE=true
echo [INFO] デモモードを有効化しました: DEMO_MODE=%DEMO_MODE%
echo.

REM カレントディレクトリを確認
echo [INFO] 現在のディレクトリ: %CD%
echo.

REM Streamlit起動
echo [INFO] Streamlitダッシュボードを起動します...
echo [INFO] ブラウザで http://localhost:8501 にアクセスしてください
echo.
echo ================================================
echo.

streamlit run src\dashboard\app.py

pause
