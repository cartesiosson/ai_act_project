import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import ForceGraph3D from "react-force-graph-3d";
import { graph, literal, sym } from "rdflib";
import { Parser as N3Parser } from "n3";
import * as THREE from "three";

interface NodeData {
  id: string;
  type: string;
  category: string;
  label: string;
  fullLabel: string;
  size: number;
  color: string;
  x?: number;
  y?: number;
  z?: number;
}

interface LinkData {
  source: string | NodeData;
  target: string | NodeData;
  predicate: string;
  predicateLabel: string;
  color: string;
}

interface GraphData {
  nodes: NodeData[];
  links: LinkData[];
}

const NODE_CATEGORIES: { [key: string]: { color: string; icon: string; label: string } } = {
  system: { color: "#3b82f6", icon: "S", label: "System" },
  purpose: { color: "#8b5cf6", icon: "P", label: "Purpose" },
  deployment: { color: "#ec4899", icon: "D", label: "Deployment" },
  technical: { color: "#f97316", icon: "T", label: "Technical" },
  capability: { color: "#10b981", icon: "C", label: "Capability" },
  compliance: { color: "#14b8a6", icon: "R", label: "Compliance" },
  other: { color: "#6b7280", icon: "O", label: "Other" },
};

export default function GraphView() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(undefined);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [systems, setSystems] = useState<string[]>([]);
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [selectedSystemData, setSelectedSystemData] = useState<any | null>(null);
  const [store, setStore] = useState<any>(null);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loadingError, setLoadingError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [hoveredNode, setHoveredNode] = useState<NodeData | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [showLabels, setShowLabels] = useState(true);
  const [showLinkLabels, setShowLinkLabels] = useState(true);
  const [linkDistance, setLinkDistance] = useState(100);

  // Detect dark mode
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark');
  const bgColor = isDark ? "#030712" : "#f3f4f6";
  const linkColor = isDark ? "#4b5563" : "#9ca3af";

  const getNodeType = (uri: string, predicateUri?: string): string => {
    if (uri.startsWith("urn:uuid:") || uri.startsWith("urn:forensic:")) return "system";
    const lowerUri = uri.toLowerCase();
    const lowerPredicate = predicateUri?.toLowerCase() || "";

    if (lowerPredicate.includes("purpose")) return "purpose";
    if (lowerPredicate.includes("deployment") || lowerPredicate.includes("deploymentcontext")) return "deployment";
    if (lowerPredicate.includes("trainingdata") || lowerPredicate.includes("dataorigin")) return "technical";
    if (lowerPredicate.includes("algorithm")) return "technical";
    if (lowerPredicate.includes("model")) return "technical";
    if (lowerPredicate.includes("scale")) return "technical";
    if (lowerPredicate.includes("hasactivatedcriterion")) return "compliance";
    if (lowerPredicate.includes("hasmanuallyidentifiedcriterion")) return "compliance";
    if (lowerPredicate.includes("hascapabilitymetric")) return "technical";
    if (lowerPredicate.includes("systemcapability")) return "capability";

    if (lowerUri.includes("algorithmtype") || lowerUri.includes("algorithm")) return "technical";
    if (lowerUri.includes("modelscale") || (lowerUri.includes("model") && lowerUri.includes("scale"))) return "technical";
    if (lowerUri.includes("training")) return "technical";
    if (lowerUri.includes("data")) return "technical";
    if (lowerUri.includes("metric") || lowerUri.includes("performance")) return "technical";
    if (lowerUri.includes("scale")) return "technical";
    if (lowerUri.includes("criterion") && lowerUri.includes("capability")) return "technical";
    if (lowerUri.includes("purpose")) return "purpose";
    if (lowerUri.includes("deployment") || lowerUri.includes("context")) return "deployment";
    if (lowerUri.includes("capability")) return "capability";
    if (lowerUri.includes("criterion") || lowerUri.includes("requirement")) return "compliance";

    return "other";
  };

  const getNodeCategory = (type: string): string => {
    return NODE_CATEGORIES[type] ? type : "other";
  };

  const extractLabel = (uri: string): string => {
    const label = uri.split("#").pop() || uri.split("/").pop() || uri;
    return label;
  };

  const truncateLabel = (text: string, maxLength: number = 18): string => {
    const label = extractLabel(text);
    return label.length > maxLength ? label.substring(0, maxLength) + "..." : label;
  };

  const fetchGraph = async (): Promise<string> => {
    const query = `
      CONSTRUCT { ?s ?p ?o }
      WHERE {
        { GRAPH <http://ai-act.eu/ontology/data> { ?s ?p ?o } }
        UNION
        { ?s ?p ?o }
      }
    `;
    const response = await fetch("http://localhost:3030/ds/sparql", {
      method: "POST",
      headers: {
        "Content-Type": "application/sparql-query",
        Accept: "text/turtle",
      },
      body: query,
    });

    if (!response.ok) {
      throw new Error("Error fetching graph: " + response.statusText);
    }

    return response.text();
  };

  const buildGraphData = useCallback((triples: any[]): GraphData => {
    const nodes = new Map<string, NodeData>();
    const links: LinkData[] = [];
    const nodeCount = new Map<string, number>();

    triples.forEach((triple) => {
      if (triple.predicate.value !== "http://ai-act.eu/ai#hasUrn") {
        const sourceId = triple.subject.value;
        const targetId = triple.object.value;
        const predicateUri = triple.predicate.value;
        const predicateLabel = extractLabel(predicateUri);

        if (!nodes.has(sourceId)) {
          const type = getNodeType(sourceId, predicateUri);
          const category = getNodeCategory(type);
          nodes.set(sourceId, {
            id: sourceId,
            type,
            category,
            label: truncateLabel(sourceId),
            fullLabel: extractLabel(sourceId),
            size: 8,
            color: NODE_CATEGORIES[category].color,
          });
        }

        if (!nodes.has(targetId)) {
          const type = getNodeType(targetId, predicateUri);
          const category = getNodeCategory(type);
          nodes.set(targetId, {
            id: targetId,
            type,
            category,
            label: truncateLabel(targetId),
            fullLabel: extractLabel(targetId),
            size: 8,
            color: NODE_CATEGORIES[category].color,
          });
        }

        nodeCount.set(sourceId, (nodeCount.get(sourceId) || 0) + 1);
        nodeCount.set(targetId, (nodeCount.get(targetId) || 0) + 1);

        links.push({
          source: sourceId,
          target: targetId,
          predicate: predicateUri,
          predicateLabel,
          color: linkColor,
        });
      }
    });

    // Adjust node sizes based on connections
    nodeCount.forEach((count, nodeId) => {
      const node = nodes.get(nodeId);
      if (node) {
        node.size = Math.min(15, 6 + count * 1.5);
      }
    });

    return {
      nodes: Array.from(nodes.values()),
      links,
    };
  }, [linkColor]);

  // Filter graph data based on active filter and search
  const filteredGraphData = useMemo(() => {
    let filteredNodes = graphData.nodes;
    let filteredLinks = graphData.links;

    // Apply category filter
    if (activeFilter) {
      filteredLinks = graphData.links.filter((l) => {
        const sourceNode = graphData.nodes.find(n => n.id === (typeof l.source === 'string' ? l.source : l.source.id));
        const targetNode = graphData.nodes.find(n => n.id === (typeof l.target === 'string' ? l.target : l.target.id));
        return sourceNode?.category === activeFilter || targetNode?.category === activeFilter;
      });

      const nodeIdsInLinks = new Set<string>();
      filteredLinks.forEach((l) => {
        nodeIdsInLinks.add(typeof l.source === 'string' ? l.source : l.source.id);
        nodeIdsInLinks.add(typeof l.target === 'string' ? l.target : l.target.id);
      });
      filteredNodes = graphData.nodes.filter((n) => nodeIdsInLinks.has(n.id));
    }

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filteredNodes = filteredNodes.filter((n) =>
        n.label.toLowerCase().includes(query) ||
        n.fullLabel.toLowerCase().includes(query) ||
        n.id.toLowerCase().includes(query)
      );
      const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = filteredLinks.filter((l) => {
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
        const targetId = typeof l.target === 'string' ? l.target : l.target.id;
        return filteredNodeIds.has(sourceId) && filteredNodeIds.has(targetId);
      });
    }

    return { nodes: filteredNodes, links: filteredLinks };
  }, [graphData, activeFilter, searchQuery]);

  // Create text sprite for node labels
  const createTextSprite = useCallback((text: string, color: string, size: number = 4) => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return null;

    canvas.width = 256;
    canvas.height = 64;

    context.fillStyle = 'transparent';
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.font = 'Bold 24px Arial';
    context.fillStyle = isDark ? '#ffffff' : '#1f2937';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;

    const spriteMaterial = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
    });

    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(size * 4, size, 1);

    return sprite;
  }, [isDark]);

  // Custom node rendering with 3D sphere and label
  const nodeThreeObject = useCallback((node: NodeData) => {
    const group = new THREE.Group();

    // Create sphere
    const geometry = new THREE.SphereGeometry(node.size, 16, 16);
    const material = new THREE.MeshLambertMaterial({
      color: node.color,
      transparent: true,
      opacity: 0.9,
    });
    const sphere = new THREE.Mesh(geometry, material);
    group.add(sphere);

    // Add label if enabled
    if (showLabels) {
      const sprite = createTextSprite(node.label, node.color, node.size);
      if (sprite) {
        sprite.position.set(0, node.size + 5, 0);
        group.add(sprite);
      }
    }

    return group;
  }, [showLabels, createTextSprite]);

  // Custom link rendering with labels
  const linkThreeObject = useCallback((link: LinkData) => {
    if (!showLinkLabels) return null;

    const sprite = createTextSprite(link.predicateLabel, linkColor, 3);
    return sprite;
  }, [showLinkLabels, createTextSprite, linkColor]);

  const linkPositionUpdate = useCallback((sprite: any, { start, end }: { start: any; end: any }) => {
    if (sprite) {
      const middlePos = {
        x: (start.x + end.x) / 2,
        y: (start.y + end.y) / 2,
        z: (start.z + end.z) / 2,
      };
      Object.assign(sprite.position, middlePos);
    }
  }, []);

  // Handle node click
  const handleNodeClick = useCallback((node: NodeData) => {
    if (fgRef.current) {
      // Focus camera on node
      const distance = 150;
      const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);

      fgRef.current.cameraPosition(
        {
          x: (node.x || 0) * distRatio,
          y: (node.y || 0) * distRatio,
          z: (node.z || 0) * distRatio,
        },
        { x: node.x || 0, y: node.y || 0, z: node.z || 0 },
        1000
      );
    }
  }, []);

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Load graph data
  useEffect(() => {
    const graphStore = graph();
    setIsLoading(true);
    setLoadingError(null);

    fetchGraph()
      .then((ttlData) => {
        const n3Parser = new N3Parser();
        const triples = n3Parser.parse(ttlData);

        if (triples.length === 0) {
          setLoadingError("No data found in the RDF graph. Please create a system first.");
          setIsLoading(false);
          return;
        }

        triples.forEach((t) => {
          const subject = sym(t.subject.id || t.subject.value);
          const predicate = sym(t.predicate.id || t.predicate.value);
          const object = t.object.termType === "Literal"
            ? literal(t.object.value)
            : sym(t.object.id || t.object.value);

          graphStore.add(subject, predicate, object);
        });

        setStore(graphStore);

        const systemNames = graphStore
          .statementsMatching(undefined, sym("http://ai-act.eu/ai#hasName"))
          .map((st) => st.object.value);
        const uniqueNames = Array.from(new Set(systemNames));
        setSystems(uniqueNames);

        // Build initial graph data
        const data = buildGraphData(triples);
        setGraphData(data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Failed to load or parse RDF graph", error);
        setLoadingError(`Error loading graph: ${error instanceof Error ? error.message : "Unknown error"}`);
        setIsLoading(false);
      });
  }, [buildGraphData]);

  // Update graph when system is selected
  useEffect(() => {
    if (store && selectedSystem) {
      const subjects = store
        .statementsMatching(undefined, sym("http://ai-act.eu/ai#hasName"), literal(selectedSystem))
        .map((st: any) => st.subject);

      const filteredTriples = store.statements.filter((st: any) =>
        subjects.some((subj: any) => subj.equals(st.subject))
      );

      const data = buildGraphData(filteredTriples);
      setGraphData(data);

      const subject = subjects[0];
      if (subject) {
        const get = (p: string) =>
          store.any(subject, sym(`http://ai-act.eu/ai#${p}`))?.value ?? "N/A";

        setSelectedSystemData({
          name: get("hasName"),
          riskLevel: get("hasRiskLevel"),
          purpose: store
            .each(subject, sym("http://ai-act.eu/ai#hasPurpose"))
            .map((o: any) => extractLabel(o.value))
            .join(", ") || "N/A",
          deploymentContext: store
            .each(subject, sym("http://ai-act.eu/ai#hasDeploymentContext"))
            .map((o: any) => extractLabel(o.value))
            .join(", ") || "N/A",
          trainingDataOrigin: store
            .each(subject, sym("http://ai-act.eu/ai#hasTrainingDataOrigin"))
            .map((o: any) => o.value)
            .join(", ") || "N/A",
          version: get("hasVersion"),
          urn: store.any(subject, sym("http://ai-act.eu/ai#hasUrn"))?.value ??
               subject.value ?? "N/A",
        });
      }
    }
  }, [selectedSystem, store, buildGraphData]);

  // Reset view
  const resetView = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.cameraPosition({ x: 0, y: 0, z: 500 }, { x: 0, y: 0, z: 0 }, 1000);
    }
  }, []);

  // Update link distance when slider changes
  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force('link')?.distance(linkDistance);
      fgRef.current.d3ReheatSimulation();
    }
  }, [linkDistance]);

  return (
    <div ref={containerRef} className="w-full h-[calc(100vh-120px)] bg-white dark:bg-gray-900 text-gray-900 dark:text-white overflow-hidden flex flex-col -mx-4 -mb-4">
      {/* Header Controls */}
      <div className="relative z-10 bg-gray-50 dark:bg-gray-800 p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-3 items-center flex-wrap">
          <select
            onChange={(e) => setSelectedSystem(e.target.value || null)}
            value={selectedSystem || ""}
            className="p-2 text-sm rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select System --</option>
            {systems.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="p-2 text-sm rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[150px]"
          />

          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setActiveFilter(null)}
              className={`px-3 py-1.5 text-xs rounded border transition-colors ${
                activeFilter === null
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600"
              }`}
            >
              All
            </button>
            {Object.entries(NODE_CATEGORIES).map(([key, { icon, label, color }]) => (
              <button
                key={key}
                onClick={() => setActiveFilter(activeFilter === key ? null : key)}
                className={`px-3 py-1.5 text-xs rounded border transition-colors ${
                  activeFilter === key
                    ? "text-white"
                    : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                }`}
                style={{
                  backgroundColor: activeFilter === key ? color : undefined,
                  borderColor: color,
                }}
                title={label}
              >
                {icon} {label}
              </button>
            ))}
          </div>

          <div className="flex gap-4 ml-auto items-center">
            <label className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
              <span>Distance:</span>
              <input
                type="range"
                min="30"
                max="300"
                value={linkDistance}
                onChange={(e) => setLinkDistance(Number(e.target.value))}
                className="w-20 h-1 accent-blue-500"
              />
              <span className="w-8 text-center">{linkDistance}</span>
            </label>
            <label className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
              <input
                type="checkbox"
                checked={showLabels}
                onChange={(e) => setShowLabels(e.target.checked)}
                className="rounded"
              />
              Node Labels
            </label>
            <label className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
              <input
                type="checkbox"
                checked={showLinkLabels}
                onChange={(e) => setShowLinkLabels(e.target.checked)}
                className="rounded"
              />
              Link Labels
            </label>
            <button
              onClick={resetView}
              className="px-3 py-1.5 text-xs rounded border bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Reset View
            </button>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div className="relative flex-1 w-full h-full">
        {isLoading && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center z-20">
            <p className="text-lg mb-2 text-gray-700 dark:text-gray-300">Loading graph data...</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Fetching systems from RDF store</p>
          </div>
        )}

        {loadingError && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-600 text-red-700 dark:text-red-400 p-5 rounded-lg max-w-md text-center z-20">
            <p className="text-base font-semibold mb-2">Error loading graph</p>
            <p className="text-sm">{loadingError}</p>
            <p className="text-xs mt-3 text-red-600 dark:text-red-500">
              Check the console for more details
            </p>
          </div>
        )}

        {!isLoading && !loadingError && (
          <ForceGraph3D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height - 60}
            graphData={filteredGraphData}
            backgroundColor={bgColor}
            nodeThreeObject={nodeThreeObject}
            nodeThreeObjectExtend={false}
            linkColor={() => linkColor}
            linkWidth={1.5}
            linkOpacity={0.6}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkThreeObject={linkThreeObject}
            linkPositionUpdate={linkPositionUpdate}
            linkThreeObjectExtend={true}
            onNodeClick={handleNodeClick}
            onNodeHover={(node) => setHoveredNode(node as NodeData | null)}
            enableNodeDrag={true}
            enableNavigationControls={true}
            showNavInfo={false}
          />
        )}

        {/* Hover tooltip */}
        {hoveredNode && (
          <div className="absolute top-5 left-5 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10 max-w-sm">
            <p className="font-bold text-sm" style={{ color: hoveredNode.color }}>
              {hoveredNode.fullLabel}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Category: {NODE_CATEGORIES[hoveredNode.category]?.label || "Other"}
            </p>
          </div>
        )}

        {/* System Info Panel */}
        {selectedSystemData && (
          <div className="absolute bottom-5 right-5 w-[360px] max-h-[400px] bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-4 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-auto z-10">
            <h3 className="text-base font-bold mb-3 pb-2 border-b-2 border-blue-500">
              {selectedSystemData.name}
            </h3>
            <div className="text-sm leading-relaxed space-y-1">
              <p><strong>Risk Level:</strong> {extractLabel(selectedSystemData.riskLevel)}</p>
              <p><strong>Purpose(s):</strong> {selectedSystemData.purpose}</p>
              <p><strong>Deployment Context(s):</strong> {selectedSystemData.deploymentContext}</p>
              <p><strong>Data Origin:</strong> {selectedSystemData.trainingDataOrigin}</p>
              <p><strong>Version:</strong> {selectedSystemData.version}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                <strong>URN:</strong> <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded break-all">{selectedSystemData.urn}</code>
              </p>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="absolute bottom-5 left-5 bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg text-xs z-10">
          <span className="font-semibold">{filteredGraphData.nodes.length}</span> nodes |
          <span className="font-semibold ml-1">{filteredGraphData.links.length}</span> links
        </div>

        {/* 3D Controls Help */}
        <div className="absolute top-5 right-5 bg-white/80 dark:bg-gray-800/80 text-gray-600 dark:text-gray-400 px-3 py-2 rounded-lg text-xs z-10">
          <p><strong>Controls:</strong></p>
          <p>Left-click + drag: Rotate</p>
          <p>Right-click + drag: Pan</p>
          <p>Scroll: Zoom</p>
          <p>Click node: Focus</p>
        </div>
      </div>
    </div>
  );
}
