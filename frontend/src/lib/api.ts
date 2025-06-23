const API_BASE = "http://localhost:8000"; // Usa tu backend real si cambia

export async function fetchSystems() {
  const response = await fetch(`${API_BASE}/systems`);
  if (!response.ok) {
    throw new Error("Failed to fetch systems");
  }
  return response.json();
}

export async function fetchVocabulary(path: string): Promise<{ id: string; label: string }[]> {
  const response = await fetch(`${API_BASE}/vocab/${path}?lang=en`);
  if (!response.ok) {
    throw new Error(`Failed to fetch vocabulary for ${path}`);
  }
  return response.json();
}

export async function createSystem(data: {
  hasName: string;
  hasPurpose: string;
  hasRiskLevel: string;
  hasDeploymentContext: string;
  hasTrainingDataOrigin: string;
  hasVersion: string;
}) {
  const payload = {
    "@context": "http://ontologias/docs/context.jsonld",
    "@type": "ai:IntelligentSystem",
    ...data,
  };

  const response = await fetch(`${API_BASE}/systems`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to create system");
  }

  return response.json();
}

