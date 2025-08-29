#!/bin/bash
# scripts/init_database.sh

echo "🔄 Initializing TradeBot Database..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✅ PostgreSQL is running"

# Check if database exists, create if not
echo "📊 Checking database..."
if ! psql -U postgres -h localhost -lqt | cut -d \| -f 1 | grep -qw tradebot; then
    echo "🔄 Creating database 'tradebot'..."
    psql -U postgres -h localhost -c "CREATE DATABASE tradebot;"
    echo "✅ Database 'tradebot' created"
else
    echo "✅ Database 'tradebot' already exists"
fi

# Check if user exists, create if not
echo "👤 Checking database user..."
if ! psql -U postgres -h localhost -t -c "SELECT 1 FROM pg_roles WHERE rolname='tradebot_user'" | grep -q 1; then
    echo "🔄 Creating user 'tradebot_user'..."
    psql -U postgres -h localhost -c "CREATE USER tradebot_user WITH PASSWORD 'postgres';"
    psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE tradebot TO tradebot_user;"
    echo "✅ User 'tradebot_user' created with permissions"
else
    echo "✅ User 'tradebot_user' already exists"
fi

# Run schema
echo "🏗️ Running database schema..."
if psql -U tradebot_user -h localhost -d tradebot -f database/schema.sql; then
    echo "✅ Database schema applied successfully"
else
    echo "❌ Failed to apply database schema"
    exit 1
fi

# Test connection
echo "🧪 Testing database connection..."
python3 database/db_connector.py

echo "🎉 Database initialization complete!"