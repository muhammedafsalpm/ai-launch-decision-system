"""Orchestrator - Coordinates all agents and produces final decision"""

import json
from typing import Dict, Any
from agents.data_analyst import DataAnalystAgent
from agents.marketing_agent import MarketingAgent
from agents.pm_agent import PMAgent
from agents.risk_agent import RiskAgent
from utils.llm_client import LLMClient


class Orchestrator:
    """Coordinates all agents and manages the war room workflow"""
    
    def __init__(self):
        self.data_agent = DataAnalystAgent()
        self.marketing_agent = MarketingAgent()
        self.pm_agent = PMAgent()
        self.risk_agent = RiskAgent()
        self.llm = LLMClient()
    
    def log(self, message: str):
        """Orchestrator-specific logging"""
        print(f"[ORCHESTRATOR] {message}")
    
    def run(self, metrics: Dict, feedback: list, release_notes: str) -> Dict[str, Any]:
        """
        Execute the complete war room workflow.
        
        Args:
            metrics: Metrics data dictionary
            feedback: List of feedback entries
            release_notes: Release notes string
            
        Returns:
            Final decision dictionary
        """
        self.log("=" * 60)
        self.log("WAR ROOM SIMULATION STARTING")
        self.log("=" * 60)
        
        context = {
            "metrics": metrics,
            "feedback": feedback,
            "release_notes": release_notes
        }
        
        # Step 1: Data Analyst
        self.log("Dispatching to Data Analyst Agent...")
        data_result = self.data_agent.analyze(context)
        context["data_analyst"] = data_result
        
        # Step 2: Marketing Agent
        self.log("Dispatching to Marketing Agent...")
        marketing_result = self.marketing_agent.analyze(context)
        context["marketing"] = marketing_result
        
        # Step 3: PM Agent
        self.log("Dispatching to Product Manager Agent...")
        pm_result = self.pm_agent.analyze(context)
        context["pm"] = pm_result
        
        # Step 4: Risk Agent
        self.log("Dispatching to Risk Agent...")
        risk_result = self.risk_agent.analyze(context)
        context["risk"] = risk_result
        
        # Step 5: Final Decision
        self.log("All agents have reported. Making final decision...")
        final_decision = self._make_decision(context)
        
        return final_decision
    
    def _make_decision(self, context: Dict) -> Dict[str, Any]:
        """Generate final structured decision using LLM"""
        
        system_prompt = """You are the war room coordinator making the final launch decision.
        
        Based on all agent inputs, produce a structured JSON decision.
        
        Decision options: "Proceed", "Pause", or "Roll Back"
        
        Return valid JSON with these exact keys:
        - decision: string
        - rationale: string (include specific metric references and feedback summary)
        - risk_register: array of objects with "risk" and "mitigation" keys
        - action_plan: array of objects with "action", "owner", and "timeline" keys
        - communication_plan: object with "internal" and "external" keys
        - confidence_score: number between 0 and 1
        - confidence_increase_condition: string
        
        Be specific and actionable in your recommendations."""
        
        user_prompt = f"""
        CONTEXT SUMMARY:
        
        Feature: {context.get('metrics', {}).get('feature', 'Unknown')}
        Launch Day: {context.get('metrics', {}).get('launch_day', 'Unknown')}
        
        DATA ANALYST FINDINGS:
        {context['data_analyst'].get('summary', '')}
        - Error Rate: {context['data_analyst'].get('error_analysis', {}).get('pct_change', 0)}% change
        - Latency p95: {context['data_analyst'].get('latency_analysis', {}).get('pct_change', 0)}% change
        - DAU: {context['data_analyst'].get('dau_analysis', {}).get('pct_change', 0)}% change
        - Crash Rate: {context['data_analyst'].get('crash_analysis', {}).get('pct_change', 0)}% change
        
        MARKETING FINDINGS:
        {context['marketing'].get('summary', '')}
        - Sentiment Score: {context['marketing'].get('sentiment_analysis', {}).get('sentiment_score', 0)}
        - Primary Issue: {context['marketing'].get('top_issues', {}).get('primary_issue', 'unknown')}
        
        PM ASSESSMENT:
        {context['pm'].get('summary', '')}
        - Success Criteria: {context['pm'].get('success_criteria_check', {})}
        
        RISK ASSESSMENT:
        {context['risk'].get('challenges', '')}
        
        Based on ALL evidence above, what is your final decision?
        """
        
        response = self.llm.chat_completion(
            system_prompt, 
            user_prompt, 
            temperature=0.2,
            response_format="json_object"
        )
        
        try:
            decision = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            decision = {
                "decision": "PAUSE",
                "rationale": "Multiple critical metrics showing anomalies with negative user sentiment. Error parsing LLM response.",
                "risk_register": [
                    {"risk": "System instability", "mitigation": "Rollback via feature flag"}
                ],
                "action_plan": [
                    {"action": "Investigate root cause", "owner": "Engineering", "timeline": "4 hours"}
                ],
                "communication_plan": {
                    "internal": "War room reconvene in 2 hours",
                    "external": "Acknowledge issues, commit to fix"
                },
                "confidence_score": 0.7,
                "confidence_increase_condition": "Root cause identified and fix validated"
            }
        
        self.log(f"Final Decision: {decision.get('decision', 'UNKNOWN')}")
        return decision
