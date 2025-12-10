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
  hasAlgorithmType: string[];
  hasModelScale?: string[];
  hasCapability?: string[];
  hasActivatedCriterion?: string[];
  hasManuallyIdentifiedCriterion?: string[];
  hasCapabilityMetric?: string[];
  parameterCount?: number;
  autonomyLevel?: string;
  isGenerallyApplicable?: boolean;
  hasGPAIClassification?: string[];
  hasContextualCriteria?: string[];
  hasISORequirements?: string[];
  hasComplianceRequirement?: string[];
  hasTechnicalRequirement?: string[];
  hasSecurityRequirement?: string[];
  hasRobustnessRequirement?: string[];
  hasDocumentationRequirement?: string[];
  hasDataGovernanceRequirement?: string[];
  requiresHumanOversight?: boolean;
  hasTransparencyLevel?: string;
  requiresFundamentalRightsAssessment?: boolean;
  hasVersion: string;
  "ai:hasUrn": string;
  // AIRO stakeholder fields (Art. 3.3-3.4 EU AI Act)
  hasProvider?: string;
  hasDeployer?: string;
  hasDeveloper?: string;
  hasUser?: string;
  hasSubject?: string;
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

  const [showValidation, setShowValidation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    identification: true,
    purposes: true,
    deployment: true,
    technical: true,
    capabilities: true,
  });

  const [purposes, setPurposes] = useState<{ id: string; label: string }[]>([]);
  const [risks, setRisks] = useState<{ id: string; label: string }[]>([]);
  const [contexts, setContexts] = useState<{ id: string; label: string }[]>([]);
  const [origins, setOrigins] = useState<{ id: string; label: string }[]>([]);
  const [systemCapabilityCriteria, setSystemCapabilityCriteria] = useState<{ id: string; label: string }[]>([]);
  const [algorithmTypes, setAlgorithmTypes] = useState<{ id: string; label: string }[]>([]);
  const [modelScales, setModelScales] = useState<{ id: string; label: string }[]>([]);
  const [capabilities, setCapabilities] = useState<{ id: string; label: string }[]>([]);
  const [gpaiClassifications, setGPAIClassifications] = useState<{ id: string; label: string }[]>([]);
  const [contextualCriteria, setContextualCriteria] = useState<{ id: string; label: string }[]>([]);
  const [isoRequirements, setISORequirements] = useState<{ id: string; label: string }[]>([]);
  const [complianceRequirements, setComplianceRequirements] = useState<{ id: string; label: string }[]>([]);
  const [technicalRequirements, setTechnicalRequirements] = useState<{ id: string; label: string }[]>([]);
  const [securityRequirements, setSecurityRequirements] = useState<{ id: string; label: string }[]>([]);
  const [robustnessRequirements, setRobustnessRequirements] = useState<{ id: string; label: string }[]>([]);
  const [documentationRequirements, setDocumentationRequirements] = useState<{ id: string; label: string }[]>([]);
  const [dataGovernanceRequirements, setDataGovernanceRequirements] = useState<{ id: string; label: string }[]>([]);
  const [transparencyLevels, setTransparencyLevels] = useState<{ id: string; label: string }[]>([]);

  const [form, setForm] = useState({
    hasName: "",
    hasPurpose: [] as string[],
    hasDeploymentContext: [] as string[],
    hasTrainingDataOrigin: [] as string[],
    hasAlgorithmType: [] as string[],
    hasModelScale: [] as string[],
    hasCapability: [] as string[],
    hasActivatedCriterion: [] as string[],
    hasManuallyIdentifiedCriterion: [] as string[],
    hasCapabilityMetric: [] as string[],
    parameterCount: undefined as number | undefined,
    autonomyLevel: "" as string,
    isGenerallyApplicable: false as boolean,
    hasGPAIClassification: [] as string[],
    hasContextualCriteria: [] as string[],
    hasISORequirements: [] as string[],
    hasComplianceRequirement: [] as string[],
    hasTechnicalRequirement: [] as string[],
    hasSecurityRequirement: [] as string[],
    hasRobustnessRequirement: [] as string[],
    hasDocumentationRequirement: [] as string[],
    hasDataGovernanceRequirement: [] as string[],
    requiresHumanOversight: false as boolean,
    hasTransparencyLevel: "" as string,
    requiresFundamentalRightsAssessment: false as boolean,
    hasVersion: "",
    // AIRO stakeholder fields
    hasProvider: "" as string,
    hasDeployer: "" as string,
    hasDeveloper: "" as string,
    hasUser: "" as string,
    hasSubject: "" as string,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!form.hasName.trim()) {
      setShowValidation(true);
      setSubmitError("System name is required");
      return;
    }

    if (form.hasPurpose.length === 0) {
      setShowValidation(true);
      setSubmitError("At least one purpose is required");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

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

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `${isModifying ? 'Modify' : 'Create'} failed`);
      }

      // Clear form, loaded system, and algorithm type/subtypes selection
      setForm({
        hasName: "",
        hasPurpose: [],
        hasDeploymentContext: [],
        hasTrainingDataOrigin: [],
        hasAlgorithmType: [],
        hasModelScale: [],
        hasCapability: [],
        hasActivatedCriterion: [],
        hasManuallyIdentifiedCriterion: [],
        hasCapabilityMetric: [],
        parameterCount: undefined,
        autonomyLevel: "",
        isGenerallyApplicable: false,
        hasGPAIClassification: [],
        hasContextualCriteria: [],
        hasISORequirements: [],
        hasComplianceRequirement: [],
        hasTechnicalRequirement: [],
        hasSecurityRequirement: [],
        hasRobustnessRequirement: [],
        hasDocumentationRequirement: [],
        hasDataGovernanceRequirement: [],
        requiresHumanOversight: false,
        hasTransparencyLevel: "",
        requiresFundamentalRightsAssessment: false,
        hasVersion: "",
        hasProvider: "",
        hasDeployer: "",
        hasDeveloper: "",
        hasUser: "",
        hasSubject: "",
      });
      setLoadedSystem(null);
      setShowValidation(false);
      setSubmitSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => setSubmitSuccess(false), 3000);

      await loadSystems(0);
      setOffset(0);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error occurred";
      console.error(`Error ${loadedSystem ? 'modifying' : 'creating'} system:`, err);
      setSubmitError(errorMsg);
    } finally {
      setIsSubmitting(false);
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
        hasAlgorithmType: systemToLoad.hasAlgorithmType || [],
        hasModelScale: systemToLoad.hasModelScale || [],
        hasCapability: systemToLoad.hasCapability || [],
        hasActivatedCriterion: systemToLoad.hasActivatedCriterion || [],
        hasManuallyIdentifiedCriterion: systemToLoad.hasManuallyIdentifiedCriterion || [],
        hasCapabilityMetric: systemToLoad.hasCapabilityMetric || [],
        parameterCount: systemToLoad.parameterCount,
        autonomyLevel: systemToLoad.autonomyLevel || "",
        isGenerallyApplicable: systemToLoad.isGenerallyApplicable ?? false,
        hasGPAIClassification: systemToLoad.hasGPAIClassification || [],
        hasContextualCriteria: systemToLoad.hasContextualCriteria || [],
        hasISORequirements: systemToLoad.hasISORequirements || [],
        hasComplianceRequirement: systemToLoad.hasComplianceRequirement || [],
        hasTechnicalRequirement: systemToLoad.hasTechnicalRequirement || [],
        hasSecurityRequirement: systemToLoad.hasSecurityRequirement || [],
        hasRobustnessRequirement: systemToLoad.hasRobustnessRequirement || [],
        hasDocumentationRequirement: systemToLoad.hasDocumentationRequirement || [],
        hasDataGovernanceRequirement: systemToLoad.hasDataGovernanceRequirement || [],
        requiresHumanOversight: systemToLoad.requiresHumanOversight ?? false,
        hasTransparencyLevel: systemToLoad.hasTransparencyLevel || "",
        requiresFundamentalRightsAssessment: systemToLoad.requiresFundamentalRightsAssessment ?? false,
        hasVersion: systemToLoad.hasVersion,
        hasProvider: systemToLoad.hasProvider || "",
        hasDeployer: systemToLoad.hasDeployer || "",
        hasDeveloper: systemToLoad.hasDeveloper || "",
        hasUser: systemToLoad.hasUser || "",
        hasSubject: systemToLoad.hasSubject || "",
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
      const apiBase = (window as any).VITE_API_URL || "http://localhost:8000";
      const [
        purposesData,
        risksData,
        contextsData,
        originsData,
        systemCapabilityCriteriaData,
        algorithmTypesData,
        modelScalesData,
        capabilitiesData,
        gpaiClassificationsData,
        contextualCriteriaData,
        isoRequirementsData,
        complianceRequirementsData,
        technicalRequirementsData,
        securityRequirementsData,
        robustnessRequirementsData,
        documentationRequirementsData,
        dataGovernanceRequirementsData,
        transparencyLevelsData
      ] = await Promise.all([
        fetchVocabulary("purposes"),
        fetchVocabulary("risks"),
        fetchVocabulary("contexts"),
        fetchVocabulary("training_origins"),
        fetchVocabulary("system_capability_criteria"),
        fetch(`${apiBase}/vocab/algorithmtypes?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:NeuralNetwork", "label": "Neural Network"},
          {"id": "ai:TransformerModel", "label": "Transformer Model"},
          {"id": "ai:DecisionTree", "label": "Decision Tree"},
          {"id": "ai:BayesianModel", "label": "Bayesian Model"}
        ]),
        fetch(`${apiBase}/vocab/modelscales?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:FoundationModelScale", "label": "Foundation Model Scale"}
        ]),
        fetch(`${apiBase}/vocab/capabilities?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:GenerativeCapability", "label": "Generative Capability"}
        ]),
        fetch(`${apiBase}/vocab/gpai?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:GeneralPurposeAIModel", "label": "General Purpose AI"},
          {"id": "ai:HighCapabilityGPAIModel", "label": "High Capability GPAI"}
        ]),
        fetch(`${apiBase}/vocab/contextualcriteria?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/iso?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/compliance?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/technical?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/security?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/robustness?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/documentation?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/datagovernance?lang=en`).then(r => r.json()).catch(() => []),
        fetch(`${apiBase}/vocab/transparency?lang=en`).then(r => r.json()).catch(() => [
          {"id": "ai:High", "label": "High"},
          {"id": "ai:Medium", "label": "Medium"},
          {"id": "ai:Low", "label": "Low"}
        ]),
      ]);
      setPurposes(purposesData);
      setRisks(risksData);
      setContexts(contextsData);
      setOrigins(originsData);
      setSystemCapabilityCriteria(systemCapabilityCriteriaData);
      setAlgorithmTypes(algorithmTypesData);
      setModelScales(modelScalesData);
      setCapabilities(capabilitiesData);
      setGPAIClassifications(gpaiClassificationsData);
      setContextualCriteria(contextualCriteriaData);
      setISORequirements(isoRequirementsData);
      setComplianceRequirements(complianceRequirementsData);
      setTechnicalRequirements(technicalRequirementsData);
      setSecurityRequirements(securityRequirementsData);
      setRobustnessRequirements(robustnessRequirementsData);
      setDocumentationRequirements(documentationRequirementsData);
      setDataGovernanceRequirements(dataGovernanceRequirementsData);
      setTransparencyLevels(transparencyLevelsData);
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
      <form
        onSubmit={handleSubmit}
        className="space-y-6 mb-12"
      >
        {/* SECTION 1: Basic Information - COLLAPSIBLE */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <button
            type="button"
            onClick={() => setExpandedSections({ ...expandedSections, identification: !expandedSections.identification })}
            className="w-full flex items-center justify-between hover:opacity-80 transition-opacity"
          >
            <div className="flex items-center">
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 mr-3">📋</span>
              <h2 className="text-xl font-bold">System Identification</h2>
            </div>
            <span className="text-xl">{expandedSections.identification ? '▼' : '▶'}</span>
          </button>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Basic information about your AI system</p>

          {expandedSections.identification && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block font-semibold">System Name *</label>
                  <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="A unique identifier for your AI system">ℹ️</span>
                </div>
                <input
                  className={`w-full border rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                    showValidation && !form.hasName ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  placeholder="e.g., EduAssess-AI, BiometricAccess-System"
                  value={form.hasName}
                  onChange={(e) => setForm({ ...form, hasName: e.target.value })}
                />
                {showValidation && !form.hasName && (
                  <p className="text-red-500 text-xs mt-1">System name is required</p>
                )}
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block font-semibold">Version</label>
                  <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="System version (optional)">ℹ️</span>
                </div>
                <input
                  className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 1.0.0"
                  value={form.hasVersion}
                  onChange={(e) => setForm({ ...form, hasVersion: e.target.value })}
                />
              </div>
            </div>
          )}
        </div>

        {/* SECTION 1: Purposes - COLLAPSIBLE */}
        <div className="bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700 p-6 mb-6">
          <button
            type="button"
            onClick={() => setExpandedSections({ ...expandedSections, purposes: !expandedSections.purposes })}
            className="w-full flex items-center justify-between hover:opacity-80 transition-opacity mb-3"
          >
            <div className="flex items-center">
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 mr-3">🎯</span>
              <h2 className="text-xl font-bold">1. System Purposes</h2>
            </div>
            <span className="text-xl">{expandedSections.purposes ? '▼' : '▶'}</span>
          </button>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">What is this AI system designed to do? Select all applicable primary functions.</p>

          {expandedSections.purposes && (
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">Primary Purpose(s) *</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Select the primary business function(s) of your AI system according to EU AI Act">ℹ️</span>
              </div>
              <select
                multiple
                size={6}
                className={`w-full border rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                  showValidation && form.hasPurpose.length === 0 ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'
                }`}
                value={form.hasPurpose}
                onChange={e =>
                  setForm({ ...form, hasPurpose: Array.from(e.target.selectedOptions, (opt) => opt.value) })
                }
              >
                {purposes.map((p) => (
                  <option key={p.id} value={p.id}>{p.label}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">💡 Hold Ctrl/Cmd to select multiple</p>
              {showValidation && form.hasPurpose.length === 0 && (
                <p className="text-red-500 text-xs mt-1">At least one purpose is required</p>
              )}
            </div>
          )}
        </div>

        {/* SECTION 2: Deployment Context */}
        <div className="bg-purple-50 dark:bg-purple-900 rounded-lg border border-purple-200 dark:border-purple-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-purple-600 dark:text-purple-400 mr-3">📍</span>
            <h2 className="text-xl font-bold">2. Deployment Context</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">Where and how will this system be used? These contexts trigger specific regulatory requirements.</p>
          <div className="bg-white dark:bg-gray-800 rounded p-4">
            <label className="block font-semibold mb-2">Deployment Context(s) *</label>
            <select
              multiple
              size={5}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
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
        </div>

        {/* SECTION 3: Technical Factors */}
        <div className="bg-orange-50 dark:bg-orange-900 rounded-lg border border-orange-200 dark:border-orange-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-orange-600 dark:text-orange-400 mr-3">⚙️</span>
            <h2 className="text-xl font-bold">3. Technical Factors</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">Technical characteristics of your AI system that impact risk assessment.</p>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <label className="block font-semibold mb-2">Algorithm Type(s)</label>
              <select
                multiple
                size={4}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                value={form.hasAlgorithmType}
                onChange={e => {
                  const values = Array.from(e.target.selectedOptions, (opt) => opt.value);
                  setForm({ ...form, hasAlgorithmType: values });
                }}
              >
                {algorithmTypes.map((a) => (
                  <option key={a.id} value={a.id}>{a.label}</option>
                ))}
              </select>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <label className="block font-semibold mb-2">Model Scale</label>
              <select
                multiple
                size={4}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                value={form.hasModelScale}
                onChange={e =>
                  setForm({ ...form, hasModelScale: Array.from(e.target.selectedOptions, (opt) => opt.value) })
                }
              >
                {modelScales.map((m) => (
                  <option key={m.id} value={m.id}>{m.label}</option>
                ))}
              </select>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <label className="block font-semibold mb-2">Training Data Origin(s) *</label>
              <select
                multiple
                size={4}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
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
          </div>
        </div>

        {/* SECTION 4: System Capabilities */}
        <div className="bg-green-50 dark:bg-green-900 rounded-lg border border-green-200 dark:border-green-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-green-600 dark:text-green-400 mr-3">🚀</span>
            <h2 className="text-xl font-bold">4. System Capabilities</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">What specific capabilities does your system have? These may trigger additional compliance requirements.</p>
          <div className="bg-white dark:bg-gray-800 rounded p-4">
            <label className="block font-semibold mb-2">Specific Capabilities</label>
            <select
              multiple
              size={5}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              value={form.hasCapability}
              onChange={e =>
                setForm({ ...form, hasCapability: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {capabilities.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* SECTION 5: System Capability Metrics (Articles 51-55 GPAI Indicators) */}
        <div className="bg-purple-50 dark:bg-purple-900 rounded-lg border border-purple-200 dark:border-purple-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-purple-600 dark:text-purple-400 mr-3">📊</span>
            <h2 className="text-xl font-bold">5. Capability Metrics (GPAI Classification Indicators)</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
            Technical metrics that may trigger GPAI (General Purpose AI) classification under Articles 51-55 of the EU AI Act.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <label className="block font-semibold mb-2">Parameter Count (Model Size)</label>
              <input
                type="number"
                placeholder="e.g., 7000000000 for 7B parameters"
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                value={form.parameterCount || ""}
                onChange={e => {
                  const val = e.target.value ? parseInt(e.target.value) : undefined;
                  setForm({ ...form, parameterCount: val });
                }}
              />
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Models with &gt;10B parameters are high-capability indicators</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <label className="block font-semibold mb-2">Autonomy Level</label>
              <select
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                value={form.autonomyLevel}
                onChange={e => setForm({ ...form, autonomyLevel: e.target.value })}
              >
                <option value="">Select autonomy level...</option>
                <option value="NoAutonomy">No Autonomy (Human-controlled)</option>
                <option value="LimitedAutonomy">Limited Autonomy (Human-in-loop)</option>
                <option value="HighAutonomy">High Autonomy (Minimal human intervention)</option>
                <option value="FullyAutonomous">Fully Autonomous (Systemic risk indicator)</option>
              </select>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4 md:col-span-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={form.isGenerallyApplicable}
                  onChange={e => setForm({ ...form, isGenerallyApplicable: e.target.checked })}
                  className="mr-3 w-4 h-4 border border-gray-300 dark:border-gray-600 rounded bg-white text-purple-600 focus:ring-2 focus:ring-purple-500"
                />
                <span className="font-semibold">Generally Applicable to Multiple Domains (Broad Impact Indicator)</span>
              </label>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Check if your system can be adapted to multiple use cases or domains without major retraining</p>
            </div>
          </div>
        </div>

        {/* SECTION 6: Expert Evaluation - Manually Identified Criteria */}
        <div className="bg-indigo-50 dark:bg-indigo-900 rounded-lg border border-indigo-200 dark:border-indigo-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mr-3">👨‍⚖️</span>
            <h2 className="text-xl font-bold">6. Expert Evaluation - Additional Risk Criteria</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
            Manually identified criteria by experts for residual high-risk cases not covered by automated rules (Article 6(3) of EU AI Act).
            These criteria are identified beyond what is automatically derived from Purpose/DeploymentContext.
          </p>
          <div className="bg-white dark:bg-gray-800 rounded p-4">
            <label className="block font-semibold mb-2">Additional Risk Criteria (Manually Identified)</label>
            <select
              multiple
              size={6}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.hasManuallyIdentifiedCriterion}
              onChange={e =>
                setForm({ ...form, hasManuallyIdentifiedCriterion: Array.from(e.target.selectedOptions, (opt) => opt.value) })
              }
            >
              {systemCapabilityCriteria.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
              These criteria apply when expert evaluation identifies additional high-risk factors beyond the system's primary purpose or deployment context.
            </p>
          </div>
        </div>

        {/* SECTION 7: AIRO Stakeholders */}
        <div className="bg-teal-50 dark:bg-teal-900 rounded-lg border border-teal-200 dark:border-teal-700 p-6 mb-6">
          <div className="flex items-center mb-4">
            <span className="text-2xl font-bold text-teal-600 dark:text-teal-400 mr-3">👥</span>
            <h2 className="text-xl font-bold">7. AIRO Stakeholders (EU AI Act Art. 3)</h2>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
            Identify the key stakeholders involved with this AI system according to AIRO (AI Risk Ontology) aligned with EU AI Act definitions.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">Provider (Art. 3.3)</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Entity that develops or has an AI system developed and places it on the market or puts it into service under its own name or trademark">ℹ️</span>
              </div>
              <input
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., OpenAI, Google DeepMind"
                value={form.hasProvider}
                onChange={(e) => setForm({ ...form, hasProvider: e.target.value })}
              />
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">Deployer (Art. 3.4)</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Entity that uses an AI system under its authority, except where the AI system is used in the course of a personal non-professional activity">ℹ️</span>
              </div>
              <input
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., Company deploying the system"
                value={form.hasDeployer}
                onChange={(e) => setForm({ ...form, hasDeployer: e.target.value })}
              />
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">Developer</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Entity that developed the AI system (may differ from provider)">ℹ️</span>
              </div>
              <input
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., Research lab, contractor"
                value={form.hasDeveloper}
                onChange={(e) => setForm({ ...form, hasDeveloper: e.target.value })}
              />
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">User</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Natural person who interacts with the AI system">ℹ️</span>
              </div>
              <input
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., End users, operators"
                value={form.hasUser}
                onChange={(e) => setForm({ ...form, hasUser: e.target.value })}
              />
            </div>
            <div className="bg-white dark:bg-gray-800 rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block font-semibold">Affected Person (Art. 86)</label>
                <span className="text-xs text-gray-500 dark:text-gray-400 cursor-help" title="Natural person subject to a decision taken by the deployer on the basis of the output from a high-risk AI system, or whose fundamental rights are affected by such system">ℹ️</span>
              </div>
              <input
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white text-black dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., Job applicants, loan applicants, citizens"
                value={form.hasSubject}
                onChange={(e) => setForm({ ...form, hasSubject: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Derived Classifications - Read-only Info Panel */}
        {(form.hasGPAIClassification.length > 0 || form.hasContextualCriteria.length > 0) && (
          <div className="border-t pt-4 mt-4 mb-4 bg-blue-50 dark:bg-blue-900 rounded p-4">
            <h3 className="text-sm font-bold mb-2 text-blue-900 dark:text-blue-100">System Classifications (Auto-derived)</h3>
            <p className="text-xs text-blue-800 dark:text-blue-200 mb-3">These are automatically derived from your technical characteristics and deployment context above:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {form.hasGPAIClassification.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-blue-900 dark:text-blue-100 mb-1">GPAI Classification:</p>
                  <p className="text-sm text-blue-800 dark:text-blue-200">{form.hasGPAIClassification.map(g => g.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
              {form.hasContextualCriteria.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-blue-900 dark:text-blue-100 mb-1">Contextual Criteria:</p>
                  <p className="text-sm text-blue-800 dark:text-blue-200">{form.hasContextualCriteria.map(c => c.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {submitError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{submitError}</p>
            </div>
          )}
          {submitSuccess && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              <p className="font-semibold">✓ Success</p>
              <p className="text-sm">{loadedSystem ? 'System modified successfully' : 'System created successfully'}</p>
            </div>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed font-semibold transition-colors"
          >
            {isSubmitting ? (
              <>
                <span className="inline-block mr-2">⏳</span>
                {loadedSystem ? 'Modifying System...' : 'Creating System...'}
              </>
            ) : (
              <>
                <span className="inline-block mr-2">💾</span>
                {loadedSystem ? 'Modify System' : 'Create System'}
              </>
            )}
          </button>
        </div>
        {loadedSystem && (
          <button
            type="button"
            onClick={() => {
              setForm({
                hasName: "",
                hasPurpose: [],
                hasDeploymentContext: [],
                hasTrainingDataOrigin: [],
                hasAlgorithmType: [],
                hasModelScale: [],
                hasCapability: [],
                hasActivatedCriterion: [],
                hasManuallyIdentifiedCriterion: [],
                hasCapabilityMetric: [],
                parameterCount: undefined,
                autonomyLevel: "",
                isGenerallyApplicable: false,
                hasGPAIClassification: [],
                hasContextualCriteria: [],
                hasISORequirements: [],
                hasComplianceRequirement: [],
                hasTechnicalRequirement: [],
                hasSecurityRequirement: [],
                hasRobustnessRequirement: [],
                hasDocumentationRequirement: [],
                hasDataGovernanceRequirement: [],
                requiresHumanOversight: false,
                hasTransparencyLevel: "",
                requiresFundamentalRightsAssessment: false,
                hasVersion: "",
                hasProvider: "",
                hasDeployer: "",
                hasDeveloper: "",
                hasUser: "",
                hasSubject: "",
              });
              setLoadedSystem(null);
            }}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 ml-2"
          >
            Clear Form
          </button>
        )}
      </form>

      {/* System Card Preview */}
      {form.hasName && (
        <div className="border-t pt-6 mt-6 mb-6">
          <h3 className="text-lg font-bold mb-4">System Preview</h3>
          <SystemCard
            name={form.hasName}
            riskLevel="To be determined"
            purpose={form.hasPurpose.map(p => purposes.find(pr => pr.id === p)?.label || p)}
            deploymentContext={form.hasDeploymentContext.map(d => contexts.find(c => c.id === d)?.label || d)}
            trainingDataOrigin={form.hasTrainingDataOrigin.map(o => origins.find(org => org.id === o)?.label || o)}
            algorithmType={form.hasAlgorithmType.map(a => algorithmTypes.find(at => at.id === a)?.label || a)}
            modelScale={form.hasModelScale.map(m => modelScales.find(ms => ms.id === m)?.label || m)}
            capabilities={form.hasCapability.map(c => capabilities.find(cap => cap.id === c)?.label || c)}
            gpaiClassification={form.hasGPAIClassification.map(g => gpaiClassifications.find(gp => gp.id === g)?.label || g)}
            contextualCriteria={form.hasContextualCriteria.map(cc => contextualCriteria.find(c => c.id === cc)?.label || cc)}
            isoRequirements={form.hasISORequirements.map(i => isoRequirements.find(ir => ir.id === i)?.label || i)}
            complianceRequirements={form.hasComplianceRequirement.map(c => complianceRequirements.find(cr => cr.id === c)?.label || c)}
            technicalRequirements={form.hasTechnicalRequirement.map(t => technicalRequirements.find(tr => tr.id === t)?.label || t)}
            securityRequirements={form.hasSecurityRequirement.map(s => securityRequirements.find(sr => sr.id === s)?.label || s)}
            robustnessRequirements={form.hasRobustnessRequirement.map(r => robustnessRequirements.find(rr => rr.id === r)?.label || r)}
            documentationRequirements={form.hasDocumentationRequirement.map(d => documentationRequirements.find(dr => dr.id === d)?.label || d)}
            dataGovernanceRequirements={form.hasDataGovernanceRequirement.map(dg => dataGovernanceRequirements.find(dgr => dgr.id === dg)?.label || dg)}
            humanOversightRequired={form.requiresHumanOversight}
            transparencyLevel={form.hasTransparencyLevel ? transparencyLevels.find(t => t.id === form.hasTransparencyLevel)?.label : undefined}
            fundamentalRightsAssessment={form.requiresFundamentalRightsAssessment}
            version={form.hasVersion || "0.0.0"}
            urn={loadedSystem?.["ai:hasUrn"] || "urn:uuid:new-system"}
          />
        </div>
      )}

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
              <th className="p-2 text-left w-[50%]">Name</th>
              <th className="p-2 text-left w-[20%]">Version</th>
              <th className="p-2 text-left w-[30%]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <tr key={s["@id"]} className="border-t dark:border-gray-700">
                <td className="p-2 truncate" title={s.hasName}>{s.hasName}</td>
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
