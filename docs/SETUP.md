# 🚀 WC26 Intelligence Platform - Setup Guide

Complete setup instructions for the AI-powered football prediction platform.

---

## 📋 Prerequisites

Ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/))
- **Redis 7+** ([Download](https://redis.io/download))
- **Docker & Docker Compose** (Optional) ([Download](https://www.docker.com/get-started))

---

## 🐳 Option 1: Docker Setup (Recommended)

The easiest way to get started.

### Step 1: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd wc26-platform

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
nano .env
```

### Step 2: Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

### Step 3: Initialize Database

```bash
# Access backend container
docker exec -it wc26_backend bash

# Initialize database
python -m app.core.init_db

# Exit container
exit
```

### Step 4: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MLflow** (optional): http://localhost:5000

---

## 💻 Option 2: Manual Setup

For development or when Docker is not available.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env with your database credentials

# Initialize database
python -m app.core.init_db

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### PostgreSQL Setup

```bash
# Create database and user
psql postgres

CREATE DATABASE wc26_db;
CREATE USER wc26 WITH PASSWORD 'wc26pass';
GRANT ALL PRIVILEGES ON DATABASE wc26_db TO wc26;
\q
```

### Redis Setup

```bash
# Start Redis server
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🧠 Machine Learning Setup

### Train Models

```bash
cd ml

# Install ML dependencies
pip install -r requirements.txt

# Train models
python pipelines/train_model.py
```

This will:
- Generate synthetic training data
- Train XGBoost classifier and Random Forest regressors
- Evaluate model performance
- Save models to `ml/models/`

### Model Files

After training, you'll have:
- `classifier_v1.0.0_*.pkl` - Match outcome predictor
- `home_regressor_v1.0.0_*.pkl` - Home goals predictor
- `away_regressor_v1.0.0_*.pkl` - Away goals predictor

---

## ✅ Verification

### 1. Check Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "wc26-platform",
  "version": "1.0.0"
}
```

### 2. Check Frontend

Open http://localhost:3000 - you should see the landing page.

### 3. Test API

Visit http://localhost:8000/docs to explore the interactive API documentation.

### 4. Create Test Account

1. Navigate to http://localhost:3000/register
2. Create an account
3. Login and explore the dashboard

---

## 📊 Sample Data

The database initialization script includes sample data:
- 3 test users (password: `password123`)
  - john@example.com
  - sarah@example.com
  - mike@example.com
- 17 sample matches (12 upcoming, 5 finished)
- Group stage and knockout matches

---

## 🛠️ Development Workflow

### Backend Development

```bash
# Run tests
cd backend
pytest tests/ -v

# Check code coverage
pytest tests/ --cov=app

# Format code
black app/
flake8 app/
```

### Frontend Development

```bash
# Run tests
cd frontend
npm test

# Build for production
npm run build

# Lint code
npm run lint
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🔧 Common Issues & Solutions

### Issue: Database Connection Failed

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env
DATABASE_URL=postgresql://wc26:wc26pass@localhost:5432/wc26_db
```

### Issue: Redis Connection Failed

**Solution:**
```bash
# Check Redis is running
redis-cli ping
# Expected: PONG

# Or start Redis
redis-server
```

### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>
```

### Issue: CORS Errors

**Solution:**
- Ensure frontend URL is in `CORS_ORIGINS` in `.env`
- Default: `http://localhost:3000`

### Issue: npm install fails

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 🚀 Production Deployment

### Environment Variables

Update `.env` for production:

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-secret-key>
DATABASE_URL=<production-database-url>
REDIS_URL=<production-redis-url>
CORS_ORIGINS=<your-production-domain>
```

### Backend Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

```bash
# Build production bundle
npm run build

# Serve with nginx or deploy to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
```

### Database

- Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- Enable SSL connections
- Regular backups
- Connection pooling

### Redis

- Use managed Redis (AWS ElastiCache, Redis Cloud, etc.)
- Enable persistence
- Configure eviction policies

---

## 📈 Monitoring

### Application Logs

```bash
# Backend logs
tail -f logs/app.log

# With Docker
docker logs -f wc26_backend
```

### Database Monitoring

```bash
# PostgreSQL stats
psql wc26_db -c "SELECT * FROM pg_stat_activity;"

# Redis stats
redis-cli info
```

### Performance

- API response time: <100ms (p95)
- Prediction generation: <200ms
- Simulation (10K): ~5 seconds

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [XGBoost Guide](https://xgboost.readthedocs.io/)
- [SHAP Documentation](https://shap.readthedocs.io/)

---

## 🤝 Support

If you encounter issues:

1. Check this guide
2. Review error logs
3. Search existing issues
4. Create new issue with:
   - Error message
   - Steps to reproduce
   - Environment details

---

## ✨ Next Steps

1. ✅ Complete setup
2. 📖 Read API documentation
3. 🧪 Explore sample data
4. 🎯 Make your first prediction
5. 🏆 Join the leaderboard
6. 🎲 Run a tournament simulation

**Happy predicting! ⚽**
