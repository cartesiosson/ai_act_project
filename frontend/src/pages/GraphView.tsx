import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { graph, NamedNode, literal, sym } from "rdflib";
import { Parser as N3Parser } from "n3";

interface NodeData {
  id: string;
  type: string;
  category: string;
  label: string;
  size: number;
}

interface LinkData {
  source: string;
  target: string;
  predicate: string;
  predicateLabel: string;
}

const NODE_CATEGORIES: { [key: string]: { color: string; icon: string; label: string } } = {
  system: { color: "#3b82f6", icon: "🏢", label: "Sistema" },
  purpose: { color: "#8b5cf6", icon: "🎯", label: "Propósito" },
  deployment: { color: "#ec4899", icon: "📍", label: "Despliegue" },
  technical: { color: "#f97316", icon: "⚙️", label: "Técnico" },
  capability: { color: "#10b981", icon: "🚀", label: "Capacidad" },
  compliance: { color: "#14b8a6", icon: "✅", label: "Cumplimiento" },
  other: { color: "#6b7280", icon: "◦", label: "Otro" },
};

export default function GraphView() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [systems, setSystems] = useState<string[]>([]);
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [selectedSystemData, setSelectedSystemData] = useState<any | null>(null);
  const [store, setStore] = useState<any>(null);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loadingError, setLoadingError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getNodeType = (uri: string, predicateUri?: string): string => {
    if (uri.startsWith("urn:uuid:")) return "system";
    const lowerUri = uri.toLowerCase();
    const lowerPredicate = predicateUri?.toLowerCase() || "";

    // Check predicate first to determine category based on relationship
    if (lowerPredicate.includes("purpose")) return "purpose";
    if (lowerPredicate.includes("deployment") || lowerPredicate.includes("deploymentcontext")) return "deployment";
    if (lowerPredicate.includes("trainingdata") || lowerPredicate.includes("dataorigin")) return "technical";
    if (lowerPredicate.includes("algorithm")) return "technical";
    if (lowerPredicate.includes("model")) return "technical";
    if (lowerPredicate.includes("scale")) return "technical";

    // Option C criteria properties (new)
    if (lowerPredicate.includes("hasactivatedcriterion")) return "compliance";
    if (lowerPredicate.includes("hasmanuallyidentifiedcriterion")) return "compliance";
    if (lowerPredicate.includes("hascapabilitymetric")) return "technical";

    // Legacy
    if (lowerPredicate.includes("systemcapability")) return "capability";

    // Then check the URI itself for more specific categorization
    // Technical concepts first (more specific)
    if (lowerUri.includes("algorithmtype") || lowerUri.includes("algorithm")) return "technical";
    if (lowerUri.includes("modelscale") || lowerUri.includes("model") && lowerUri.includes("scale")) return "technical";
    if (lowerUri.includes("training")) return "technical";
    if (lowerUri.includes("data")) return "technical";
    if (lowerUri.includes("metric") || lowerUri.includes("performance")) return "technical";
    if (lowerUri.includes("scale")) return "technical";
    if (lowerUri.includes("criterion") && lowerUri.includes("capability")) return "technical";

    // Then check for other categories
    if (lowerUri.includes("purpose")) return "purpose";
    if (lowerUri.includes("deployment") || lowerUri.includes("context")) return "deployment";
    if (lowerUri.includes("capability")) return "capability";
    if (lowerUri.includes("criterion") || lowerUri.includes("requirement")) return "compliance";

    return "other";
  };

  const getNodeCategory = (type: string): string => {
    return NODE_CATEGORIES[type] ? type : "other";
  };

  const truncateLabel = (text: string, maxLength: number = 20): string => {
    const label = text.split("/").pop() || text;
    return label.length > maxLength ? label.substring(0, maxLength) + "..." : label;
  };

  const fetchGraph = async (): Promise<string> => {
    // Try to fetch from the specific graph first, then fall back to all graphs
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

  const renderGraph = (triples: any[]) => {
    if (!svgRef.current) {
      console.error("SVG ref not available");
      return;
    }

    // Detect dark mode
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#ffffff' : '#1f2937';
    const linkColor = isDark ? '#6b7280' : '#9ca3af';
    const linkLabelColor = isDark ? '#9ca3af' : '#6b7280';

    const nodes = new Map<string, NodeData>();
    const links: LinkData[] = [];
    const nodeCount = new Map<string, number>();

    triples.forEach((triple) => {
      if (triple.predicate.value !== "http://ai-act.eu/ai#hasUrn") {
        const sourceId = triple.subject.value;
        const targetId = triple.object.value;
        const predicateUri = triple.predicate.value;
        const predicateLabel = predicateUri.split("#").pop() || predicateUri.split("/").pop() || predicateUri;

        if (!nodes.has(sourceId)) {
          const type = getNodeType(sourceId, predicateUri);
          nodes.set(sourceId, {
            id: sourceId,
            type,
            category: getNodeCategory(type),
            label: truncateLabel(sourceId),
            size: 15,
          });
        }

        if (!nodes.has(targetId)) {
          // For target nodes, use the predicate to categorize what they are
          const type = getNodeType(targetId, predicateUri);
          nodes.set(targetId, {
            id: targetId,
            type,
            category: getNodeCategory(type),
            label: truncateLabel(targetId),
            size: 15,
          });
        }

        nodeCount.set(sourceId, (nodeCount.get(sourceId) || 0) + 1);
        nodeCount.set(targetId, (nodeCount.get(targetId) || 0) + 1);

        links.push({
          source: sourceId,
          target: targetId,
          predicate: predicateUri,
          predicateLabel,
        });
      }
    });

    nodeCount.forEach((count, nodeId) => {
      const node = nodes.get(nodeId);
      if (node) {
        node.size = Math.min(30, 15 + count * 2);
      }
    });

    let nodeArray = Array.from(nodes.values());
    let linksToRender = links;

    // Apply category filter
    if (activeFilter) {
      linksToRender = links.filter(
        (l) =>
          nodes.get(l.source)?.category === activeFilter ||
          nodes.get(l.target)?.category === activeFilter
      );
      const nodeIdsInLinks = new Set<string>();
      linksToRender.forEach((l) => {
        nodeIdsInLinks.add(l.source);
        nodeIdsInLinks.add(l.target);
      });
      nodeArray = nodeArray.filter((n) => nodeIdsInLinks.has(n.id));
    }

    // Apply search filter
    if (searchQuery) {
      nodeArray = nodeArray.filter((n) =>
        n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.id.toLowerCase().includes(searchQuery.toLowerCase())
      );
      linksToRender = linksToRender.filter(
        (l) =>
          nodeArray.some((n) => n.id === l.source) &&
          nodeArray.some((n) => n.id === l.target)
      );
    }

    console.log(`Rendering graph: ${nodeArray.length} nodes, ${linksToRender.length} links`);

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Get actual dimensions from SVG element
    const svgElement = svgRef.current;
    const width = svgElement.clientWidth || window.innerWidth;
    const height = svgElement.clientHeight || window.innerHeight;

    console.log(`SVG dimensions: ${width}x${height}`);

    const simulation = d3
      .forceSimulation(nodeArray as any)
      .force("link", d3.forceLink(linksToRender as any).id((d: any) => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(40));

    const g = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    const link = g
      .append("g")
      .selectAll("line")
      .data(linksToRender)
      .enter()
      .append("line")
      .attr("stroke", linkColor)
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.6)
      .attr("marker-end", "url(#arrowhead)");

    svg
      .append("defs")
      .append("marker")
      .attr("id", "arrowhead")
      .attr("markerWidth", 10)
      .attr("markerHeight", 10)
      .attr("refX", 25)
      .attr("refY", 3)
      .attr("orient", "auto")
      .append("polygon")
      .attr("points", "0 0, 10 3, 0 6")
      .attr("fill", linkColor);

    const linkLabels = g
      .append("g")
      .selectAll("text")
      .data(linksToRender)
      .enter()
      .append("text")
      .text((d) => d.predicateLabel)
      .attr("font-size", 11)
      .attr("fill", linkLabelColor)
      .attr("text-anchor", "middle")
      .attr("dy", -5);

    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodeArray)
      .enter()
      .append("circle")
      .attr("r", (d: any) => d.size)
      .attr("fill", (d: any) => NODE_CATEGORIES[d.category].color)
      .attr("stroke", isDark ? "#374151" : "#fff")
      .attr("stroke-width", 2)
      .attr("opacity", 0.85)
      .style("cursor", "pointer")
      .call(
        d3
          .drag<SVGCircleElement, any>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      )
      .on("mouseover", function () {
        d3.select(this).transition().duration(200).attr("stroke-width", 3).attr("opacity", 1);
      })
      .on("mouseout", function () {
        d3.select(this).transition().duration(200).attr("stroke-width", 2).attr("opacity", 0.85);
      });

    const text = g
      .append("g")
      .selectAll("text")
      .data(nodeArray)
      .enter()
      .append("text")
      .text((d: any) => d.label)
      .attr("font-size", 12)
      .attr("font-weight", "bold")
      .attr("text-anchor", "middle")
      .attr("fill", textColor)
      .attr("pointer-events", "none")
      .attr("dy", ".35em");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      text.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
      linkLabels
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);
    });
  };

  useEffect(() => {
    const store = graph();
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

          store.add(subject, predicate, object);
        });

        setStore(store);

        const systems = store
          .statementsMatching(undefined, sym("http://ai-act.eu/ai#hasName"))
          .map((st) => st.object.value);
        const uniqueNames = Array.from(new Set(systems));
        setSystems(uniqueNames);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Failed to load or parse RDF graph", error);
        setLoadingError(`Error loading graph: ${error instanceof Error ? error.message : "Unknown error"}`);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    if (store && selectedSystem) {
      const subjects = store
        .statementsMatching(undefined, sym("http://ai-act.eu/ai#hasName"), literal(selectedSystem))
        .map((st) => st.subject);

      const filteredTriples = store.statements.filter((st) =>
        subjects.some((subj) => subj.equals(st.subject))
      );

      renderGraph(filteredTriples);

      const subject = subjects[0];
      if (subject) {
        const get = (p: string) =>
          store.any(subject, sym(`http://ai-act.eu/ai#${p}`))?.value ?? "N/A";

        setSelectedSystemData({
          name: get("hasName"),
          riskLevel: get("hasRiskLevel"),
          purpose: store
            .each(subject, sym("http://ai-act.eu/ai#hasPurpose"))
            .map((o) => o.value)
            .join(", ") || "N/A",
          deploymentContext: store
            .each(subject, sym("http://ai-act.eu/ai#hasDeploymentContext"))
            .map((o) => o.value)
            .join(", ") || "N/A",
          trainingDataOrigin: store
            .each(subject, sym("http://ai-act.eu/ai#hasTrainingDataOrigin"))
            .map((o) => o.value)
            .join(", ") || "N/A",
          version: get("hasVersion"),
          urn: store.any(subject, sym("http://ai-act.eu/ai#hasUrn"))?.value ?? "N/A",
        });
      }
    }
  }, [selectedSystem, store, activeFilter, searchQuery]);

  return (
    <div ref={containerRef} className="w-full h-[calc(100vh-120px)] bg-white dark:bg-gray-900 text-gray-900 dark:text-white overflow-hidden flex flex-col -mx-4 -mb-4">
      {/* Header Controls */}
      <div className="relative z-10 bg-gray-50 dark:bg-gray-800 p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-3 items-center flex-wrap">
          <select
            onChange={(e) => setSelectedSystem(e.target.value)}
            value={selectedSystem || ""}
            className="p-2 text-sm rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Seleccionar Sistema --</option>
            {systems.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Buscar nodos..."
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
              Todos
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
        </div>
      </div>

      {/* Graph Container */}
      <div className="relative flex-1 w-full h-full">
        {isLoading && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center z-20">
            <p className="text-lg mb-2 text-gray-700 dark:text-gray-300">Cargando datos del grafo...</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Obteniendo sistemas del almacén RDF</p>
          </div>
        )}

        {loadingError && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-600 text-red-700 dark:text-red-400 p-5 rounded-lg max-w-md text-center z-20">
            <p className="text-base font-semibold mb-2">Error cargando el grafo</p>
            <p className="text-sm">{loadingError}</p>
            <p className="text-xs mt-3 text-red-600 dark:text-red-500">
              Revisa la consola para más detalles
            </p>
          </div>
        )}

        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          className={`${isLoading || loadingError ? "hidden" : "block"} bg-gray-100 dark:bg-gray-950`}
        ></svg>

        {selectedSystemData && (
          <div className="absolute bottom-5 right-5 w-[360px] max-h-[400px] bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-4 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-auto z-10">
            <h3 className="text-base font-bold mb-3 pb-2 border-b-2 border-blue-500">
              {selectedSystemData.name}
            </h3>
            <div className="text-sm leading-relaxed space-y-1">
              <p><strong>Nivel de Riesgo:</strong> {selectedSystemData.riskLevel}</p>
              <p><strong>Propósito(s):</strong> {selectedSystemData.purpose}</p>
              <p><strong>Contexto(s) de Despliegue:</strong> {selectedSystemData.deploymentContext}</p>
              <p><strong>Origen de Datos:</strong> {selectedSystemData.trainingDataOrigin}</p>
              <p><strong>Versión:</strong> {selectedSystemData.version}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                <strong>URN:</strong> <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{selectedSystemData.urn}</code>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
