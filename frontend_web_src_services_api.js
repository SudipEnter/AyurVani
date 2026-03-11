import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Consultation ──────────────────────────────────────────
export async function sendMessage(userId, message, language, sessionId = null) {
  const { data } = await api.post('/consultation/chat', {
    user_id: userId,
    message,
    language,
    session_id: sessionId,
  });
  return data;
}

export async function analyzeSymptoms(userId, symptoms, language, options = {}) {
  const { data } = await api.post('/consultation/symptoms', {
    user_id: userId,
    symptoms,
    language,
    ...options,
  });
  return data;
}

export async function assessDosha(userId, responses, language) {
  const { data } = await api.post('/consultation/dosha-assessment', {
    user_id: userId,
    responses,
    language,
  });
  return data;
}

// ── Voice ─────────────────────────────────────────────────
export async function sendVoiceAudio(userId, audioBlob, language, sessionId = null) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  formData.append('user_id', userId);
  formData.append('language', language);
  if (sessionId) formData.append('session_id', sessionId);

  const { data } = await api.post('/voice/consultation', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  });
  return data;
}

export function createVoiceWebSocket(userId, language) {
  const ws = new WebSocket(`${WS_BASE}/api/voice/stream`);

  ws.onopen = () => {
    ws.send(JSON.stringify({ user_id: userId, language }));
  };

  return ws;
}

// ── Multimodal ────────────────────────────────────────────
export async function analyzeImage(userId, imageFile, analysisType, language) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('user_id', userId);
  formData.append('analysis_type', analysisType);
  formData.append('language', language);

  const { data } = await api.post('/multimodal/analyze-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function searchKnowledge(query, topK = 5) {
  const { data } = await api.post('/multimodal/search', {
    query,
    top_k: topK,
  });
  return data;
}

export default api;