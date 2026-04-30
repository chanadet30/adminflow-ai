"use client";
import { useState, useEffect } from "react";
import jsPDF from "jspdf";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

export default function Home() {
  const [mode, setMode] = useState("email");
  const [email, setEmail] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [history, setHistory] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [advancedStats, setAdvancedStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // EMAIL
  const analyzeEmail = async () => {
    if (!email) return alert("Ajoute un email");

    setLoading(true);
    setResult("");

    const res = await fetch(
      "http://127.0.0.1:8000/email?content=" + encodeURIComponent(email),
      { method: "POST" }
    );

    const data = await res.json();
    const resText = data.result || data.error;

    setResult(resText);
    setHistory(prev => [{ type: "email", content: resText }, ...prev]);

    setLoading(false);
  };

  // FACTURE
  const analyzeInvoice = async () => {
    if (!file) return alert("Choisis une facture");

    setLoading(true);
    setResult("");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/invoice", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    const resText = data.invoice_data || data.error;

    const formatted =
      typeof resText === "object"
        ? JSON.stringify(resText, null, 2)
        : resText;

    setResult(formatted);

    setHistory(prev => [
      { type: "facture", content: formatted },
      ...prev
    ]);

    loadChart();
    loadAdvancedStats();

    setLoading(false);
  };

  // GRAPH
  const loadChart = async () => {
    const res = await fetch("http://127.0.0.1:8000/history");
    const data = await res.json();

    const categories = {};

    data.forEach(item => {
      if (item.type === "facture") {
        try {
          const parsed = JSON.parse(item.content);
          const cat = parsed.categorie || "autre";
          const montant = parseFloat(parsed.montant) || 0;

          categories[cat] = (categories[cat] || 0) + montant;
        } catch {}
      }
    });

    const chart = Object.keys(categories).map(cat => ({
      name: cat,
      montant: categories[cat]
    }));

    setChartData(chart);
  };

  // DASHBOARD
  const loadAdvancedStats = async () => {
    const res = await fetch("http://127.0.0.1:8000/advanced-stats");
    const data = await res.json();
    setAdvancedStats(data);
  };

  useEffect(() => {
    loadChart();
    loadAdvancedStats();
  }, []);

  // EXPORT
  const downloadTXT = () => {
    const blob = new Blob([result], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "resultat.txt";
    link.click();
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.text(result, 10, 10);
    doc.save("resultat.pdf");
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>

        {/* HEADER */}
        <div style={styles.header}>
          <img src="/logo.png" style={styles.logo} />
          <h1>AdminFlow AI 💎</h1>
          <p>Assistant administratif intelligent</p>
        </div>

        {/* DASHBOARD */}
        {advancedStats && (
          <div style={styles.dashboard}>
            <h3>💰 Dashboard financier</h3>

            <h4>📊 Catégories</h4>
            {Object.entries(advancedStats.categories).map(([cat, val]) => (
              <p key={cat}>{cat} : {val} €</p>
            ))}

            <h4>📅 Mensuel</h4>
            {Object.entries(advancedStats.monthly).map(([m, val]) => (
              <p key={m}>{m} : {val} €</p>
            ))}
          </div>
        )}

        {/* GRAPH */}
        {chartData.length > 0 && (
          <div style={{ height: 300 }}>
            <h3>📊 Dépenses par catégorie</h3>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar
                  dataKey="montant"
                  fill="#007bff"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* TABS */}
        <div style={styles.tabs}>
          <button onClick={() => setMode("email")}>📧 Email</button>
          <button onClick={() => setMode("invoice")}>📄 Facture</button>
        </div>

        {/* EMAIL */}
        {mode === "email" && (
          <>
            <textarea
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Collez un email..."
              style={styles.textarea}
            />
            <button onClick={analyzeEmail} style={styles.button}>
              {loading ? "Analyse..." : "Analyser"}
            </button>
          </>
        )}

        {/* FACTURE */}
        {mode === "invoice" && (
          <>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={analyzeInvoice} style={styles.button}>
              {loading ? "Analyse..." : "Analyser facture"}
            </button>
          </>
        )}

        {/* RESULT */}
        {result && (
          <div style={styles.result}>
            <pre>{result}</pre>

            <button onClick={downloadTXT}>TXT</button>
            <button onClick={downloadPDF}>PDF</button>
          </div>
        )}

        {/* HISTORY */}
        {history.length > 0 && (
          <div style={styles.history}>
            <h3>Historique</h3>
            {history.map((item, i) => (
              <div key={i} style={styles.historyItem}>
                <strong>{item.type}</strong>
                <pre>{item.content}</pre>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

const styles = {
  container: {
    background: "linear-gradient(135deg,#eef2f7,#dce6f5)",
    minHeight: "100vh",
    padding: 40
  },
  card: {
    maxWidth: 800,
    margin: "auto",
    background: "white",
    padding: 30,
    borderRadius: 16,
    boxShadow: "0 10px 30px rgba(0,0,0,0.1)"
  },
  header: {
    textAlign: "center",
    marginBottom: 20
  },
  logo: {
    width: 60,
    marginBottom: 10
  },
  dashboard: {
    background: "#f4f6fb",
    padding: 15,
    borderRadius: 10,
    marginBottom: 20
  },
  tabs: {
    display: "flex",
    gap: 10,
    marginTop: 20
  },
  textarea: {
    width: "100%",
    height: 120,
    marginTop: 10
  },
  button: {
    marginTop: 10,
    padding: 12,
    background: "#007bff",
    color: "white",
    border: "none",
    borderRadius: 8
  },
  result: {
    marginTop: 20,
    background: "#f9f9f9",
    padding: 10
  },
  history: {
    marginTop: 20
  },
  historyItem: {
    background: "#eee",
    padding: 10,
    marginTop: 10
  }
};