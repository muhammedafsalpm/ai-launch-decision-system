#!/usr/bin/env python3
"""
AI/ML Engineer Assessment - Assignment 1
Multi-Agent War Room Simulation

Author: [Your Name]
Date: April 2026
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from agents.orchestrator import Orchestrator

# Load environment variables
load_dotenv()

# Validate configuration
if not os.getenv("LLM_PROVIDER"):
    print("ERROR: LLM_PROVIDER not set in .env file")
    sys.exit(1)

if os.getenv("LLM_PROVIDER") == "openai" and not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY required when using OpenAI")
    sys.exit(1)


def print_banner():
    """Print application banner"""
    print("\n" + "=" * 70)
    print(" " * 18 + "Multi-Agent War Room Simulation")
    print("=" * 70)
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER').upper()}")
    if os.getenv("LLM_PROVIDER") == "openai":
        print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    else:
        print(f"Model: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
    print("=" * 70 + "\n")


def load_data():
    """Load all input data files"""
    data_dir = Path("data")
    
    print("[SETUP] Loading mock dashboard data...")
    
    # Load metrics
    metrics_path = data_dir / "metrics.json"
    if not metrics_path.exists():
        print(f"ERROR: {metrics_path} not found")
        sys.exit(1)
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
    print(f"  ✓ Loaded {len(metrics['days'])} days of metrics")
    
    # Load feedback
    feedback_path = data_dir / "feedback.json"
    if not feedback_path.exists():
        print(f"ERROR: {feedback_path} not found")
        sys.exit(1)
    with open(feedback_path, "r") as f:
        feedback = json.load(f)
    print(f"  ✓ Loaded {len(feedback)} user feedback entries")
    
    # Load release notes
    release_path = data_dir / "release_notes.txt"
    if not release_path.exists():
        print(f"ERROR: {release_path} not found")
        sys.exit(1)
    with open(release_path, "r") as f:
        release_notes = f.read()
    print(f"  ✓ Loaded release notes")
    
    return metrics, feedback, release_notes


def save_output(decision: dict, name: str = "MUHAMMED_AFSAL"):
    """Save final decision to JSON file"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filename = f"AI_ML_Engineer_{name}_April2026.json"
    output_path = output_dir / filename
    
    # Add metadata
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "llm_provider": os.getenv("LLM_PROVIDER"),
        **decision
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    return output_path


def main():
    """Main entry point"""
    print_banner()
    
    # Load data
    metrics, feedback, release_notes = load_data()
    
    print("\n" + "=" * 70)
    print(" " * 25 + "EXECUTION TRACE")
    print("=" * 70 + "\n")
    
    # Run orchestration
    orchestrator = Orchestrator()
    final_decision = orchestrator.run(metrics, feedback, release_notes)
    
    # Output structured result
    print("\n" + "=" * 70)
    print(" " * 25 + "FINAL DECISION")
    print("=" * 70)
    print(json.dumps(final_decision, indent=2))
    
    # Save to file
    output_path = save_output(final_decision)
    
    print("\n" + "=" * 70)
    print(f"✅ Decision saved to: {output_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
