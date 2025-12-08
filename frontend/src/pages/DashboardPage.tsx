import { useEffect, useState } from "react";
import Markdown from "react-markdown";

export default function DashboardPage() {
  const [welcomeContent, setWelcomeContent] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadWelcome() {
      try {
        const response = await fetch("/Welcome2SERAMIS.md");
        if (response.ok) {
          const text = await response.text();
          setWelcomeContent(text);
        }
      } catch (error) {
        console.error("Failed to load welcome content:", error);
      } finally {
        setLoading(false);
      }
    }
    loadWelcome();
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6 text-gray-900 dark:text-white">
      {/* Welcome Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Welcome to the Semantic Regulation Intelligence System
        </h1>
        <p className="text-2xl font-semibold text-blue-600 dark:text-blue-400">
          SERAMIS
        </p>
      </div>

      {/* Logo */}
      <div className="flex justify-center mb-8">
        <img
          src="/seramis-logo.svg"
          alt="SERAMIS Logo"
          className="h-20 object-contain"
        />
      </div>

      {/* Markdown Content */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8">
        {loading ? (
          <p className="text-center text-gray-500 dark:text-gray-400">Loading...</p>
        ) : (
          <div className="prose prose-gray dark:prose-invert max-w-none">
            <Markdown
              components={{
                h2: ({ children }) => (
                  <h2 className="text-2xl font-bold mt-6 mb-4 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-xl font-semibold mt-5 mb-3 text-gray-800 dark:text-gray-200">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-6 space-y-3 mb-4 text-gray-700 dark:text-gray-300">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-6 space-y-3 mb-4 text-gray-700 dark:text-gray-300">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="pl-2">{children}</li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900 dark:text-white">
                    {children}
                  </strong>
                ),
                hr: () => (
                  <hr className="my-6 border-gray-300 dark:border-gray-600" />
                ),
                em: ({ children }) => (
                  <em className="italic text-gray-600 dark:text-gray-400">
                    {children}
                  </em>
                ),
              }}
            >
              {welcomeContent}
            </Markdown>
          </div>
        )}
      </div>

      {/* Technology Logos */}
      <div className="mt-8">
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-4">
          Powered by
        </p>
        <div className="flex justify-center items-start gap-8">
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/react.svg"
              alt="React"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">React 18</span>
          </div>
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/python.svg"
              alt="Python"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Python 3.11</span>
          </div>
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/fastapi.png"
              alt="FastAPI"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">FastAPI 0.124</span>
          </div>
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/mongodb.svg"
              alt="MongoDB"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">MongoDB 7</span>
          </div>
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/jena.png"
              alt="Apache Jena Fuseki"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Jena 5.2</span>
          </div>
          <div className="flex flex-col items-center">
            <img
              src="/tech-logos/ollama.png"
              alt="Ollama"
              className="h-10 w-10 object-contain"
            />
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Ollama + Llama3</span>
          </div>
        </div>
      </div>
    </div>
  );
}
