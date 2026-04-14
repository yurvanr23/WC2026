import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../utils/AuthContext';
import api from '../services/api';

function ProfilePage() {
  const { user } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [userRank, setUserRank] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const [profileData, rankData] = await Promise.all([
        api.getCurrentUser(),
        api.getUserRank(user.user_id || 1)
      ]);
      setProfile(profileData);
      setUserRank(rankData);
    } catch (error) {
      console.error('Error loading profile:', error);
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Profile</h1>
          <p className="text-slate-400">Your prediction statistics and achievements</p>
        </div>

        {/* Profile Header */}
        <div className="card mb-8">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-4xl font-bold text-white">
              {profile?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-white mb-1">{profile?.username}</h2>
              <p className="text-slate-400">{profile?.email}</p>
              {userRank && (
                <div className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg">
                  <span className="text-slate-400">Global Rank:</span>
                  <span className="text-xl font-bold gradient-text">#{userRank.rank}</span>
                  <span className="text-slate-500">({userRank.percentile}th percentile)</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="stat-card text-center">
            <div className="text-sm text-slate-400 mb-2">Total Points</div>
            <div className="text-4xl font-bold gradient-text">
              {profile?.total_points || 0}
            </div>
          </div>
          <div className="stat-card text-center">
            <div className="text-sm text-slate-400 mb-2">Predictions Made</div>
            <div className="text-4xl font-bold text-white">
              {profile?.predictions_count || 0}
            </div>
          </div>
          <div className="stat-card text-center">
            <div className="text-sm text-slate-400 mb-2">Accuracy</div>
            <div className="text-4xl font-bold text-emerald-400">
              {profile?.accuracy?.toFixed(1) || 0}%
            </div>
          </div>
          <div className="stat-card text-center">
            <div className="text-sm text-slate-400 mb-2">Exact Scores</div>
            <div className="text-4xl font-bold text-indigo-400">
              {profile?.exact_scores || 0}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h3 className="text-2xl font-bold text-white mb-6">Recent Activity</h3>
          <div className="text-center py-12 text-slate-400">
            <p>No recent activity</p>
            <p className="text-sm mt-2">Start making predictions to see your activity here</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
