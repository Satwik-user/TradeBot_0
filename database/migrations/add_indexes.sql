-- Migration to add indexes to improve query performance

-- Add indexes for the trades table
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_pair_id ON trades(pair_id);
CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trades(created_at);

-- Add indexes for user_balances table
CREATE INDEX IF NOT EXISTS idx_user_balances_user_id ON user_balances(user_id, asset);

-- Add indexes for voice_commands table
CREATE INDEX IF NOT EXISTS idx_voice_commands_user_id ON voice_commands(user_id);

-- Add indexes for market_data table
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);