/**
 * CityVotes API Client
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

const CityVotesAPI = {
    // Store session info
    sessionId: localStorage.getItem('sessionId') || null,
    currentCity: localStorage.getItem('currentCity') || null,

    /**
     * Save session info to localStorage
     */
    saveSession: function(sessionId, city) {
        this.sessionId = sessionId;
        this.currentCity = city;
        localStorage.setItem('sessionId', sessionId);
        localStorage.setItem('currentCity', city);
    },

    /**
     * Clear session info
     */
    clearSession: function() {
        this.sessionId = null;
        this.currentCity = null;
        localStorage.removeItem('sessionId');
        localStorage.removeItem('currentCity');
    },

    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },

    // ==================== Cities ====================

    /**
     * Get all configured cities
     */
    async getCities() {
        return this.request('/cities');
    },

    /**
     * Get specific city configuration
     */
    async getCity(cityKey) {
        return this.request(`/cities/${cityKey}`);
    },

    // ==================== Upload ====================

    /**
     * Upload a voting data JSON file
     */
    async uploadFile(file, cityKey) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('city_key', cityKey);

        const url = `${API_BASE_URL}/upload`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Save session info
            this.saveSession(data.session_id, cityKey);

            return data;
        } catch (error) {
            console.error('Upload Error:', error);
            throw error;
        }
    },

    // ==================== Sessions ====================

    /**
     * Get session info
     */
    async getSession(sessionId = null) {
        const id = sessionId || this.sessionId;
        if (!id) throw new Error('No session ID');
        return this.request(`/sessions/${id}`);
    },

    /**
     * Get cities in session
     */
    async getSessionCities(sessionId = null) {
        const id = sessionId || this.sessionId;
        if (!id) throw new Error('No session ID');
        return this.request(`/sessions/${id}/cities`);
    },

    // ==================== Dashboard ====================

    /**
     * Get vote summary for a city
     */
    async getVoteSummary(cityKey = null, sessionId = null) {
        const id = sessionId || this.sessionId;
        const city = cityKey || this.currentCity;
        if (!id) throw new Error('No session ID');
        if (!city) throw new Error('No city selected');
        return this.request(`/dashboard/${id}/${city}/summary`);
    },

    /**
     * Get member analysis for a city
     */
    async getMemberAnalysis(cityKey = null, sessionId = null) {
        const id = sessionId || this.sessionId;
        const city = cityKey || this.currentCity;
        if (!id) throw new Error('No session ID');
        if (!city) throw new Error('No city selected');
        return this.request(`/dashboard/${id}/${city}/members`);
    },

    /**
     * Get member profile
     */
    async getMemberProfile(memberName, cityKey = null, sessionId = null) {
        const id = sessionId || this.sessionId;
        const city = cityKey || this.currentCity;
        if (!id) throw new Error('No session ID');
        if (!city) throw new Error('No city selected');
        return this.request(`/dashboard/${id}/${city}/members/${encodeURIComponent(memberName)}`);
    },

    /**
     * Get agenda items list
     */
    async getAgendaItems(cityKey = null, sessionId = null) {
        const id = sessionId || this.sessionId;
        const city = cityKey || this.currentCity;
        if (!id) throw new Error('No session ID');
        if (!city) throw new Error('No city selected');
        return this.request(`/dashboard/${id}/${city}/agenda-items`);
    },

    /**
     * Get agenda item detail
     */
    async getAgendaItemDetail(itemId, cityKey = null, sessionId = null) {
        const id = sessionId || this.sessionId;
        const city = cityKey || this.currentCity;
        if (!id) throw new Error('No session ID');
        if (!city) throw new Error('No city selected');
        return this.request(`/dashboard/${id}/${city}/agenda-items/${encodeURIComponent(itemId)}`);
    },

    /**
     * Get city comparison data
     */
    async getCityComparison(sessionId = null) {
        const id = sessionId || this.sessionId;
        if (!id) throw new Error('No session ID');
        return this.request(`/dashboard/${id}/comparison`);
    },

    // ==================== Utilities ====================

    /**
     * Check if user has an active session
     */
    hasSession() {
        return !!this.sessionId;
    },

    /**
     * Switch to a different city
     */
    switchCity(cityKey) {
        this.currentCity = cityKey;
        localStorage.setItem('currentCity', cityKey);
    },

    /**
     * Get current city
     */
    getCurrentCity() {
        return this.currentCity;
    },

    /**
     * Get session ID
     */
    getSessionId() {
        return this.sessionId;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CityVotesAPI };
}
