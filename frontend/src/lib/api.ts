const API_BASE = import.meta.env.VITE_API_URL || "/api";


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
  hasSystemCapabilityCriteria: string[];
  hasVersion: string;
}) {
  const payload = {
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

export async function fetchAlgorithmSubtypes(algotypeId: string): Promise<{ id: string; label: string }[]> {
  const response = await fetch(`${API_BASE}/vocab/algorithmtypes/${algotypeId}/subtypes?lang=en`);
  if (!response.ok) {
    throw new Error(`Failed to fetch subtypes for ${algotypeId}`);
  }
  return response.json();
}

// Evidence Plan Types
export interface EvidenceItem {
  id: string;
  name: string;
  description: string;
  evidence_type: string;
  priority: string;
  frequency: string;
  responsible_role: string;
  dpv_measure?: string;
  templates?: string[];
  guidance?: string;
}

export interface RequirementEvidencePlan {
  requirement_uri: string;
  requirement_label: string;
  priority: string;
  dpv_measures: string[];
  evidence_items: EvidenceItem[];
  deadline_recommendation: string;
  responsible_roles: string[];
  article_reference?: string;
  estimated_effort?: string;
}

export interface EvidencePlan {
  plan_id: string;
  generated_at: string;
  system_name: string;
  risk_level: string;
  total_gaps: number;
  requirement_plans: RequirementEvidencePlan[];
  summary: {
    total_evidence_items?: number;
    by_priority?: Record<string, number>;
    by_type?: Record<string, number>;
    by_role?: Record<string, number>;
  };
  recommendations: string[];
}

export interface EvidencePlanResponse {
  status: string;
  urn: string;
  evidence_plan: EvidencePlan;
  message: string;
}

/**
 * Generate DPV-based evidence plan for a manual system
 */
export async function generateEvidencePlan(urn: string): Promise<EvidencePlanResponse> {
  const response = await fetch(`${API_BASE}/systems/${encodeURIComponent(urn)}/generate-evidence-plan`, {
    method: "POST",
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to generate evidence plan" }));
    throw new Error(error.detail || "Failed to generate evidence plan");
  }
  return response.json();
}

/**
 * Get stored evidence plan for a manual system
 */
export async function getEvidencePlan(urn: string): Promise<{ urn: string; evidence_plan: EvidencePlan; generated_at: string } | null> {
  const response = await fetch(`${API_BASE}/systems/${encodeURIComponent(urn)}/evidence-plan`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to get evidence plan" }));
    throw new Error(error.detail || "Failed to get evidence plan");
  }
  return response.json();
}

/**
 * Fetch a system by URN with full details
 */
export async function fetchSystemByUrn(urn: string): Promise<Record<string, unknown> | null> {
  const response = await fetch(`${API_BASE}/systems/${encodeURIComponent(urn)}`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to fetch system");
  }
  return response.json();
}

