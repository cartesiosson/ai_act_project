import { useEffect, useState, useMemo } from "react";
import { getForensicSystems, type ForensicSystem } from "../lib/forensicApi";
import { fetchSystems } from "../lib/api";

// Types for Evidence Plan structure
interface EvidenceItem {
  id: string;
  name: string;
  description: string;
  evidence_type: string;
  priority: string;
  frequency: string;
  responsible_role: string;
  dpv_measure?: string;
  templates?: string[];
  guidance?: string;
}

interface RequirementEvidencePlan {
  requirement_uri: string;
  requirement_label: string;
  priority: string;
  dpv_measures: string[];
  evidence_items: EvidenceItem[];
  deadline_recommendation: string;
  responsible_roles: string[];
  article_reference?: string;
  estimated_effort?: string;
}

interface EvidencePlan {
  plan_id: string;
  generated_at: string;
  system_name: string;
  risk_level: string;
  total_gaps: number;
  requirement_plans: RequirementEvidencePlan[];
  summary: {
    total_evidence_items?: number;
    by_priority?: Record<string, number>;
    by_type?: Record<string, number>;
    by_role?: Record<string, number>;
  };
  recommendations: string[];
}

interface ForensicSystemWithEvidence extends ForensicSystem {
  evidence_plan?: EvidencePlan;
}

const FORENSIC_API_BASE = import.meta.env.VITE_FORENSIC_API_URL || "/forensic-api";

// Priority badge colors
const priorityColors: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  HIGH: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
  MEDIUM: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  LOW: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
};

// Evidence type colors
const typeColors: Record<string, string> = {
  PolicyEvidence: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  TechnicalEvidence: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
  AuditEvidence: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400",
  TrainingEvidence: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400",
  AssessmentEvidence: "bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-400",
  ContractualEvidence: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
};

// Role colors
const roleColors: Record<string, string> = {
  DEPLOYER: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
  PROVIDER: "bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-400",
  DPO: "bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-400",
  LEGAL: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
  TECHNICAL: "bg-fuchsia-100 text-fuchsia-800 dark:bg-fuchsia-900/30 dark:text-fuchsia-400",
  COMPLIANCE: "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400",
};

