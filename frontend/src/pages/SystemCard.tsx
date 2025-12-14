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
  // ARTICLE 5: PROHIBITED PRACTICES (v0.37.4)
  prohibitedPractices?: string[];
  legalExceptions?: string[];
  hasJudicialAuthorization?: boolean;
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
  prohibitedPractices,
  legalExceptions,
  hasJudicialAuthorization,
}: SystemCardProps) {
  const renderSection = (title: string, icon: string, color: string, fields: { label: string; values?: string[] }[]) => {
    const hasContent = fields.some(f => f.values && f.values.length > 0);
    if (!hasContent) return null;

    return (
      <div className={`mb-6 pb-6 border-b last:border-b-0`}>
        <div className="flex items-center mb-3">
          <span className="text-xl mr-2">{icon}</span>
          <h4 className={`font-bold text-sm ${color}`}>{title}</h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 ml-6">
          {fields.map((field, idx) => {
            if (!field.values || field.values.length === 0) return null;
            return (
              <div key={idx} className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase mb-1">{field.label}</p>
                <p className="text-sm text-gray-900 dark:text-white">
                  {field.values.map(v => v.replace(/^ai:/, '')).join(", ")}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const getRiskBadgeColor = (risk: string) => {
    const cleanRisk = risk.toLowerCase();
    if (cleanRisk.includes('unacceptable')) return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100';
    if (cleanRisk.includes('high')) return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100';
    if (cleanRisk.includes('limited')) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportJSON = () => {
    const data = {
      name,
      urn,
      version,
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
      complianceRequirements,
      technicalRequirements,
      securityRequirements,
      robustnessRequirements,
      documentationRequirements,
      dataGovernanceRequirements,
      humanOversightRequired,
      transparencyLevel,
      fundamentalRightsAssessment,
      prohibitedPractices,
      legalExceptions,
      hasJudicialAuthorization,
    };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name.replace(/\s+/g, '-').toLowerCase()}-system-assessment.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-lg shadow-lg bg-white dark:bg-gray-800 overflow-hidden border border-gray-200 dark:border-gray-700 print:shadow-none print:border-0">
      {/* Header - System Identity */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-700 dark:to-blue-800 px-6 py-4 print:bg-blue-600">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="text-2xl font-bold text-white mb-1">{name}</h3>
            <p className="text-sm text-blue-100">URN: {urn}</p>
            {version && <p className="text-xs text-blue-100 mt-1">Version {version}</p>}
          </div>
          <div className="flex gap-2 print:hidden">
            <button
              onClick={handlePrint}
              className="text-blue-100 hover:text-white px-3 py-1 rounded text-xs bg-blue-700 hover:bg-blue-800 transition-colors"
              title="Print this assessment"
            >
              🖨️ Print
            </button>
            <button
              onClick={handleExportJSON}
              className="text-blue-100 hover:text-white px-3 py-1 rounded text-xs bg-blue-700 hover:bg-blue-800 transition-colors"
              title="Download as JSON"
            >
              💾 Export
            </button>
          </div>
        </div>
      </div>

      {/* Risk & Classification Banner */}
      <div className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 px-6 py-4">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400 uppercase mb-1">Risk Level</p>
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${getRiskBadgeColor(riskLevel)}`}>
              {riskLevel}
            </span>
          </div>
          {gpaiClassification && gpaiClassification.length > 0 && (
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400 uppercase mb-1">GPAI Classification</p>
              <div className="flex flex-wrap gap-2">
                {gpaiClassification.map((g, i) => (
                  <span key={i} className="inline-block px-2 py-1 rounded text-xs bg-blue-200 text-blue-800 dark:bg-blue-700 dark:text-blue-100">
                    {g.replace(/^ai:/, '')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ARTICLE 5: PROHIBITED PRACTICES WARNING (v0.37.4) */}
      {prohibitedPractices && prohibitedPractices.length > 0 && (
        <div className="bg-red-100 dark:bg-red-900 border-t-4 border-red-500 dark:border-red-700 px-6 py-4">
          <div className="flex items-start gap-3">
            <span className="text-3xl">🚫</span>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-900 dark:text-red-100 mb-2">
                ⚠️ ARTICLE 5: PROHIBITED PRACTICE DETECTED
              </h3>
              <p className="text-sm text-red-800 dark:text-red-200 mb-3 font-semibold">
                This system CANNOT be deployed in the EU. Maximum penalties: €35M or 7% of global annual turnover.
              </p>
              <div className="bg-red-200 dark:bg-red-800 rounded p-3 mb-3">
                <p className="text-xs font-semibold text-red-900 dark:text-red-100 uppercase mb-2">Prohibited Practices:</p>
                <ul className="list-disc list-inside text-sm text-red-900 dark:text-red-100">
                  {prohibitedPractices.map((practice, i) => (
                    <li key={i}>{practice.replace(/^ai:/, '').replace(/Criterion$/, '')}</li>
                  ))}
                </ul>
              </div>

              {/* Legal Exceptions (only for real-time biometric) */}
              {legalExceptions && legalExceptions.length > 0 && (
                <div className="bg-yellow-100 dark:bg-yellow-900 rounded p-3 mb-2 border border-yellow-400 dark:border-yellow-600">
                  <p className="text-xs font-semibold text-yellow-900 dark:text-yellow-100 uppercase mb-2">
                    ⚖️ Legal Exceptions Claimed (Article 5.2):
                  </p>
                  <ul className="list-disc list-inside text-sm text-yellow-900 dark:text-yellow-100 mb-2">
                    {legalExceptions.map((exception, i) => (
                      <li key={i}>{exception.replace(/^ai:/, '').replace(/Exception$/, '')}</li>
                    ))}
                  </ul>
                  {hasJudicialAuthorization !== undefined && (
                    <div className={`mt-2 p-2 rounded ${hasJudicialAuthorization ? 'bg-blue-200 dark:bg-blue-800' : 'bg-red-300 dark:bg-red-700'}`}>
                      <p className={`text-xs font-bold ${hasJudicialAuthorization ? 'text-blue-900 dark:text-blue-100' : 'text-red-900 dark:text-red-100'}`}>
                        {hasJudicialAuthorization
                          ? '✓ Has Prior Judicial Authorization'
                          : '⚠️ NO Judicial Authorization - System remains PROHIBITED'}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Content Sections */}
      <div className="px-6 py-6">
        {/* SECTION 1: Purposes */}
        {renderSection(
          "1. System Purposes",
          "🎯",
          "text-blue-600 dark:text-blue-400",
          [{ label: "Primary Purpose(s)", values: purpose }]
        )}

        {/* SECTION 2: Deployment Context */}
        {renderSection(
          "2. Deployment Context",
          "📍",
          "text-purple-600 dark:text-purple-400",
          [
            { label: "Deployment Context(s)", values: deploymentContext }
          ]
        )}

        {/* SECTION 3: Technical Factors */}
        {renderSection(
          "3. Technical Factors",
          "⚙️",
          "text-orange-600 dark:text-orange-400",
          [
            { label: "Algorithm Type(s)", values: algorithmType },
            { label: "Model Scale", values: modelScale },
            { label: "System Capability Criteria", values: systemCapabilityCriteria },
            { label: "Training Data Origin(s)", values: trainingDataOrigin }
          ]
        )}

        {/* SECTION 4: Capabilities */}
        {capabilities && capabilities.length > 0 && renderSection(
          "4. System Capabilities",
          "🚀",
          "text-green-600 dark:text-green-400",
          [{ label: "Specific Capabilities", values: capabilities }]
        )}

        {/* Contextual Criteria */}
        {contextualCriteria && contextualCriteria.length > 0 && (
          <div className="mb-6 pb-6 border-b">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">📊</span>
              <h4 className="font-bold text-sm text-indigo-600 dark:text-indigo-400">Contextual Criteria</h4>
            </div>
            <div className="ml-6 bg-indigo-50 dark:bg-indigo-900 p-3 rounded">
              <p className="text-sm text-indigo-900 dark:text-indigo-100">
                {contextualCriteria.map(c => c.replace(/^ai:/, '')).join(", ")}
              </p>
            </div>
          </div>
        )}

        {/* Compliance Requirements */}
        {(complianceRequirements && complianceRequirements.length > 0 ||
          technicalRequirements && technicalRequirements.length > 0 ||
          securityRequirements && securityRequirements.length > 0 ||
          robustnessRequirements && robustnessRequirements.length > 0 ||
          documentationRequirements && documentationRequirements.length > 0 ||
          dataGovernanceRequirements && dataGovernanceRequirements.length > 0) && (
          <div className="mb-6 pb-6 border-b">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">✅</span>
              <h4 className="font-bold text-sm text-green-600 dark:text-green-400">Compliance Requirements</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 ml-6">
              {technicalRequirements && technicalRequirements.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 p-3 rounded">
                  <p className="text-xs font-semibold text-green-600 dark:text-green-300 uppercase mb-1">Technical</p>
                  <p className="text-sm text-gray-900 dark:text-white">{technicalRequirements.map(t => t.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
              {securityRequirements && securityRequirements.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 p-3 rounded">
                  <p className="text-xs font-semibold text-green-600 dark:text-green-300 uppercase mb-1">Security</p>
                  <p className="text-sm text-gray-900 dark:text-white">{securityRequirements.map(s => s.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
              {robustnessRequirements && robustnessRequirements.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 p-3 rounded">
                  <p className="text-xs font-semibold text-green-600 dark:text-green-300 uppercase mb-1">Robustness</p>
                  <p className="text-sm text-gray-900 dark:text-white">{robustnessRequirements.map(r => r.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
              {documentationRequirements && documentationRequirements.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 p-3 rounded">
                  <p className="text-xs font-semibold text-green-600 dark:text-green-300 uppercase mb-1">Documentation</p>
                  <p className="text-sm text-gray-900 dark:text-white">{documentationRequirements.map(d => d.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
              {dataGovernanceRequirements && dataGovernanceRequirements.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900 p-3 rounded">
                  <p className="text-xs font-semibold text-green-600 dark:text-green-300 uppercase mb-1">Data Governance</p>
                  <p className="text-sm text-gray-900 dark:text-white">{dataGovernanceRequirements.map(dg => dg.replace(/^ai:/, '')).join(", ")}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Standards & Frameworks */}
        {isoRequirements && isoRequirements.length > 0 && (
          <div className="mb-6 pb-6 border-b">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">📋</span>
              <h4 className="font-bold text-sm text-cyan-600 dark:text-cyan-400">Standards & Frameworks</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-1 gap-3 ml-6">
              <div className="bg-cyan-50 dark:bg-cyan-900 p-3 rounded">
                <p className="text-xs font-semibold text-cyan-600 dark:text-cyan-300 uppercase mb-1">ISO 42001</p>
                <p className="text-sm text-gray-900 dark:text-white">{isoRequirements.map(i => i.replace(/^ai:/, '')).join(", ")}</p>
              </div>
            </div>
          </div>
        )}

        {/* Governance & Human Oversight */}
        {(humanOversightRequired !== undefined || transparencyLevel || fundamentalRightsAssessment !== undefined) && (
          <div className="mb-6 pb-6 border-b">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">👥</span>
              <h4 className="font-bold text-sm text-rose-600 dark:text-rose-400">Governance & Oversight</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 ml-6">
              {humanOversightRequired !== undefined && (
                <div className="bg-rose-50 dark:bg-rose-900 p-3 rounded">
                  <p className="text-xs font-semibold text-rose-600 dark:text-rose-300 uppercase mb-1">Human Oversight</p>
                  <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${humanOversightRequired ? 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-100' : 'bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100'}`}>
                    {humanOversightRequired ? "Required" : "Not Required"}
                  </span>
                </div>
              )}
              {transparencyLevel && (
                <div className="bg-rose-50 dark:bg-rose-900 p-3 rounded">
                  <p className="text-xs font-semibold text-rose-600 dark:text-rose-300 uppercase mb-1">Transparency Level</p>
                  <p className="text-sm text-gray-900 dark:text-white font-semibold">{transparencyLevel}</p>
                </div>
              )}
              {fundamentalRightsAssessment !== undefined && (
                <div className="bg-rose-50 dark:bg-rose-900 p-3 rounded">
                  <p className="text-xs font-semibold text-rose-600 dark:text-rose-300 uppercase mb-1">Fundamental Rights</p>
                  <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${fundamentalRightsAssessment ? 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-100' : 'bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100'}`}>
                    {fundamentalRightsAssessment ? "Assessment Required" : "Not Required"}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


