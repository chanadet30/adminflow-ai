"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

const API = "https://adminflow-ai-production.up.railway.app";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [user, setUser] = useState<any>(null);
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [invoiceResult, setInvoiceResult] = useState("");

  // 🔑 Charger token au démarrage
  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
  }, []);

  // 👤 Charger user
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

  // 🔐 LOGIN
  const login = async () => {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
    } else {
      alert("Erreur login");
    }
  };

  // 📧 EMAIL
  const analyze = async () => {
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
  };

  // 📄 FACTURE
  const analyzeInvoice = async () => {
    if (!file) {
      alert("Ajoute un fichier");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API}/invoice`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: formData,
    });

    const data = await res.json();
    setInvoiceResult(JSON.stringify(data, null, 2));
  };

  // 💳 STRIPE (FIX FINAL)
  const upgrade = async () => {
    const token = localStorage.getItem("token");

    console.log("TOKEN:", token);

    if (!token) {
      alert("Reconnecte-toi");
      return;
    }

    const res = await fetch(`${API}/create-checkout-session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log("DATA:", data);

    if (res.status === 401) {
      alert("Session expirée → reconnecte-toi");
      return;
    }

    if (data.url) {
      window.location.href = data.url;
    } else {
      alert("Erreur Stripe");
    }
  };

  // 🚪 LOGOUT
  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">

      {!token ? (
        <div className="flex items-center justify-center w-full">
          <div className="bg-white p-8 rounded-xl shadow w-96 text-center">

            <Image src="/logo.png" alt="logo" width={80} height={80} className="mx-auto mb-4"/>

            <h1 className="text-xl font-bold mb-4">AdminFlow AI</h1>

            <input
              placeholder="Email"
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded mb-2"
            />

            <input
              type="password"
              placeholder="Mot de passe"
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded mb-4"
            />

            <button onClick={login} className="w-full bg-indigo-600 text-white p-2 rounded">
              Login
            </button>

          </div>
        </div>

      ) : (

        <>
          <aside className="w-64 bg-white p-6 shadow flex flex-col">
            <h2 className="font-bold mb-6">Dashboard</h2>

            <button onClick={upgrade} className="mt-auto bg-yellow-400 p-2 rounded">
              ⭐ Premium
            </button>

            <button onClick={logout} className="mt-2 bg-red-500 text-white p-2 rounded">
              Logout
            </button>
          </aside>

          <main className="flex-1 p-10">

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-4 rounded shadow">
                Emails: {user?.usage}
              </div>
              <div className="bg-white p-4 rounded shadow">
                Statut: {user?.premium ? "Premium" : "Free"}
              </div>
              <div className="bg-white p-4 rounded shadow">
                API: Active
              </div>
            </div>

            <textarea
              placeholder="Colle un email..."
              onChange={(e) => setContent(e.target.value)}
              className="w-full p-3 border rounded mb-3"
            />

            <button onClick={analyze} className="bg-indigo-600 text-white p-2 rounded">
              Analyser email
            </button>

            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="mt-4"
            />

            <button onClick={analyzeInvoice} className="bg-green-600 text-white p-2 mt-2 rounded">
              Analyser facture
            </button>

            <pre className="mt-4">{result}</pre>
            <pre>{invoiceResult}</pre>

          </main>
        </>
      )}
    </div>
  );
}