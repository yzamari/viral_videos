import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator_agent import OrchestratorAgent


def main():
    topic = "funny cat videos"
    sentiment = "funny"
    style = "comedy"

    orchestrator = OrchestratorAgent(topic, sentiment, style)
    orchestrator.run()


if __name__ == "__main__":
    main() 