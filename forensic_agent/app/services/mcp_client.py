"""MCP Client for SPARQL queries via MCP Server using FastMCP Client"""

import os
import json
from typing import Dict, List, Optional, Any
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPClient:
    """
    Client to interact with MCP SPARQL Server via Streamable HTTP transport.
    Uses FastMCP Client for proper MCP protocol communication.
    """

    def __init__(self, mcp_url: Optional[str] = None):
        """
        Initialize MCP client.

        Args:
            mcp_url: URL of MCP server (default from env MCP_SERVER_URL)
        """
        base_url = mcp_url or os.getenv("MCP_SERVER_URL", "http://mcp_sparql:8080")
        # Ensure URL ends with /mcp for streamable-http transport
        if not base_url.endswith("/mcp"):
            base_url = f"{base_url}/mcp"
        self.mcp_url = base_url
        # Create transport explicitly for streamable HTTP
        self.transport = StreamableHttpTransport(url=self.mcp_url)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool using FastMCP Client.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response
        """
        try:
            async with Client(self.transport) as client:
                result = await client.call_tool(tool_name, arguments)
                return self._parse_result(result)
        except Exception as e:
            return {"error": str(e)}

    async def query_ontology(self, query: str) -> Dict:
        """Execute a SPARQL query against the ontology."""
        return await self.call_tool("query_ontology", {"query": query})

    async def get_requirements_for_system(
        self,
        purpose: str,
        contexts: Optional[List[str]] = None
    ) -> Dict:
        """Get EU AI Act requirements for a system."""
        return await self.call_tool("get_requirements_for_system", {
            "purpose": purpose,
            "contexts": contexts or []
        })

    async def determine_risk_level(
        self,
        purpose: str,
        contexts: Optional[List[str]] = None
    ) -> Dict:
        """Determine EU AI Act risk level."""
        return await self.call_tool("determine_risk_level", {
            "purpose": purpose,
            "contexts": contexts or []
        })

    async def get_ontology_stats(self) -> Dict:
        """Get ontology statistics."""
        return await self.call_tool("get_ontology_stats", {})

    async def query_iso_mappings(self, requirement: str) -> Dict:
        """Query ISO 42001 mappings for a requirement."""
        return await self.call_tool("query_iso_mappings", {"requirement": requirement})

    async def query_nist_mappings(self, requirement: str) -> Dict:
        """Query NIST AI RMF mappings for a requirement."""
        return await self.call_tool("query_nist_mappings", {"requirement": requirement})

    async def get_inference_rules(self) -> Dict:
        """
        Get all EU AI Act inference rules from the reasoning engine.

        Returns:
            Dict with condition_consequence_rules, navigation_rules, and metadata
        """
        return await self.call_tool("get_inference_rules", {})

    async def explain_rule(self, rule_id: str) -> Dict:
        """
        Get detailed explanation of a specific inference rule.

        Args:
            rule_id: Rule identifier (e.g., rule13_flops_systemic_risk)

        Returns:
            Dict with rule details and human-readable interpretation
        """
        return await self.call_tool("explain_rule", {"rule_id": rule_id})

    def _parse_result(self, result: Any) -> Dict:
        """Parse MCP tool result."""
        if result is None:
            return {"error": "No result returned"}

        # FastMCP returns content directly or as list of content blocks
        if isinstance(result, list):
            # Extract text content from content blocks
            for item in result:
                if hasattr(item, 'text'):
                    try:
                        return json.loads(item.text)
                    except json.JSONDecodeError:
                        return {"raw": item.text}
            return {"raw": str(result)}

        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"raw": result}

        if isinstance(result, dict):
            return result

        # Handle content object with text attribute
        if hasattr(result, 'text'):
            try:
                return json.loads(result.text)
            except json.JSONDecodeError:
                return {"raw": result.text}

        return {"raw": str(result)}

    async def health_check(self) -> bool:
        """Check if MCP server is available by listing tools."""
        try:
            async with Client(self.transport) as client:
                tools = await client.list_tools()
                return len(tools) > 0
        except Exception as e:
            print(f"MCP health check failed: {e}")
            return False

    async def list_tools(self) -> List[str]:
        """List available MCP tools."""
        try:
            async with Client(self.transport) as client:
                tools = await client.list_tools()
                return [t.name for t in tools]
        except Exception as e:
            print(f"Failed to list MCP tools: {e}")
            return []
