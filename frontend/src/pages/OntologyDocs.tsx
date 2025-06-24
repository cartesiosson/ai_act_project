export default function OntologyDocs() {
  const locale = navigator.language.startsWith("es") ? "es" : "en";
  const docsUrl = `http://localhost/docs/index-${locale}.html`;

  return (
    <div className="w-full h-[calc(100vh-4rem)]"> {/* Ajusta 4rem si tu navbar tiene otra altura */}
      <iframe
        src={docsUrl}
        className="w-full h-full border-0"
        title="Ontology Documentation"
      />
    </div>
  );
}