import { useEffect, useState } from "react";
import { fetchSystems, createSystem, fetchVocabulary } from "../lib/api";

type System = {
  _id?: string;
  "@id": string;
  hasName: string;
  hasPurpose: string[];
  hasRiskLevel: string;
  hasDeploymentContext: string[];
  hasTrainingDataOrigin: string;
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
    hasTrainingDataOrigin: "",
    hasVersion: "1.0.0",
  });

  useEffect(() => {
    fetchSystems()
      .then((data) => {
        console.log("Fetched systems:", data);
        setSystems(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));

    fetchVocabulary("purposes").then(setPurposes).catch(console.error);
    fetchVocabulary("risks").then(setRisks).catch(console.error);
    fetchVocabulary("contexts").then(setContexts).catch(console.error);
    fetchVocabulary("training_origins").then(setOrigins).catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Submitting form:", form);
    try {
      await createSystem(form);
      const updated = await fetchSystems();
      setSystems(updated);
      setForm({ ...form, hasName: "", hasPurpose: [], hasDeploymentContext: [] });
    } catch (error) {
      console.error("Error submitting system:", error);
    }
  };

  const handleMultiChange = (e: React.ChangeEvent<HTMLSelectElement>, field: "hasPurpose" | "hasDeploymentContext") => {
    const selected = Array.from(e.target.selectedOptions, (option) => option.value);
    console.log(`Updated ${field}:`, selected);
    setForm({ ...form, [field]: selected });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Intelligent Systems</h2>

      <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white dark:bg-gray-800 rounded shadow">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">System Name</label>
          <input
            required
            className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            value={form.hasName}
            onChange={(e) => setForm({ ...form, hasName: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Purpose</label>
            <select
              multiple
              value={form.hasPurpose}
              onChange={(e) => handleMultiChange(e, "hasPurpose")}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            >
              {purposes.map(({ id, label }) => (
                <option key={id} value={id}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Risk Level</label>
            <select
              value={form.hasRiskLevel}
              onChange={(e) => setForm({ ...form, hasRiskLevel: e.target.value })}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            >
              <option value="">Select...</option>
              {risks.map(({ id, label }) => (
                <option key={id} value={id}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Deployment Context</label>
            <select
              multiple
              value={form.hasDeploymentContext}
              onChange={(e) => handleMultiChange(e, "hasDeploymentContext")}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            >
              {contexts.map(({ id, label }) => (
                <option key={id} value={id}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Training Data Origin</label>
            <select
              value={form.hasTrainingDataOrigin}
              onChange={(e) => setForm({ ...form, hasTrainingDataOrigin: e.target.value })}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            >
              <option value="">Select...</option>
              {origins.map(({ id, label }) => (
                <option key={id} value={id}>{label}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Version</label>
          <input
            className="mt-1 block w-full rounded border-gray-300 shadow-sm dark:bg-gray-700 dark:text-white"
            value={form.hasVersion}
            onChange={(e) => setForm({ ...form, hasVersion: e.target.value })}
          />
        </div>

        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add System
        </button>
      </form>

      {loading ? (
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      ) : systems.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400">No systems found.</p>
      ) : (
        <ul className="space-y-3">
          {systems.map((system) => (
            <li
              key={system["@id"]}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow space-y-1"
            >
              <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                {system.hasName} — <span className="text-sm">{system.hasVersion}</span>
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                <strong>Purpose:</strong> {Array.isArray(system.hasPurpose) ? system.hasPurpose.map(p => p.replace("ai:", "")).join(", ") : system.hasPurpose}<br />
                <strong>Risk:</strong> {system.hasRiskLevel.replace("ai:", "")}<br />
                <strong>Context:</strong> {Array.isArray(system.hasDeploymentContext) ? system.hasDeploymentContext.map(c => c.replace("ai:", "")).join(", ") : system.hasDeploymentContext}<br />
                <strong>Training:</strong> {system.hasTrainingDataOrigin.replace("ai:", "")}
              </p>
              <p className="text-xs text-gray-400 mt-2">
                <strong>URN:</strong> {system["ai:hasUrn"]}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
