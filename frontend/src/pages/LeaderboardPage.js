import React, { useState, useEffect } from 'react';
import api from '../services/api';

function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    loadLeaderboard();
  }, [page]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const data = await api.getGlobalLeaderboard(page, 20);
      setLeaderboard(data.leaderboard);
      setTotalUsers(data.total_users);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  return (
    <div className="min-h-screen bg-slate-900 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Global Leaderboard</h1>
          <p className="text-slate-400">Top predictors worldwide</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="card">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-4 px-4 text-slate-400 font-semibold">Rank</th>
                    <th className="text-left py-4 px-4 text-slate-400 font-semibold">User</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold">Points</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold">Predictions</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold">Accuracy</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold">Exact Scores</th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboard.map((entry) => (
                    <tr
                      key={entry.user_id}
                      className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors duration-200"
                    >
                      <td className="py-4 px-4">
                        <span className="text-2xl">{getRankBadge(entry.rank)}</span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="font-semibold text-white">{entry.username}</div>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-lg font-bold gradient-text">
                          {entry.total_points}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center text-slate-300">
                        {entry.predictions_count}
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-emerald-400 font-semibold">
                          {entry.accuracy.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center text-slate-300">
                        {entry.exact_scores}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-6 pt-6 border-t border-slate-700">
              <div className="text-slate-400">
                Showing {(page - 1) * 20 + 1} - {Math.min(page * 20, totalUsers)} of {totalUsers} users
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page * 20 >= totalUsers}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default LeaderboardPage;
