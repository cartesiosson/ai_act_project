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
      .catch((e) => setError("Error cargando sistemas: " + e.message));
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
        throw new Error("Selecciona un sistema válido");
      }

      // Usar el ID correcto del sistema
      const systemId = selectedSystem._id || selectedSystem["@id"] || selectedSystemId;
      
      const response = await fetch(`${REASONING_URL}/system/${systemId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Error ${response.status}: ${errorData}`);
      }

      const reasoningResult: ReasoningResult = await response.json();
      setResult(reasoningResult);
      
    } catch (e: any) {
      setError(e.message || "Error durante el razonamiento");
    } finally {
      setLoading(false);
    }
  };

  const formatRelationshipName = (name: string): string => {
    const translations: Record<string, string> = {
      hasNormativeCriterion: "Criterios Normativos",
      hasTechnicalCriterion: "Criterios Técnicos", 
      hasContextualCriterion: "Criterios Contextuales",
      hasRequirement: "Requisitos Generales",
      hasTechnicalRequirement: "Requisitos Técnicos"
    };
    return translations[name] || name;
  };

  const formatUri = (uri: string): string => {
    const parts = uri.split("#");
    return parts.length > 1 ? parts[1] : uri.split("/").pop() || uri;
  };

  return (
    <div style={{ width: "100vw", minHeight: "100vh", background: "#222", color: "white" }}>
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
        <h2 className="text-3xl font-bold mb-8 text-center">🧠 Razonamiento Semántico AI Act</h2>
        
        {/* Selector de sistema */}
        <div className="mb-6 bg-gray-800 p-6 rounded-lg">
          <label className="block mb-3 text-lg font-medium">Selecciona un sistema para análisis:</label>
          {error && (
            <div className="mb-4 text-red-400 bg-red-900/20 p-3 rounded border border-red-500">
              ❌ {error}
            </div>
          )}
          
          <select
            value={selectedSystemId}
            onChange={(e: any) => setSelectedSystemId(e.target.value)}
            className="w-full p-3 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
          >
            <option value="">-- Selecciona un sistema --</option>
            {systems.map((sys: any, idx: number) => (
              <option key={sys._id || sys["ai:hasUrn"] || sys.hasName || idx} value={sys._id || sys["ai:hasUrn"] || sys.hasName}>
                {sys.hasName} {sys["ai:hasUrn"] ? `(${sys["ai:hasUrn"]})` : ""}
              </option>
            ))}
          </select>
          
          {selectedSystem && (
            <div className="mt-4 p-4 bg-gray-700 rounded">
              <h4 className="font-medium text-blue-300 mb-2">Sistema seleccionado:</h4>
              <p><strong>Nombre:</strong> {selectedSystem.hasName}</p>
              {selectedSystem.hasPurpose?.length > 0 && (
                <p><strong>Propósitos:</strong> {selectedSystem.hasPurpose.join(", ")}</p>
              )}
              {selectedSystem.hasDeploymentContext?.length > 0 && (
                <p><strong>Contextos:</strong> {selectedSystem.hasDeploymentContext.join(", ")}</p>
              )}
            </div>
          )}
          
          <button
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            disabled={!selectedSystemId || loading}
            onClick={handleReasoning}
          >
            {loading ? "🔄 Procesando..." : "🧠 Ejecutar Razonamiento"}
          </button>
        </div>

        {/* Resultados del razonamiento */}
        {result && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-4 text-green-300">✅ Razonamiento Completado</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-700 p-4 rounded">
                <p><strong>Sistema:</strong> {result.system_name}</p>
                <p><strong>Reglas aplicadas:</strong> {
                  Object.values(result.inferred_relationships).reduce((total, arr) => total + arr.length, 0)
                }</p>
                <p><strong>Estado:</strong> {result.reasoning_completed ? "✅ Exitoso" : "⚠️ Parcial"}</p>
              </div>
            </div>

            {/* Relaciones inferidas */}
            <div className="mb-6">
              <h4 className="text-lg font-medium mb-3 text-yellow-300">🔗 Relaciones Inferidas:</h4>
              <div className="space-y-3">
                {Object.entries(result.inferred_relationships).map(([relType, values]) => (
                  values.length > 0 && (
                    <div key={relType} className="bg-gray-700 p-3 rounded">
                      <h5 className="font-medium text-blue-300 mb-2">{formatRelationshipName(relType)}:</h5>
                      <ul className="list-disc list-inside text-gray-300 space-y-1">
                        {values.map((value, idx) => (
                          <li key={idx} className="text-sm">
                            <code className="bg-gray-600 px-2 py-1 rounded text-xs">{formatUri(value)}</code>
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
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded transition-colors"
              >
                {showRawTTL ? "🙈 Ocultar TTL Raw" : "👀 Ver TTL Raw"}
              </button>
            </div>

            {showRawTTL && (
              <div className="bg-black p-4 rounded overflow-x-auto">
                <h4 className="text-sm font-medium mb-2 text-gray-400">Grafo RDF Completo (TTL):</h4>
                <pre className="text-xs text-green-400 whitespace-pre-wrap font-mono">
                  {result.raw_ttl}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
