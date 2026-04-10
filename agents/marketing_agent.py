"""Marketing Agent - Analyzes user sentiment and communication needs"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools import analyze_sentiment, extract_top_issues


class MarketingAgent(BaseAgent):
    """Assesses messaging, customer perception, and communication actions"""
    
    def __init__(self):
        super().__init__(
            name="MarketingAgent",
            role="Analyzes user sentiment and recommends communication strategy"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        feedback = context["feedback"]
        
        # TOOL CALL 1: Sentiment analysis
        self.log("Analyzing sentiment distribution", "analyze_sentiment")
        sentiment = analyze_sentiment(feedback)
        
        # TOOL CALL 2: Extract top issues
        self.log("Extracting top user complaints", "extract_top_issues")
        issues = extract_top_issues(feedback)
        
        # LLM summary
        system_prompt = """You are a marketing/communications lead in a product war room.

IMPORTANT: Respond in 3-4 sentences only. Be specific.

Focus on:
1. Overall sentiment (positive/negative %)
2. Top user complaint
3. Whether we should communicate externally

Example: "Sentiment is 60% negative with 'crash' as primary issue. Users are frustrated. Recommend acknowledging issue publicly within 2 hours."
        """
        
        user_prompt = f"""
        Sentiment Analysis:
        - Total feedback: {sentiment['total_feedback']}
        - Positive: {sentiment['sentiment_distribution_percent']['positive']}%
        - Negative: {sentiment['sentiment_distribution_percent']['negative']}%
        - Overall sentiment: {sentiment['overall_sentiment']}
        - Sentiment score: {sentiment['sentiment_score']} (-1 to 1 scale)
        
        Top User Issues:
        Primary issue: {issues['primary_issue']} ({issues['primary_issue_count']} mentions)
        
        Detailed issues:
        {issues['top_issues']}
        
        Based on this feedback:
        1. What is the current user perception?
        2. Should we communicate externally? If so, what's the key message?
        3. What communication channels would be most effective?
        """
        
        llm_summary = self.call_llm(system_prompt, user_prompt)
        self.log("Sentiment analysis complete")
        
        return {
            "agent": self.name,
            "role": self.role,
            "sentiment_analysis": sentiment,
            "top_issues": issues,
            "summary": llm_summary
        }
