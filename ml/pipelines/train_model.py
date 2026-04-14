"""
ML Pipeline - Model Training Script

Train match outcome classifier and scoreline regressor models.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss, mean_absolute_error
import xgboost as xgb
import joblib
from datetime import datetime
import os


class WC26ModelTrainer:
    """Train and evaluate ML models for match prediction"""
    
    def __init__(self, model_version="v1.0.0"):
        self.model_version = model_version
        self.classifier = None
        self.regressor = None
        self.feature_names = self._get_feature_names()
        
    def _get_feature_names(self):
        """Define feature names"""
        return [
            'team_form_home', 'team_form_away',
            'goal_diff_home', 'goal_diff_away',
            'goals_scored_home_avg', 'goals_scored_away_avg',
            'goals_conceded_home_avg', 'goals_conceded_away_avg',
            'fifa_rank_home', 'fifa_rank_away',
            'rank_difference',
            'home_advantage',
            'h2h_wins_home', 'h2h_wins_away', 'h2h_draws',
            'squad_age_home', 'squad_age_away',
            'squad_experience_home', 'squad_experience_away',
            'recent_goals_home', 'recent_goals_away',
            'clean_sheets_home', 'clean_sheets_away',
            'tournament_stage_encoded',
            'days_since_last_match_home', 'days_since_last_match_away'
        ]
    
    def generate_synthetic_data(self, n_samples=1000):
        """
        Generate synthetic training data for demonstration.
        In production, this would load real historical match data.
        """
        print(f"Generating {n_samples} synthetic training samples...")
        
        np.random.seed(42)
        
        # Generate features
        data = {}
        for feature in self.feature_names:
            if 'rank' in feature:
                data[feature] = np.random.randint(1, 100, n_samples)
            elif 'form' in feature:
                data[feature] = np.random.uniform(0, 3, n_samples)
            elif 'goal' in feature or 'goals' in feature:
                data[feature] = np.random.uniform(0, 3, n_samples)
            elif 'advantage' in feature:
                data[feature] = np.random.choice([0, 1], n_samples)
            elif 'age' in feature:
                data[feature] = np.random.uniform(23, 30, n_samples)
            elif 'experience' in feature:
                data[feature] = np.random.uniform(20, 70, n_samples)
            elif 'clean_sheets' in feature or 'h2h' in feature:
                data[feature] = np.random.randint(0, 5, n_samples)
            elif 'stage' in feature:
                data[feature] = np.random.randint(0, 5, n_samples)
            elif 'days' in feature:
                data[feature] = np.random.randint(3, 10, n_samples)
            else:
                data[feature] = np.random.uniform(0, 10, n_samples)
        
        X = pd.DataFrame(data)
        
        # Generate targets
        # Match outcome: 0=Home Win, 1=Draw, 2=Away Win
        probabilities = self._calculate_outcome_probabilities(X)
        y_outcome = np.array([
            np.random.choice([0, 1, 2], p=prob) 
            for prob in probabilities
        ])
        
        # Goals (for regression)
        y_home_goals = np.random.poisson(
            1.5 + X['team_form_home'] * 0.3 + X['home_advantage'] * 0.2,
            n_samples
        )
        y_away_goals = np.random.poisson(
            1.2 + X['team_form_away'] * 0.3,
            n_samples
        )
        
        return X, y_outcome, y_home_goals, y_away_goals
    
    def _calculate_outcome_probabilities(self, X):
        """Calculate outcome probabilities based on features"""
        form_diff = X['team_form_home'] - X['team_form_away']
        rank_diff = X['fifa_rank_away'] - X['fifa_rank_home']  # Lower rank is better
        
        base_home = 0.4
        base_draw = 0.3
        base_away = 0.3
        
        # Adjust based on form and rank
        adjustment = (form_diff * 0.05 + rank_diff * 0.002 + 
                     X['home_advantage'] * 0.1)
        
        home_prob = np.clip(base_home + adjustment, 0.1, 0.8)
        away_prob = np.clip(base_away - adjustment, 0.1, 0.8)
        draw_prob = np.clip(1 - home_prob - away_prob, 0.1, 0.5)
        
        # Normalize
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        return np.column_stack([home_prob, draw_prob, away_prob])
    
    def train_classifier(self, X_train, y_train):
        """Train match outcome classifier"""
        print("\nTraining XGBoost Classifier...")
        
        self.classifier = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            objective='multi:softprob',
            num_class=3
        )
        
        self.classifier.fit(X_train, y_train)
        print("✓ Classifier trained")
    
    def train_regressor(self, X_train, y_home_train, y_away_train):
        """Train scoreline regressor"""
        print("\nTraining Random Forest Regressors...")
        
        # Home goals regressor
        self.home_regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.home_regressor.fit(X_train, y_home_train)
        
        # Away goals regressor
        self.away_regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.away_regressor.fit(X_train, y_away_train)
        
        print("✓ Regressors trained")
    
    def evaluate(self, X_test, y_outcome_test, y_home_test, y_away_test):
        """Evaluate models"""
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        
        # Classifier evaluation
        y_pred = self.classifier.predict(X_test)
        y_proba = self.classifier.predict_proba(X_test)
        
        accuracy = accuracy_score(y_outcome_test, y_pred)
        logloss = log_loss(y_outcome_test, y_proba)
        
        print(f"\nClassifier Performance:")
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  Log Loss: {logloss:.3f}")
        
        # Regressor evaluation
        y_home_pred = self.home_regressor.predict(X_test)
        y_away_pred = self.away_regressor.predict(X_test)
        
        home_mae = mean_absolute_error(y_home_test, y_home_pred)
        away_mae = mean_absolute_error(y_away_test, y_away_pred)
        
        print(f"\nRegressor Performance:")
        print(f"  Home Goals MAE: {home_mae:.3f}")
        print(f"  Away Goals MAE: {away_mae:.3f}")
        
        # Feature importance
        print(f"\nTop 10 Important Features:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.classifier.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
    
    def save_models(self, output_dir="../ml/models"):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        classifier_path = f"{output_dir}/classifier_{self.model_version}_{timestamp}.pkl"
        home_reg_path = f"{output_dir}/home_regressor_{self.model_version}_{timestamp}.pkl"
        away_reg_path = f"{output_dir}/away_regressor_{self.model_version}_{timestamp}.pkl"
        
        joblib.dump(self.classifier, classifier_path)
        joblib.dump(self.home_regressor, home_reg_path)
        joblib.dump(self.away_regressor, away_reg_path)
        
        print(f"\n✓ Models saved to {output_dir}")
        print(f"  Classifier: {os.path.basename(classifier_path)}")
        print(f"  Home Regressor: {os.path.basename(home_reg_path)}")
        print(f"  Away Regressor: {os.path.basename(away_reg_path)}")


def main():
    """Main training pipeline"""
    print("="*50)
    print("WC26 ML MODEL TRAINING PIPELINE")
    print("="*50)
    
    # Initialize trainer
    trainer = WC26ModelTrainer()
    
    # Generate training data
    X, y_outcome, y_home_goals, y_away_goals = trainer.generate_synthetic_data(n_samples=2000)
    
    # Split data
    (X_train, X_test, 
     y_outcome_train, y_outcome_test,
     y_home_train, y_home_test,
     y_away_train, y_away_test) = train_test_split(
        X, y_outcome, y_home_goals, y_away_goals,
        test_size=0.2,
        random_state=42
    )
    
    print(f"\nDataset split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # Train models
    trainer.train_classifier(X_train, y_outcome_train)
    trainer.train_regressor(X_train, y_home_train, y_away_train)
    
    # Evaluate
    trainer.evaluate(X_test, y_outcome_test, y_home_test, y_away_test)
    
    # Save models
    trainer.save_models()
    
    print("\n✅ Training pipeline completed successfully!")


if __name__ == "__main__":
    main()
