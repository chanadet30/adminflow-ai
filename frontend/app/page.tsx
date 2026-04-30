"use client";

import { useState } from "react";

export default function Home() {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const API_URL = "https://adminflow-ai-production.up.railway.app";

  const handleAnalyze = async () => {
    setLoading(true);
    setResult("");

    try {
      const res = await fetch(`${API_URL}/email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: email }),
      });

      const data = await res.json();

      if (data.result) {
        setResult(data.result);
      } else {
        setResult("Erreur API");
      }
    } catch (err) {
      setResult("Erreur réseau");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl">

        <h1 className="text-2xl font-bold text-center mb-2">
          🚀 AdminFlow AI
        </h1>
        <p className="text-center text-gray-500 mb-6">
          Assistant administratif intelligent
        </p>

        <textarea
          className="w-full border rounded-lg p-3 mb-4"
          rows={6}
          placeholder="Colle ton email ici..."
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <button
          onClick={handleAnalyze}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
        >
          {loading ? "Analyse en cours..." : "Analyser Email"}
        </button>

        {result && (
          <div className="mt-6 bg-gray-50 p-4 rounded-lg border">
            <h2 className="font-semibold mb-2">📊 Résultat</h2>
            <pre className="whitespace-pre-wrap text-sm">{result}</pre>
          </div>
        )}
      </div>
    </div>
  );
}