"""Risk/Critic Agent - Challenges assumptions and identifies risks"""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Challenges assumptions, highlights risks, and requests additional evidence"""
    
    def __init__(self):
        super().__init__(
            name="RiskAgent",
            role="Challenges assumptions and identifies blind spots"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Collect all previous agent outputs
        data = context.get("data_analyst", {})
        marketing = context.get("marketing", {})
        pm = context.get("pm", {})
        
        self.log("Challenging assumptions from all agents")
        
        system_prompt = """You are a Risk/Critic in a product war room.

IMPORTANT: Respond in 3-4 sentences only. Challenge something specific.

Focus on:
1. One assumption being made
2. One blind spot
3. Worst-case scenario

Example: "Assuming crash is from new code, but could be third-party API. Blind spot: payment failures not investigated. Worst case: data corruption."
        """
        
        user_prompt = f"""
        Review all agent assessments:
        
        DATA ANALYST: {data.get('summary', '')}
        Key metrics: Error rate {data.get('error_analysis', {}).get('pct_change', 0)}% change,
        Latency {data.get('latency_analysis', {}).get('pct_change', 0)}% change
        
        MARKETING: {marketing.get('summary', '')}
        Sentiment score: {marketing.get('sentiment_analysis', {}).get('sentiment_score', 0)}
        
        PM ASSESSMENT: {pm.get('summary', '')}
        Success criteria status: {pm.get('success_criteria_check', {})}
        
        Questions to address:
        1. What assumptions are being made that could be wrong?
        2. Is correlation being confused with causation?
        3. What risks haven't been considered?
        4. What additional evidence would increase confidence?
        5. What's the worst-case scenario if we make the wrong decision?
        """
        
        llm_summary = self.call_llm(system_prompt, user_prompt)
        self.log("Risk assessment complete")
        
        return {
            "agent": self.name,
            "role": self.role,
            "challenges": llm_summary,
            "top_risks": [
                "Accelerating user churn due to poor experience",
                "Brand reputation damage from negative sentiment",
                "Revenue impact from failed transactions",
                "Engineering team burnout from firefighting",
                "Loss of user trust in feature releases"
            ],
            "mitigation_suggestions": [
                "Feature flag rollback capability confirmed",
                "Communication draft ready for external messaging",
                "On-call engineering team on standby"
            ]
        }
