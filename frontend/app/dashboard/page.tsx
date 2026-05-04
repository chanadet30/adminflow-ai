"use client";

import { useState } from "react";

export default function Dashboard() {
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");

  const analyze = async () => {
    console.log("CLICK");

    const token = localStorage.getItem("token");

    const res = await fetch(
      "https://adminflow-ai-production.up.railway.app/email", // 🔥 HARD FIX
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
      }
    );

    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log("DATA:", data);

    setResult(data.result);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-8 rounded-xl shadow w-full max-w-xl">

        <h1 className="text-2xl font-bold mb-4">
          Test Analyse
        </h1>

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-3 border rounded mb-4"
        />

        <button
          onClick={analyze}
          className="bg-indigo-600 text-white px-4 py-2 rounded"
        >
          Analyser
        </button>

        {result && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <pre>{result}</pre>
          </div>
        )}

      </div>
    </div>
  );
}