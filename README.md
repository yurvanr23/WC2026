# 🏆 WC26 Intelligence Platform

**AI-Powered Football Analytics & Prediction System for FIFA World Cup 2026**

A production-grade, portfolio-ready platform demonstrating advanced full-stack development, machine learning engineering, and system design.

---

## 🌟 Features

### Core Capabilities
- **Match Prediction**: AI-powered win/draw/loss predictions with confidence intervals
- **Scoreline Forecasting**: Expected goals and exact score predictions
- **Tournament Simulation**: Monte Carlo simulations (10,000+ iterations) for tournament outcomes
- **Explainable AI**: SHAP-based model interpretability showing why predictions were made
- **Competitive Leaderboards**: Global and private league rankings with Redis-powered real-time updates
- **User Predictions**: Track, score, and compare predictions against AI and other users

### Technical Highlights
- **Full-Stack Architecture**: React frontend + FastAPI backend
- **ML Pipeline**: Automated feature engineering, model training, and versioning
- **Real-Time Updates**: Redis caching and pub/sub for live leaderboards
- **Scalable Design**: Microservices-ready, containerized architecture
- **Production-Ready**: Comprehensive testing, logging, and monitoring

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React SPA     │◄────►│  FastAPI Backend │◄────►│   PostgreSQL    │
│   (Frontend)    │      │   (REST API)     │      │   (Primary DB)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │  Redis   │  │ ML Engine│  │ Simulator│
            │ (Cache)  │  │ (SHAP)   │  │ (Monte C)│
            └──────────┘  └──────────┘  └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Installation

```bash
# Clone repository
git clone <repository-url>
cd wc26-platform

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Start with Docker Compose (recommended)
docker-compose up --build

# OR Manual Setup:

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.core.init_db
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start

# ML Pipeline
cd ml
pip install -r requirements.txt
python pipelines/train_model.py
```

### Access Points
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1

---

## 📊 Tech Stack

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **State Management**: React Context + Hooks
- **Visualization**: Chart.js, D3.js
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Authentication**: JWT with bcrypt
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Async**: asyncio + asyncpg

### Database
- **Primary**: PostgreSQL 14
- **Cache**: Redis 7
- **Migrations**: Alembic

### Machine Learning
- **Core**: scikit-learn, XGBoost
- **Explainability**: SHAP
- **Tracking**: MLflow (optional)
- **Features**: pandas, numpy

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Logging**: Python logging + structlog
- **Monitoring**: Prometheus-ready metrics

---

## 🗄️ Database Schema

### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    points INTEGER DEFAULT 0
);
```

### Matches
```sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    match_date TIMESTAMP NOT NULL,
    stage VARCHAR(50) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(20) DEFAULT 'scheduled'
);
```

### Predictions
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    match_id INTEGER REFERENCES matches(id),
    predicted_home_score INTEGER NOT NULL,
    predicted_away_score INTEGER NOT NULL,
    confidence INTEGER CHECK (confidence BETWEEN 0 AND 100),
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, match_id)
);
```

### AI Predictions
```sql
CREATE TABLE ai_predictions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    win_prob FLOAT NOT NULL,
    draw_prob FLOAT NOT NULL,
    loss_prob FLOAT NOT NULL,
    expected_home_goals FLOAT NOT NULL,
    expected_away_goals FLOAT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    shap_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/register     - Register new user
POST   /api/v1/auth/login        - Login and get JWT token
POST   /api/v1/auth/refresh      - Refresh JWT token
```

### Matches
```
GET    /api/v1/matches           - List all matches (with filters)
GET    /api/v1/matches/{id}      - Get match details
GET    /api/v1/matches/upcoming  - Get upcoming matches
```

### Predictions
```
POST   /api/v1/predictions       - Submit prediction
GET    /api/v1/predictions/user  - Get user's predictions
GET    /api/v1/predictions/{id}  - Get specific prediction
PUT    /api/v1/predictions/{id}  - Update prediction (before match)
```

### AI Predictions
```
GET    /api/v1/ai/predictions/{match_id}  - Get AI prediction
GET    /api/v1/ai/explain/{match_id}      - Get SHAP explanation
POST   /api/v1/ai/retrain                 - Trigger model retraining
```

### Simulation
```
POST   /api/v1/simulate/tournament         - Run tournament simulation
GET    /api/v1/simulate/results/{sim_id}  - Get simulation results
GET    /api/v1/simulate/probabilities      - Get winner probabilities
```

### Leaderboard
```
GET    /api/v1/leaderboard/global          - Global leaderboard
GET    /api/v1/leaderboard/league/{id}    - League-specific leaderboard
POST   /api/v1/leaderboard/league          - Create private league
POST   /api/v1/leaderboard/league/{id}/join - Join league
```

---

## 🧠 Machine Learning Pipeline

### Feature Engineering
- **Team Form**: Rolling window statistics (last 5 matches)
- **Goal Difference**: Cumulative and recent trends
- **FIFA Rankings**: Current position and momentum
- **Squad Metrics**: Age, experience, caps
- **Home Advantage**: Host nation bonus
- **Head-to-Head**: Historical matchup data
- **Tournament Stage**: Group vs knockout dynamics

### Models
1. **Match Outcome Classifier** (XGBoost)
   - Predicts: Win/Draw/Loss probabilities
   - Features: 25+ engineered features
   - Evaluation: Log loss, accuracy, calibration

