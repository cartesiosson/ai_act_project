import React, { useEffect, useState, useMemo } from "react";
import Markdown from "react-markdown";
import type { Incident, ForensicAnalysisResult } from "../lib/forensicApi";
import {
  loadIncidents,
  analyzeIncident,
  buildNarrative,
  getUniqueValues,
  checkHealth,
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

  // Service health
  const [serviceHealthy, setServiceHealthy] = useState<boolean | null>(null);

  // Load incidents on mount
  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [data, healthy] = await Promise.all([loadIncidents(), checkHealth()]);
        setIncidents(data);
        setServiceHealthy(healthy);
      } catch (err: any) {
        setError(err.message || "Failed to load incidents");
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

  // Analysis handler
  const handleAnalyze = async () => {
    if (selectedIds.size === 0) return;

    setAnalyzing(true);
    setProgress({ current: 0, total: selectedIds.size, currentId: "" });
    setResults(new Map());

    const selectedIncidents = incidents.filter((i) => selectedIds.has(i.id));

    for (const incident of selectedIncidents) {
      setProgress((prev) => ({ ...prev, currentId: incident.id }));

      try {
        const narrative = buildNarrative(incident);
        const result = await analyzeIncident({
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
        });

        setResults((prev) => new Map(prev).set(incident.id, result));
      } catch (err: any) {
        setResults((prev) =>
          new Map(prev).set(incident.id, {
            status: "ERROR",
            error: err.message,
          } as ForensicAnalysisResult)
        );
      }

      setProgress((prev) => ({ ...prev, current: prev.current + 1 }));
    }

    setAnalyzing(false);
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
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !serviceHealthy}
            className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? "Analyzing..." : "Run Forensic Analysis"}
          </button>
        </div>
      )}

      {/* Analysis Progress */}
      {analyzing && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-semibold mb-4">Analyzing Incidents</h3>
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress</span>
                <span>{progress.current} / {progress.total}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.current / progress.total) * 100}%` }}
                ></div>
              </div>
            </div>
            {progress.currentId && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Currently analyzing: <span className="font-mono">{progress.currentId}</span>
              </p>
            )}
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
