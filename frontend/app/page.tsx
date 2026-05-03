"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

const API = "https://adminflow-ai-production.up.railway.app";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [invoiceResult, setInvoiceResult] = useState("");

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
  }, []);

  const loadUser = async () => {
    const res = await fetch(`${API}/me`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    const data = await res.json();
    setUser(data);
  };

  useEffect(() => {
    if (token) loadUser();
  }, [token]);

  const login = async () => {
    setLoading(true);

    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    setLoading(false);

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
    } else {
      alert("Erreur login");
    }
  };

  const analyze = async () => {
    if (!user?.premium) {
      alert("🔒 Premium requis pour analyser les emails");
      return;
    }

    setLoading(true);

    const res = await fetch(`${API}/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ content }),
    });

    const data = await res.json();
    setResult(JSON.stringify(data, null, 2));
    setLoading(false);
    loadUser();
  };

  const analyzeInvoice = async () => {
    if (!file) {
      alert("Ajoute un fichier PDF");
      return;
    }

    if (!user?.premium) {
      alert("🔒 Premium requis pour les factures");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    const res = await fetch(`${API}/invoice`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: formData,
    });

    const data = await res.json();
    setInvoiceResult(JSON.stringify(data, null, 2));
    setLoading(false);
  };

  const upgrade = async () => {
    const res = await fetch(`${API}/create-checkout-session`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    const data = await res.json();
    window.location.href = data.url;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {!token ? (
        <div className="flex items-center justify-center w-full">
          <div className="bg-white p-8 rounded-2xl shadow-xl w-[380px] text-center">
            <Image
              src="/logo.png"
              alt="logo"
              width={90}
              height={90}
              className="mx-auto mb-4"
            />

            <h1 className="text-xl font-bold mb-2">AdminFlow AI</h1>
            <p className="text-gray-500 text-sm mb-4">
              Assistant intelligent
            </p>

            <input
              placeholder="Email"
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 mb-3 border rounded-lg"
            />

            <input
              type="password"
              placeholder="Mot de passe"
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 mb-4 border rounded-lg"
            />

            <button
              onClick={login}
              className="w-full p-3 bg-indigo-600 text-white rounded-lg"
            >
              {loading ? "Connexion..." : "Se connecter"}
            </button>
          </div>
        </div>
      ) : (
        <>
          <aside className="w-64 bg-white shadow-md p-6 flex flex-col">
            <div className="flex items-center gap-2 mb-8">
              <Image src="/logo.png" alt="logo" width={30} height={30} />
              <span className="font-bold text-lg">AdminFlow</span>
            </div>

            <button className="mb-3 p-2 rounded hover:bg-gray-100 text-left">
              📊 Dashboard
            </button>

            <button className="mb-3 p-2 rounded hover:bg-gray-100 text-left">
              📧 Emails
            </button>

            <button className="mb-3 p-2 rounded hover:bg-gray-100 text-left">
              📄 Factures
            </button>

            <button
              onClick={upgrade}
              className="mt-auto bg-yellow-400 p-2 rounded font-semibold"
            >
              ⭐ Premium
            </button>

            <button
              onClick={logout}
              className="mt-2 bg-red-500 text-white p-2 rounded"
            >
              Logout
            </button>
          </aside>

          <main className="flex-1 p-10">
            <div className="flex justify-between mb-8">
              <h1 className="text-2xl font-bold">Dashboard</h1>
              <span className="text-sm text-gray-600">{user?.email}</span>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-gray-500 text-sm">Emails analysés</p>
                <p className="text-2xl font-bold">{user?.usage || 0}</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-gray-500 text-sm">Statut</p>
                <p className="text-2xl font-bold">
                  {user?.premium ? "Premium" : "Free"}
                </p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-gray-500 text-sm">API</p>
                <p className="text-2xl font-bold">Active</p>
              </div>
            </div>

            {/* EMAIL */}
            <div className="bg-white p-6 rounded-xl shadow mb-6">
              <h2 className="font-semibold mb-3">📧 Analyse Email</h2>

              <textarea
                placeholder="Colle un email ici..."
                onChange={(e) => setContent(e.target.value)}
                className="w-full p-3 border rounded-lg mb-4 h-32"
              />

              <button
                onClick={analyze}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
              >
                {loading ? "Analyse..." : "Analyser"}
              </button>

              {result && (
                <pre className="mt-4 bg-gray-100 p-3 rounded text-sm">
                  {result}
                </pre>
              )}
            </div>

            {/* FACTURE */}
            <div className="bg-white p-6 rounded-xl shadow">
              <h2 className="font-semibold mb-3">📄 Analyse Facture</h2>

              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mb-4"
              />

              <button
                onClick={analyzeInvoice}
                className="bg-green-600 text-white px-4 py-2 rounded-lg"
              >
                Analyser la facture
              </button>

              {invoiceResult && (
                <pre className="mt-4 bg-gray-100 p-3 rounded text-sm">
                  {invoiceResult}
                </pre>
              )}
            </div>
          </main>
        </>
      )}
    </div>
  );
}