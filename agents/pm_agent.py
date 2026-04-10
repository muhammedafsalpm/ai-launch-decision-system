"""Product Manager Agent - Defines success criteria and user impact"""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class PMAgent(BaseAgent):
    """Defines success criteria, user impact, and go/no-go framing"""
    
    def __init__(self):
        super().__init__(
            name="ProductManager",
            role="Defines success criteria and evaluates user impact"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        release_notes = context.get("release_notes", "")
        data_summary = context.get("data_analyst", {}).get("summary", "")
        marketing_summary = context.get("marketing", {}).get("summary", "")
        
        # Extract key metrics for success criteria check
        error_analysis = context.get("data_analyst", {}).get("error_analysis", {})
        latency_analysis = context.get("data_analyst", {}).get("latency_analysis", {})
        dau_analysis = context.get("data_analyst", {}).get("dau_analysis", {})
        sentiment = context.get("marketing", {}).get("sentiment_analysis", {})
        
        # Success criteria evaluation
        success_criteria = {
            "error_rate": {
                "threshold": "< 1.5%",
                "current": f"{error_analysis.get('post_launch_mean', 0) * 100:.2f}%",
                "status": "FAIL" if error_analysis.get('post_launch_mean', 0) > 0.015 else "PASS"
            },
            "latency_p95": {
                "threshold": "< 150ms",
                "current": f"{latency_analysis.get('post_launch_mean', 0):.0f}ms",
                "status": "FAIL" if latency_analysis.get('post_launch_mean', 0) > 150 else "PASS"
            },
            "dau": {
                "threshold": "Stable or growing",
                "current": f"{dau_analysis.get('pct_change', 0):.1f}% change",
                "status": "FAIL" if dau_analysis.get('pct_change', 0) < -5 else "PASS"
            },
            "adoption": {
                "threshold": "> 15%",
                "current": f"{context.get('metrics', {}).get('days', [{}])[-1].get('adoption_rate', 0) * 100:.1f}%",
                "status": "PASS"
            },
            "sentiment": {
                "threshold": "Negative < 30%",
                "current": f"{sentiment.get('sentiment_distribution_percent', {}).get('negative', 0):.1f}%",
                "status": "FAIL" if sentiment.get('sentiment_distribution_percent', {}).get('negative', 0) > 30 else "PASS"
            }
        }
        
        self.log("Reviewing release scope and user impact")
        
        system_prompt = """You are a Product Manager in a launch war room.

IMPORTANT: Respond in 3-4 sentences only. Be decisive.

Focus on:
1. Which success criteria failed
2. User impact severity
3. Your recommendation

Example: "Error rate and latency criteria failed. User impact is high with crashes. Recommend PAUSE until root cause identified."
        """
        
        user_prompt = f"""
        Release Notes: {release_notes}
        
        Success Criteria Check:
        {success_criteria}
        
        Data Analyst Summary: {data_summary}
        Marketing Summary: {marketing_summary}
        
        Based on the above:
        1. Which criteria are failing and why does it matter?
        2. What is the user impact?
        3. What is your preliminary recommendation?
        """
        
        llm_summary = self.call_llm(system_prompt, user_prompt)
        self.log("PM assessment complete")
        
        return {
            "agent": self.name,
            "role": self.role,
            "success_criteria_check": success_criteria,
            "summary": llm_summary
        }
