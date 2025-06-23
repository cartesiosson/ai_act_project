import { useEffect, useState } from "react";
import { fetchSystems, createSystem, fetchVocabulary } from "../lib/api";
import SystemCard from "./SystemCard";

type System = {
  _id?: string;
  "@id": string;
  hasName: string;
  hasPurpose: string[];
  hasRiskLevel: string;
  hasDeploymentContext: string[];
  hasTrainingDataOrigin: string[];
  hasVersion: string;
  "ai:hasUrn": string;
};

export default function SystemsPage() {
  const [systems, setSystems] = useState<System[]>([]);
  const [loading, setLoading] = useState(true);

  const [purposes, setPurposes] = useState<{ id: string; label: string }[]>([]);
  const [risks, setRisks] = useState<{ id: string; label: string }[]>([]);
  const [contexts, setContexts] = useState<{ id: string; label: string }[]>([]);
  const [origins, setOrigins] = useState<{ id: string; label: string }[]>([]);

  const [form, setForm] = useState({
    hasName: "",
    hasPurpose: [] as string[],
    hasRiskLevel: "",
    hasDeploymentContext: [] as string[],
    hasTrainingDataOrigin: [] as string[],
    hasVersion: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createSystem(form);
    const data = await fetchSystems();
    setSystems(data);
  };

  const handleDelete = async (urn: string) => {
    const confirmed = confirm(`Are you sure you want to delete system with URN: ${urn}?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:8000/systems/${encodeURIComponent(urn)}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete failed");

      setSystems((prev) => prev.filter((s) => s["ai:hasUrn"] !== urn));
    } catch (err) {
      console.error("Error deleting system:", err);
      alert("Failed to delete system");
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [systemsData, purposesData, risksData, contextsData, originsData] = await Promise.all([
        fetchSystems(),
        fetchVocabulary("purposes"),
        fetchVocabulary("risks"),
        fetchVocabulary("contexts"),
        fetchVocabulary("training_origins"),
      ]);
      setSystems(systemsData);
      setPurposes(purposesData);
      setRisks(risksData);
      setContexts(contextsData);
      setOrigins(originsData);
      setLoading(false);
    };
    load();
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-8">Intelligent Systems</h1>

      <form onSubmit={handleSubmit} className="space-y-6 mb-12">
        <div>
          <label className="block font-semibold mb-1">System Name</label>
          <input
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            placeholder="System Name"
            value={form.hasName}
            onChange={(e) => setForm({ ...form, hasName: e.target.value })}
          />
        </div>

        <div>
          <label className="block font-semibold mb-1">Purpose(s)</label>
          <select
            multiple
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            value={form.hasPurpose}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, opt => opt.value);
              setForm({ ...form, hasPurpose: selected });
            }}
          >
            {purposes.map((p) => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-1">Risk Level</label>
          <select
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            value={form.hasRiskLevel}
            onChange={(e) => setForm({ ...form, hasRiskLevel: e.target.value })}
          >
            <option value="">Select risk level</option>
            {risks.map((r) => (
              <option key={r.id} value={r.id}>{r.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-1">Deployment Context(s)</label>
          <select
            multiple
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            value={form.hasDeploymentContext}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, opt => opt.value);
              setForm({ ...form, hasDeploymentContext: selected });
            }}
          >
            {contexts.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-1">Training Data Origin(s)</label>
          <select
            multiple
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            value={form.hasTrainingDataOrigin}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, opt => opt.value);
              setForm({ ...form, hasTrainingDataOrigin: selected });
            }}
          >
            {origins.map((o) => (
              <option key={o.id} value={o.id}>{o.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-1">Version</label>
          <input
            className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
            placeholder="e.g. 1.0.0"
            value={form.hasVersion}
            onChange={(e) => setForm({ ...form, hasVersion: e.target.value })}
          />
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create System
        </button>
      </form>

      <h2 className="text-xl font-bold mb-4">Registered Systems</h2>

      {loading ? (
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      ) : (
        <div className="space-y-2">
          {systems.map((s) => (
            <div key={s["@id"]} className="border p-4 rounded shadow bg-white dark:bg-gray-800">
              <SystemCard
                name={s.hasName ?? "Unnamed System"}
                riskLevel={s.hasRiskLevel ?? "N/A"}
                purpose={
                  (Array.isArray(s.hasPurpose) ? s.hasPurpose : [s.hasPurpose])
                    .filter(Boolean)
                    .join(", ") || "N/A"
                }
                deploymentContext={
                  (Array.isArray(s.hasDeploymentContext) ? s.hasDeploymentContext : [s.hasDeploymentContext])
                    .filter(Boolean)
                    .join(", ") || "N/A"
                }
                trainingDataOrigin={
                  (Array.isArray(s.hasTrainingDataOrigin) ? s.hasTrainingDataOrigin : [s.hasTrainingDataOrigin])
                    .filter(Boolean)
                    .join(", ") || "N/A"
                }
                version={s.hasVersion ?? "N/A"}
                urn={s["ai:hasUrn"] ?? "N/A"}
              />
              <button
                onClick={() => handleDelete(s["ai:hasUrn"])}
                className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
