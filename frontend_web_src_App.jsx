import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import VoiceConsultation from './components/VoiceConsultation';
import SymptomAnalyzer from './components/SymptomAnalyzer';
import TreatmentPlan from './components/TreatmentPlan';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'മലയാളം' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'mr', label: 'मराठी' },
  { code: 'gu', label: 'ગુજરાતી' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ' },
  { code: 'sa', label: 'संस्कृतम्' },
];

function Navbar({ language, setLanguage }) {
  return (
    <nav className="bg-ayur-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold">
          <span className="text-2xl">🌿</span> AyurVani
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm">
          <Link to="/" className="hover:text-ayur-200 transition">Home</Link>
          <Link to="/consultation" className="hover:text-ayur-200 transition">Voice Consultation</Link>
          <Link to="/symptoms" className="hover:text-ayur-200 transition">Symptom Analyzer</Link>
          <Link to="/treatment" className="hover:text-ayur-200 transition">Treatment Plan</Link>
        </div>

        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-ayur-700 text-white rounded px-2 py-1 text-sm border border-ayur-600"
        >
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      </div>
    </nav>
  );
}

function Home() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <h1 className="text-5xl font-bold text-ayur-800 mb-4">🌿 AyurVani</h1>
      <p className="text-xl text-gray-600 mb-8">
        Multilingual Ayurveda Healthcare Assistant powered by Amazon Nova
      </p>

      <div className="grid md:grid-cols-3 gap-6 mt-12">
        <Link to="/consultation" className="block p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition border border-ayur-100">
          <div className="text-4xl mb-3">🎙️</div>
          <h3 className="font-semibold text-lg text-ayur-800">Voice Consultation</h3>
          <p className="text-gray-500 text-sm mt-2">Speak with AyurVani in your language for personalized Ayurvedic guidance.</p>
        </Link>

        <Link to="/symptoms" className="block p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition border border-ayur-100">
          <div className="text-4xl mb-3">🔍</div>
          <h3 className="font-semibold text-lg text-ayur-800">Symptom Analyzer</h3>
          <p className="text-gray-500 text-sm mt-2">Describe your symptoms for dosha-based analysis and herb recommendations.</p>
        </Link>

        <Link to="/treatment" className="block p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition border border-ayur-100">
          <div className="text-4xl mb-3">📋</div>
          <h3 className="font-semibold text-lg text-ayur-800">Treatment Plan</h3>
          <p className="text-gray-500 text-sm mt-2">Get a personalized Ayurvedic treatment plan including diet, herbs, and yoga.</p>
        </Link>
      </div>

      <p className="mt-16 text-xs text-gray-400">
        ⚠️ AyurVani provides educational information only. Always consult a qualified healthcare provider.
      </p>
    </div>
  );
}

export default function App() {
  const [language, setLanguage] = useState('en');

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-b from-ayur-50 to-white">
        <Navbar language={language} setLanguage={setLanguage} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/consultation" element={<VoiceConsultation language={language} />} />
          <Route path="/symptoms" element={<SymptomAnalyzer language={language} />} />
          <Route path="/treatment" element={<TreatmentPlan language={language} />} />
        </Routes>
      </div>
    </Router>
  );
}