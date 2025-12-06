import React, { useEffect, useState } from "react";
import { fetchSystems } from "../lib/api";

const API_BASE = "http://localhost:8000";
const REASONING_URL = `${API_BASE}/reasoning`;

interface ReasoningResult {
  system_id: string;
  system_name: string;
  reasoning_completed: boolean;
  inferred_relationships: {
    hasNormativeCriterion: string[];
    hasTechnicalCriterion: string[];
    hasContextualCriterion: string[];
    hasRequirement: string[];
    hasTechnicalRequirement: string[];
  };
  raw_ttl: string;
  rules_applied: number;
}

export default function ReasoningPage() {
  const [systems, setSystems] = useState<any[]>([]);
  const [selectedSystemId, setSelectedSystemId] = useState<string>("");
  const [selectedSystem, setSelectedSystem] = useState<any | null>(null);
  const [result, setResult] = useState<ReasoningResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [showRawTTL, setShowRawTTL] = useState(false);

  useEffect(() => {
    fetchSystems()
      .then((data) => setSystems(data))
      .catch((e) => setError("Error loading systems: " + e.message));
  }, []);

  useEffect(() => {
    if (selectedSystemId) {
      const sys = systems.find((s: any) =>
        s._id === selectedSystemId ||
        s["ai:hasUrn"] === selectedSystemId ||
        s.hasName === selectedSystemId ||
        s["@id"] === selectedSystemId
      );
      setSelectedSystem(sys || null);
    } else {
      setSelectedSystem(null);
    }
  }, [selectedSystemId, systems]);

  const handleReasoning = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      if (!selectedSystem) {
        throw new Error("Please select a valid system");
      }

      // Usar el ID correcto del sistema
      const systemId = selectedSystem._id || selectedSystem["@id"] || selectedSystemId;

      const response = await fetch(`${REASONING_URL}/system/${systemId}`, {
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
      hasTechnicalRequirement: "Technical Requirements"
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

      {/* Selector de sistema */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <label className="block mb-3 text-lg font-medium">Select a system for analysis:</label>

        {error && (
          <div className="mb-4 text-red-700 dark:text-red-400 bg-red-100 dark:bg-red-900/20 p-3 rounded border border-red-300 dark:border-red-500">
            {error}
          </div>
        )}

        <select
          value={selectedSystemId}
          onChange={(e: any) => setSelectedSystemId(e.target.value)}
          className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">-- Select a system --</option>
          {systems.map((sys: any, idx: number) => (
            <option key={sys._id || sys["ai:hasUrn"] || sys.hasName || idx} value={sys._id || sys["ai:hasUrn"] || sys.hasName}>
              {sys.hasName} {sys["ai:hasUrn"] ? `(${sys["ai:hasUrn"]})` : ""}
            </option>
          ))}
        </select>

        {selectedSystem && (
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
            <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">Selected system:</h4>
            <p className="text-gray-700 dark:text-gray-300"><strong>Name:</strong> {selectedSystem.hasName}</p>
            {selectedSystem.hasPurpose?.length > 0 && (
              <p className="text-gray-700 dark:text-gray-300"><strong>Purposes:</strong> {selectedSystem.hasPurpose.join(", ")}</p>
            )}
            {selectedSystem.hasDeploymentContext?.length > 0 && (
              <p className="text-gray-700 dark:text-gray-300"><strong>Contexts:</strong> {selectedSystem.hasDeploymentContext.join(", ")}</p>
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

      {/* Resultados del razonamiento */}
      {result && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-xl font-bold mb-4 text-green-700 dark:text-green-400">Reasoning Complete</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
              <p className="text-gray-700 dark:text-gray-300"><strong>System:</strong> {result.system_name}</p>
              <p className="text-gray-700 dark:text-gray-300"><strong>Inferences applied:</strong> {result.rules_applied}</p>
              <p className="text-gray-700 dark:text-gray-300">
                <strong>Status:</strong> {result.reasoning_completed ? " Successful" : " Partial"}
              </p>
            </div>
          </div>

          {/* Relaciones inferidas */}
          <div className="mb-6">
            <h4 className="text-lg font-medium mb-3 text-amber-700 dark:text-amber-400">Inferred Relationships:</h4>
            <div className="space-y-3">
              {Object.entries(result.inferred_relationships).map(([relType, values]) => (
                values.length > 0 && (
                  <div key={relType} className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                    <h5 className="font-medium text-blue-700 dark:text-blue-300 mb-2">{formatRelationshipName(relType)}:</h5>
                    <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 space-y-1">
                      {values.map((value, idx) => (
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

          {/* TTL Raw */}
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
