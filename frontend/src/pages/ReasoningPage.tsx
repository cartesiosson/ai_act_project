import React, { useEffect, useState } from "react";
import { fetchSystems } from "../lib/api";

const REASONER_URL = "http://localhost:8001/reason";

export default function ReasoningPage() {
  const [systems, setSystems] = useState<any[]>([]);
  const [selectedSystemId, setSelectedSystemId] = useState<string>("");
  const [selectedSystem, setSelectedSystem] = useState<any | null>(null);
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetchSystems()
      .then((data) => setSystems(data))
      .catch((e) => setError("Error cargando sistemas: " + e.message));
  }, []);

  useEffect(() => {
    if (selectedSystemId) {
      const sys = systems.find((s) => s["ai:hasUrn"] === selectedSystemId || s.hasName === selectedSystemId || s["@id"] === selectedSystemId);
      setSelectedSystem(sys || null);
    } else {
      setSelectedSystem(null);
    }
  }, [selectedSystemId, systems]);

  // Serializa todos los campos relevantes del sistema a TTL
  function systemToTTL(sys: any): string {
    if (!sys) return "";
    const subject = sys["@id"] ? `<${sys["@id"]}>` : `_:system`;
    let ttl = `@prefix ai: <http://ai-act.eu/ai#> .\n\n${subject} a ai:IntelligentSystem`;
    if (sys.hasName) ttl += ` ;\n  ai:hasName \"${sys.hasName}\"`;
    if (sys.hasPurpose && sys.hasPurpose.length)
      ttl += sys.hasPurpose.map((p: string) => ` ;\n  ai:hasPurpose ${p.startsWith('ai:') ? p : `ai:${p}`}`).join("");
    if (sys.hasDeploymentContext && sys.hasDeploymentContext.length)
      ttl += sys.hasDeploymentContext.map((c: string) => ` ;\n  ai:hasDeploymentContext ${c.startsWith('ai:') ? c : `ai:${c}`}`).join("");
    if (sys.hasTrainingDataOrigin && sys.hasTrainingDataOrigin.length)
      ttl += sys.hasTrainingDataOrigin.map((o: string) => ` ;\n  ai:hasTrainingDataOrigin ${o.startsWith('ai:') ? o : `ai:${o}`}`).join("");
    if (sys.hasInnerSystemCriteria && sys.hasInnerSystemCriteria.length)
      ttl += sys.hasInnerSystemCriteria.map((c: string) => ` ;\n  ai:hasInnerSystemCriteria ${c.startsWith('ai:') ? c : `ai:${c}`}`).join("");
    if (sys.hasVersion) ttl += ` ;\n  ai:hasVersion \"${sys.hasVersion}\"`;
    if (sys["ai:hasUrn"]) ttl += ` ;\n  ai:hasUrn \"${sys["ai:hasUrn"]}\"`;
    ttl += " .\n";
    return ttl;
  }

  // Regla SWRL de ejemplo
  const swrlRule = `ai:IntelligentSystem(?s), ai:Education(?c), ai:hasDeploymentContext(?s, ?c) -> ai:appliesCriterion(?s, ai:EducationCriterion), ai:appliesCompliance(?s, ai:EducationCompliance)`;

  const handleReasoning = async () => {
    setLoading(true);
    setError("");
    setResult("");
    try {
      if (!selectedSystem) throw new Error("Selecciona un sistema válido");
      const ttlData = systemToTTL(selectedSystem);
      const dataFile = new Blob([ttlData], { type: "text/turtle" });
      const rulesFile = new Blob([
        `@prefix ai: <http://ai-act.eu/ai#> .\n\n[rule1: ${swrlRule}]\n`
      ], { type: "text/turtle" });
      const form = new FormData();
      form.append("data", dataFile, "system.ttl");
      form.append("swrl_rules", rulesFile, "rules.ttl");
      const res = await fetch(REASONER_URL, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("Reasoner error");
      const ttl = await res.text();
      setResult(ttl);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: "100vw", minHeight: "100vh", background: "#222", color: "white" }}>
      <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
        <h2 className="text-2xl font-bold mb-6">Reasoning sobre Sistemas</h2>
        <label className="block mb-2">Selecciona un sistema:</label>
        {error && <div className="mb-2 text-red-600 bg-white p-2 rounded">{error}</div>}
        <select
          value={selectedSystemId}
          onChange={e => setSelectedSystemId(e.target.value)}
          style={{
            marginBottom: 24,
            width: "100%",
            padding: "8px 12px",
            fontSize: 16,
            borderRadius: 8,
            backgroundColor: "#333",
            color: "white",
            border: "1px solid #555",
            appearance: "none",
            WebkitAppearance: "none",
            MozAppearance: "none",
          }}
        >
          <option value="">-- Selecciona --</option>
          {systems.map((sys, idx) => (
            <option key={sys["ai:hasUrn"] || sys.hasName || sys["@id"] || idx} value={sys["ai:hasUrn"] || sys.hasName || sys["@id"] || idx}>
              {sys.hasName}
            </option>
          ))}
        </select>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={!selectedSystemId || loading}
          onClick={handleReasoning}
        >
          Reasoning
        </button>
        {loading && <div className="mt-4">Procesando...</div>}
        {result && (
          <div className="m-4 p-4 rounded shadow bg-white text-black max-w-xl">
            <h3 className="font-semibold mb-2">Resultado TTL:</h3>
            <pre className="bg-gray-100 p-2 overflow-x-auto text-xs">{result}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
