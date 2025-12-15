/**
 * Forensic Agent API Client
 */

const FORENSIC_API_BASE = import.meta.env.VITE_FORENSIC_API_URL || "http://localhost:8002";

// Stream Event Types
export type StreamEventType =
  | "step_start"
  | "step_progress"
  | "step_complete"
  | "llm_prompt"
  | "llm_response"
  | "sparql_query"
  | "sparql_result"
  | "analysis_complete"
  | "error";

export interface ConversationMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  timestamp: string;
}

export interface StreamEvent {
  event_type: StreamEventType;
  step_number?: number;
  step_name?: string;
  timestamp: string;
  data?: Record<string, unknown>;
  message?: ConversationMessage;
  progress_percent?: number;
}

// Types
export interface Incident {
  id: string;
  headline: string;
  system_name: string;
  technology: string;
  sector: string;
  country: string;
  occurred: string;
  issues: string;
  purpose: string;
  deployer: string;
  developer: string;
  news_trigger: string;
  summary_url: string;
}

export interface ForensicAnalysisResult {
  status: "COMPLETED" | "ERROR" | "PENDING";
  error?: string;
  extraction?: {
    system?: {
      system_name: string;
      organization: string;
      system_type: string;
    };
    incident?: {
      incident_type: string;
      severity: string;
    };
    confidence?: {
      overall: number;
    };
  };
  eu_ai_act?: {
    risk_level: string;
    total_requirements: number;
    criteria: string[];
  };
  compliance_gaps?: {
    compliance_ratio: number;
    missing: number;
    severity: string;
    critical_gaps: Array<string | { reason?: string; requirement?: string }>;
  };
  iso_42001?: {
    total_mapped: number;
    certification_gap_detected: boolean;
  };
  nist_ai_rmf?: {
    total_mapped: number;
    jurisdiction_applicable: boolean;
  };
  report?: string;
  requires_expert_review?: boolean;
  metadata?: Record<string, unknown>;
  source?: string;
  persisted?: {
    success: boolean;
    urn?: string;
    error?: string;
    message?: string;
  };
}

export interface ForensicSystem {
  urn: string;
  hasName: string;
  hasOrganization: string;
  hasRiskLevel: string;
  complianceRatio: number;
  jurisdiction: string;
  source: string;
  aiaaic_id?: string;
  headline?: string;
  incident?: {
    type: string;
    severity: string;
    affectedPopulations: string[];
  };
  missingRequirements?: string[];
  iso_42001?: {
    total_mapped: number;
    certification_gap_detected: boolean;
  };
  nist_ai_rmf?: {
    total_mapped: number;
    jurisdiction_applicable: boolean;
  };
  report?: string;
}

export interface ForensicSystemsResponse {
  items: ForensicSystem[];
  total: number;
}

// AIAAIC CSV URL - fetch via backend
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const AIAAIC_CSV_URL = `${API_BASE}/aiaaic/incidents`;

/**
 * Load incidents from AIAAIC CSV
 */
export async function loadIncidents(): Promise<Incident[]> {
  try {
    const response = await fetch(AIAAIC_CSV_URL);
    if (!response.ok) {
      throw new Error("Failed to fetch AIAAIC data");
    }
    const csvText = await response.text();
    return parseCSV(csvText);
  } catch (error) {
    console.error("Error loading incidents:", error);
    throw error;
  }
}

/**
 * Parse CSV text into Incident objects
 */
function parseCSV(csvText: string): Incident[] {
  const lines = csvText.split("\n");
  if (lines.length < 4) return [];

  // Line 0 is title, Line 1 is headers, Line 2 is subheaders, Line 3+ is data
  const headers = parseCSVLine(lines[1]);

  const headerMap: Record<string, string> = {
    "AIAAIC ID#": "id",
    "AIAAIC ID": "id",
    "Headline": "headline",
    "System name(s)": "system_name",
    "Technology(ies)": "technology",
    "Sector(s)": "sector",
    "Country(ies)": "country",
    "Occurred": "occurred",
    "Issue(s)": "issues",
    "Purpose(s)": "purpose",
    "Deployer(s)": "deployer",
    "Developer(s)": "developer",
    "News trigger(s)": "news_trigger",
    "News trigger": "news_trigger",
    "Summary/links": "summary_url",
    "Summary/URL": "summary_url",
  };

  const incidents: Incident[] = [];

  for (let i = 3; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const values = parseCSVLine(line);
    const incident: Partial<Incident> = {};

    headers.forEach((header, index) => {
      const field = headerMap[header.trim()];
      if (field && values[index] !== undefined) {
        (incident as Record<string, string>)[field] = values[index].trim();
      }
    });

    if (incident.id && incident.id.startsWith("AIAAIC")) {
      incidents.push({
        id: incident.id || "",
        headline: incident.headline || "",
        system_name: incident.system_name || "",
        technology: incident.technology || "",
        sector: incident.sector || "",
        country: incident.country || "",
        occurred: incident.occurred || "",
        issues: incident.issues || "",
        purpose: incident.purpose || "",
        deployer: incident.deployer || "",
        developer: incident.developer || "",
        news_trigger: incident.news_trigger || "",
        summary_url: incident.summary_url || "",
      });
    }
  }

  return incidents;
}

function parseCSVLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

export function getUniqueValues(incidents: Incident[], field: keyof Incident): string[] {
  const values = new Set<string>();
  incidents.forEach((incident) => {
    const value = incident[field];
    if (value) {
      value.split(";").forEach((v) => {
        const trimmed = v.trim();
        if (trimmed) values.add(trimmed);
      });
    }
  });
  return Array.from(values).sort();
}

export interface HealthResponse {
  status: string;
  services: Record<string, string>;
  llm?: {
    provider: string;
    model: string;
  };
  mcp?: {
    connected: boolean;
    stats?: Record<string, unknown>;
  };
}

export async function checkHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${FORENSIC_API_BASE}/health`);
    if (response.ok) {
      return response.json();
    }
    return null;
  } catch {
    return null;
  }
}

export function buildNarrative(incident: Incident): string {
  const parts: string[] = [];
  if (incident.headline) parts.push(incident.headline);
  if (incident.system_name) parts.push(`The AI system "${incident.system_name}" was involved.`);
  if (incident.developer) parts.push(`Developed by: ${incident.developer}.`);
  if (incident.deployer) parts.push(`Deployed by: ${incident.deployer}.`);
  if (incident.technology) parts.push(`Technologies used: ${incident.technology}.`);
  if (incident.purpose) parts.push(`Purpose: ${incident.purpose}.`);
  if (incident.sector) parts.push(`Sector(s) affected: ${incident.sector}.`);
  if (incident.country) parts.push(`Country/region: ${incident.country}.`);
  if (incident.occurred) parts.push(`Occurred in: ${incident.occurred}.`);
  if (incident.issues) parts.push(`Issues identified: ${incident.issues}.`);
  return parts.join(" ");
}

export async function analyzeIncident(request: {
  narrative: string;
  source?: string;
  metadata?: Record<string, unknown>;
  withEvidencePlan?: boolean;
}): Promise<ForensicAnalysisResult> {
  const endpoint = request.withEvidencePlan
    ? `${FORENSIC_API_BASE}/forensic/analyze-with-evidence-plan`
    : `${FORENSIC_API_BASE}/forensic/analyze`;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      narrative: request.narrative,
      source: request.source,
      metadata: request.metadata,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(error.detail || "Analysis failed");
  }
  return response.json();
}

export async function getForensicSystems(
  limit: number = 20,
  offset: number = 0,
  source?: string,
  riskLevel?: string
): Promise<ForensicSystemsResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });
  if (source) params.append("source", source);
  if (riskLevel) params.append("risk_level", riskLevel);

  const response = await fetch(`${FORENSIC_API_BASE}/forensic/systems?${params}`);
  if (!response.ok) throw new Error("Failed to fetch forensic systems");
  return response.json();
}

export async function getForensicSystem(urn: string): Promise<ForensicSystem> {
  const response = await fetch(`${FORENSIC_API_BASE}/forensic/systems/${encodeURIComponent(urn)}`);
  if (!response.ok) throw new Error("Failed to fetch forensic system");
  return response.json();
}

export async function deleteForensicSystem(urn: string): Promise<void> {
  const response = await fetch(`${FORENSIC_API_BASE}/forensic/systems/${encodeURIComponent(urn)}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete forensic system");
}

/**
 * Analyze incident with streaming events (SSE)
 * Returns an async generator that yields StreamEvent objects in real-time
 */
export async function* analyzeIncidentStream(request: {
  narrative: string;
  source?: string;
  metadata?: Record<string, unknown>;
  withEvidencePlan?: boolean;
}): AsyncGenerator<StreamEvent, void, unknown> {
  const endpoint = request.withEvidencePlan
    ? `${FORENSIC_API_BASE}/forensic/analyze-stream-with-evidence-plan`
    : `${FORENSIC_API_BASE}/forensic/analyze-stream`;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      narrative: request.narrative,
      source: request.source,
      metadata: request.metadata,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(error.detail || "Analysis failed");
  }

  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");

      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6).trim();
          if (jsonStr) {
            try {
              const event: StreamEvent = JSON.parse(jsonStr);
              yield event;
            } catch (e) {
              console.error("Failed to parse SSE event:", e, jsonStr);
            }
          }
        }
      }
    }

    // Process any remaining data in buffer
    if (buffer.startsWith("data: ")) {
      const jsonStr = buffer.slice(6).trim();
      if (jsonStr) {
        try {
          const event: StreamEvent = JSON.parse(jsonStr);
          yield event;
        } catch (e) {
          console.error("Failed to parse final SSE event:", e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
