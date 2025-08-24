-- TradeBot Database Schema

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS voice_commands;
DROP TABLE IF EXISTS market_data;
DROP TABLE IF EXISTS user_balances;
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS trading_pairs;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    balance DECIMAL(16, 2) DEFAULT 10000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trading_pairs table
CREATE TABLE trading_pairs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_asset VARCHAR(10) NOT NULL,
    quote_asset VARCHAR(10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trades table
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pair_id INTEGER REFERENCES trading_pairs(id),
    order_type VARCHAR(10) NOT NULL, -- 'buy' or 'sell'
    order_subtype VARCHAR(10) NOT NULL, -- 'market' or 'limit'
    quantity DECIMAL(16, 8) NOT NULL,
    price DECIMAL(16, 2) NOT NULL,
    total_value DECIMAL(16, 2) NOT NULL,
    fee DECIMAL(16, 2) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'filled', 'cancelled', 'simulated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_balances table to track asset balances
CREATE TABLE user_balances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    asset VARCHAR(10) NOT NULL,
    balance DECIMAL(16, 8) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, asset)
);

-- Create voice_commands table to log user voice interactions
CREATE TABLE voice_commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    command_text TEXT NOT NULL,
    detected_intent VARCHAR(50),
    response_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create market_data table to cache recent market data
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(16, 2) NOT NULL,
    change_24h DECIMAL(8, 2),
    volume DECIMAL(24, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, timestamp)
);

-- Create indexes for better performance
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_pair_id ON trades(pair_id);
CREATE INDEX idx_trades_created_at ON trades(created_at);
CREATE INDEX idx_user_balances_user_id ON user_balances(user_id, asset);
CREATE INDEX idx_voice_commands_user_id ON voice_commands(user_id);
CREATE INDEX idx_market_data_symbol ON market_data(symbol);
CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);

-- Insert some initial data

-- Add some trading pairs
INSERT INTO trading_pairs (symbol, base_asset, quote_asset, description) VALUES
('BTCUSDT', 'BTC', 'USDT', 'Bitcoin to Tether'),
('ETHUSDT', 'ETH', 'USDT', 'Ethereum to Tether'),
('DOGEUSDT', 'DOGE', 'USDT', 'Dogecoin to Tether'),
('ADAUSDT', 'ADA', 'USDT', 'Cardano to Tether'),
('SOLUSDT', 'SOL', 'USDT', 'Solana to Tether');

-- Create a demo user (password: demo123)
INSERT INTO users (username, password_hash, email) VALUES
('demo', '$2b$12$XQ0bZlT8EYmvsJlr6Z3GIOtqYqnL1Ix6GGVm7xjJjRqwIGNnr0yRG', 'demo@example.com');

-- Add some initial balance for the demo user
INSERT INTO user_balances (user_id, asset, balance) VALUES
(1, 'USDT', 10000),
(1, 'BTC', 0.1),
(1, 'ETH', 1.5),
(1, 'DOGE', 1000);

-- Add some initial market data
INSERT INTO market_data (symbol, price, change_24h, volume) VALUES
('BTCUSDT', 58243.25, 2.35, 5243651200.45),
('ETHUSDT', 3218.76, -1.24, 2135487600.12),
('DOGEUSDT', 0.12, 5.67, 352164800.56);