export default function DPVPage() {
  // State
  const [systems, setSystems] = useState<ForensicSystemWithEvidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSystemUrn, setSelectedSystemUrn] = useState<string>("");
  const [selectedSystem, setSelectedSystem] = useState<ForensicSystemWithEvidence | null>(null);
  const [expandedRequirements, setExpandedRequirements] = useState<Set<string>>(new Set());

  // Filters
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [searchFilter, setSearchFilter] = useState<string>("");

  // Load systems with evidence plans (both forensic and manual)
  useEffect(() => {
    async function loadAllSystems() {
      setLoading(true);
      setError(null);
      try {
        const systemsWithPlans: ForensicSystemWithEvidence[] = [];

        // 1. Load forensic systems (from AIAAIC analysis)
        try {
          const forensicResponse = await getForensicSystems(100, 0);
          for (const sys of forensicResponse.items) {
            try {
              const fullSystem = await fetch(
                `${FORENSIC_API_BASE}/forensic/systems/${encodeURIComponent(sys.urn)}`
              );
              if (fullSystem.ok) {
                const data = await fullSystem.json();
                if (data.evidence_plan) {
                  systemsWithPlans.push({
                    ...data,
                    source: "forensic"
                  });
                }
              }
            } catch (err) {
              console.warn(`Failed to fetch forensic details for ${sys.urn}:`, err);
            }
          }
        } catch (err) {
          console.warn("Failed to load forensic systems:", err);
        }

        // 2. Load manual systems (from backend /api/systems)
        try {
          const manualSystems = await fetchSystems();
          for (const sys of manualSystems) {
            // Check if system has an evidence plan
            if (sys.evidencePlan) {
              systemsWithPlans.push({
                urn: sys["ai:hasUrn"] || sys["@id"],
                hasName: sys.hasName,
                hasOrganization: sys.hasOrganization || "Manual Entry",
                hasRiskLevel: sys.hasRiskLevel || "Unknown",
                complianceRatio: 0,
                jurisdiction: "EU",
                source: "manual",
                evidence_plan: sys.evidencePlan
              });
            }
          }
        } catch (err) {
          console.warn("Failed to load manual systems:", err);
        }

        setSystems(systemsWithPlans);
      } catch (err) {
        console.error("Error loading systems:", err);
        setError(err instanceof Error ? err.message : "Failed to load systems");
      } finally {
        setLoading(false);
      }
    }
    loadAllSystems();
  }, []);

  // Update selected system when selection changes
  useEffect(() => {
    if (selectedSystemUrn) {
      const sys = systems.find((s) => s.urn === selectedSystemUrn);
      if (sys) {
        setSelectedSystem(sys);
        setExpandedRequirements(new Set());
        setPriorityFilter("");
        setTypeFilter("");
        setRoleFilter("");
        setSearchFilter("");
      }
    } else {
      setSelectedSystem(null);
    }
  }, [selectedSystemUrn, systems]);

  const handleSelectionChange = (value: string) => {
    setSelectedSystemUrn(value);
  };

  // Get unique filter options from selected system's evidence plan
  const filterOptions = useMemo(() => {
    if (!selectedSystem?.evidence_plan?.requirement_plans) {
      return { priorities: [], types: [], roles: [] };
    }

    const priorities = new Set<string>();
    const types = new Set<string>();
    const roles = new Set<string>();

    selectedSystem.evidence_plan.requirement_plans.forEach(plan => {
      if (plan.priority) priorities.add(plan.priority);
      if (plan.evidence_items) {
        plan.evidence_items.forEach(item => {
          if (item.evidence_type) types.add(item.evidence_type);
          if (item.responsible_role) roles.add(item.responsible_role);
        });
      }
    });

    return {
      priorities: Array.from(priorities),
      types: Array.from(types),
      roles: Array.from(roles),
    };
  }, [selectedSystem]);

  // Filter evidence items
  const filteredRequirementPlans = useMemo(() => {
    if (!selectedSystem?.evidence_plan?.requirement_plans) return [];

    return selectedSystem.evidence_plan.requirement_plans
      .map(plan => {
        // Filter evidence items within each plan
        const items = plan.evidence_items || [];
        const filteredItems = items.filter(item => {
          if (priorityFilter && item.priority !== priorityFilter) return false;
          if (typeFilter && item.evidence_type !== typeFilter) return false;
          if (roleFilter && item.responsible_role !== roleFilter) return false;
          if (searchFilter) {
            const search = searchFilter.toLowerCase();
            const name = item.name || "";
            const description = item.description || "";
            const id = item.id || "";
            if (
              !name.toLowerCase().includes(search) &&
              !description.toLowerCase().includes(search) &&
              !id.toLowerCase().includes(search)
            ) {
              return false;
            }
          }
          return true;
        });

        return { ...plan, evidence_items: filteredItems };
      })
      .filter(plan => plan.evidence_items.length > 0);
  }, [selectedSystem, priorityFilter, typeFilter, roleFilter, searchFilter]);

  // Toggle requirement expansion
  const toggleRequirement = (uri: string) => {
    setExpandedRequirements(prev => {
      const next = new Set(prev);
      if (next.has(uri)) {
        next.delete(uri);
      } else {
        next.add(uri);
      }
      return next;
    });
  };

  // Expand all requirements
  const expandAll = () => {
    if (!selectedSystem?.evidence_plan?.requirement_plans) return;
    setExpandedRequirements(new Set(
      selectedSystem.evidence_plan.requirement_plans.map(p => p.requirement_uri)
    ));
  };

  // Collapse all requirements
  const collapseAll = () => {
    setExpandedRequirements(new Set());
  };

  // Count total evidence items after filtering
  const totalFilteredItems = filteredRequirementPlans.reduce(
    (sum, plan) => sum + plan.evidence_items.length,
    0
  );

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 text-gray-900 dark:text-white">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <span className="ml-4 text-lg">Loading systems with evidence plans...</span>
        </div>
      </div>
    );
  }

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
    <div className="max-w-6xl mx-auto p-6 text-gray-900 dark:text-white">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
          <span className="text-purple-600 dark:text-purple-400">DPV</span>
          Evidence Plans
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Data Privacy Vocabulary (DPV) based evidence requirements for AI systems compliance.
          Select a system with an evidence plan to view its required evidence items.
        </p>
      </div>

      {/* System Selector */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <label className="block mb-3 text-lg font-medium">Select a system:</label>

        {systems.length === 0 ? (
          <div className="text-center py-4 text-gray-500 dark:text-gray-400">
            <p className="mb-2">No systems with evidence plans found.</p>
            <p className="text-sm">
              Generate evidence plans from the Systems page (DPV Plan button) or run forensic analysis with evidence plan enabled.
            </p>
          </div>
        ) : (
          <select
            value={selectedSystemUrn}
            onChange={(e) => handleSelectionChange(e.target.value)}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">-- Select a system --</option>
            {systems.filter(s => s.source === "manual").length > 0 && (
              <optgroup label="Manual Systems">
                {systems.filter(s => s.source === "manual").map((sys) => (
                  <option key={sys.urn} value={sys.urn}>
                    {sys.hasName} ({(sys.hasRiskLevel || "Unknown").replace("ai:", "")} - {sys.evidence_plan?.total_gaps || 0} requirements)
                  </option>
                ))}
              </optgroup>
            )}
            {systems.filter(s => s.source === "forensic").length > 0 && (
              <optgroup label="Forensic Analyzed Systems">
                {systems.filter(s => s.source === "forensic").map((sys) => (
                  <option key={sys.urn} value={sys.urn}>
                    {sys.hasName} ({(sys.hasRiskLevel || "Unknown").replace("ai:", "")} - {sys.evidence_plan?.total_gaps || 0} gaps)
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        )}

        {/* Selected system preview */}
        {selectedSystem && (
          <div className={`mt-4 p-4 rounded-lg border ${
            selectedSystem.source === "manual"
              ? "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700"
              : "bg-purple-50 dark:bg-purple-900/30 border-purple-200 dark:border-purple-700"
          }`}>
            <div className="flex items-center mb-2">
              <span className="mr-2">{selectedSystem.source === "manual" ? "📝" : "🔬"}</span>
              <h4 className={`font-medium ${
                selectedSystem.source === "manual"
                  ? "text-green-700 dark:text-green-300"
                  : "text-purple-700 dark:text-purple-300"
              }`}>
                {selectedSystem.source === "manual" ? "Manual System" : "Forensic Analyzed System"}
              </h4>
            </div>
            <p className="text-gray-700 dark:text-gray-300">
              <strong>Name:</strong> {selectedSystem.hasName}
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <strong>Organization:</strong> {selectedSystem.hasOrganization}
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <strong>Risk Level:</strong>{" "}
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                (selectedSystem.hasRiskLevel || "").includes("High")
                  ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  : (selectedSystem.hasRiskLevel || "").includes("Limited")
                  ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                  : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
              }`}>
                {(selectedSystem.hasRiskLevel || "Unknown").replace("ai:", "")}
              </span>
            </p>
            {selectedSystem.evidence_plan && (
              <p className="text-gray-700 dark:text-gray-300">
                <strong>Compliance Gaps:</strong> {selectedSystem.evidence_plan.total_gaps}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Evidence Plan Details */}
      <div>
          {!selectedSystem ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
              <div className="text-gray-400 dark:text-gray-500 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400">
                Select a system to view its evidence plan
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Choose a system from the left panel to see the required evidence items for compliance.
              </p>
            </div>
          ) : !selectedSystem.evidence_plan ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
              <p className="text-gray-600 dark:text-gray-400">
                This system does not have an evidence plan.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* System Summary */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-bold">{selectedSystem.hasName}</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Plan generated: {new Date(selectedSystem.evidence_plan.generated_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={expandAll}
                      className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      Expand All
                    </button>
                    <button
                      onClick={collapseAll}
                      className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      Collapse All
                    </button>
                  </div>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {selectedSystem.evidence_plan.total_gaps}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Compliance Gaps</p>
                  </div>
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {selectedSystem.evidence_plan.summary?.total_evidence_items || 0}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Evidence Items</p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                      {selectedSystem.evidence_plan.summary?.by_priority?.CRITICAL || 0}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Critical Items</p>
                  </div>
                  <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                      {selectedSystem.evidence_plan.summary?.by_priority?.HIGH || 0}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">High Priority</p>
                  </div>
                </div>

                {/* Recommendations */}
                {selectedSystem.evidence_plan.recommendations && selectedSystem.evidence_plan.recommendations.length > 0 && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
                    <h4 className="font-semibold text-amber-800 dark:text-amber-400 mb-2">
                      Recommendations
                    </h4>
                    <ul className="list-disc list-inside text-sm text-amber-700 dark:text-amber-300 space-y-1">
                      {selectedSystem.evidence_plan.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Filters */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Search</label>
                    <input
                      type="text"
                      placeholder="Search evidence..."
                      value={searchFilter}
                      onChange={(e) => setSearchFilter(e.target.value)}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Priority</label>
                    <select
                      value={priorityFilter}
                      onChange={(e) => setPriorityFilter(e.target.value)}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-sm"
                    >
                      <option value="">All Priorities</option>
                      {filterOptions.priorities.map((p) => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Evidence Type</label>
                    <select
                      value={typeFilter}
                      onChange={(e) => setTypeFilter(e.target.value)}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-sm"
                    >
                      <option value="">All Types</option>
                      {filterOptions.types.map((t) => (
                        <option key={t} value={t}>{t.replace("Evidence", "")}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Responsible Role</label>
                    <select
                      value={roleFilter}
                      onChange={(e) => setRoleFilter(e.target.value)}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-700 text-sm"
                    >
                      <option value="">All Roles</option>
                      {filterOptions.roles.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="mt-3 flex justify-between items-center">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    Showing {totalFilteredItems} evidence items in {filteredRequirementPlans.length} requirements
                  </span>
                  <button
                    onClick={() => {
                      setSearchFilter("");
                      setPriorityFilter("");
                      setTypeFilter("");
                      setRoleFilter("");
                    }}
                    className="text-sm text-purple-600 dark:text-purple-400 hover:underline"
                  >
                    Clear Filters
                  </button>
                </div>
              </div>

              {/* Evidence Items by Requirement */}
              <div className="space-y-4">
                {filteredRequirementPlans.map((plan, planIdx) => {
                  const isExpanded = expandedRequirements.has(plan.requirement_uri);

                  return (
                    <div
                      key={plan.requirement_uri || `plan-${planIdx}`}
                      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                    >
                      {/* Requirement Header */}
                      <button
                        onClick={() => toggleRequirement(plan.requirement_uri)}
                        className="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <svg
                            className={`w-5 h-5 transform transition-transform ${isExpanded ? "rotate-90" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                          <div className="text-left">
                            <span className="font-semibold">{plan.requirement_label || "Unknown Requirement"}</span>
                            {plan.article_reference && (
                              <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                                ({plan.article_reference})
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColors[plan.priority] || "bg-gray-100"}`}>
                            {plan.priority || "N/A"}
                          </span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {plan.evidence_items.length} items
                          </span>
                          {plan.deadline_recommendation && (
                            <span className="text-xs text-gray-400 dark:text-gray-500">
                              {plan.deadline_recommendation}
                            </span>
                          )}
                        </div>
                      </button>

                      {/* Evidence Items List */}
                      {isExpanded && (
                        <div className="border-t border-gray-200 dark:border-gray-700">
                          {/* DPV Measures */}
                          {plan.dpv_measures && plan.dpv_measures.length > 0 && (
                            <div className="px-4 py-2 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">DPV Measures: </span>
                              {plan.dpv_measures.map((m, idx) => (
                                <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 mr-1">
                                  {m}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Evidence Items */}
                          <div className="divide-y divide-gray-100 dark:divide-gray-700">
                            {plan.evidence_items.map((item, itemIdx) => (
                              <div key={item.id || `item-${itemIdx}`} className="px-4 py-4">
                                <div className="flex justify-between items-start mb-2">
                                  <div>
                                    <span className="font-mono text-sm text-purple-600 dark:text-purple-400 mr-2">
                                      {item.id || "N/A"}
                                    </span>
                                    <span className="font-medium">{item.name || "Unnamed Evidence"}</span>
                                  </div>
                                  <div className="flex gap-2">
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColors[item.priority] || "bg-gray-100"}`}>
                                      {item.priority || "N/A"}
                                    </span>
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${typeColors[item.evidence_type] || "bg-gray-100"}`}>
                                      {(item.evidence_type || "Unknown").replace("Evidence", "")}
                                    </span>
                                  </div>
                                </div>

                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                  {item.description || "No description available"}
                                </p>

                                <div className="flex flex-wrap gap-4 text-xs">
                                  <div className="flex items-center gap-1">
                                    <span className="text-gray-500 dark:text-gray-400">Responsible:</span>
                                    <span className={`px-2 py-0.5 rounded font-medium ${roleColors[item.responsible_role] || "bg-gray-100"}`}>
                                      {item.responsible_role || "N/A"}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <span className="text-gray-500 dark:text-gray-400">Frequency:</span>
                                    <span className="font-medium">{item.frequency || "N/A"}</span>
                                  </div>
                                  {item.dpv_measure && (
                                    <div className="flex items-center gap-1">
                                      <span className="text-gray-500 dark:text-gray-400">DPV:</span>
                                      <span className="font-mono text-purple-600 dark:text-purple-400">
                                        {item.dpv_measure}
                                      </span>
                                    </div>
                                  )}
                                </div>

                                {item.guidance && (
                                  <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm text-blue-700 dark:text-blue-300">
                                    <span className="font-medium">Guidance: </span>
                                    {item.guidance}
                                  </div>
                                )}

                                {item.templates && item.templates.length > 0 && (
                                  <div className="mt-2 flex items-center gap-2">
                                    <span className="text-xs text-gray-500 dark:text-gray-400">Templates:</span>
                                    {item.templates.map((t, idx) => (
                                      <span key={idx} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">
                                        {t}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {filteredRequirementPlans.length === 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
                  <p className="text-gray-500 dark:text-gray-400">
                    No evidence items match the current filters.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
    </div>
  );
}
