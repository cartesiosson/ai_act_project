interface SystemCardProps {
  name: string;
  riskLevel: string;
  purpose: string[];
  deploymentContext: string[];
  trainingDataOrigin: string[];
  algorithmType: string[];
  modelScale?: string[];
  systemCapabilityCriteria?: string[];
  capabilities?: string[];
  gpaiClassification?: string[];
  contextualCriteria?: string[];
  isoRequirements?: string[];
  nistRequirements?: string[];
  complianceRequirements?: string[];
  technicalRequirements?: string[];
  securityRequirements?: string[];
  robustnessRequirements?: string[];
  documentationRequirements?: string[];
  dataGovernanceRequirements?: string[];
  humanOversightRequired?: boolean;
  transparencyLevel?: string;
  fundamentalRightsAssessment?: boolean;
  version: string;
  urn: string;
}

export default function SystemCard({
  name,
  riskLevel,
  purpose,
  deploymentContext,
  trainingDataOrigin,
  algorithmType,
  modelScale,
  systemCapabilityCriteria,
  capabilities,
  gpaiClassification,
  contextualCriteria,
  isoRequirements,
  nistRequirements,
  complianceRequirements,
  technicalRequirements,
  securityRequirements,
  robustnessRequirements,
  documentationRequirements,
  dataGovernanceRequirements,
  humanOversightRequired,
  transparencyLevel,
  fundamentalRightsAssessment,
  version,
  urn,
}: SystemCardProps) {
  const renderField = (label: string, values?: string[]) => {
    if (!values || values.length === 0) return null;
    return (
      <p className="text-sm">
        <span className="font-semibold">{label}:</span> {values.map(v => v.replace(/^ai:/, '')).join(", ")}
      </p>
    );
  };

  return (
    <div className="border p-4 rounded shadow bg-white dark:bg-gray-800">
      {/* Header */}
      <div className="border-b pb-3 mb-3">
        <h3 className="text-lg font-bold">{name}</h3>
        <p className="text-xs text-gray-600 dark:text-gray-400">URN: {urn}</p>
      </div>

      {/* Risk & Classification */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 pb-3 border-b">
        <p><span className="font-semibold">Risk Level:</span> {riskLevel}</p>
        {gpaiClassification && gpaiClassification.length > 0 && (
          <p className="text-sm">
            <span className="font-semibold">GPAI Classification:</span> {gpaiClassification.map(g => g.replace(/^ai:/, '')).join(", ")}
          </p>
        )}
      </div>

      {/* Core System Properties */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 pb-3 border-b">
        <p><span className="font-semibold">Purpose(s):</span> {purpose.map(p => p.replace(/^ai:/, '')).join(", ")}</p>
        <p><span className="font-semibold">Deployment Context(s):</span> {deploymentContext.map(c => c.replace(/^ai:/, '')).join(", ")}</p>
        <p><span className="font-semibold">Training Data Origin(s):</span> {trainingDataOrigin.map(o => o.replace(/^ai:/, '')).join(", ")}</p>
        {systemCapabilityCriteria && systemCapabilityCriteria.length > 0 && (
          <p className="text-sm">
            <span className="font-semibold">System Capabilities:</span> {systemCapabilityCriteria.map(c => c.replace(/^ai:/, '')).join(", ")}
          </p>
        )}
      </div>

      {/* Algorithm & Model */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 pb-3 border-b">
        <p><span className="font-semibold">Algorithm Type(s):</span> {algorithmType.map(a => a.replace(/^ai:/, '')).join(", ")}</p>
        {modelScale && modelScale.length > 0 && (
          <p><span className="font-semibold">Model Scale:</span> {modelScale.map(m => m.replace(/^ai:/, '')).join(", ")}</p>
        )}
        {capabilities && capabilities.length > 0 && (
          <p className="text-sm">
            <span className="font-semibold">Capabilities:</span> {capabilities.map(c => c.replace(/^ai:/, '')).join(", ")}
          </p>
        )}
      </div>

      {/* Contextual & Risk Criteria */}
      {(contextualCriteria && contextualCriteria.length > 0) && (
        <div className="mb-3 pb-3 border-b">
          {renderField("Contextual Criteria", contextualCriteria)}
        </div>
      )}

      {/* Compliance Requirements */}
      {(complianceRequirements && complianceRequirements.length > 0 ||
        technicalRequirements && technicalRequirements.length > 0 ||
        securityRequirements && securityRequirements.length > 0) && (
        <div className="mb-3 pb-3 border-b">
          <p className="font-semibold text-sm mb-2">Compliance Requirements:</p>
          {renderField("Technical", technicalRequirements)}
          {renderField("Security", securityRequirements)}
          {renderField("Robustness", robustnessRequirements)}
          {renderField("Documentation", documentationRequirements)}
          {renderField("Data Governance", dataGovernanceRequirements)}
        </div>
      )}

      {/* Standards & Frameworks */}
      {(isoRequirements && isoRequirements.length > 0 ||
        nistRequirements && nistRequirements.length > 0) && (
        <div className="mb-3 pb-3 border-b">
          <p className="font-semibold text-sm mb-2">Standards & Frameworks:</p>
          {renderField("ISO 42001", isoRequirements)}
          {renderField("NIST AI RMF", nistRequirements)}
        </div>
      )}

      {/* Human & Governance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 pb-3 border-b">
        {humanOversightRequired !== undefined && (
          <p className="text-sm">
            <span className="font-semibold">Human Oversight:</span> {humanOversightRequired ? "Required" : "Not Required"}
          </p>
        )}
        {transparencyLevel && (
          <p className="text-sm">
            <span className="font-semibold">Transparency Level:</span> {transparencyLevel}
          </p>
        )}
        {fundamentalRightsAssessment !== undefined && (
          <p className="text-sm">
            <span className="font-semibold">Fundamental Rights Assessment:</span> {fundamentalRightsAssessment ? "Required" : "Not Required"}
          </p>
        )}
      </div>

      {/* Version */}
      <p className="text-sm text-gray-600 dark:text-gray-400">
        <span className="font-semibold">Version:</span> {version}
      </p>
    </div>
  );
}


