"""
Test the full 4-agent pipeline end-to-end.
Usage: python test_pipeline.py
"""
import asyncio
from backend.graph.pipeline import run_pipeline

if __name__ == "__main__":
    asyncio.run(run_pipeline())
