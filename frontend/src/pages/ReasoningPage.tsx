import { useEffect, useState } from "react";
import { fetchSystems } from "../lib/api";
import { getForensicSystems } from "../lib/forensicApi";
import type { ForensicSystem } from "../lib/forensicApi";

const API_BASE = "http://localhost:8000";
const REASONING_URL = `${API_BASE}/reasoning`;

interface ReasoningResult {
  system_id: string;
  system_name: string;
  system_type?: string;
  organization?: string;
  original_risk_level?: string;
  reasoning_completed: boolean;
  inferred_relationships: {
    hasNormativeCriterion: string[];
    hasTechnicalCriterion: string[];
    hasContextualCriterion: string[];
    hasRequirement: string[];
    hasTechnicalRequirement: string[];
    hasCriteria?: string[];
    hasComplianceRequirement?: string[];
    hasRiskLevel?: string[];
    hasGPAIClassification?: string[];
  };
  raw_ttl: string;
  rules_applied: number;
}

// Union type for both system types
type SystemItem = {
  type: "regular";
  id: string;
  name: string;
  data: any;
} | {
  type: "forensic";
  id: string;
  name: string;
  data: ForensicSystem;
};

export default function ReasoningPage() {
  const [regularSystems, setRegularSystems] = useState<any[]>([]);
  const [forensicSystems, setForensicSystems] = useState<ForensicSystem[]>([]);
  const [selectedSystemId, setSelectedSystemId] = useState<string>("");
  const [selectedSystemType, setSelectedSystemType] = useState<"regular" | "forensic" | "">("");
  const [selectedSystem, setSelectedSystem] = useState<SystemItem | null>(null);
  const [result, setResult] = useState<ReasoningResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingSystems, setLoadingSystems] = useState(true);
  const [error, setError] = useState<string>("");
  const [showRawTTL, setShowRawTTL] = useState(false);

  // Load both regular and forensic systems
  useEffect(() => {
    const loadAllSystems = async () => {
      setLoadingSystems(true);
      try {
        const [regular, forensicResponse] = await Promise.all([
          fetchSystems().catch(() => []),
          getForensicSystems(100, 0).catch(() => ({ items: [], total: 0 }))
        ]);
        setRegularSystems(regular);
        setForensicSystems(forensicResponse.items || []);
      } catch (e: any) {
        setError("Error loading systems: " + e.message);
      } finally {
        setLoadingSystems(false);
      }
    };
    loadAllSystems();
  }, []);

  // Update selected system when selection changes
  useEffect(() => {
    if (selectedSystemId && selectedSystemType) {
      if (selectedSystemType === "regular") {
        const sys = regularSystems.find((s: any) =>
          s._id === selectedSystemId ||
          s["ai:hasUrn"] === selectedSystemId ||
          s["@id"] === selectedSystemId
        );
        if (sys) {
          setSelectedSystem({
            type: "regular",
            id: sys._id || sys["ai:hasUrn"] || sys["@id"],
            name: sys.hasName,
            data: sys
          });
        }
      } else if (selectedSystemType === "forensic") {
        const sys = forensicSystems.find((s) => s.urn === selectedSystemId);
        if (sys) {
          setSelectedSystem({
            type: "forensic",
            id: sys.urn,
            name: sys.hasName,
            data: sys
          });
        }
      }
    } else {
      setSelectedSystem(null);
    }
  }, [selectedSystemId, selectedSystemType, regularSystems, forensicSystems]);

  const handleSelectionChange = (value: string) => {
    if (!value) {
      setSelectedSystemId("");
      setSelectedSystemType("");
      return;
    }

    // Parse the combined value (type:id)
    const [type, ...idParts] = value.split(":");
    const id = idParts.join(":"); // Rejoin in case ID contains colons

    if (type === "regular" || type === "forensic") {
      setSelectedSystemType(type);
      setSelectedSystemId(id);
    }
  };

  const handleReasoning = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      if (!selectedSystem) {
        throw new Error("Please select a valid system");
      }

      let endpoint: string;
      if (selectedSystem.type === "forensic") {
        // Use forensic reasoning endpoint
        endpoint = `${REASONING_URL}/forensic/${encodeURIComponent(selectedSystem.id)}`;
      } else {
        // Use regular reasoning endpoint
        endpoint = `${REASONING_URL}/system/${encodeURIComponent(selectedSystem.id)}`;
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Error ${response.status}: ${errorData}`);
      }

      const reasoningResult: ReasoningResult = await response.json();
      setResult(reasoningResult);

    } catch (e: any) {
      setError(e.message || "Error during reasoning");
    } finally {
      setLoading(false);
    }
  };

  const formatRelationshipName = (name: string): string => {
    const translations: Record<string, string> = {
      hasNormativeCriterion: "Normative Criteria",
      hasTechnicalCriterion: "Technical Criteria",
      hasContextualCriterion: "Contextual Criteria",
      hasRequirement: "General Requirements",
      hasTechnicalRequirement: "Technical Requirements",
      hasCriteria: "Criteria",
      hasComplianceRequirement: "Compliance Requirements",
      hasRiskLevel: "Risk Level",
      hasGPAIClassification: "GPAI Classification"
    };
    return translations[name] || name;
  };

  const formatUri = (uri: string): string => {
    const parts = uri.split("#");
    return parts.length > 1 ? parts[1] : uri.split("/").pop() || uri;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 text-gray-900 dark:text-white">
      <h2 className="text-3xl font-bold mb-8 text-center">AI Act Semantic Reasoning</h2>

      {/* System selector */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <label className="block mb-3 text-lg font-medium">Select a system for analysis:</label>

        {error && (
          <div className="mb-4 text-red-700 dark:text-red-400 bg-red-100 dark:bg-red-900/20 p-3 rounded border border-red-300 dark:border-red-500">
            {error}
          </div>
        )}

        {loadingSystems ? (
          <p className="text-gray-500 dark:text-gray-400">Loading systems...</p>
        ) : (
          <select
            value={selectedSystemType && selectedSystemId ? `${selectedSystemType}:${selectedSystemId}` : ""}
            onChange={(e) => handleSelectionChange(e.target.value)}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a system --</option>

            {/* Regular systems group */}
            {regularSystems.length > 0 && (
              <optgroup label="Manual Systems (Systems DB)">
                {regularSystems.map((sys: any, idx: number) => (
                  <option
                    key={`regular-${sys._id || sys["ai:hasUrn"] || idx}`}
                    value={`regular:${sys._id || sys["ai:hasUrn"] || sys["@id"]}`}
                  >
                    {sys.hasName} {sys["ai:hasUrn"] ? `(${sys["ai:hasUrn"].slice(0, 20)}...)` : ""}
                  </option>
                ))}
              </optgroup>
            )}

            {/* Forensic systems group */}
            {forensicSystems.length > 0 && (
              <optgroup label="Forensic Analyzed Systems">
                {forensicSystems.map((sys) => (
                  <option
                    key={`forensic-${sys.urn}`}
                    value={`forensic:${sys.urn}`}
                  >
                    {sys.hasName} ({sys.aiaaic_id || sys.urn.slice(-8)})
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        )}

        {/* Selected system preview */}
        {selectedSystem && (
          <div className={`mt-4 p-4 rounded-lg border ${
            selectedSystem.type === "forensic"
              ? "bg-purple-50 dark:bg-purple-900/30 border-purple-200 dark:border-purple-700"
              : "bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700"
          }`}>
            <div className="flex items-center mb-2">
              <span className="mr-2">{selectedSystem.type === "forensic" ? "🔬" : "📋"}</span>
              <h4 className={`font-medium ${
                selectedSystem.type === "forensic"
                  ? "text-purple-700 dark:text-purple-300"
                  : "text-blue-700 dark:text-blue-300"
              }`}>
                {selectedSystem.type === "forensic" ? "Forensic Analyzed System" : "Manual System"}
              </h4>
            </div>

            <p className="text-gray-700 dark:text-gray-300">
              <strong>Name:</strong> {selectedSystem.name}
            </p>

            {selectedSystem.type === "forensic" && (
              <>
                <p className="text-gray-700 dark:text-gray-300">
                  <strong>Organization:</strong> {selectedSystem.data.hasOrganization}
                </p>
                <p className="text-gray-700 dark:text-gray-300">
                  <strong>Risk Level:</strong>{" "}
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    selectedSystem.data.hasRiskLevel?.includes("High")
                      ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                      : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                  }`}>
                    {selectedSystem.data.hasRiskLevel?.replace("ai:", "")}
                  </span>
                </p>
                {selectedSystem.data.aiaaic_id && (
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>AIAAIC ID:</strong> {selectedSystem.data.aiaaic_id}
                  </p>
                )}
              </>
            )}

            {selectedSystem.type === "regular" && (
              <>
                {selectedSystem.data.hasPurpose?.length > 0 && (
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Purposes:</strong> {selectedSystem.data.hasPurpose.map((p: string) => p.replace("ai:", "")).join(", ")}
                  </p>
                )}
                {selectedSystem.data.hasDeploymentContext?.length > 0 && (
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Contexts:</strong> {selectedSystem.data.hasDeploymentContext.map((c: string) => c.replace("ai:", "")).join(", ")}
                  </p>
                )}
              </>
            )}
          </div>
        )}

        <button
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
          disabled={!selectedSystemId || loading}
          onClick={handleReasoning}
        >
          {loading ? "Processing..." : "Run Reasoning"}
        </button>
      </div>

      {/* Reasoning results */}
      {result && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-xl font-bold mb-4 text-green-700 dark:text-green-400">Reasoning Complete</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
              <p className="text-gray-700 dark:text-gray-300"><strong>System:</strong> {result.system_name}</p>
              {result.system_type === "forensic" && result.organization && (
                <p className="text-gray-700 dark:text-gray-300"><strong>Organization:</strong> {result.organization}</p>
              )}
              <p className="text-gray-700 dark:text-gray-300"><strong>Inferences applied:</strong> {result.rules_applied}</p>
              <p className="text-gray-700 dark:text-gray-300">
                <strong>Status:</strong> {result.reasoning_completed ? " Successful" : " Partial"}
              </p>
              {result.system_type === "forensic" && (
                <p className="text-xs text-purple-600 dark:text-purple-400 mt-2">
                  Source: Forensic Analysis
                </p>
              )}
            </div>
          </div>

          {/* Inferred relationships */}
          <div className="mb-6">
            <h4 className="text-lg font-medium mb-3 text-amber-700 dark:text-amber-400">Inferred Relationships:</h4>
            <div className="space-y-3">
              {Object.entries(result.inferred_relationships).map(([relType, values]) => (
                values && values.length > 0 && (
                  <div key={relType} className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                    <h5 className="font-medium text-blue-700 dark:text-blue-300 mb-2">{formatRelationshipName(relType)}:</h5>
                    <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 space-y-1">
                      {values.map((value: string, idx: number) => (
                        <li key={idx} className="text-sm">
                          <code className="bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded text-xs">{formatUri(value)}</code>
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              ))}
            </div>
          </div>

          {/* Raw TTL */}
          <div className="mb-4">
            <button
              onClick={() => setShowRawTTL(!showRawTTL)}
              className="bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-white px-4 py-2 rounded-lg transition-colors"
            >
              {showRawTTL ? "Hide Raw TTL" : "Show Raw TTL"}
            </button>
          </div>

          {showRawTTL && (
            <div className="bg-gray-900 dark:bg-black p-4 rounded-lg overflow-x-auto border border-gray-700">
              <h4 className="text-sm font-medium mb-2 text-gray-400">Complete RDF Graph (TTL):</h4>
              <pre className="text-xs text-green-400 whitespace-pre-wrap font-mono">
                {result.raw_ttl}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