2. **Scoreline Regressor** (Random Forest)
   - Predicts: Expected goals for each team
   - Output: Continuous goal expectation
   - Evaluation: MAE, RMSE

3. **Team Strength Model** (Hybrid ELO + ML)
   - Dynamic team ratings
   - Bayesian updates after each match
   - Combined with feature-based predictions

### Model Explainability
- **SHAP Values**: Feature importance per prediction
- **Force Plots**: Individual prediction breakdowns
- **Summary Plots**: Global feature impact
- **Dependence Plots**: Feature interaction analysis

### Training Pipeline
```bash
# Full pipeline execution
cd ml
python pipelines/train_model.py --model all --eval

# Individual steps
python pipelines/feature_engineering.py
python pipelines/train_classifier.py
python pipelines/train_regressor.py
python pipelines/evaluate_models.py
```

---

## 🎲 Tournament Simulation

### Monte Carlo Method
- **Iterations**: 10,000+ simulations
- **Approach**: 
  1. Use ML model probabilities for each match
  2. Sample outcomes based on probabilities
  3. Progress winners through bracket
  4. Aggregate results across all simulations

### Outputs
- **Winner Probabilities**: Likelihood each team wins tournament
- **Stage Reach**: Probability of reaching each stage
- **Expected Finalists**: Most likely championship matchup
- **Dark Horses**: Teams exceeding expectations
- **Upset Analysis**: Low-probability paths that occurred

---

## 📈 Scoring System

### Points Breakdown
- **Correct Result** (W/D/L): 3 points
- **Exact Score**: 5 points (includes result points = 8 total)
- **Correct Winner** (wrong score): 2 points
- **Upset Prediction Bonus**: +2 points (underdog wins)
- **Confidence Calibration**: ±1 point based on Brier score

### Leaderboard Updates
- Real-time updates via Redis sorted sets
- Batch recalculation after match completion
- Historical snapshots for trend analysis
- League isolation with private rankings

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# ML pipeline tests
cd ml
pytest tests/ -v

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Test Coverage
- Unit tests: API endpoints, services, utilities
- Integration tests: Database operations, ML pipeline
- ML tests: Model performance, data validation
- E2E tests: Critical user flows

---

## 📦 Project Structure

```
wc26-platform/
├── frontend/                 # React application
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-level components
│   │   ├── services/        # API clients
│   │   ├── utils/           # Helpers and utilities
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── matches.py
│   │   │   ├── predictions.py
│   │   │   ├── ai.py
│   │   │   ├── simulation.py
│   │   │   └── leaderboard.py
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── ml/             # ML integration
│   │   ├── core/           # Config, auth, DB
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── alembic/            # Database migrations
│
├── ml/                      # Machine learning pipeline
│   ├── models/             # Trained model artifacts
│   ├── data/               # Datasets
│   ├── pipelines/          # Training scripts
│   │   ├── feature_engineering.py
│   │   ├── train_classifier.py
│   │   ├── train_regressor.py
│   │   └── evaluate_models.py
│   ├── evaluation/         # Model evaluation
│   └── requirements.txt
│
├── data/                    # Data storage
│   ├── raw/                # Raw data files
│   ├── processed/          # Cleaned data
│   └── features/           # Engineered features
│
├── docker/                  # Docker configurations
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── ml.Dockerfile
│
├── docs/                    # Documentation
│   ├── api.md
│   ├── ml_pipeline.md
│   └── deployment.md
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/wc26
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Configuration
MODEL_VERSION=v1.0.0
SHAP_ENABLED=true
MLFLOW_TRACKING_URI=http://localhost:5000

# Application
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

---

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set up PostgreSQL and Redis instances
2. Configure environment variables
3. Run database migrations: `alembic upgrade head`
4. Build frontend: `npm run build`
5. Start backend: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
6. Serve frontend with nginx

### CI/CD Pipeline
- GitHub Actions workflow included
- Automated testing on PR
- Containerized builds
- Environment-specific deployments

---

## 📊 Performance Metrics

### Model Performance (Example)
- **Match Outcome Classifier**: 68% accuracy, 0.52 log loss
- **Scoreline Regressor**: 0.87 MAE, 1.21 RMSE
- **Calibration Score**: 0.15 (well-calibrated)

### System Performance
- **API Response Time**: <100ms (p95)
- **Prediction Generation**: <200ms
- **Simulation (10K iterations)**: ~5 seconds
- **Leaderboard Query**: <50ms (Redis cache)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core prediction system
- ✅ ML pipeline
- ✅ Tournament simulation
- ✅ Basic leaderboards

### Phase 2 (Planned)
- 🔄 Real-time match updates via WebSocket
- 🔄 Mobile app (React Native)
- 🔄 Social features (comments, sharing)
- 🔄 Advanced analytics dashboard

### Phase 3 (Future)
- 📅 Player-level predictions
- 📅 Live betting odds comparison
- 📅 Multi-tournament support
- 📅 AI assistant chatbot

---

## 📞 Contact

**Project Maintainer**: [Your Name]
- Portfolio: [your-portfolio.com]
- LinkedIn: [your-linkedin]
- Email: [your-email]

---

## 🙏 Acknowledgments

- FIFA for tournament data structure
- Open-source ML community
- FastAPI and React teams
- All contributors

---

**Built with ❤️ for the beautiful game**
