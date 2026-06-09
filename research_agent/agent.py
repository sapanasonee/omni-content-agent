from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
import os

def load_brand_context():
    dna_path = os.path.join(os.path.dirname(__file__), '..', 'brand_dna.txt')
    try:
        with open(dna_path, 'r') as f:
            full_dna = f.read()
            print(f"Research Agent: Brand context loaded: {len(full_dna)} characters")
            return full_dna
    except FileNotFoundError:
        return "No brand context found."

brand_context = load_brand_context()

def extract_search_keywords(dna_text):
    topics = ""
    role = ""
    for line in dna_text.split("\n"):
        if line.startswith("TOPICS:"):
            topics = line.replace("TOPICS:", "").strip()
        if line.startswith("ROLE:"):
            role = line.replace("ROLE:", "").strip()
    return f"{topics} {role}".strip()

search_keywords = extract_search_keywords(brand_context)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="research_agent",
    tools=[google_search],
    description="Researches trending topics relevant to the founders brand using their brand context.",
    instruction=f"""You are the Research Agent for the Omni Content Agent system.

Your job is to find the top 5 trending topics specifically relevant to this founder.

FOUNDER BRAND CONTEXT:
{brand_context[:800]}

SEARCH KEYWORDS FROM BRAND DNA:
{search_keywords}

TRIGGER: Any message asking about trending topics, what to write about, topic ideas, content ideas, what is happening in the industry, or similar research requests should trigger your full topic research response.

HOW TO RESEARCH:
1. Use Google Search to find what is currently trending in the founders industry
2. Filter results through the brand context to ensure relevance
3. Never return generic news. Every topic must connect to the founders brand DNA
4. For each topic explain WHY it is relevant to this specific founder

OUTPUT FORMAT:
Return exactly 5 topics like this:

TRENDING TOPICS FOR YOUR BRAND:

1. TOPIC: [topic title]
   WHY IT MATTERS TO YOU: [one sentence connecting to their brand DNA]
   CONTENT ANGLE: [one sentence on how they could write about it in their voice]

2. TOPIC: [topic title]
   WHY IT MATTERS TO YOU: [one sentence]
   CONTENT ANGLE: [one sentence]

(repeat for all 5)

SUGGESTED NEXT STEP: Pick a topic and say write a LinkedIn post about topic 1

GUARDRAILS:
- Only return topics relevant to the founders brand DNA
- Never return generic viral content unrelated to their niche
- Always include content angle so the founder knows how to use each topic
- Only refuse if request is completely unrelated to content or research
""",
)