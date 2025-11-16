interface SystemCardProps {
  name: string;
  riskLevel: string;
  purpose: string[];
  deploymentContext: string[];
  trainingDataOrigin: string[];
  algorithmType: string[];
  modelScale?: string[];
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
  version,
  urn,
}: SystemCardProps) {
  return (
    <div className="border p-4 rounded shadow bg-white dark:bg-gray-800">
      <h3 className="text-lg font-bold mb-1">{name}</h3>
      <p><span className="font-semibold">Risk Level:</span> {riskLevel}</p>
      <p><span className="font-semibold">Purpose(s):</span> {purpose.join(", ")}</p>
      <p><span className="font-semibold">Deployment Context(s):</span> {deploymentContext.join(", ")}</p>
      <p><span className="font-semibold">Training Data Origin(s):</span> {trainingDataOrigin.join(", ")}</p>
      <p><span className="font-semibold">Algorithm Type(s):</span> {algorithmType.join(", ")}</p>
      {modelScale && modelScale.length > 0 && (
        <p><span className="font-semibold">Model Scale(s):</span> {modelScale.join(", ")}</p>
      )}
      <p><span className="font-semibold">Version:</span> {version}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">
        <span className="font-semibold">URN:</span> {urn}
      </p>
    </div>
  );
}


