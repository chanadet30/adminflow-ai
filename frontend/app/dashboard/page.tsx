"use client";

import { useEffect, useState } from "react";

const API = "https://adminflow-ai-production.up.railway.app";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // -------------------------
  // LOAD USER
  // -------------------------
  const loadUser = async () => {
    const res = await fetch(`${API}/me`);
    const data = await res.json();
    setUser(data);
  };

  // -------------------------
  // LOAD HISTORY
  // -------------------------
  const loadHistory = async () => {
    const res = await fetch(`${API}/history`);
    const data = await res.json();

    if (Array.isArray(data)) {
      setHistory(data);
    } else {
      setHistory([]);
    }
  };

  useEffect(() => {
    loadUser();
    loadHistory();
  }, []);

  // -------------------------
  // ANALYZE
  // -------------------------
  const analyze = async () => {
    if (!content.trim()) {
      alert("Ajoute un email");
      return;
    }

    setLoading(true);

    const res = await fetch(`${API}/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    });

    const data = await res.json();

    // 🔒 LIMIT FREE
    if (data.error === "LIMIT_REACHED") {
      alert("🚀 Passe Premium pour continuer");
      setLoading(false);
      return;
    }

    setResult(data.result);

    await loadHistory();
    await loadUser();

    setLoading(false);
  };

  // -------------------------
  // UPGRADE
  // -------------------------
  const upgrade = async () => {
    const res = await fetch(`${API}/create-checkout-session`, {
      method: "POST",
    });

    const data = await res.json();

    window.location.href = data.url;
  };

  // -------------------------
  // UI
  // -------------------------
  return (
    <div className="min-h-screen bg-gray-100 flex">

      {/* SIDEBAR */}
      <aside className="w-64 bg-white border-r p-6 flex flex-col">
        <h2 className="text-xl font-bold mb-10 text-indigo-600">
          AdminFlow
        </h2>

        <div className="mt-auto">

          <div className="mb-4">
            {user?.premium ? (
              <span className="text-green-600 font-semibold">
                💎 Premium actif
              </span>
            ) : (
              <span className="text-gray-500">
                Free plan
              </span>
            )}
          </div>

          {!user?.premium && (
            <button
              onClick={upgrade}
              className="bg-indigo-600 text-white px-4 py-2 rounded w-full"
            >
              🚀 Passer Premium
            </button>
          )}

        </div>
      </aside>

      {/* MAIN */}
      <main className="flex-1 p-10">

        <h1 className="text-3xl font-bold mb-6">
          Dashboard
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* ANALYSE */}
          <div className="bg-white p-6 rounded-xl shadow">

            <textarea
              placeholder="Colle un email..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full p-4 border rounded mb-4"
            />

            <button
              onClick={analyze}
              className="bg-indigo-600 text-white px-4 py-2 rounded"
            >
              {loading ? "Analyse..." : "Analyser"}
            </button>

            {result && (
              <div className="mt-4 bg-gray-50 p-3 rounded">
                <pre>{result}</pre>
              </div>
            )}
          </div>

          {/* HISTORIQUE */}
          <div className="bg-white p-6 rounded-xl shadow">

            <h3 className="font-bold mb-4">
              Historique
            </h3>

            <div className="space-y-3 max-h-96 overflow-auto">

              {history.length === 0 && (
                <p className="text-gray-400 text-sm">
                  Aucun historique
                </p>
              )}

              {history.map((h, i) => (
                <div
                  key={i}
                  className="p-3 bg-gray-50 rounded border"
                >
                  <p className="text-xs text-gray-500 mb-1">
                    Email
                  </p>
                  <p className="text-sm truncate">
                    {h.content}
                  </p>

                  <p className="text-xs text-gray-500 mt-2">
                    Résultat
                  </p>
                  <p className="text-sm truncate">
                    {h.result}
                  </p>
                </div>
              ))}

            </div>

          </div>

        </div>

      </main>
    </div>
  );
}