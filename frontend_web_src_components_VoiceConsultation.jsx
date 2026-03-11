import React, { useState, useRef, useCallback, useEffect } from 'react';

const STATES = { IDLE: 'idle', RECORDING: 'recording', PROCESSING: 'processing' };

export default function VoiceConsultation({ language }) {
  const [state, setState] = useState(STATES.IDLE);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach((t) => t.stop());
        await processAudio(blob);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setState(STATES.RECORDING);
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setState(STATES.PROCESSING);
    }
  }, []);

  const processAudio = async (blob) => {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    formData.append('user_id', 'web-user');
    formData.append('language', language);
    if (sessionId) formData.append('session_id', sessionId);

    try {
      const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API}/api/voice/consultation`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: 'user', text: data.transcript || '🎤 (audio)' },
        { role: 'assistant', text: data.response_text },
      ]);
    } catch (err) {
      console.error('Voice processing failed:', err);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Sorry, I had trouble processing your audio. Please try again.' },
      ]);
    } finally {
      setState(STATES.IDLE);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold text-ayur-800 mb-2">🎙️ Voice Consultation</h2>
      <p className="text-gray-500 mb-6">Speak with AyurVani for personalized Ayurvedic guidance.</p>

      {/* Messages */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-6 min-h-[300px] max-h-[500px] overflow-y-auto space-y-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-center mt-20">
            Press the microphone button and start speaking...
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
                msg.role === 'user'
                  ? 'bg-ayur-600 text-white rounded-br-sm'
                  : 'bg-gray-100 text-gray-800 rounded-bl-sm'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="flex justify-center">
        {state === STATES.IDLE && (
          <button
            onClick={startRecording}
            className="w-20 h-20 rounded-full bg-ayur-600 hover:bg-ayur-700 text-white text-3xl shadow-lg transition transform hover:scale-105"
          >
            🎙️
          </button>
        )}
        {state === STATES.RECORDING && (
          <button
            onClick={stopRecording}
            className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 text-white text-3xl shadow-lg animate-pulse"
          >
            ⏹️
          </button>
        )}
        {state === STATES.PROCESSING && (
          <div className="w-20 h-20 rounded-full bg-saffron-500 text-white text-2xl flex items-center justify-center shadow-lg animate-spin-slow">
            ⏳
          </div>
        )}
      </div>

      <p className="text-center text-xs text-gray-400 mt-4">
        {state === STATES.RECORDING && 'Listening... tap ⏹️ when done.'}
        {state === STATES.PROCESSING && 'AyurVani is thinking...'}
        {state === STATES.IDLE && 'Tap the mic to start.'}
      </p>
    </div>
  );
}