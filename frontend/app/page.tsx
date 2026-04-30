"use client";

import { useState } from "react";

export default function Home() {
  const [email, setEmail] = useState("");
  const [emailResult, setEmailResult] = useState("");

  const [file, setFile] = useState<File | null>(null);
  const [invoiceResult, setInvoiceResult] = useState("");

  const API_URL = "https://adminflow-ai-production.up.railway.app";

  // EMAIL
  const handleEmail = async () => {
    const res = await fetch(`${API_URL}/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: email }),
    });

    const data = await res.json();
    setEmailResult(data.result);
  };

  // INVOICE
  const handleInvoice = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_URL}/invoice`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setInvoiceResult(data.result);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-xl space-y-6">

        <h1 className="text-xl font-bold text-center">
          🚀 AdminFlow AI
        </h1>

        {/* EMAIL */}
        <div>
          <h2 className="font-semibold">📧 Analyse Email</h2>

          <textarea
            className="w-full border p-2 rounded mt-2"
            rows={4}
            placeholder="Colle ton email..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <button
            onClick={handleEmail}
            className="w-full bg-blue-600 text-white py-2 rounded mt-2"
          >
            Analyser Email
          </button>

          {emailResult && (
            <div className="mt-2 bg-gray-100 p-2 rounded">
              <pre>{emailResult}</pre>
            </div>
          )}
        </div>

        {/* INVOICE */}
        <div>
          <h2 className="font-semibold">📄 Analyse Facture</h2>

          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="mt-2"
          />

          <button
            onClick={handleInvoice}
            className="w-full bg-green-600 text-white py-2 rounded mt-2"
          >
            Analyser Facture
          </button>

          {invoiceResult && (
            <div className="mt-2 bg-gray-100 p-2 rounded">
              <pre>{invoiceResult}</pre>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}