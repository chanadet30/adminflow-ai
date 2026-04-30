"use client";

import { useState } from "react";
import { analyzeEmail, analyzeInvoice } from "../lib/api";

export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState("");

  // 📧 EMAIL
  const handleEmail = async () => {
    const data = await analyzeEmail(text);
    setResult(JSON.stringify(data, null, 2));
  };

  // 📄 FACTURE
  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const data = await analyzeInvoice(file);
    setResult(JSON.stringify(data, null, 2));
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>AdminFlow AI</h1>

      {/* EMAIL */}
      <h2>Email</h2>
      <textarea
        placeholder="Colle ton email ici..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", height: 150 }}
      />
      <br />
      <button onClick={handleEmail}>Analyser Email</button>

      <hr style={{ margin: "30px 0" }} />

      {/* FACTURE */}
      <h2>Facture</h2>
      <input type="file" onChange={handleFile} />

      <hr style={{ margin: "30px 0" }} />

      {/* RESULT */}
      <h2>Résultat</h2>
      <pre>{result}</pre>
    </div>
  );
}