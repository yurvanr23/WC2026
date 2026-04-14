import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

function Dashboard() {
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [userPredictions, setUserPredictions] = useState([]);
  const [aiPredictions, setAIPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [matches, predictions, aiPreds] = await Promise.all([
        api.getUpcomingMatches(6),
        api.getUserPredictions(),
        api.getUpcomingAIPredictions(6)
      ]);
      
      setUpcomingMatches(matches);
      setUserPredictions(predictions.slice(0, 5));
      setAIPredictions(aiPreds);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Dashboard</h1>
          <p className="text-slate-400">Your prediction hub for World Cup 2026</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="stat-card">
            <div className="text-sm text-slate-400 mb-1">Total Predictions</div>
            <div className="text-3xl font-bold text-white">{userPredictions.length}</div>
          </div>
          <div className="stat-card">
            <div className="text-sm text-slate-400 mb-1">Points Earned</div>
            <div className="text-3xl font-bold gradient-text">0</div>
          </div>
          <div className="stat-card">
            <div className="text-sm text-slate-400 mb-1">Accuracy</div>
            <div className="text-3xl font-bold text-emerald-400">0%</div>
          </div>
          <div className="stat-card">
            <div className="text-sm text-slate-400 mb-1">Global Rank</div>
            <div className="text-3xl font-bold text-indigo-400">-</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Matches */}
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">Upcoming Matches</h2>
              <span className="badge badge-info">{upcomingMatches.length} matches</span>
            </div>

            <div className="space-y-4">
              {upcomingMatches.map((match) => (
                <Link
                  key={match.id}
                  to={`/match/${match.id}`}
                  className="block p-4 bg-slate-900 rounded-lg border border-slate-700 hover:border-indigo-500 transition-all duration-200"
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-slate-400">
                      {new Date(match.match_date).toLocaleDateString()}
                    </span>
                    <span className="badge badge-info text-xs">{match.stage}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-white font-semibold">{match.home_team}</div>
                    <div className="text-slate-400">vs</div>
                    <div className="text-white font-semibold">{match.away_team}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* AI Predictions */}
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">AI Predictions</h2>
              <span className="text-xs text-indigo-400">Powered by ML</span>
            </div>

            <div className="space-y-4">
              {aiPredictions.slice(0, 5).map((item) => (
                <div
                  key={item.match.id}
                  className="p-4 bg-slate-900 rounded-lg border border-slate-700"
                >
                  <div className="flex justify-between items-center mb-3">
                    <div className="text-sm text-white font-semibold">
                      {item.match.home_team} vs {item.match.away_team}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-2 bg-slate-800 rounded">
                      <div className="text-xs text-slate-400">Home</div>
                      <div className="text-sm font-bold text-emerald-400">
                        {(item.prediction.win_prob * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="p-2 bg-slate-800 rounded">
                      <div className="text-xs text-slate-400">Draw</div>
                      <div className="text-sm font-bold text-amber-400">
                        {(item.prediction.draw_prob * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="p-2 bg-slate-800 rounded">
                      <div className="text-xs text-slate-400">Away</div>
                      <div className="text-sm font-bold text-red-400">
                        {(item.prediction.loss_prob * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Predictions */}
        {userPredictions.length > 0 && (
          <div className="card mt-8">
            <h2 className="text-2xl font-bold text-white mb-6">Your Recent Predictions</h2>
            
            <div className="space-y-4">
              {userPredictions.map((pred) => (
                <div
                  key={pred.id}
                  className="p-4 bg-slate-900 rounded-lg border border-slate-700"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-white font-semibold mb-1">
                        {pred.match.home_team} vs {pred.match.away_team}
                      </div>
                      <div className="text-sm text-slate-400">
                        Predicted: {pred.predicted_home_score}-{pred.predicted_away_score}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold gradient-text">
                        {pred.points_earned} pts
                      </div>
                      <div className="text-xs text-slate-400">
                        {pred.confidence}% confidence
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
