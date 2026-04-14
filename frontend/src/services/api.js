const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'An error occurred');
    }
    return response.json();
  }

  // Auth endpoints
  async register(username, email, password) {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    return this.handleResponse(response);
  }

  async login(email, password) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return this.handleResponse(response);
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseUrl}/auth/me`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Matches endpoints
  async getMatches(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseUrl}/matches?${queryString}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getMatch(matchId) {
    const response = await fetch(`${this.baseUrl}/matches/${matchId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getUpcomingMatches(limit = 10) {
    const response = await fetch(`${this.baseUrl}/matches/upcoming?limit=${limit}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Predictions endpoints
  async createPrediction(matchId, homeScore, awayScore, confidence) {
    const response = await fetch(`${this.baseUrl}/predictions`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        match_id: matchId,
        predicted_home_score: homeScore,
        predicted_away_score: awayScore,
        confidence
      })
    });
    return this.handleResponse(response);
  }

  async getUserPredictions() {
    const response = await fetch(`${this.baseUrl}/predictions/user`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async updatePrediction(predictionId, homeScore, awayScore, confidence) {
    const response = await fetch(`${this.baseUrl}/predictions/${predictionId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        predicted_home_score: homeScore,
        predicted_away_score: awayScore,
        confidence
      })
    });
    return this.handleResponse(response);
  }

  // AI predictions endpoints
  async getAIPrediction(matchId) {
    const response = await fetch(`${this.baseUrl}/ai/predictions/${matchId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getAIExplanation(matchId) {
    const response = await fetch(`${this.baseUrl}/ai/explain/${matchId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getUpcomingAIPredictions(limit = 10) {
    const response = await fetch(`${this.baseUrl}/ai/predictions/upcoming?limit=${limit}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Simulation endpoints
  async runSimulation(iterations = 10000) {
    const response = await fetch(`${this.baseUrl}/simulate/tournament`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ iterations, use_latest_model: true })
    });
    return this.handleResponse(response);
  }

  async getSimulationResults(simulationId) {
    const response = await fetch(`${this.baseUrl}/simulate/results/${simulationId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getWinnerProbabilities() {
    const response = await fetch(`${this.baseUrl}/simulate/probabilities`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Leaderboard endpoints
  async getGlobalLeaderboard(page = 1, pageSize = 20) {
    const response = await fetch(
      `${this.baseUrl}/leaderboard/global?page=${page}&page_size=${pageSize}`,
      { headers: this.getAuthHeaders() }
    );
    return this.handleResponse(response);
  }

  async getLeagueLeaderboard(leagueId) {
    const response = await fetch(`${this.baseUrl}/leaderboard/league/${leagueId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createLeague(name, description, maxMembers = 50) {
    const response = await fetch(`${this.baseUrl}/leaderboard/league`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name,
        description,
        max_members: maxMembers,
        is_private: true
      })
    });
    return this.handleResponse(response);
  }

  async joinLeague(leagueId, inviteCode) {
    const response = await fetch(`${this.baseUrl}/leaderboard/league/${leagueId}/join`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ invite_code: inviteCode })
    });
    return this.handleResponse(response);
  }

  async getUserLeagues() {
    const response = await fetch(`${this.baseUrl}/leaderboard/user/leagues`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getUserRank(userId) {
    const response = await fetch(`${this.baseUrl}/leaderboard/rank/${userId}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }
}

export default new ApiService();
