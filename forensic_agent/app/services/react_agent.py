"""
LangGraph ReAct Agent for Forensic Compliance Analysis

This agent uses a Thought -> Action -> Observation loop to dynamically
decide which tools to invoke based on the incident properties.
"""

import os
import json
from typing import Dict, List, Any, Optional, Annotated, TypedDict, AsyncGenerator
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .sparql_queries import ForensicSPARQLService
from .incident_extractor import IncidentExtractorService
from ..models.forensic_report import StreamEvent, StreamEventType, ConversationMessage


# Agent State
class AgentState(TypedDict):
    """State maintained throughout the agent execution"""
    messages: Annotated[List[BaseMessage], add_messages]
    narrative: str
    extracted_incident: Optional[Dict]
    eu_requirements: Optional[Dict]
    iso_mappings: Optional[Dict]
    nist_mappings: Optional[Dict]
    compliance_gaps: Optional[Dict]
    inference_rules: Optional[Dict]
    final_report: Optional[str]
    current_step: str
    steps_executed: List[str]
    jurisdiction: str
    risk_level: str


class ForensicReActAgent:
    """
    ReAct Agent for forensic compliance analysis using LangGraph.

    Uses Ollama with Llama 3.2 for reasoning and dynamically decides
    which regulatory frameworks to query based on incident properties.
    """

    def __init__(
        self,
        sparql_service: ForensicSPARQLService,
        extractor_service: IncidentExtractorService,
        ollama_base_url: Optional[str] = None,
        model_name: str = "llama3.2"
    ):
        self.sparql = sparql_service
        self.extractor = extractor_service
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        self.model_name = model_name

        # Initialize LLM
        self.llm = ChatOllama(
            base_url=self.ollama_base_url,
            model=self.model_name,
            temperature=0.1,  # Low for deterministic reasoning
        )

        # Build tools and graph
        self._tools = self._create_tools()
        self._graph = self._build_graph()

        # For streaming events
        self._stream_events: List[StreamEvent] = []

    def _create_tools(self) -> List:
        """Create LangChain tools wrapping our services"""

        sparql = self.sparql
        extractor = self.extractor

        @tool
        async def extract_incident_properties(narrative: str) -> str:
            """
            Extract structured properties from an incident narrative using LLM.
            Returns system properties, incident classification, timeline, and confidence scores.
            Use this FIRST to understand what the incident is about.
            """
            try:
                incident = await extractor.extract_incident(narrative)
                return json.dumps(incident.dict(), indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        async def query_eu_ai_act_requirements(
            purpose: str,
            contexts: str,
            data_types: str
        ) -> str:
            """
            Query EU AI Act mandatory requirements based on system purpose and context.
            Returns risk level, activated criteria, and required compliance measures.
            Use this for systems operating in EU jurisdiction or globally.

            Args:
                purpose: Primary purpose (e.g., BiometricIdentification, GenerativeAIContentCreation)
                contexts: Comma-separated deployment contexts (e.g., PublicSpaces,HighVolume)
                data_types: Comma-separated data types (e.g., PersonalData,BiometricData)
            """
            try:
                contexts_list = [c.strip() for c in contexts.split(",") if c.strip()]
                data_types_list = [d.strip() for d in data_types.split(",") if d.strip()]

                result = await sparql.query_mandatory_requirements(
                    purpose=purpose,
                    contexts=contexts_list,
                    data_types=data_types_list
                )
                return json.dumps(result, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        async def query_iso_42001_mappings(requirement_uris: str) -> str:
            """
            Query ISO 42001 control mappings for EU AI Act requirements.
            Use this when the organization needs ISO certification guidance.

            Args:
                requirement_uris: Comma-separated EU AI Act requirement URIs
            """
            try:
                uris = [u.strip() for u in requirement_uris.split(",") if u.strip()]
                result = await sparql.query_iso_42001_mappings(uris)
                return json.dumps({
                    "total_mapped": len(result),
                    "mappings": result
                }, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        async def query_nist_ai_rmf_mappings(
            requirement_uris: str,
            jurisdiction: str = "GLOBAL"
        ) -> str:
            """
            Query NIST AI Risk Management Framework mappings.
            Use this for US jurisdiction or for global compliance frameworks.

            Args:
                requirement_uris: Comma-separated requirement URIs
                jurisdiction: US, EU, or GLOBAL
            """
            try:
                uris = [u.strip() for u in requirement_uris.split(",") if u.strip()]
                result = await sparql.query_nist_ai_rmf_mappings(uris, jurisdiction=jurisdiction)
                return json.dumps({
                    "total_mapped": len(result),
                    "jurisdiction": jurisdiction,
                    "mappings": result
                }, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        async def analyze_compliance_gaps(
            requirement_uris: str,
            incident_json: str
        ) -> str:
            """
            Analyze compliance gaps between mandatory requirements and incident properties.
            Returns compliance ratio, missing requirements, and critical gaps.

            Args:
                requirement_uris: Comma-separated mandatory requirement URIs
                incident_json: JSON string of extracted incident properties
            """
            try:
                uris = [u.strip() for u in requirement_uris.split(",") if u.strip()]
                incident_props = json.loads(incident_json)

                result = await sparql.analyze_compliance_gaps(
                    mandatory_requirements=uris,
                    incident_properties=incident_props
                )
                return json.dumps(result, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        async def get_applicable_inference_rules(incident_json: str) -> str:
            """
            Get applicable EU AI Act inference rules based on incident properties.
            Returns rules that triggered and their explanations.
            Use this to understand why certain requirements apply.

            Args:
                incident_json: JSON string of extracted incident properties
            """
            try:
                incident_props = json.loads(incident_json)
                result = await sparql.get_applicable_rules(incident_props)
                return json.dumps(result, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        def generate_forensic_report(
            system_name: str,
            organization: str,
            risk_level: str,
            requirements_count: int,
            compliance_ratio: float,
            critical_gaps: str,
            jurisdiction: str
        ) -> str:
            """
            Generate the final forensic compliance report.
            Use this as the FINAL step after gathering all analysis data.

            Args:
                system_name: Name of the AI system
                organization: Organization name
                risk_level: EU AI Act risk classification
                requirements_count: Number of mandatory requirements
                compliance_ratio: Ratio of compliant requirements (0.0 to 1.0)
                critical_gaps: Comma-separated critical compliance gaps
                jurisdiction: Primary jurisdiction (EU, US, GLOBAL)
            """
            gaps_list = [g.strip() for g in critical_gaps.split(",") if g.strip()]

            severity = "CRITICAL" if compliance_ratio < 0.3 else "HIGH" if compliance_ratio < 0.5 else "MEDIUM" if compliance_ratio < 0.7 else "LOW"

            report = f"""# FORENSIC COMPLIANCE AUDIT REPORT

## Executive Summary
- **System**: {system_name}
- **Organization**: {organization}
- **Risk Classification**: {risk_level}
- **Compliance Status**: {severity}
- **Compliance Ratio**: {compliance_ratio:.1%}
- **Jurisdiction**: {jurisdiction}

## Regulatory Analysis
- **Mandatory Requirements**: {requirements_count}
- **Critical Gaps Identified**: {len(gaps_list)}

## Critical Compliance Gaps
{chr(10).join(f'- {gap}' for gap in gaps_list) if gaps_list else '- No critical gaps identified'}

## Recommendations
1. {"Immediate remediation required for critical gaps" if severity in ["CRITICAL", "HIGH"] else "Address identified gaps in compliance roadmap"}
2. {"Consider engaging legal counsel for regulatory risk" if risk_level == "HighRisk" else "Continue monitoring regulatory developments"}
3. Document all AI governance measures

---
*Report generated: {datetime.utcnow().isoformat()}*
*Analysis method: ReAct Agent with LangGraph*
"""
            return report

        return [
            extract_incident_properties,
            query_eu_ai_act_requirements,
            query_iso_42001_mappings,
            query_nist_ai_rmf_mappings,
            analyze_compliance_gaps,
            get_applicable_inference_rules,
            generate_forensic_report
        ]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph ReAct agent graph"""

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(self._tools)

        # Define the reasoning node
        async def reasoning_node(state: AgentState) -> Dict:
            """Agent reasoning - decides what to do next"""
            messages = state["messages"]
            response = await llm_with_tools.ainvoke(messages)
            return {"messages": [response]}

        # Tool execution node
        tool_node = ToolNode(self._tools)

        # Routing function
        def should_continue(state: AgentState) -> str:
            """Determine if agent should continue or end"""
            messages = state["messages"]
            last_message = messages[-1]

            # If no tool calls, we're done
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return "end"

            return "tools"

        # Build graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("tools", tool_node)

        # Set entry point
        workflow.set_entry_point("reasoning")

        # Add edges
        workflow.add_conditional_edges(
            "reasoning",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "reasoning")

        return workflow.compile()

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the ReAct agent"""
        return """You are a forensic AI compliance analyst. You MUST use the provided tools to analyze incidents.

CRITICAL: You have access to function/tool calling. When you want to use a tool, you MUST invoke it directly - do NOT write code or describe what you would do.

## Your Workflow (follow this EXACTLY):

STEP 1: Call extract_incident_properties with the narrative
STEP 2: Based on jurisdiction from step 1:
  - If EU or GLOBAL: call query_eu_ai_act_requirements
  - If US: call query_nist_ai_rmf_mappings
STEP 3: Call analyze_compliance_gaps with the requirement URIs
STEP 4: Call generate_forensic_report with the gathered data

## Tool Usage Rules:
- You MUST call tools using the function calling mechanism
- Do NOT write Python code - just invoke the tools directly
- After each tool result, briefly note what you learned, then call the next tool
- Keep your text responses SHORT - focus on using tools

## Required Tool Sequence:
1. extract_incident_properties(narrative="...") -> Get system info and jurisdiction
2. query_eu_ai_act_requirements(purpose="...", contexts="...", data_types="...") -> Get requirements
3. analyze_compliance_gaps(requirement_uris="...", incident_json="...") -> Find gaps
4. generate_forensic_report(...) -> Create final report

START NOW by calling extract_incident_properties with the incident narrative."""

    async def analyze_incident_streaming(
        self,
        narrative: str
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Run the ReAct agent with streaming events.

        Yields StreamEvent objects for real-time visibility into agent reasoning.
        """
        self._stream_events = []

        # Initial state with system prompt
        system_prompt = self._get_system_prompt()
        initial_state: AgentState = {
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analyze this AI incident:\n\n{narrative}")
            ],
            "narrative": narrative,
            "extracted_incident": None,
            "eu_requirements": None,
            "iso_mappings": None,
            "nist_mappings": None,
            "compliance_gaps": None,
            "inference_rules": None,
            "final_report": None,
            "current_step": "starting",
            "steps_executed": [],
            "jurisdiction": "GLOBAL",
            "risk_level": "Unknown"
        }

        # Emit start event
        yield StreamEvent(
            event_type=StreamEventType.STEP_START,
            step_name="ReAct Agent Starting",
            data={"model": self.model_name},
            progress_percent=0.0
        )

        # Emit system prompt for visibility
        yield StreamEvent(
            event_type=StreamEventType.LLM_PROMPT,
            step_number=0,
            step_name="System Prompt",
            message=ConversationMessage(
                role="system",
                content=f"**System Prompt loaded** ({len(system_prompt)} chars)\n\nAgent configured with 7 tools for forensic analysis."
            ),
            progress_percent=5.0
        )

        step_count = 0
        max_steps = 20  # Safety limit

        try:
            # Stream through graph execution
            async for event in self._graph.astream(initial_state):
                step_count += 1

                if step_count > max_steps:
                    yield StreamEvent(
                        event_type=StreamEventType.ERROR,
                        step_name="Max steps reached",
                        data={"error": "Agent exceeded maximum step limit"}
                    )
                    break

                # Process different event types
                for node_name, node_output in event.items():
                    if node_name == "reasoning":
                        # Agent is thinking
                        messages = node_output.get("messages", [])
                        if messages:
                            last_msg = messages[-1]

                            # Emit thought
                            yield StreamEvent(
                                event_type=StreamEventType.LLM_RESPONSE,
                                step_number=step_count,
                                step_name="Agent Reasoning",
                                message=ConversationMessage(
                                    role="assistant",
                                    content=last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                                ),
                                progress_percent=min(step_count * 10, 90)
                            )

                            # Check for tool calls
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    yield StreamEvent(
                                        event_type=StreamEventType.SPARQL_QUERY,
                                        step_number=step_count,
                                        step_name=f"Calling: {tc['name']}",
                                        message=ConversationMessage(
                                            role="tool",
                                            content=f"**Tool Call:** {tc['name']}\n**Args:** {json.dumps(tc['args'], indent=2)}"
                                        )
                                    )

                    elif node_name == "tools":
                        # Tool execution result
                        messages = node_output.get("messages", [])
                        for msg in messages:
                            if isinstance(msg, ToolMessage):
                                yield StreamEvent(
                                    event_type=StreamEventType.SPARQL_RESULT,
                                    step_number=step_count,
                                    step_name=f"Tool Result",
                                    message=ConversationMessage(
                                        role="tool",
                                        content=f"**Result:**\n```json\n{msg.content[:1000]}{'...' if len(msg.content) > 1000 else ''}\n```"
                                    )
                                )

            # Final event
            yield StreamEvent(
                event_type=StreamEventType.STEP_COMPLETE,
                step_name="Analysis Complete",
                progress_percent=100.0,
                data={"total_steps": step_count}
            )

        except Exception as e:
            yield StreamEvent(
                event_type=StreamEventType.ERROR,
                step_name="Agent Error",
                data={"error": str(e)}
            )

    async def analyze_incident(self, narrative: str) -> Dict:
        """
        Run the ReAct agent and return structured result.

        This is a non-streaming version for simple API calls.
        """
        result = {
            "status": "COMPLETED",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "agent_type": "react",
            "model": self.model_name
        }

        # Collect all events
        events = []
        async for event in self.analyze_incident_streaming(narrative):
            events.append(event)

            # Extract final report from events
            if event.message and "FORENSIC COMPLIANCE AUDIT REPORT" in event.message.content:
                result["report"] = event.message.content

        result["events_count"] = len(events)

        return result
