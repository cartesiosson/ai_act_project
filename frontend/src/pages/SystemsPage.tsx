import { useEffect, useState } from "react";
import { fetchSystems, createSystem, fetchVocabulary } from "../lib/api";
import SystemCard from "./SystemCard";

export type System = {
  _id?: string;
  "@id": string;
  hasName: string;
  hasPurpose: string[];
  hasDeploymentContext: string[];
  hasTrainingDataOrigin: string[];
  hasInnerSystemCriteria: string[];
  hasVersion: string;
  "ai:hasUrn": string;
};

export default function SystemsPage() {
  const [systems, setSystems] = useState<System[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 10;

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

  const [form, setForm] = useState({
    hasName: "",
    hasPurpose: [] as string[],
    hasDeploymentContext: [] as string[],
    hasTrainingDataOrigin: [] as string[],
    hasInnerSystemCriteria: [] as string[],
    hasVersion: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createSystem(form);
    await loadSystems();
  };

  const handleDelete = async (urn: string) => {
    const confirmed = confirm(`Are you sure you want to delete system with URN: ${urn}?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:8000/systems/${encodeURIComponent(urn)}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Delete failed");

      await loadSystems();
    } catch (err) {
      console.error("Error deleting system:", err);
      alert("Failed to delete system");
    }
  };

  const loadSystems = async () => {
    setLoading(true);
    const query = new URLSearchParams();
    if (filters.name) query.append("name", filters.name);
    if (filters.risk) query.append("risk", filters.risk);
    if (filters.purpose) query.append("purpose", filters.purpose);
    if (filters.context) query.append("context", filters.context);
    if (filters.origin) query.append("origin", filters.origin);
    query.append("offset", offset.toString());
    query.append("limit", limit.toString());

    const res = await fetch(`http://localhost:8000/systems?${query.toString()}`);
    const json = await res.json();
    setSystems(json.items);
    setTotal(json.total);
    setLoading(false);
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [purposesData, risksData, contextsData, originsData] = await Promise.all([
        fetchVocabulary("purposes"),
        fetchVocabulary("risks"),
        fetchVocabulary("contexts"),
        fetchVocabulary("training_origins"),
      ]);
      setPurposes(purposesData);
      setRisks(risksData);
      setContexts(contextsData);
      setOrigins(originsData);
      await loadSystems();
    };
    load();
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
              onChange={(e) =>
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
              onChange={(e) =>
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
              onChange={(e) =>
                setForm({ ...form, hasTrainingDataOrigin: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {origins.map((o) => (
                <option key={o.id} value={o.id}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Añadir input para Inner System Criteria */}
        <div>
          <label className="block font-semibold mt-2">Inner System Criteria</label>
          <input
            type="text"
            value={form.hasInnerSystemCriteria.join(",")}
            onChange={e => setForm(f => ({ ...f, hasInnerSystemCriteria: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }))}
            placeholder="ai:CustomCriterion1, ai:CustomCriterion2"
            className="border rounded px-2 py-1 w-full"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create System
        </button>
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
              <th className="p-2 text-left w-[25%]">Name</th>
              <th className="p-2 text-left w-[15%]">Purpose</th>
              <th className="p-2 text-left w-[15%]">Context</th>
              <th className="p-2 text-left w-[15%]">Origin</th>
              <th className="p-2 text-left w-[10%]">Version</th>
              <th className="p-2 text-left w-[10%]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <tr key={s["@id"]} className="border-t dark:border-gray-700">
                <td className="p-2 truncate" title={s.hasName}>{s.hasName}</td>
                <td className="p-2 truncate" title={(s.hasPurpose ?? []).join(", ")}>{(s.hasPurpose ?? []).join(", ")}</td>
                <td className="p-2 truncate" title={(s.hasDeploymentContext ?? []).join(", ")}>{(s.hasDeploymentContext ?? []).join(", ")}</td>
                <td className="p-2 truncate" title={(s.hasTrainingDataOrigin ?? []).join(", ")}>{(s.hasTrainingDataOrigin ?? []).join(", ")}</td>
                <td className="p-2 truncate" title={s.hasVersion}>{s.hasVersion}</td>
                <td className="p-2">
                  <button
                    onClick={() => handleDelete(s["ai:hasUrn"])}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
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
    </div>
  );
}
