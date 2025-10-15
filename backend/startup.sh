#!/bin/bash
set -e

echo "🔄 Backend startup script..."

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=kovaaks_pass psql -h postgres -U kovaaks -d kovaaks_ai -c '\q' 2>/dev/null; do
  sleep 1
done
echo "✅ PostgreSQL is ready"

# Enable pgvector extension
echo "📦 Ensuring pgvector extension..."
PGPASSWORD=kovaaks_pass psql -h postgres -U kovaaks -d kovaaks_ai -c "CREATE EXTENSION IF NOT EXISTS vector;" || echo "Extension already exists"

# Run Alembic migrations
echo "🗄️  Running database migrations..."
export ALEMBIC_DATABASE_URL=postgresql://kovaaks:kovaaks_pass@postgres:5432/kovaaks_ai

# Check if tables already exist
TABLE_EXISTS=$(PGPASSWORD=kovaaks_pass psql -h postgres -U kovaaks -d kovaaks_ai -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='rag_documents');" 2>/dev/null || echo "f")

# Check current migration state
CURRENT=$(alembic current 2>&1 | grep -o '[a-f0-9]\{12\}' | head -1 || echo "")

if [ "$TABLE_EXISTS" = "t" ] && [ -z "$CURRENT" ]; then
  echo "📊 Tables exist but no migrations recorded, stamping to latest (0a2f121dc56d)..."
  alembic stamp 0a2f121dc56d
  echo "✅ Migrations stamped"
elif [ -z "$CURRENT" ]; then
  echo "🆕 No migrations applied yet, running from scratch..."
  alembic upgrade head
  echo "✅ Migrations applied"
else
  echo "🔄 Running pending migrations from $CURRENT..."
  alembic upgrade head || echo "⚠️  Migration upgrade had issues, but continuing..."
  echo "✅ Migrations complete"
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

