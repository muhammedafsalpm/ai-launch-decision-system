"""Data Analyst Agent - Analyzes metrics and detects anomalies"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools import detect_anomalies, compare_trends


class DataAnalystAgent(BaseAgent):
    """Analyzes quantitative metrics, trends, and anomalies"""
    
    def __init__(self):
        super().__init__(
            name="DataAnalyst",
            role="Analyzes metrics and detects anomalies in time-series data"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics = context["metrics"]["days"]
        
        # TOOL CALL 1: Detect anomalies in critical metrics
        self.log("Running anomaly detection on error rate", "detect_anomalies")
        error_analysis = detect_anomalies(metrics, "error_rate")
        
        self.log("Running anomaly detection on latency p95", "detect_anomalies")
        latency_analysis = detect_anomalies(metrics, "latency_p95")
        
        self.log("Running anomaly detection on DAU", "detect_anomalies")
        dau_analysis = detect_anomalies(metrics, "dau")
        
        self.log("Running anomaly detection on crash rate", "detect_anomalies")
        crash_analysis = detect_anomalies(metrics, "crash_rate")
        
        # TOOL CALL 2: Compare all trends
        self.log("Comparing all metric trends", "compare_trends")
        trend_comparison = compare_trends(metrics)
        
        # LLM summary
        system_prompt = """You are a data analyst in a product war room.

IMPORTANT: Respond in 3-4 sentences only. Be specific with numbers.

Focus on:
1. Which metric is most critical
2. The exact percentage change
3. Whether this is a launch issue

Example: "Error rate increased 137.5% from 0.8% to 1.9% post-launch. Latency up 75%. DAU dropped 28%. This indicates a critical launch issue."
        """
        
        user_prompt = f"""
        Metric Analysis Results:
        
        Error Rate: {error_analysis['pct_change']}% change
        - Pre-launch: {error_analysis['pre_launch_mean']}, Post-launch: {error_analysis['post_launch_mean']}
        - Severity: {error_analysis['severity']}, Trend: {error_analysis['recent_trend']}
        
        Latency (p95): {latency_analysis['pct_change']}% change
        - Pre-launch: {latency_analysis['pre_launch_mean']}ms, Post-launch: {latency_analysis['post_launch_mean']}ms
        - Severity: {latency_analysis['severity']}
        
        DAU: {dau_analysis['pct_change']}% change
        - Pre-launch: {dau_analysis['pre_launch_mean']:.0f}, Post-launch: {dau_analysis['post_launch_mean']:.0f}
        - Trend: {dau_analysis['recent_trend']}
        
        Crash Rate: {crash_analysis['pct_change']}% change
        - Severity: {crash_analysis['severity']}
        
        Overall: {trend_comparison['correlation_summary']}
        
        Provide a 3-4 sentence summary of the data situation, highlighting the most critical issues.
        """
        
        llm_summary = self.call_llm(system_prompt, user_prompt)
        self.log(f"Analysis complete: {llm_summary[:100]}...")
        
        return {
            "agent": self.name,
            "role": self.role,
            "error_analysis": error_analysis,
            "latency_analysis": latency_analysis,
            "dau_analysis": dau_analysis,
            "crash_analysis": crash_analysis,
            "trend_comparison": trend_comparison,
            "summary": llm_summary
        }
