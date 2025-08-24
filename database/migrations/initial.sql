-- Initial database migration
-- Execute this script to create the initial database schema

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