import React, { useState } from 'react';
import { assessDosha, sendMessage } from '../services/api';

const PRAKRITI_QUESTIONS = [
  { id: 'body_frame', q: 'What best describes your body frame?', opts: { vata: 'Thin, light build', pitta: 'Medium, athletic build', kapha: 'Large, sturdy build' } },
  { id: 'skin_type', q: 'How is your skin?', opts: { vata: 'Dry, rough, cool', pitta: 'Warm, oily, sensitive', kapha: 'Thick, smooth, oily' } },
  { id: 'appetite', q: 'How is your appetite?', opts: { vata: 'Irregular', pitta: 'Strong, can\'t skip meals', kapha: 'Steady, can skip meals' } },
  { id: 'digestion', q: 'How is your digestion?', opts: { vata: 'Gas, bloating, irregular', pitta: 'Quick, sometimes acidic', kapha: 'Slow, heavy after meals' } },
  { id: 'sleep', q: 'How do you sleep?', opts: { vata: 'Light, interrupted', pitta: 'Moderate, vivid dreams', kapha: 'Deep, hard to wake' } },
  { id: 'temperament', q: 'Your mental nature?', opts: { vata: 'Creative, anxious, restless', pitta: 'Sharp, driven, irritable', kapha: 'Calm, steady, attached' } },
  { id: 'stress', q: 'How do you handle stress?', opts: { vata: 'Worry and anxiety', pitta: 'Frustration and anger', kapha: 'Withdrawal and lethargy' } },
];

export default function TreatmentPlan({ language }) {
  const [step, setStep] = useState(0); // 0: quiz, 1: result, 2: plan
  const [answers, setAnswers] = useState({});
  const [doshaResult, setDoshaResult] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnswer = (questionId, dosha) => {
    setAnswers((prev) => ({ ...prev, [questionId]: dosha }));
  };

  const submitAssessment = async () => {
    setLoading(true);
    try {
      const data = await assessDosha('web-user', answers, language);
      setDoshaResult(data);
      setStep(1);
    } catch (err) {
      console.error('Assessment failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const generatePlan = async () => {
    setLoading(true);
    try {
      const data = await sendMessage(
        'web-user',
        `Generate a comprehensive weekly Ayurvedic treatment plan for a ${doshaResult.primary_dosha} constitution person. Include daily routine (dinacharya), diet plan, herbs, yoga, and lifestyle tips.`,
        language
      );
      setPlan(data);
      setStep(2);
    } catch (err) {
      console.error('Plan generation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const allAnswered = Object.keys(answers).length === PRAKRITI_QUESTIONS.length;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold text-ayur-800 mb-2">📋 Treatment Plan</h2>
      <p className="text-gray-500 mb-6">
        Answer questions to determine your Prakriti, then get a personalized plan.
      </p>

      {/* Step 0: Quiz */}
      {step === 0 && (
        <div className="space-y-4">
          {PRAKRITI_QUESTIONS.map((pq, idx) => (
            <div key={pq.id} className="bg-white rounded-xl shadow-md p-4">
              <p className="font-medium text-gray-800 mb-3">
                {idx + 1}. {pq.q}
              </p>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(pq.opts).map(([dosha, label]) => (
                  <button
                    key={dosha}
                    onClick={() => handleAnswer(pq.id, dosha)}
                    className={`p-2 rounded-lg text-sm border transition ${
                      answers[pq.id] === dosha
                        ? 'bg-ayur-600 text-white border-ayur-600'
                        : 'bg-gray-50 text-gray-700 border-gray-200 hover:border-ayur-400'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <button
            onClick={submitAssessment}
            disabled={!allAnswered || loading}
            className="w-full bg-ayur-600 hover:bg-ayur-700 text-white font-medium py-3 rounded-lg transition disabled:opacity-50"
          >
            {loading ? '⏳ Analyzing...' : '🧬 Determine My Prakriti'}
          </button>
        </div>
      )}

      {/* Step 1: Dosha Result */}
      {step === 1 && doshaResult && (
        <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
          <div className="text-center">
            <p className="text-sm text-gray-500">Your Prakriti (Constitution)</p>
            <h3 className="text-3xl font-bold text-ayur-700 capitalize mt-1">
              {doshaResult.primary_dosha}
              {doshaResult.secondary_dosha && (
                <span className="text-xl text-gray-400"> / {doshaResult.secondary_dosha}</span>
              )}
            </h3>
          </div>

          <p className="text-gray-700">{doshaResult.prakriti_description}</p>

          {doshaResult.characteristics?.length > 0 && (
            <div>
              <h4 className="font-semibold text-ayur-800 mb-1">Key Characteristics</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {doshaResult.characteristics.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}

          {doshaResult.dietary_guidelines?.length > 0 && (
            <div>
              <h4 className="font-semibold text-ayur-800 mb-1">🍽️ Dietary Guidelines</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {doshaResult.dietary_guidelines.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => { setStep(0); setAnswers({}); setDoshaResult(null); }}
              className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition"
            >
              ↩ Retake Quiz
            </button>
            <button
              onClick={generatePlan}
              disabled={loading}
              className="flex-1 bg-ayur-600 hover:bg-ayur-700 text-white py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? '⏳ Generating...' : '📋 Generate Treatment Plan'}
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Full Plan */}
      {step === 2 && plan && (
        <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
          <h3 className="font-bold text-ayur-800 text-lg">
            Your Personalized Ayurvedic Plan
          </h3>
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
            {plan.response}
          </div>

          {plan.recommendations?.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="font-semibold text-ayur-800 mb-2">Key Recommendations</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {plan.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}

          <button
            onClick={() => { setStep(0); setAnswers({}); setDoshaResult(null); setPlan(null); }}
            className="w-full border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition mt-4"
          >
            ↩ Start Over
          </button>

          <p className="text-xs text-gray-400">
            ⚠️ This plan is for educational purposes. Consult an Ayurvedic practitioner before starting.
          </p>
        </div>
      )}
    </div>
  );
}