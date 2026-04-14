import React from 'react';
import { Link } from 'react-router-dom';

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className="text-center fade-in">
            <h1 className="text-6xl md:text-8xl font-black mb-6 leading-tight">
              <span className="gradient-text">WC26</span>
              <br />
              <span className="text-white">Intelligence</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto">
              AI-Powered Football Analytics & Prediction Platform for FIFA World Cup 2026
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link
                to="/register"
                className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-bold rounded-lg transition-all duration-200 shadow-2xl hover:shadow-indigo-500/50 hover:-translate-y-1"
              >
                Get Started Free
              </Link>
              <Link
                to="/simulation"
                className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white text-lg font-bold rounded-lg transition-all duration-200 border-2 border-slate-600 hover:border-indigo-500"
              >
                Try Simulation
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              {[
                { value: '10K+', label: 'Simulations' },
                { value: '25+', label: 'ML Features' },
                { value: '68%', label: 'Accuracy' },
                { value: 'Real-time', label: 'Updates' }
              ].map((stat, idx) => (
                <div key={idx} className="glass rounded-xl p-6 hover-lift">
                  <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">
                    {stat.value}
                  </div>
                  <div className="text-slate-400 text-sm">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 gradient-text">
            Powered by Advanced AI
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: '🎯',
                title: 'ML Predictions',
                description: 'XGBoost and Random Forest models trained on historical match data with 25+ engineered features.'
              },
              {
                icon: '🔬',
                title: 'Explainable AI',
                description: 'SHAP values reveal exactly why the model made each prediction. Full transparency.'
              },
              {
                icon: '🎲',
                title: 'Monte Carlo Simulation',
                description: '10,000+ tournament simulations to calculate winner probabilities and dark horses.'
              },
              {
                icon: '🏆',
                title: 'Competitive Leaderboards',
                description: 'Global rankings and private leagues. Compete with friends and climb the ranks.'
              },
              {
                icon: '⚡',
                title: 'Real-time Updates',
                description: 'Redis-powered live leaderboards and instant match predictions.'
              },
              {
                icon: '📊',
                title: 'Advanced Analytics',
                description: 'Team form, goal statistics, FIFA rankings, and head-to-head analysis.'
              }
            ].map((feature, idx) => (
              <div
                key={idx}
                className="card hover-lift hover-glow fade-in"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-2xl font-bold mb-3 text-white">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 text-white">
            How It Works
          </h2>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: '1', title: 'Create Account', desc: 'Sign up in seconds' },
              { step: '2', title: 'Make Predictions', desc: 'Predict match outcomes' },
              { step: '3', title: 'Earn Points', desc: 'Get scored on accuracy' },
              { step: '4', title: 'Climb Ranks', desc: 'Compete globally' }
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-2xl font-bold">
                  {item.step}
                </div>
                <h4 className="text-xl font-bold mb-2 text-white">{item.title}</h4>
                <p className="text-slate-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Ready to Predict the Future?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join thousands of football fans using AI to enhance their World Cup experience.
          </p>
          <Link
            to="/register"
            className="inline-block px-12 py-4 bg-white text-indigo-600 text-lg font-bold rounded-lg hover:bg-slate-100 transition-all duration-200 shadow-2xl hover:-translate-y-1"
          >
            Start Predicting Now
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-12 bg-slate-950 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-slate-400">
            <p className="mb-2">© 2026 WC26 Intelligence Platform. All rights reserved.</p>
            <p className="text-sm">Built with FastAPI, React, PostgreSQL, and AI ⚽</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
