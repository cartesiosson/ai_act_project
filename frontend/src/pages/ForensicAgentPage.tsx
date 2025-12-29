import { useEffect, useState, useMemo, useRef } from "react";
import Markdown from "react-markdown";
import type { Incident, ForensicAnalysisResult, ForensicSystem, StreamEvent, AgentMode } from "../lib/forensicApi";
import {
  loadIncidents,
  analyzeIncidentStream,
  buildNarrative,
  getUniqueValues,
  checkHealth,
  getForensicSystems,
  deleteForensicSystem,
} from "../lib/forensicApi";

const ITEMS_PER_PAGE = 20;

export default function ForensicAgentPage() {
  // Data state
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  // Filter state
  const [filters, setFilters] = useState({
    sector: "",
    country: "",
    year: "",
    technology: "",
    search: "",
  });

  // Pagination state
  const [page, setPage] = useState(1);

  // Selection state
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Detail modal state
  const [detailIncident, setDetailIncident] = useState<Incident | null>(null);

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, currentId: "" });
  const [results, setResults] = useState<Map<string, ForensicAnalysisResult>>(new Map());
  const [expandedResult, setExpandedResult] = useState<string | null>(null);
  const [withEvidencePlan, setWithEvidencePlan] = useState(true); // Include DPV Evidence Plan

  // Streaming state
  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([]);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [streamProgress, setStreamProgress] = useState(0);
  const [showStreamModal, setShowStreamModal] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const streamContainerRef = useRef<HTMLDivElement>(null);

  // Service health
  const [serviceHealthy, setServiceHealthy] = useState<boolean | null>(null);
  const [llmInfo, setLlmInfo] = useState<{ provider: string; model: string } | null>(null);
  const [reactAgentInfo, setReactAgentInfo] = useState<{ enabled: boolean; model: string } | null>(null);

  // Agent mode selection
  const [agentMode, setAgentMode] = useState<AgentMode>("pipeline");

  // Forensic analyzed systems state
  const [forensicSystems, setForensicSystems] = useState<ForensicSystem[]>([]);
  const [forensicLoading, setForensicLoading] = useState(true);
  const [forensicTotal, setForensicTotal] = useState(0);
  const [forensicOffset, setForensicOffset] = useState(0);
  const [forensicError, setForensicError] = useState<string | null>(null);
  const [selectedForensicSystem, setSelectedForensicSystem] = useState<ForensicSystem | null>(null);
  const forensicLimit = 10;

  // Ref for PDF export
  const reportRef = useRef<HTMLDivElement>(null);

  // Export report to PDF using print dialog
  const handleExportPdf = () => {
    if (!reportRef.current || !selectedForensicSystem) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const content = reportRef.current.innerHTML;
    const systemName = selectedForensicSystem.hasName;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Forensic Report - ${systemName}</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
            color: #333;
          }
          h1 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 10px; }
          h2 { font-size: 20px; color: #444; margin-top: 30px; }
          h3 { font-size: 16px; color: #555; }
          p { margin: 10px 0; }
          ul, ol { margin: 10px 0; padding-left: 25px; }
          li { margin: 5px 0; }
          hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
          strong { color: #222; }
          code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
          pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
          img { max-width: 200px; height: auto; }
          @media print {
            body { padding: 20px; }
            @page { margin: 20mm; }
          }
        </style>
      </head>
      <body>
        ${content}
      </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();

    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);
  };

  // Load incidents on mount
  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [data, healthResponse] = await Promise.all([loadIncidents(), checkHealth()]);
        setIncidents(data);
        setServiceHealthy(healthResponse !== null);
        if (healthResponse?.llm) {
          setLlmInfo(healthResponse.llm);
        }
        if (healthResponse?.react_agent) {
          setReactAgentInfo(healthResponse.react_agent);
        }
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load incidents";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Get unique values for filter dropdowns
  const filterOptions = useMemo(() => ({
    sectors: getUniqueValues(incidents, "sector"),
    countries: getUniqueValues(incidents, "country"),
    years: getUniqueValues(incidents, "occurred").sort((a, b) => b.localeCompare(a)),
    technologies: getUniqueValues(incidents, "technology"),
  }), [incidents]);

  // Filter incidents
  const filteredIncidents = useMemo(() => {
    return incidents.filter((inc) => {
      if (filters.sector && !inc.sector.includes(filters.sector)) return false;
      if (filters.country && !inc.country.includes(filters.country)) return false;
      if (filters.year && inc.occurred !== filters.year) return false;
      if (filters.technology && !inc.technology.includes(filters.technology)) return false;
      if (filters.search) {
        const search = filters.search.toLowerCase();
        if (
          !inc.headline.toLowerCase().includes(search) &&
          !inc.id.toLowerCase().includes(search) &&
          !inc.system_name.toLowerCase().includes(search)
        ) {
          return false;
        }
      }
      return true;
    });
  }, [incidents, filters]);

  // Paginate
  const totalPages = Math.ceil(filteredIncidents.length / ITEMS_PER_PAGE);
  const paginatedIncidents = useMemo(() => {
    const start = (page - 1) * ITEMS_PER_PAGE;
    return filteredIncidents.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredIncidents, page]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [filters]);

  // Load forensic systems
  const loadForensicSystems = async (customOffset?: number) => {
    setForensicLoading(true);
    setForensicError(null);
    try {
      const result = await getForensicSystems(
        forensicLimit,
        customOffset !== undefined ? customOffset : forensicOffset
      );
      setForensicSystems(result.items);
      setForensicTotal(result.total);
    } catch (err) {
      console.error("Failed to load forensic systems:", err);
      setForensicError(err instanceof Error ? err.message : "Failed to load forensic systems");
    } finally {
      setForensicLoading(false);
    }
  };

  // Handle delete forensic system
  const handleDeleteForensicSystem = async (urn: string) => {
    const confirmed = confirm(`Are you sure you want to delete this analyzed system?`);
    if (!confirmed) return;

    try {
      await deleteForensicSystem(urn);
      await loadForensicSystems();
    } catch (err) {
      console.error("Error deleting forensic system:", err);
      alert("Failed to delete forensic system");
    }
  };

  // Load forensic systems on mount and when pagination changes
  useEffect(() => {
    loadForensicSystems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forensicOffset]);

  // Reload forensic systems after analysis completes
  useEffect(() => {
    if (!analyzing && results.size > 0) {
      loadForensicSystems();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [analyzing]);

  // Selection handlers
  const handleSelectAll = () => {
    if (selectedIds.size === paginatedIncidents.length) {
      // Deselect all on current page
      const newSelected = new Set(selectedIds);
      paginatedIncidents.forEach((inc) => newSelected.delete(inc.id));
      setSelectedIds(newSelected);
    } else {
      // Select all on current page
      const newSelected = new Set(selectedIds);
      paginatedIncidents.forEach((inc) => newSelected.add(inc.id));
      setSelectedIds(newSelected);
    }
  };

  const handleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleClearSelection = () => {
    setSelectedIds(new Set());
  };

  // Auto-scroll stream container
  useEffect(() => {
    if (streamContainerRef.current) {
      streamContainerRef.current.scrollTop = streamContainerRef.current.scrollHeight;
    }
  }, [streamEvents]);

  // Analysis handler with streaming
  const handleAnalyze = async () => {
    if (selectedIds.size === 0) return;

    setAnalyzing(true);
    setShowStreamModal(true);
    setAnalysisComplete(false);
    setProgress({ current: 0, total: selectedIds.size, currentId: "" });
    setResults(new Map());
    setStreamEvents([]);
    setCurrentStep("");
    setStreamProgress(0);

    const selectedIncidents = incidents.filter((i) => selectedIds.has(i.id));

    for (const incident of selectedIncidents) {
      setProgress((prev) => ({ ...prev, currentId: incident.id }));
      setStreamEvents([]); // Reset stream for each incident
      setStreamProgress(0);

      try {
        const narrative = buildNarrative(incident);

        // Use streaming API
        const stream = analyzeIncidentStream({
          narrative,
          source: "AIAAIC Repository",
          metadata: {
            aiaaic_id: incident.id,
            headline: incident.headline,
            system_name: incident.system_name,
            technology: incident.technology,
            sector: incident.sector,
            country: incident.country,
          },
          withEvidencePlan,
          agentMode,
        });

        let finalResult: ForensicAnalysisResult | null = null;

        for await (const event of stream) {
          // Add event to stream
          setStreamEvents((prev) => [...prev, event]);

          // Update current step
          if (event.step_name) {
            setCurrentStep(event.step_name);
          }

          // Update progress
          if (event.progress_percent !== undefined) {
            setStreamProgress(event.progress_percent);
          }

          // Capture final result
          if (event.event_type === "analysis_complete" && event.data) {
            finalResult = event.data as unknown as ForensicAnalysisResult;
          }

          // Handle errors
          if (event.event_type === "error") {
            finalResult = {
              status: "ERROR",
              error: event.data?.error as string || "Unknown error",
            } as ForensicAnalysisResult;
          }
        }

        if (finalResult) {
          setResults((prev) => new Map(prev).set(incident.id, finalResult!));
        }
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setResults((prev) =>
          new Map(prev).set(incident.id, {
            status: "ERROR",
            error: errorMessage,
          } as ForensicAnalysisResult)
        );
      }

      setProgress((prev) => ({ ...prev, current: prev.current + 1 }));
    }

    setAnalyzing(false);
    setAnalysisComplete(true);
  };

  // Close stream modal handler
  const handleCloseStreamModal = () => {
    setShowStreamModal(false);
    setStreamEvents([]);
    setAnalysisComplete(false);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 text-gray-900 dark:text-white">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-lg">Loading AIAAIC incidents...</span>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-6 text-gray-900 dark:text-white">
        <div className="bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg p-4">
          <h3 className="text-red-700 dark:text-red-400 font-semibold">Error</h3>
          <p className="text-red-600 dark:text-red-300">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 text-gray-900 dark:text-white">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Forensic AI Agent</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Analyze AIAAIC incidents for EU AI Act, ISO 42001, and NIST AI RMF compliance
        </p>
        <div className="mt-2 flex items-center gap-2">
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              serviceHealthy
                ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
            }`}
          >
            {serviceHealthy ? "Service Online" : "Service Offline"}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {incidents.length} incidents available
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Search</label>
            <input
              type="text"
              placeholder="ID, headline, system..."
              value={filters.search}
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Sector</label>
            <select
              value={filters.sector}
              onChange={(e) => setFilters((f) => ({ ...f, sector: e.target.value }))}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">All Sectors</option>
              {filterOptions.sectors.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Country</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters((f) => ({ ...f, country: e.target.value }))}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">All Countries</option>
              {filterOptions.countries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Year</label>
            <select
              value={filters.year}
              onChange={(e) => setFilters((f) => ({ ...f, year: e.target.value }))}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">All Years</option>
              {filterOptions.years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Technology</label>
            <select
              value={filters.technology}
              onChange={(e) => setFilters((f) => ({ ...f, technology: e.target.value }))}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="">All Technologies</option>
              {filterOptions.technologies.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-3 flex justify-between items-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Showing {filteredIncidents.length} of {incidents.length} incidents
          </span>
          <button
            onClick={() => setFilters({ sector: "", country: "", year: "", technology: "", search: "" })}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={paginatedIncidents.length > 0 && paginatedIncidents.every((i) => selectedIds.has(i.id))}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                ID
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Headline
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                System
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Year
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Issues
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {paginatedIncidents.map((incident) => (
              <tr
                key={incident.id}
                className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${
                  selectedIds.has(incident.id) ? "bg-blue-50 dark:bg-blue-900/20" : ""
                }`}
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(incident.id)}
                    onChange={() => handleSelect(incident.id)}
                    className="rounded border-gray-300 dark:border-gray-600"
                  />
                </td>
                <td className="px-4 py-3 text-sm font-mono text-gray-700 dark:text-gray-300">
                  {incident.id}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-md">
                  <span className="line-clamp-2">{incident.headline}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {incident.system_name || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {incident.occurred}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {incident.issues.split(";").slice(0, 2).map((issue, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                      >
                        {issue.trim()}
                      </span>
                    ))}
                    {incident.issues.split(";").length > 2 && (
                      <span className="text-xs text-gray-500">+{incident.issues.split(";").length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => setDetailIncident(incident)}
                    className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Page {page} of {totalPages}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>

      {/* Selection Bar */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-blue-600 text-white py-4 px-6 flex justify-between items-center shadow-lg z-50">
          <div className="flex items-center gap-4">
            <span className="font-semibold">{selectedIds.size} incident(s) selected</span>
            <button
              onClick={handleClearSelection}
              className="text-blue-200 hover:text-white text-sm"
            >
              Clear Selection
            </button>
          </div>
          <div className="flex items-center gap-4">
            {/* Agent Mode Selector */}
            <div className="flex items-center gap-2 bg-blue-700 px-3 py-2 rounded-lg">
              <span className="text-sm font-medium">Agent:</span>
              <select
                value={agentMode}
                onChange={(e) => setAgentMode(e.target.value as AgentMode)}
                disabled={agentMode === "react" && !reactAgentInfo?.enabled}
                className="bg-blue-800 text-white text-sm rounded px-2 py-1 border border-blue-500 focus:ring-purple-400"
              >
                <option value="pipeline">Pipeline (7-step)</option>
                <option value="react" disabled={!reactAgentInfo?.enabled}>
                  ReAct (LangGraph) {!reactAgentInfo?.enabled && "(disabled)"}
                </option>
              </select>
              {agentMode === "react" && reactAgentInfo && (
                <span className="text-xs text-blue-200" title={`Using ${reactAgentInfo.model}`}>
                  {reactAgentInfo.model}
                </span>
              )}
            </div>
            {/* Evidence Plan Toggle */}
            <label className={`flex items-center gap-2 cursor-pointer bg-blue-700 px-3 py-2 rounded-lg ${agentMode === "react" ? "opacity-50" : ""}`}>
              <input
                type="checkbox"
                checked={withEvidencePlan && agentMode !== "react"}
                onChange={(e) => setWithEvidencePlan(e.target.checked)}
                disabled={agentMode === "react"}
                className="w-4 h-4 rounded border-white/50 text-purple-500 focus:ring-purple-400 focus:ring-offset-0"
              />
              <span className="text-sm font-medium">
                Include DPV Evidence Plan
              </span>
              <span className="text-xs text-blue-200" title="Generate W3C DPV-based evidence requirements for compliance gaps">
                (?)
              </span>
            </label>
            <button
              onClick={handleAnalyze}
              disabled={analyzing || !serviceHealthy}
              className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analyzing ? "Analyzing..." : "Run Forensic Analysis"}
            </button>
          </div>
        </div>
      )}

      {/* Analysis Progress Modal with Streaming Conversation */}
      {showStreamModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  {analysisComplete ? (
                    <span>✅</span>
                  ) : (
                    <span className="animate-pulse">🔬</span>
                  )}
                  {analysisComplete ? "Analysis Complete" : "Forensic Analysis in Progress"}
                </h3>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    Incident {Math.min(progress.current + 1, progress.total)} / {progress.total}
                  </span>
                  {analysisComplete && (
                    <button
                      onClick={handleCloseStreamModal}
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      title="Close"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* Overall Progress */}
              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{analysisComplete ? "All analyses completed" : (currentStep || "Initializing...")}</span>
                  <span>{Math.round(streamProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      analysisComplete
                        ? "bg-green-500"
                        : "bg-gradient-to-r from-blue-500 to-purple-600"
                    }`}
                    style={{ width: `${analysisComplete ? 100 : streamProgress}%` }}
                  ></div>
                </div>
              </div>

              {progress.currentId && !analysisComplete && (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Analyzing: <span className="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">{progress.currentId}</span>
                </p>
              )}
            </div>

            {/* Conversation Stream */}
            <div
              ref={streamContainerRef}
              className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 dark:bg-gray-900"
              style={{ minHeight: "400px", maxHeight: "60vh" }}
            >
              {streamEvents.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p>Starting analysis...</p>
                  </div>
                </div>
              ) : (
                streamEvents.map((event, idx) => (
                  <StreamEventCard key={idx} event={event} />
                ))
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  {analysisComplete ? (
                    <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      Completed
                    </span>
                  ) : (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                      Live Stream
                    </span>
                  )}
                  <span>|</span>
                  <span>{streamEvents.length} events</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    LLM: <span className="font-medium text-gray-700 dark:text-gray-300">{llmInfo?.model || "Unknown"}</span> + SPARQL Reasoner
                  </div>
                  {analysisComplete && (
                    <button
                      onClick={handleCloseStreamModal}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Close
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results.size > 0 && !analyzing && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-20">
          <h3 className="text-xl font-semibold mb-4">Analysis Results</h3>
          <div className="space-y-4">
            {Array.from(results.entries()).map(([id, result]) => {
              const incident = incidents.find((i) => i.id === id);
              const isExpanded = expandedResult === id;

              return (
                <div
                  key={id}
                  className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedResult(isExpanded ? null : id)}
                    className="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-600"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-3 h-3 rounded-full ${
                          result.status === "ERROR"
                            ? "bg-red-500"
                            : result.status === "COMPLETED"
                            ? "bg-green-500"
                            : "bg-yellow-500"
                        }`}
                      ></span>
                      <span className="font-mono text-sm">{id}</span>
                      <span className="text-gray-600 dark:text-gray-300 text-sm truncate max-w-xs">
                        {incident?.headline}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      {result.eu_ai_act && (
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${
                            result.eu_ai_act.risk_level === "High" || result.eu_ai_act.risk_level === "Unacceptable"
                              ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                              : result.eu_ai_act.risk_level === "Limited"
                              ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                              : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                          }`}
                        >
                          {result.eu_ai_act.risk_level}
                        </span>
                      )}
                      <svg
                        className={`w-5 h-5 transform transition-transform ${isExpanded ? "rotate-180" : ""}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-600">
                      {result.status === "ERROR" ? (
                        <div className="text-red-600 dark:text-red-400">
                          <p className="font-semibold">Analysis Failed</p>
                          <p className="text-sm">{result.error}</p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {/* Extraction Summary */}
                          {result.extraction && (
                            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 mb-3">
                              <div className="flex items-center justify-between">
                                <div>
                                  <span className="font-medium text-gray-900 dark:text-white">
                                    {result.extraction.system?.system_name || "Unknown System"}
                                  </span>
                                  <span className="text-gray-500 dark:text-gray-400 ml-2 text-sm">
                                    by {result.extraction.system?.organization || "Unknown"}
                                  </span>
                                </div>
                                <span className="text-sm text-gray-500 dark:text-gray-400">
                                  Confidence: {((result.extraction.confidence?.overall || 0) * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="flex gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                                <span>Type: {result.extraction.system?.system_type}</span>
                                <span>Incident: {result.extraction.incident?.incident_type}</span>
                                <span>Severity: {result.extraction.incident?.severity}</span>
                              </div>
                            </div>
                          )}

                          {/* EU AI Act Section */}
                          {result.eu_ai_act && (
                            <div>
                              <h4 className="font-semibold text-blue-700 dark:text-blue-400 mb-2">
                                EU AI Act Assessment
                              </h4>
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500 dark:text-gray-400">Risk Level:</span>
                                  <span className="ml-2 font-medium">{result.eu_ai_act.risk_level}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500 dark:text-gray-400">Requirements:</span>
                                  <span className="ml-2 font-medium">
                                    {result.eu_ai_act.total_requirements || 0}
                                  </span>
                                </div>
                              </div>
                              {result.eu_ai_act.criteria && result.eu_ai_act.criteria.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Criteria:</p>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {result.eu_ai_act.criteria.map((c: string, idx: number) => (
                                      <span key={idx} className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded text-xs">
                                        {c.split('#').pop() || c}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Compliance Gaps */}
                          {result.compliance_gaps && (
                            <div>
                              <h4 className="font-semibold text-red-700 dark:text-red-400 mb-2">
                                Compliance Gaps
                              </h4>
                              <div className="grid grid-cols-3 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500 dark:text-gray-400">Compliance Ratio:</span>
                                  <span className="ml-2 font-medium">{(result.compliance_gaps.compliance_ratio * 100).toFixed(1)}%</span>
                                </div>
                                <div>
                                  <span className="text-gray-500 dark:text-gray-400">Missing:</span>
                                  <span className="ml-2 font-medium">{result.compliance_gaps.missing}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500 dark:text-gray-400">Severity:</span>
                                  <span className={`ml-2 font-medium ${
                                    result.compliance_gaps.severity === "CRITICAL" ? "text-red-600" :
                                    result.compliance_gaps.severity === "HIGH" ? "text-orange-600" :
                                    "text-gray-600"
                                  }`}>{result.compliance_gaps.severity}</span>
                                </div>
                              </div>
                              {result.compliance_gaps.critical_gaps && result.compliance_gaps.critical_gaps.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Critical Gaps:</p>
                                  <ul className="list-disc list-inside text-sm text-red-600 dark:text-red-400">
                                    {result.compliance_gaps.critical_gaps.map((g: string | { reason?: string; requirement?: string }, idx: number) => (
                                      <li key={idx}>{typeof g === 'string' ? g : (g.reason || g.requirement || 'Unknown gap')}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}

                          {/* ISO 42001 Section */}
                          {result.iso_42001 && (
                            <div>
                              <h4 className="font-semibold text-purple-700 dark:text-purple-400 mb-2">
                                ISO 42001 Assessment
                              </h4>
                              <div className="text-sm">
                                <span className="text-gray-500 dark:text-gray-400">Controls Mapped:</span>
                                <span className="ml-2 font-medium">{result.iso_42001.total_mapped}</span>
                                {result.iso_42001.certification_gap_detected && (
                                  <span className="ml-4 text-amber-600 dark:text-amber-400">
                                    ⚠ Certification Gap Detected
                                  </span>
                                )}
                              </div>
                            </div>
                          )}

                          {/* NIST RMF Section */}
                          {result.nist_ai_rmf && (
                            <div>
                              <h4 className="font-semibold text-orange-700 dark:text-orange-400 mb-2">
                                NIST AI RMF Assessment
                              </h4>
                              <div className="text-sm">
                                <span className="text-gray-500 dark:text-gray-400">Functions Mapped:</span>
                                <span className="ml-2 font-medium">{result.nist_ai_rmf.total_mapped}</span>
                                <span className="ml-4 text-gray-500 dark:text-gray-400">Jurisdiction:</span>
                                <span className="ml-2 font-medium">
                                  {result.nist_ai_rmf.jurisdiction_applicable ? "Applicable" : "Not Applicable"}
                                </span>
                              </div>
                            </div>
                          )}

                          {/* Full Report Link */}
                          {result.report && (
                            <details className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                              <summary className="cursor-pointer text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline">
                                View Full Report
                              </summary>
                              <div className="mt-2 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg prose prose-sm dark:prose-invert max-w-none max-h-[600px] overflow-y-auto">
                                <Markdown>{result.report}</Markdown>
                              </div>
                            </details>
                          )}

                          {/* Expert Review Warning */}
                          {result.requires_expert_review && (
                            <div className="mt-3 p-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-sm text-amber-700 dark:text-amber-400">
                              ⚠ This analysis requires expert review before use in enforcement decisions.
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Forensic Analyzed Systems Section */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-20">
        <h3 className="text-xl font-semibold mb-4 flex items-center">
          <span className="mr-2">🔬</span>
          Analyzed Systems Database
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          AI systems that have been analyzed and persisted for compliance tracking.
        </p>

        {forensicError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p className="font-semibold">Error loading analyzed systems</p>
            <p className="text-sm">{forensicError}</p>
          </div>
        )}

        {forensicLoading ? (
          <p className="text-gray-500 dark:text-gray-400">Loading analyzed systems...</p>
        ) : forensicSystems.length === 0 ? (
          <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 text-center">
            <p className="text-gray-600 dark:text-gray-400">No analyzed systems yet.</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Select incidents above and run forensic analysis to populate this database.
            </p>
          </div>
        ) : (
          <div>
            <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-4">
            <table className="min-w-full table-fixed">
              <thead>
                <tr className="bg-purple-100 dark:bg-purple-900">
                  <th className="p-2 text-left w-[40%]">System Name</th>
                  <th className="p-2 text-left w-[25%]">Organization</th>
                  <th className="p-2 text-left w-[18%]">Risk Level</th>
                  <th className="p-2 text-left w-[17%]">Actions</th>
                </tr>
              </thead>
              <tbody>
                {forensicSystems.map((fs) => (
                  <tr key={fs.urn} className="border-t dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="p-2">
                      <div className="truncate font-medium" title={fs.hasName}>{fs.hasName}</div>
                      {fs.aiaaic_id && (
                        <span className="text-xs text-purple-600 dark:text-purple-400">{fs.aiaaic_id}</span>
                      )}
                    </td>
                    <td className="p-2 truncate" title={fs.hasOrganization}>{fs.hasOrganization || "-"}</td>
                    <td className="p-2">
                      {(() => {
                        const riskLevel = Array.isArray(fs.hasRiskLevel)
                          ? fs.hasRiskLevel[0] || ""
                          : (fs.hasRiskLevel || "");
                        const riskStr = String(riskLevel);
                        return (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            riskStr.includes("High") ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" :
                            riskStr.includes("Limited") ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" :
                            riskStr.includes("Minimal") ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" :
                            "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                          }`}>
                            {riskStr.replace("ai:", "")}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <button
                        onClick={() => setSelectedForensicSystem(fs)}
                        className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm mr-1"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteForensicSystem(fs.urn)}
                        className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>

            {/* Forensic Pagination */}
            <div className="flex justify-between items-center">
              <button
                disabled={forensicOffset === 0}
                onClick={() => setForensicOffset((o) => Math.max(o - forensicLimit, 0))}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span>
                Showing {forensicOffset + 1} to {Math.min(forensicOffset + forensicLimit, forensicTotal)} of {forensicTotal}
              </span>
              <button
                disabled={forensicOffset + forensicLimit >= forensicTotal}
                onClick={() => setForensicOffset((o) => o + forensicLimit)}
                className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Forensic System Detail Modal */}
      {selectedForensicSystem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {selectedForensicSystem.hasName}
                </h3>
                <button
                  onClick={() => setSelectedForensicSystem(null)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
                >
                  &times;
                </button>
              </div>

              {selectedForensicSystem.headline && (
                <p className="text-gray-600 dark:text-gray-400 mb-4 italic">
                  "{selectedForensicSystem.headline}"
                </p>
              )}

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Organization</p>
                  <p className="font-medium">{selectedForensicSystem.hasOrganization}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Risk Level</p>
                  <p className="font-medium">{(Array.isArray(selectedForensicSystem.hasRiskLevel) ? selectedForensicSystem.hasRiskLevel[0] : selectedForensicSystem.hasRiskLevel || "Unknown").replace("ai:", "")}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Compliance Ratio</p>
                  <p className="font-medium">{Math.round(selectedForensicSystem.complianceRatio * 100)}%</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Jurisdiction</p>
                  <p className="font-medium">{selectedForensicSystem.jurisdiction}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Source</p>
                  <p className="font-medium">{selectedForensicSystem.source}</p>
                </div>
                {selectedForensicSystem.aiaaic_id && (
                  <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400">AIAAIC ID</p>
                    <p className="font-medium">{selectedForensicSystem.aiaaic_id}</p>
                  </div>
                )}
              </div>

              {/* Incident Info */}
              {selectedForensicSystem.incident && (
                <div className="mb-6">
                  <h4 className="font-semibold mb-2 text-red-600 dark:text-red-400">Incident Details</h4>
                  <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Type</p>
                      <p className="font-medium">{selectedForensicSystem.incident.type || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Severity</p>
                      <p className="font-medium">{selectedForensicSystem.incident.severity || "N/A"}</p>
                    </div>
                    {selectedForensicSystem.incident.affectedPopulations?.length > 0 && (
                      <div className="col-span-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400">Affected Populations</p>
                        <p className="font-medium">{selectedForensicSystem.incident.affectedPopulations.join(", ")}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Compliance Gaps */}
              {selectedForensicSystem.missingRequirements && selectedForensicSystem.missingRequirements.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold mb-2 text-orange-600 dark:text-orange-400">Missing Requirements ({selectedForensicSystem.missingRequirements.length})</h4>
                  <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded">
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {selectedForensicSystem.missingRequirements.slice(0, 10).map((req, i) => (
                        <li key={i}>{req}</li>
                      ))}
                      {selectedForensicSystem.missingRequirements.length > 10 && (
                        <li className="text-gray-500">...and {selectedForensicSystem.missingRequirements.length - 10} more</li>
                      )}
                    </ul>
                  </div>
                </div>
              )}

              {/* ISO 42001 Assessment */}
              {selectedForensicSystem.iso_42001 && (
                <div className="mb-6">
                  <h4 className="font-semibold mb-2 text-purple-600 dark:text-purple-400">ISO 42001 Assessment</h4>
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Controls Mapped</p>
                        <p className="font-medium">{selectedForensicSystem.iso_42001.total_mapped}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Certification Gap</p>
                        <p className={`font-medium ${selectedForensicSystem.iso_42001.certification_gap_detected ? 'text-amber-600' : 'text-green-600'}`}>
                          {selectedForensicSystem.iso_42001.certification_gap_detected ? '⚠ Gap Detected' : '✓ No Gap'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* NIST AI RMF Assessment */}
              {selectedForensicSystem.nist_ai_rmf && (
                <div className="mb-6">
                  <h4 className="font-semibold mb-2 text-blue-600 dark:text-blue-400">NIST AI RMF Assessment</h4>
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Functions Mapped</p>
                        <p className="font-medium">{selectedForensicSystem.nist_ai_rmf.total_mapped}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Jurisdiction Applicable</p>
                        <p className="font-medium">{selectedForensicSystem.nist_ai_rmf.jurisdiction_applicable ? 'Yes' : 'No'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Full Report */}
              {selectedForensicSystem.report && (
                <div className="mb-6">
                  <details>
                    <summary className="cursor-pointer font-semibold mb-2 text-green-600 dark:text-green-400 hover:underline">
                      📄 View Full Analysis Report
                    </summary>
                    <div ref={reportRef} className="bg-gray-50 dark:bg-gray-900 p-4 rounded mt-2 prose prose-sm dark:prose-invert max-w-none max-h-[400px] overflow-y-auto">
                      <Markdown>{selectedForensicSystem.report}</Markdown>
                    </div>
                  </details>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4 border-t dark:border-gray-700">
                {selectedForensicSystem.report && (
                  <button
                    onClick={handleExportPdf}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Export PDF
                  </button>
                )}
                <button
                  onClick={() => setSelectedForensicSystem(null)}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {detailIncident && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-start">
              <div>
                <span className="text-sm font-mono text-gray-500 dark:text-gray-400">{detailIncident.id}</span>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-1">
                  {detailIncident.headline}
                </h3>
              </div>
              <button
                onClick={() => setDetailIncident(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <DetailField label="System Name" value={detailIncident.system_name} />
                <DetailField label="Technology" value={detailIncident.technology} />
                <DetailField label="Year" value={detailIncident.occurred} />
                <DetailField label="Country" value={detailIncident.country} />
                <DetailField label="Sector" value={detailIncident.sector} />
                <DetailField label="News Trigger" value={detailIncident.news_trigger} />
                <DetailField label="Deployer" value={detailIncident.deployer} />
                <DetailField label="Developer" value={detailIncident.developer} />
              </div>

              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Purpose</span>
                <p className="text-gray-900 dark:text-white mt-1">{detailIncident.purpose || "-"}</p>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Issues</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {detailIncident.issues.split(";").map((issue, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                    >
                      {issue.trim()}
                    </span>
                  ))}
                </div>
              </div>

              {detailIncident.summary_url && (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <a
                    href={detailIncident.summary_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    View on AIAAIC Repository
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                  </a>
                </div>
              )}
            </div>

            <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => setDetailIncident(null)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleSelect(detailIncident.id);
                  setDetailIncident(null);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {selectedIds.has(detailIncident.id) ? "Deselect" : "Select for Analysis"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</span>
      <p className="text-gray-900 dark:text-white mt-1">{value || "-"}</p>
    </div>
  );
}

// Stream Event Card Component
function StreamEventCard({ event }: { event: StreamEvent }) {
  const getEventIcon = () => {
    switch (event.event_type) {
      case "step_start":
        return "🚀";
      case "step_complete":
        return "✅";
      case "llm_prompt":
        return "💬";
      case "llm_response":
        return "🤖";
      case "sparql_query":
        return "🔍";
      case "sparql_result":
        return "📊";
      case "analysis_complete":
        return "🎉";
      case "error":
        return "❌";
      default:
        return "📝";
    }
  };

  const getEventColor = () => {
    switch (event.event_type) {
      case "step_start":
        return "border-l-blue-500 bg-blue-50 dark:bg-blue-900/20";
      case "step_complete":
        return "border-l-green-500 bg-green-50 dark:bg-green-900/20";
      case "llm_prompt":
        return "border-l-purple-500 bg-purple-50 dark:bg-purple-900/20";
      case "llm_response":
        return "border-l-indigo-500 bg-indigo-50 dark:bg-indigo-900/20";
      case "sparql_query":
        return "border-l-orange-500 bg-orange-50 dark:bg-orange-900/20";
      case "sparql_result":
        return "border-l-amber-500 bg-amber-50 dark:bg-amber-900/20";
      case "analysis_complete":
        return "border-l-emerald-500 bg-emerald-50 dark:bg-emerald-900/20";
      case "error":
        return "border-l-red-500 bg-red-50 dark:bg-red-900/20";
      default:
        return "border-l-gray-500 bg-gray-50 dark:bg-gray-800";
    }
  };

  const getRoleBadge = () => {
    if (!event.message) return null;
    const role = event.message.role;
    const colors: Record<string, string> = {
      user: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      assistant: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
      tool: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      system: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
    };
    return (
      <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[role] || colors.system}`}>
        {role.toUpperCase()}
      </span>
    );
  };

  const formatTimestamp = (ts: string) => {
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      return "";
    }
  };

  return (
    <div className={`border-l-4 rounded-r-lg p-3 ${getEventColor()}`}>
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="text-lg">{getEventIcon()}</span>
          <span className="font-medium text-sm text-gray-900 dark:text-white">
            {event.step_name || event.event_type.replace(/_/g, " ").toUpperCase()}
          </span>
          {getRoleBadge()}
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          {event.step_number && <span>Step {event.step_number}</span>}
          <span>{formatTimestamp(event.timestamp)}</span>
        </div>
      </div>

      {event.message && (
        <div className="mt-2 text-sm text-gray-700 dark:text-gray-300 font-mono bg-white dark:bg-gray-800 rounded p-3 border border-gray-200 dark:border-gray-700 max-h-48 overflow-y-auto whitespace-pre-wrap">
          <Markdown>{event.message.content}</Markdown>
        </div>
      )}

      {event.data && !event.message && (
        <div className="mt-2 text-sm font-mono bg-white dark:bg-gray-800 rounded p-3 border border-gray-200 dark:border-gray-700 max-h-48 overflow-y-auto">
          <pre className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-xs">
            {JSON.stringify(event.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
