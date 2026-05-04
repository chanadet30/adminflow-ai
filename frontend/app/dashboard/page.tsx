"use client";

import { useEffect, useState } from "react";

const API = "https://adminflow-ai-production.up.railway.app";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadUser = async () => {
    const res = await fetch(`${API}/me`);
    const data = await res.json();
    setUser(data);
  };

  const loadHistory = async () => {
    const res = await fetch(`${API}/history`);
    const data = await res.json();
    setHistory(Array.isArray(data) ? data : []);
  };

  useEffect(() => {
    loadUser();
    loadHistory();
  }, []);

  const analyze = async () => {
    if (!content.trim()) return;

    setLoading(true);

    const res = await fetch(`${API}/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    });

    const data = await res.json();

    if (data.error === "LIMIT_REACHED") {
      if (confirm("🚀 Passe Premium pour continuer")) {
        upgrade();
      }
      setLoading(false);
      return;
    }

    setResult(data.result);

    await loadHistory();
    await loadUser();

    setLoading(false);
  };

  const upgrade = async () => {
    const res = await fetch(`${API}/create-checkout-session`, {
      method: "POST",
    });

    const data = await res.json();
    window.location.href = data.url;
  };

  const extractReply = (text: string) => {
    const parts = text.split("✉️ Réponse suggérée :");
    return parts[1] ? parts[1].trim() : text;
  };

  const reply = extractReply(result);

  return (
    <div className="min-h-screen bg-[#f7f8fa] flex">

      {/* SIDEBAR */}
      <aside className="w-64 bg-white border-r px-6 py-8 flex flex-col justify-between">

        <div>
          <h2 className="text-xl font-semibold text-indigo-600 mb-10">
            AdminFlow
          </h2>

          <div className="space-y-4 text-sm text-gray-600">
            <p>📊 Dashboard</p>
            <p className="opacity-40">Historique</p>
          </div>
        </div>

        <div className="text-sm">

          {user?.premium ? (
            <div className="bg-green-100 text-green-700 px-3 py-2 rounded-lg">
              💎 Premium actif
            </div>
          ) : (
            <div>
              <p className="text-gray-500 mb-2">
                Plan gratuit
              </p>

              <button
                onClick={upgrade}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition"
              >
                💎 Passer Premium
              </button>
            </div>
          )}

        </div>

      </aside>

      {/* MAIN */}
      <main className="flex-1 p-10">

        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold">
            Dashboard
          </h1>

          <p className="text-gray-500 text-sm mt-1">
            Utilisation : {history.length} / {user?.premium ? "∞" : "3"}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* ANALYSE CARD */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border">

            <textarea
              placeholder="Colle ton email ici..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full p-4 border rounded-lg mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <button
              onClick={analyze}
              className="bg-indigo-600 text-white px-5 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              {loading ? "Analyse..." : "Analyser"}
            </button>

            {result && (
              <div className="mt-6 space-y-4">

                {/* REPLY */}
                <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-xl">
                  <p className="text-xs text-indigo-500 mb-2">
                    Réponse prête
                  </p>

                  <p className="text-sm whitespace-pre-wrap">
                    {reply}
                  </p>
                </div>

                {/* COPY */}
                <button
                  onClick={() => navigator.clipboard.writeText(reply)}
                  className="text-xs text-indigo-600 hover:underline"
                >
                  Copier la réponse
                </button>

                {/* FULL */}
                <details className="text-sm text-gray-500">
                  <summary className="cursor-pointer">
                    Voir analyse complète
                  </summary>

                  <pre className="mt-2 whitespace-pre-wrap">
                    {result}
                  </pre>
                </details>

              </div>
            )}

          </div>

          {/* HISTORY */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border">

            <h3 className="font-semibold mb-4">
              Historique
            </h3>

            <div className="space-y-3 max-h-[500px] overflow-auto">

              {history.length === 0 && (
                <p className="text-gray-400 text-sm">
                  Aucun historique
                </p>
              )}

              {history.map((h, i) => (
                <div
                  key={i}
                  className="p-3 bg-gray-50 rounded-lg text-sm"
                >
                  <p className="text-gray-500 text-xs mb-1">
                    Email
                  </p>

                  <p className="truncate">
                    {h.content}
                  </p>

                  <p className="text-gray-400 text-xs mt-2">
                    Réponse
                  </p>

                  <p className="truncate">
                    {extractReply(h.result)}
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