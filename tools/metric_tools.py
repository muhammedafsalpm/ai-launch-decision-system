"""Metric analysis tools for Data Analyst Agent"""

import numpy as np
from typing import List, Dict, Any


def detect_anomalies(metrics: List[Dict], metric_name: str) -> Dict[str, Any]:
    """
    Detects statistical anomalies in time series data.
    
    Args:
        metrics: List of daily metric dictionaries
        metric_name: Name of metric to analyze
        
    Returns:
        Dictionary with anomaly analysis results
    """
    values = [day[metric_name] for day in metrics]
    
    # Split pre-launch and post-launch (launch at day 8)
    launch_day = 8
    pre_launch = values[:launch_day-1]
    post_launch = values[launch_day-1:]
    
    pre_mean = np.mean(pre_launch)
    pre_std = np.std(pre_launch)
    post_mean = np.mean(post_launch)
    
    # Calculate percentage change
    if pre_mean != 0:
        pct_change = ((post_mean - pre_mean) / pre_mean) * 100
    else:
        pct_change = 0
    
    # Determine if anomaly exists
    threshold = 2 * pre_std
    is_anomaly = abs(post_mean - pre_mean) > threshold
    
    # Determine severity
    severity = "low"
    if is_anomaly:
        if abs(pct_change) > 50:
            severity = "critical"
        elif abs(pct_change) > 25:
            severity = "high"
        elif abs(pct_change) > 10:
            severity = "medium"
    
    # Determine trend direction
    recent_trend = "stable"
    if len(post_launch) >= 3:
        recent_values = post_launch[-3:]
        if all(recent_values[i] > recent_values[i-1] for i in range(1, len(recent_values))):
            recent_trend = "increasing"
        elif all(recent_values[i] < recent_values[i-1] for i in range(1, len(recent_values))):
            recent_trend = "decreasing"
    
    return {
        "metric": metric_name,
        "pre_launch_mean": round(pre_mean, 4),
        "post_launch_mean": round(post_mean, 4),
        "pct_change": round(pct_change, 2),
        "is_anomaly": is_anomaly,
        "severity": severity,
        "threshold": round(threshold, 4),
        "trend": "increasing" if pct_change > 0 else "decreasing",
        "recent_trend": recent_trend,
        "current_value": values[-1],
        "max_value": max(values),
        "min_value": min(values)
    }


def compare_trends(metrics: List[Dict]) -> Dict[str, Any]:
    """
    Compares multiple metrics to find correlated issues.
    
    Args:
        metrics: List of daily metric dictionaries
        
    Returns:
        Dictionary with multi-metric analysis
    """
    metric_names = ["dau", "error_rate", "latency_p95", "crash_rate", "support_tickets", "adoption_rate"]
    results = {}
    
    for metric in metric_names:
        if metric in metrics[0]:  # Check if metric exists
            results[metric] = detect_anomalies(metrics, metric)
    
    # Find problem metrics
    problem_metrics = [m for m, r in results.items() if r["is_anomaly"]]
    critical_metrics = [m for m, r in results.items() if r["severity"] == "critical"]
    high_severity_metrics = [m for m, r in results.items() if r["severity"] == "high"]
    
    # Identify correlated problems
    increasing_problems = [m for m in problem_metrics if results[m]["trend"] == "increasing"]
    decreasing_problems = [m for m in problem_metrics if results[m]["trend"] == "decreasing"]
    
    return {
        "individual_analysis": results,
        "problem_metrics": problem_metrics,
        "critical_metrics": critical_metrics,
        "high_severity_metrics": high_severity_metrics,
        "increasing_problems": increasing_problems,
        "decreasing_problems": decreasing_problems,
        "total_metrics_analyzed": len(metric_names),
        "metrics_with_issues": len(problem_metrics),
        "correlation_summary": f"{len(problem_metrics)} of {len(metric_names)} metrics showing anomalies. "
                              f"Critical: {critical_metrics}, High: {high_severity_metrics}"
    }
