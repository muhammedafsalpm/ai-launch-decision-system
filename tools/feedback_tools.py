"""Feedback analysis tools for Marketing Agent"""

from typing import List, Dict, Any
from collections import Counter


def analyze_sentiment(feedback: List[Dict]) -> Dict[str, Any]:
    """
    Analyzes sentiment distribution and trends from user feedback.
    
    Args:
        feedback: List of feedback dictionaries
        
    Returns:
        Dictionary with sentiment analysis results
    """
    sentiments = [f["sentiment"] for f in feedback]
    counts = Counter(sentiments)
    total = len(feedback)
    
    # Calculate sentiment score (-1 to 1)
    positive_weight = counts.get("positive", 0)
    negative_weight = counts.get("negative", 0)
    
    if total > 0:
        sentiment_score = (positive_weight - negative_weight) / total
    else:
        sentiment_score = 0
    
    # Group by date for trend analysis
    date_sentiment = {}
    for f in feedback:
        date = f.get("date", "unknown")
        if date not in date_sentiment:
            date_sentiment[date] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
        date_sentiment[date][f["sentiment"]] += 1
        date_sentiment[date]["total"] += 1
    
    # Calculate percentages
    sentiment_distribution = {
        "positive": round((counts.get("positive", 0) / total) * 100, 1) if total > 0 else 0,
        "negative": round((counts.get("negative", 0) / total) * 100, 1) if total > 0 else 0,
        "neutral": round((counts.get("neutral", 0) / total) * 100, 1) if total > 0 else 0
    }
    
    # Determine overall sentiment
    if sentiment_score > 0.15:
        overall = "positive"
    elif sentiment_score < -0.15:
        overall = "negative"
    else:
        overall = "neutral"
    
    return {
        "total_feedback": total,
        "sentiment_counts": dict(counts),
        "sentiment_distribution_percent": sentiment_distribution,
        "sentiment_score": round(sentiment_score, 3),
        "overall_sentiment": overall,
        "daily_breakdown": date_sentiment,
        "positive_count": counts.get("positive", 0),
        "negative_count": counts.get("negative", 0),
        "neutral_count": counts.get("neutral", 0)
    }


def extract_top_issues(feedback: List[Dict], top_n: int = 5) -> Dict[str, Any]:
    """
    Extracts common themes/issues from negative feedback using keyword analysis.
    
    Args:
        feedback: List of feedback dictionaries
        top_n: Number of top issues to return
        
    Returns:
        Dictionary with extracted issues
    """
    negative_feedback = [f["text"].lower() for f in feedback if f["sentiment"] == "negative"]
    
    # Keyword mapping for issue categorization
    keyword_categories = {
        "crash": ["crash", "freeze", "not responding", "stuck", "hangs"],
        "slow": ["slow", "lag", "latency", "loading", "takes forever"],
        "bug": ["bug", "glitch", "broken", "doesn't work", "issue"],
        "error": ["error", "fail", "failed", "failing"],
        "payment": ["payment", "checkout", "card", "billing", "transaction"],
        "login": ["login", "sign in", "can't access", "password"],
        "ui": ["ui", "interface", "design", "layout", "button"],
        "battery": ["battery", "drain", "hot", "overheat"],
        "feature": ["feature", "recommendation", "new", "update"],
        "data": ["data", "lost", "missing", "sync"]
    }
    
    # Count occurrences by category
    category_counts = Counter()
    issue_examples = {cat: [] for cat in keyword_categories}
    
    for text in negative_feedback:
        for category, keywords in keyword_categories.items():
            if any(kw in text for kw in keywords):
                category_counts[category] += 1
                if len(issue_examples[category]) < 3:  # Keep up to 3 examples
                    issue_examples[category].append(text[:100])
    
    # Get top issues
    top_issues = []
    for category, count in category_counts.most_common(top_n):
        if count > 0:
            top_issues.append({
                "issue": category,
                "count": count,
                "percentage": round((count / len(negative_feedback)) * 100, 1) if negative_feedback else 0,
                "examples": issue_examples[category][:2]
            })
    
    return {
        "negative_feedback_count": len(negative_feedback),
        "total_feedback_count": len(feedback),
        "top_issues": top_issues,
        "primary_issue": top_issues[0]["issue"] if top_issues else "unknown",
        "primary_issue_count": top_issues[0]["count"] if top_issues else 0,
        "all_category_counts": dict(category_counts)
    }
