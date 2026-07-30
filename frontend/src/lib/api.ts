import axios from 'axios';

// Create a generic Axios instance for WariMitra Django backend
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT tokens if available
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('warimitra_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn('[WariMitra API Client]', error?.message || 'API Server offline, using fallback state.');
    return Promise.reject(error);
  }
);

// Authentication Service
export const authService = {
  login: (credentials: { username: string; password?: string }) => 
    api.post('/auth/login/', credentials),
  getProfile: () => api.get('/auth/profile/'),
};

// Emergency SOS Service
export const sosService = {
  getActiveIncidents: () => api.get('/sos/'),
  createEmergency: (data: { category: string; description: string; location: { lat: number; lng: number } }) => 
    api.post('/sos/', data),
  updateStatus: (id: string, status: string) => 
    api.patch(`/sos/${id}/`, { status }),
};

// Community Intelligence Service
export const communityService = {
  getReports: () => api.get('/community/reports/'),
  submitReport: (data: { category: string; description: string; image?: string }) => 
    api.post('/community/reports/', data),
  verifyReport: (id: string, action: 'confirm' | 'reject') => 
    api.post(`/community/reports/${id}/verify/`, { action }),
};

// Medical Operations Service
export const medicalService = {
  getCamps: () => api.get('/medical/camps/'),
  getAmbulances: () => api.get('/medical/ambulances/'),
  dispatchAmbulance: (ambulanceId: string, sosId: string) => 
    api.post('/medical/dispatch/', { ambulance_id: ambulanceId, sos_id: sosId }),
};

// Police Security Service
export const policeService = {
  getPatrolUnits: () => api.get('/police/patrols/'),
  getTrafficDiversions: () => api.get('/police/diversions/'),
  toggleDiversion: (id: string, active: boolean) => 
    api.patch(`/police/diversions/${id}/`, { active }),
};

// NGO Relief Service
export const ngoService = {
  getWaterTankers: () => api.get('/ngo/tankers/'),
  getFoodDistributionCamps: () => api.get('/ngo/food-relief/'),
  updateSupplyStock: (id: string, stockLiters: number) => 
    api.patch(`/ngo/tankers/${id}/`, { stock_liters: stockLiters }),
};

// Temple Queue & Crowd Flow Service
export const templeService = {
  getQueueStatus: () => api.get('/temple/queues/'),
  updateGateBypass: (gateId: string, open: boolean) => 
    api.post('/temple/bypass/', { gate_id: gateId, open }),
};

// Operational AI Predictions Service
export const aiPredictionService = {
  getQueuePredictions: () => api.get('/ai/queue-predictions/'),
  getCrowdForecasts: () => api.get('/ai/crowd-forecasts/'),
  getRiskScores: () => api.get('/ai/risk-scores/'),
};

// Pilgrim & Dindi Service
export const pilgrimService = {
  getPilgrims: () => api.get('/pilgrims/'),
  getDindiGroups: () => api.get('/pilgrims/dindis/'),
};

// Vari Heritage & Abhang Service
export const heritageService = {
  getSaints: () => api.get('/heritage/saints/'),
  getAbhangs: () => api.get('/heritage/abhangs/'),
  getMilestones: () => api.get('/heritage/milestones/'),
};

// Digital Lost & Found Service
export const lostFoundService = {
  getItems: () => api.get('/lost-found/items/'),
  reportItem: (data: any) => api.post('/lost-found/items/', data),
};

// Waste & Public Sanitation Service
export const sanitationService = {
  getToilets: () => api.get('/sanitation/toilets/'),
  getWasteReports: () => api.get('/sanitation/waste-reports/'),
};

export default api;
