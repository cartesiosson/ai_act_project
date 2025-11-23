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
      .attr("stroke", "#888")
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
      .attr("fill", "#888");

    const linkLabels = g
      .append("g")
      .selectAll("text")
      .data(linksToRender)
      .enter()
      .append("text")
      .text((d) => d.predicateLabel)
      .attr("font-size", 11)
      .attr("fill", "#bbb")
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
      .attr("stroke", "#fff")
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
      .attr("fill", "white")
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
    <div ref={containerRef} style={{ width: "100vw", height: "calc(100vh - 64px)", background: "#1a1a1a", color: "white", overflow: "hidden", display: "flex", flexDirection: "column", marginLeft: "-16px", marginRight: "-16px", marginBottom: "-16px" }}>
      <div style={{ position: "relative", top: 0, left: 0, right: 0, zIndex: 10, background: "rgba(26, 26, 26, 0.95)", padding: "12px", borderBottom: "1px solid #444" }}>
        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
          <select
            onChange={(e) => setSelectedSystem(e.target.value)}
            value={selectedSystem || ""}
            style={{
              padding: "8px 12px",
              fontSize: "14px",
              borderRadius: "6px",
              backgroundColor: "#333",
              color: "white",
              border: "1px solid #555",
            }}
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
            placeholder="🔍 Buscar nodos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              padding: "8px 12px",
              fontSize: "14px",
              borderRadius: "6px",
              backgroundColor: "#333",
              color: "white",
              border: "1px solid #555",
              minWidth: "150px",
            }}
          />

          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            <button
              onClick={() => setActiveFilter(null)}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                borderRadius: "4px",
                backgroundColor: activeFilter === null ? "#3b82f6" : "#444",
                color: "white",
                border: "1px solid #555",
                cursor: "pointer",
              }}
            >
              Todos
            </button>
            {Object.entries(NODE_CATEGORIES).map(([key, { icon, label }]) => (
              <button
                key={key}
                onClick={() => setActiveFilter(activeFilter === key ? null : key)}
                style={{
                  padding: "6px 12px",
                  fontSize: "12px",
                  borderRadius: "4px",
                  backgroundColor: activeFilter === key ? NODE_CATEGORIES[key].color : "#444",
                  color: "white",
                  border: `1px solid ${NODE_CATEGORIES[key].color}`,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                title={label}
              >
                {icon} {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ position: "relative", flex: 1, width: "100%", height: "100%" }}>
        {isLoading && (
          <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
            color: "white",
            zIndex: 20
          }}>
            <p style={{ fontSize: "18px", marginBottom: "10px" }}>⏳ Loading graph data...</p>
            <p style={{ fontSize: "14px", color: "#aaa" }}>Fetching systems from RDF store</p>
          </div>
        )}

        {loadingError && (
          <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "rgba(220, 38, 38, 0.1)",
            border: "1px solid #dc2626",
            color: "#fca5a5",
            padding: "20px",
            borderRadius: "8px",
            maxWidth: "500px",
            textAlign: "center",
            zIndex: 20
          }}>
            <p style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "8px" }}>⚠️ Error Loading Graph</p>
            <p style={{ fontSize: "14px" }}>{loadingError}</p>
            <p style={{ fontSize: "12px", marginTop: "12px", color: "#fda29b" }}>
              Check the console for more details
            </p>
          </div>
        )}

        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          style={{
            display: isLoading || loadingError ? "none" : "block",
            background: "#0f0f0f"
          }}
        ></svg>

        {selectedSystemData && (
          <div style={{
            position: "absolute",
            bottom: "20px",
            right: "20px",
            width: "360px",
            maxHeight: "400px",
            background: "rgba(255, 255, 255, 0.95)",
            color: "#1a1a1a",
            padding: "16px",
            borderRadius: "8px",
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.3)",
            overflow: "auto",
            zIndex: 5,
          }}>
            <h3 style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "12px", borderBottom: "2px solid #3b82f6", paddingBottom: "8px" }}>
              {selectedSystemData.name}
            </h3>
            <div style={{ fontSize: "13px", lineHeight: "1.6" }}>
              <p><strong>Nivel de Riesgo:</strong> {selectedSystemData.riskLevel}</p>
              <p><strong>Propósito(s):</strong> {selectedSystemData.purpose}</p>
              <p><strong>Contexto(s) de Despliegue:</strong> {selectedSystemData.deploymentContext}</p>
              <p><strong>Origen de Datos:</strong> {selectedSystemData.trainingDataOrigin}</p>
              <p><strong>Versión:</strong> {selectedSystemData.version}</p>
              <p style={{ fontSize: "11px", color: "#666", marginTop: "8px", paddingTop: "8px", borderTop: "1px solid #ccc" }}>
                <strong>URN:</strong> <code>{selectedSystemData.urn}</code>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
