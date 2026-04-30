const API_URL = "https://adminflow-ai-production.up.railway.app";

export async function analyzeEmail(text) {
  const res = await fetch(`${API_URL}/email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content: text }),
  });

  return res.json();
}

export async function analyzeInvoice(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/invoice`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}