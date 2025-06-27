const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";


export async function fetchSystems() {
  const response = await fetch(`${API_BASE}/systems`);
  if (!response.ok) {
    throw new Error("Failed to fetch systems");
  }
  const data = await response.json();
  return Array.isArray(data.items) ? data.items : [];
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
  hasPurpose: string[];
  hasDeploymentContext: string[];
  hasTrainingDataOrigin: string[];
  hasInnerSystemCriteria: string[];
  hasVersion: string;
}) {
  const payload = {
    "@context": "http://localhost:8080/ontologias/json-ld-context.json",
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

