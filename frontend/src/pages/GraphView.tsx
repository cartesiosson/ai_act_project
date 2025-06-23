import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { graph, NamedNode, literal, sym } from "rdflib";
import { Parser as N3Parser } from "n3";

export default function GraphView() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [systems, setSystems] = useState<string[]>([]);
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [selectedSystemData, setSelectedSystemData] = useState<any | null>(null);
  const [store, setStore] = useState<any>(null);

  const fetchGraph = async (): Promise<string> => {
    const query = `
      CONSTRUCT { ?s ?p ?o }
      WHERE { GRAPH <http://ai-act.eu/ontology/data> { ?s ?p ?o } }
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
    const nodes = new Set<string>();
    const links: { source: string; target: string; predicate: string }[] = [];

    triples.forEach((triple) => {
      if (triple.predicate.value !== "http://ai-act.eu/ai#hasUrn") {
        nodes.add(triple.subject.value);
        nodes.add(triple.object.value);
        links.push({
          source: triple.subject.value,
          target: triple.object.value,
          predicate: triple.predicate.value,
        });
      }
    });

    const nodeArray = Array.from(nodes).map((id) => ({ id }));
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = window.innerWidth;
    const height = window.innerHeight;

    const simulation = d3
      .forceSimulation(nodeArray)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#aaa");

    const linkLabels = svg
      .append("g")
      .selectAll("text")
      .data(links)
      .enter()
      .append("text")
      .text((d) => d.predicate.split("#").pop() || d.predicate.split("/").pop())
      .attr("font-size", 10)
      .attr("fill", "white");

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodeArray)
      .enter()
      .append("circle")
      .attr("r", (d) => (d.id.startsWith("urn:uuid:") ? 20 : 10))
      .attr("fill", "#69b3a2")
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
      );

    const text = svg
      .append("g")
      .selectAll("text")
      .data(nodeArray)
      .enter()
      .append("text")
      .text((d) =>
        d.id.startsWith("urn:uuid:") ? "urn" : d.id.split("/").pop()?.substring(0, 10) || d.id
      )
      .attr("font-size", 10)
      .attr("text-anchor", (d) => (d.id.startsWith("urn:uuid:") ? "middle" : "start"))
      .attr("fill", (d) => (d.id.startsWith("urn:uuid:") ? "black" : "white"))
      .attr("dx", (d) => (d.id.startsWith("urn:uuid:") ? 0 : 12))
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

    fetchGraph()
      .then((ttlData) => {
        const n3Parser = new N3Parser();
        const triples = n3Parser.parse(ttlData);

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
      })
      .catch((error) => {
        console.error("Failed to load or parse RDF graph", error);
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
  }, [selectedSystem, store]);

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#222", color: "white" }}>
      <select
        onChange={(e) => setSelectedSystem(e.target.value)}
        value={selectedSystem || ""}
        style={{
          margin: "10px",
          padding: "8px 12px",
          fontSize: "16px",
          borderRadius: "8px",
          backgroundColor: "#333",
          color: "white",
          border: "1px solid #555",
          appearance: "none",
          WebkitAppearance: "none",
          MozAppearance: "none",
        }}
      >
        <option value="">-- Select Intelligent System --</option>
        {systems.map((name) => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>

      {selectedSystemData && (
        <div className="m-4 p-4 rounded shadow bg-white text-black max-w-xl">
          <h3 className="text-lg font-bold mb-2">{selectedSystemData.name}</h3>
          <p><strong>Risk Level:</strong> {selectedSystemData.riskLevel}</p>
          <p><strong>Purpose(s):</strong> {selectedSystemData.purpose}</p>
          <p><strong>Deployment Context(s):</strong> {selectedSystemData.deploymentContext}</p>
          <p><strong>Training Data Origin(s):</strong> {selectedSystemData.trainingDataOrigin}</p>
          <p><strong>Version:</strong> {selectedSystemData.version}</p>
          <p className="text-sm text-gray-600">
            <strong>URN:</strong> {selectedSystemData.urn}
          </p>
        </div>
      )}

      <svg ref={svgRef} width="100%" height="100%"></svg>
    </div>
  );
}
