import { useEffect, useState } from "react";
import { fetchSystems, fetchVocabulary } from "../lib/api";
import SystemCard from "./SystemCard";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type System = {
  _id?: string;
  "@id": string;
  hasName: string;
  hasPurpose: string[];
  hasDeploymentContext: string[];
  hasTrainingDataOrigin: string[];
  hasSystemCapabilityCriteria: string[];
  hasAlgorithmType: string[];
  hasVersion: string;
  "ai:hasUrn": string;
};

export default function SystemsPage() {
  const [systems, setSystems] = useState<System[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 10;
  
  const [loadedSystem, setLoadedSystem] = useState<System | null>(null);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [systemToLoad, setSystemToLoad] = useState<System | null>(null);

  const [filters, setFilters] = useState({
    name: "",
    risk: "",
    purpose: "",
    context: "",
    origin: "",
  });

  const [purposes, setPurposes] = useState<{ id: string; label: string }[]>([]);
  const [risks, setRisks] = useState<{ id: string; label: string }[]>([]);
  const [contexts, setContexts] = useState<{ id: string; label: string }[]>([]);
  const [origins, setOrigins] = useState<{ id: string; label: string }[]>([]);
  const [systemCapabilityCriteria, setSystemCapabilityCriteria] = useState<{ id: string; label: string }[]>([]);
  const [algorithmTypes, setAlgorithmTypes] = useState<{ id: string; label: string }[]>([]);

  const [form, setForm] = useState({
    hasName: "",
    hasPurpose: [] as string[],
    hasDeploymentContext: [] as string[],
    hasTrainingDataOrigin: [] as string[],
    hasSystemCapabilityCriteria: [] as string[],
    hasAlgorithmType: [] as string[],
    hasVersion: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const isModifying = loadedSystem !== null;
      const url = isModifying 
        ? `${API_BASE}/systems/${encodeURIComponent(loadedSystem["ai:hasUrn"])}`
        : `${API_BASE}/systems`;
      const method = isModifying ? "PUT" : "POST";
      
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "@context": "http://ontologias/json-ld-context.json",
          "@type": "ai:IntelligentSystem",
          ...form,
        }),
      });
      if (!res.ok) throw new Error(`${isModifying ? 'Modify' : 'Create'} failed`);
      
      // Clear form and loaded system
      setForm({
        hasName: "",
        hasPurpose: [],
        hasDeploymentContext: [],
        hasTrainingDataOrigin: [],
        hasSystemCapabilityCriteria: [],
        hasAlgorithmType: [],
        hasVersion: "",
      });
      setLoadedSystem(null);
      await loadSystems(0);
      setOffset(0);
    } catch (err) {
      console.error(`Error ${loadedSystem ? 'modifying' : 'creating'} system:`, err);
      alert(`Failed to ${loadedSystem ? 'modify' : 'create'} system`);
    }
  };

  const handleLoadSystem = (system: System) => {
    setSystemToLoad(system);
    setShowLoadModal(true);
  };

  const confirmLoadSystem = () => {
    if (systemToLoad) {
      setForm({
        hasName: systemToLoad.hasName,
        hasPurpose: systemToLoad.hasPurpose || [],
        hasDeploymentContext: systemToLoad.hasDeploymentContext || [],
        hasTrainingDataOrigin: systemToLoad.hasTrainingDataOrigin || [],
        hasSystemCapabilityCriteria: systemToLoad.hasSystemCapabilityCriteria || [],
        hasAlgorithmType: systemToLoad.hasAlgorithmType || [],
        hasVersion: systemToLoad.hasVersion,
      });
      setLoadedSystem(systemToLoad);
    }
    setShowLoadModal(false);
    setSystemToLoad(null);
  };

  const cancelLoadSystem = () => {
    setShowLoadModal(false);
    setSystemToLoad(null);
  };

  const handleDelete = async (urn: string) => {
    const confirmed = confirm(`Are you sure you want to delete system with URN: ${urn}?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`${API_BASE}/systems/${encodeURIComponent(urn)}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete failed");

      await loadSystems();
    } catch (err) {
      console.error("Error deleting system:", err);
      alert("Failed to delete system");
    }
  };

  const loadSystems = async (customOffset?: number) => {
    setLoading(true);
    const query = new URLSearchParams();
    if (filters.name) query.append("name", filters.name);
    if (filters.risk) query.append("risk", filters.risk);
    if (filters.purpose) query.append("purpose", filters.purpose);
    if (filters.context) query.append("context", filters.context);
    if (filters.origin) query.append("origin", filters.origin);
    query.append("offset", (customOffset !== undefined ? customOffset : offset).toString());
    query.append("limit", limit.toString());

    const res = await fetch(`${API_BASE}/systems?${query.toString()}`);
    const json = await res.json();
    setSystems(json.items);
    setTotal(json.total);
    setLoading(false);
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [purposesData, risksData, contextsData, originsData, systemCapabilityCriteriaData, algorithmTypesData] = await Promise.all([
        fetchVocabulary("purposes"),
        fetchVocabulary("risks"),
        fetchVocabulary("contexts"),
        fetchVocabulary("training_origins"),
        fetchVocabulary("system_capability_criteria"),
        fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/vocab/algorithmtypes?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:NeuralNetwork", "label": "Neural Network"},
          {"id": "ai:TransformerModel", "label": "Transformer Model"}, 
          {"id": "ai:FoundationModel", "label": "Foundation Model"},
          {"id": "ai:GenerativeModel", "label": "Generative Model"}
        ]),
      ]);
      setPurposes(purposesData);
      setRisks(risksData);
      setContexts(contextsData);
      setOrigins(originsData);
      setSystemCapabilityCriteria(systemCapabilityCriteriaData);
      setAlgorithmTypes(algorithmTypesData);
      
    };
    load();
  }, []); // Only on mount, not on offset/filters

  useEffect(() => {
    // Only load on mount and when filters/offset change (not after create)
    loadSystems();
    // eslint-disable-next-line
  }, [offset, filters]);

  return (
    <div className="max-w-7xl mx-auto p-6 text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-8">Intelligent Systems</h1>

      {/* Formulario de creación */}
      <form onSubmit={handleSubmit} className="space-y-6 mb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            <label className="block font-semibold mb-1">Version</label>
            <input
              className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
              placeholder="e.g. 1.0.0"
              value={form.hasVersion}
              onChange={(e) => setForm({ ...form, hasVersion: e.target.value })}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block font-semibold mb-1">Purpose(s)</label>
            <select
              multiple
              className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
              value={form.hasPurpose}
              onChange={e =>
                setForm({ ...form, hasPurpose: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {purposes.map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-1">Deployment Context(s)</label>
            <select
              multiple
              className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
              value={form.hasDeploymentContext}
              onChange={e =>
                setForm({ ...form, hasDeploymentContext: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
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
              onChange={e =>
                setForm({ ...form, hasTrainingDataOrigin: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {origins.map((o) => (
                <option key={o.id} value={o.id}>{o.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold mt-2">System Capability Criteria</label>
            <select
              multiple
              className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
              value={form.hasSystemCapabilityCriteria}
              onChange={e =>
                setForm({ ...form, hasSystemCapabilityCriteria: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {systemCapabilityCriteria.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold mt-2">Algorithm Types</label>
            <select
              multiple
              className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
              value={form.hasAlgorithmType}
              onChange={e =>
                setForm({ ...form, hasAlgorithmType: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {algorithmTypes.map((a) => (
                <option key={a.id} value={a.id}>{a.label}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loadedSystem ? 'Modify System' : 'Create System'}
        </button>
        {loadedSystem && (
          <button
            type="button"
            onClick={() => {
              setForm({
                hasName: "",
                hasPurpose: [],
                hasDeploymentContext: [],
                hasTrainingDataOrigin: [],
                hasSystemCapabilityCriteria: [],
                hasAlgorithmType: [],
                hasVersion: "",
              });
              setLoadedSystem(null);
            }}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 ml-2"
          >
            Clear Form
          </button>
        )}
      </form>

      {/* Filtros */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-5 gap-4">
        <input
          className="border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
          placeholder="Filter by name"
          value={filters.name}
          onChange={(e) => setFilters({ ...filters, name: e.target.value })}
        />
        <select
          className="border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
          value={filters.risk}
          onChange={(e) => setFilters({ ...filters, risk: e.target.value })}
        >
          <option value="">All Risks</option>
          {risks.map((r) => (
            <option key={r.id} value={r.id}>{r.label}</option>
          ))}
        </select>
        <select
          className="border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
          value={filters.purpose}
          onChange={(e) => setFilters({ ...filters, purpose: e.target.value })}
        >
          <option value="">All Purposes</option>
          {purposes.map((p) => (
            <option key={p.id} value={p.id}>{p.label}</option>
          ))}
        </select>
        <select
          className="border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
          value={filters.context}
          onChange={(e) => setFilters({ ...filters, context: e.target.value })}
        >
          <option value="">All Contexts</option>
          {contexts.map((c) => (
            <option key={c.id} value={c.id}>{c.label}</option>
          ))}
        </select>
        <select
          className="border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white"
          value={filters.origin}
          onChange={(e) => setFilters({ ...filters, origin: e.target.value })}
        >
          <option value="">All Origins</option>
          {origins.map((o) => (
            <option key={o.id} value={o.id}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Tabla de resultados */}
      {loading ? (
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      ) : (
        <div>
        <table className="min-w-full border dark:border-gray-700 mb-4 table-fixed">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="p-2 text-left w-[35%]">Name</th>
              <th className="p-2 text-left w-[35%]">Purpose</th>
              <th className="p-2 text-left w-[15%]">Version</th>
              <th className="p-2 text-left w-[15%]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <tr key={s["@id"]} className="border-t dark:border-gray-700">
                <td className="p-2 truncate" title={s.hasName}>{s.hasName}</td>
                <td className="p-2 truncate" title={(s.hasPurpose ?? []).join(", ")}>{(s.hasPurpose ?? []).join(", ")}</td>
                <td className="p-2 truncate" title={s.hasVersion}>{s.hasVersion}</td>
                <td className="p-2 space-x-2">
                  <button
                    onClick={() => handleLoadSystem(s)}
                    className="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                  >
                    Load
                  </button>
                  <button
                    onClick={() => handleDelete(s["ai:hasUrn"])}
                    className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
          {/* Paginación */}
          <div className="flex justify-between items-center">
            <button
              disabled={offset === 0}
              onClick={() => setOffset((o) => Math.max(o - limit, 0))}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span>
              Showing {offset + 1} to {Math.min(offset + limit, total)} of {total}
            </span>
            <button
              disabled={offset + limit >= total}
              onClick={() => setOffset((o) => o + limit)}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Modal de confirmación para cargar sistema */}
      {showLoadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
              Load System
            </h3>
            <p className="mb-6 text-gray-700 dark:text-gray-300">
              Loading this system will discard all current form data. Do you want to proceed?
            </p>
            <div className="flex space-x-4 justify-end">
              <button
                onClick={cancelLoadSystem}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={confirmLoadSystem}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Proceed
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
