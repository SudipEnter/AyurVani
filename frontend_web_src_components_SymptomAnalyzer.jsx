import React, { useState } from 'react';
import { analyzeSymptoms } from '../services/api';

export default function SymptomAnalyzer({ language }) {
  const [symptoms, setSymptoms] = useState('');
  const [duration, setDuration] = useState('');
  const [severity, setSeverity] = useState(5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!symptoms.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const symptomList = symptoms.split(',').map((s) => s.trim()).filter(Boolean);
      const data = await analyzeSymptoms('web-user', symptomList, language, {
        duration,
        severity,
      });
      setResult(data);
    } catch (err) {
      console.error('Symptom analysis failed:', err);
      setResult({ analysis: 'Analysis failed. Please try again.', possible_imbalances: [] });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold text-ayur-800 mb-2">🔍 Symptom Analyzer</h2>
      <p className="text-gray-500 mb-6">
        Describe your symptoms for an Ayurvedic dosha-based analysis.
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-md p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Symptoms (comma separated)
          </label>
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            rows={3}
            placeholder="e.g., headache, fatigue, poor digestion, joint pain"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-ayur-400 focus:border-transparent"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
            <input
              type="text"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              placeholder="e.g., 2 weeks"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-ayur-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity: {severity}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={severity}
              onChange={(e) => setSeverity(Number(e.target.value))}
              className="w-full accent-ayur-600"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-ayur-600 hover:bg-ayur-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50"
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyze Symptoms'}
        </button>
      </form>

      {/* Results */}
      {result && (
        <div className="mt-8 bg-white rounded-xl shadow-md p-6 space-y-6">
          <div>
            <h3 className="font-semibold text-ayur-800 text-lg mb-2">Analysis</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.analysis}</p>
          </div>

          {result.possible_imbalances?.length > 0 && (
            <div>
              <h3 className="font-semibold text-ayur-800 mb-2">Dosha Imbalances</h3>
              <div className="flex flex-wrap gap-2">
                {result.possible_imbalances.map((imb, i) => (
                  <span key={i} className="bg-saffron-500 text-white text-sm px-3 py-1 rounded-full">
                    {imb}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.recommended_herbs?.length > 0 && (
            <div>
              <h3 className="font-semibold text-ayur-800 mb-2">🌿 Recommended Herbs</h3>
              <div className="grid md:grid-cols-2 gap-3">
                {result.recommended_herbs.map((herb, i) => (
                  <div key={i} className="border border-ayur-200 rounded-lg p-3">
                    <p className="font-medium text-ayur-700">
                      {herb.name} {herb.sanskrit_name && <span className="text-gray-400 text-xs">({herb.sanskrit_name})</span>}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{herb.benefits}</p>
                    {herb.dosage && <p className="text-xs text-gray-500 mt-1">💊 {herb.dosage}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.dietary_suggestions?.length > 0 && (
            <div>
              <h3 className="font-semibold text-ayur-800 mb-2">🍽️ Dietary Suggestions</h3>
              <ul className="list-disc list-inside text-gray-700 text-sm space-y-1">
                {result.dietary_suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}

          {result.yoga_recommendations?.length > 0 && (
            <div>
              <h3 className="font-semibold text-ayur-800 mb-2">🧘 Yoga Recommendations</h3>
              <ul className="list-disc list-inside text-gray-700 text-sm space-y-1">
                {result.yoga_recommendations.map((y, i) => <li key={i}>{y}</li>)}
              </ul>
            </div>
          )}

          {result.disclaimer && (
            <p className="text-xs text-gray-400 border-t pt-3">⚠️ {result.disclaimer}</p>
          )}
        </div>
      )}
    </div>
  );
}