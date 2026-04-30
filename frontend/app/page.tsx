"use client";

import { useState } from "react";
import { analyzeEmail, analyzeInvoice } from "../lib/api";

export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  // 📧 EMAIL
  const handleEmail = async () => {
    if (!text) return;

    setLoading(true);
    try {
      const data = await analyzeEmail(text);
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error(err);
      setResult("Erreur API");
    }
    setLoading(false);
  };

  // 📄 FACTURE
  const handleFile = async (e: any) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const data = await analyzeInvoice(file);
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error(err);
      setResult("Erreur upload");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 40, maxWidth: 800, margin: "auto" }}>
      <h1>🚀 AdminFlow AI</h1>
      <p>Assistant administratif intelligent</p>

      {/* EMAIL */}
      <h2>📧 Analyse Email</h2>
      <textarea
        placeholder="Colle ton email ici..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{
          width: "100%",
          height: 120,
          marginBottom: 10,
          padding: 10,
        }}
      />

      <button onClick={handleEmail} disabled={loading}>
        {loading ? "Analyse..." : "Analyser Email"}
      </button>

      <hr style={{ margin: "30px 0" }} />

      {/* FACTURE */}
      <h2>📄 Analyse Facture</h2>
      <input type="file" onChange={handleFile} />

      <hr style={{ margin: "30px 0" }} />

      {/* RESULT */}
      <h2>📊 Résultat</h2>
      <pre
        style={{
          background: "#111",
          color: "#0f0",
          padding: 20,
          borderRadius: 10,
        }}
      >
        {result}
      </pre>
    </div>
  );
}