from google.adk.agents.llm_agent import Agent
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from content_agent.agent import root_agent as content_agent
from research_agent.agent import root_agent as research_agent
from brand_dna_agent.agent import root_agent as brand_dna_agent

def load_brand_dna():
    dna_path = os.path.join(os.path.dirname(__file__), '..', 'brand_dna.txt')
    try:
        with open(dna_path, 'r') as f:
            content = f.read()
            print(f"Orchestrator: Brand DNA loaded: {len(content)} characters")
            return content
    except FileNotFoundError:
        return "No brand DNA found."

brand_dna = load_brand_dna()

root_agent = Agent(
    model="gemini-2.5-flash",
    name="orchestrator",
    description="Master orchestrator that routes user requests to specialist agents.",
    sub_agents=[content_agent, research_agent, brand_dna_agent],
    instruction=f"""You are the master orchestrator of the Omni Content Agent system.

You have three specialist agents available:
1. Content Agent: generates brand-aware content for LinkedIn, Twitter, Newsletter, Blog, Executive Brief
2. Research Agent: finds top 5 trending topics relevant to the founders brand
3. Brand DNA Agent: retrieves brand context from Vertex AI Search RAG store

ROUTING RULES:
1. Content generation requests: confirm platform and campaign context, then delegate to Content Agent
2. Research requests: delegate to Research Agent  
3. Brand DNA questions: delegate to Brand DNA Agent
4. Scheduling: Publisher Agent coming soon

GUARDRAILS:
- Never generate content yourself. Always delegate to Content Agent.
- Never do research yourself. Always delegate to Research Agent.
- Every content request must confirm platform before delegating.
- Off-topic: My role is to coordinate content creation for your brand. What would you like to create today?
""",
)
