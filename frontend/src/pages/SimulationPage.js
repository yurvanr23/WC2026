import React, { useState, useEffect } from 'react';
import api from '../services/api';

function SimulationPage() {
  const [simulating, setSimulating] = useState(false);
  const [probabilities, setProbabilities] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLatestSimulation();
  }, []);

  const loadLatestSimulation = async () => {
    try {
      const data = await api.getWinnerProbabilities();
      setProbabilities(data);
    } catch (error) {
      console.log('No simulation results yet');
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    setSimulating(true);
    try {
      const { simulation_id } = await api.runSimulation(10000);
      
      // Poll for results
      let attempts = 0;
      const checkResults = setInterval(async () => {
        attempts++;
        try {
          const result = await api.getSimulationResults(simulation_id);
          if (result.status === 'completed') {
            clearInterval(checkResults);
            loadLatestSimulation();
            setSimulating(false);
          }
        } catch (error) {
          // Still running
        }
        
        if (attempts > 30) {
          clearInterval(checkResults);
          setSimulating(false);
        }
      }, 2000);
    } catch (error) {
      console.error('Simulation error:', error);
      setSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Tournament Simulation</h1>
          <p className="text-slate-400">Monte Carlo analysis of World Cup 2026 outcomes</p>
        </div>

        {/* Simulation Control */}
        <div className="card mb-8 text-center">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">Run New Simulation</h2>
            <p className="text-slate-400">10,000 iterations using latest AI model</p>
          </div>
          
          <button
            onClick={runSimulation}
            disabled={simulating}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
          >
            {simulating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Simulating...
              </>
            ) : (
              <>
                🎲 Run Simulation
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="spinner"></div>
          </div>
        ) : probabilities ? (
          <div className="space-y-8">
            {/* Winner Probabilities */}
            <div className="card">
              <h2 className="text-2xl font-bold text-white mb-6">Winner Probabilities</h2>
              
              <div className="space-y-4">
                {probabilities.top_5.map(([team, prob], idx) => (
                  <div key={team} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{idx === 0 ? '🏆' : `${idx + 1}.`}</span>
                        <span className="text-lg font-semibold text-white">{team}</span>
                      </div>
                      <span className="text-2xl font-bold gradient-text">
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Simulation Info */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="stat-card text-center">
                <div className="text-sm text-slate-400 mb-2">Total Simulations</div>
                <div className="text-3xl font-bold gradient-text">10,000</div>
              </div>
              <div className="stat-card text-center">
                <div className="text-sm text-slate-400 mb-2">Model Version</div>
                <div className="text-xl font-bold text-white">v1.0.0</div>
              </div>
              <div className="stat-card text-center">
                <div className="text-sm text-slate-400 mb-2">Last Updated</div>
                <div className="text-sm text-white">
                  {new Date(probabilities.simulation_date).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card text-center py-12">
            <p className="text-slate-400 text-lg mb-6">No simulation results available</p>
            <p className="text-slate-500">Run your first simulation to see predictions</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default SimulationPage;
