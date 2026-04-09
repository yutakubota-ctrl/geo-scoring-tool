-- v2.1 データベーススキーマ: llm_thought_log テーブル
-- ChatGPT o1の思考プロセスを保存するテーブル
--
-- v2.1_design.md 第8章「データスキーマ」に基づく

CREATE TABLE IF NOT EXISTS llm_thought_log (
    id SERIAL PRIMARY KEY,
    query_id VARCHAR(36) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    llm_model VARCHAR(50) NOT NULL,  -- 'o1-preview', 'o1-mini', 'gemini-1.5-pro' etc
    thought_trace JSONB,  -- 7ステップの推論プロセス
    search_queries_used TEXT[],  -- 使用された検索クエリ群
    selected_urls TEXT[],  -- 参照されたURL
    final_reasoning TEXT,  -- 最終判断の根拠
    brand_mentions JSONB,  -- 各ブランドの言及状況
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_query_id ON llm_thought_log(query_id);
CREATE INDEX IF NOT EXISTS idx_executed_at ON llm_thought_log(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_model ON llm_thought_log(llm_model);

-- コメント追加
COMMENT ON TABLE llm_thought_log IS 'ChatGPT o1等のLLM思考プロセスログ';
COMMENT ON COLUMN llm_thought_log.query_id IS 'クエリ一意ID（例: q_20260409_120530）';
COMMENT ON COLUMN llm_thought_log.thought_trace IS '7ステップの推論プロセス（JSON形式）';
COMMENT ON COLUMN llm_thought_log.search_queries_used IS 'LLMが内部で使用した検索クエリ';
COMMENT ON COLUMN llm_thought_log.selected_urls IS 'LLMが参照したURLリスト';
COMMENT ON COLUMN llm_thought_log.brand_mentions IS 'ブランド言及状況（JSON形式）';
