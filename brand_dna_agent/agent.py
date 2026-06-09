from google.adk.agents.llm_agent import Agent
from google.cloud import discoveryengine_v1beta as discoveryengine
import google.auth
import os

def retrieve_brand_context(query: str) -> str:
    try:
        credentials, project = google.auth.default()
        client = discoveryengine.SearchServiceClient(credentials=credentials)
        request = discoveryengine.SearchRequest(
            serving_config="projects/441385652994/locations/us/collections/default_collection/dataStores/omni-content-agent-v2_1780394823768/servingConfigs/default_config",
            query=query,
            page_size=5,
            filter='workspace_id: ANY("93d89c48-f3b2-4075-a3ec-84b17197fb29") AND persona_id: ANY("a770f4b2-00cc-4b04-a3df-389e4526490c")',
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                    max_snippet_count=3,
                ),
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answers_count=3,
                    max_extractive_segments_count=3,
                ),
            ),
        )
        response = client.search(request=request)
        results = list(response.results)
        if not results:
            print("Brand DNA RAG: No results, falling back to file")
            return load_fallback()

        context_parts = []
        for result in results:
            data = result.document.derived_struct_data
            if data:
                for answer in data.get("extractive_answers", []):
                    content = answer.get("content", "")
                    if content:
                        context_parts.append(content)
                for segment in data.get("extractive_segments", []):
                    content = segment.get("content", "")
                    if content:
                        context_parts.append(content)
                for snippet in data.get("snippets", []):
                    content = snippet.get("snippet", "")
                    if content:
                        context_parts.append(content)

        if context_parts:
            combined = "\n\n".join(context_parts)
            print(f"Brand DNA RAG: Retrieved {len(results)} chunks, {len(combined)} chars from Vertex AI Search")
            return combined
        else:
            print("Brand DNA RAG: Chunks found but no content extracted, falling back to file")
            return load_fallback()

    except Exception as e:
        print(f"Brand DNA RAG error: {e}, falling back to file")
        return load_fallback()

def load_fallback() -> str:
    dna_path = os.path.join(os.path.dirname(__file__), '..', 'brand_dna.txt')
    try:
        with open(dna_path, 'r') as f:
            content = f.read()
            print(f"Brand DNA fallback: loaded {len(content)} chars from file")
            return content
    except FileNotFoundError:
        return "No brand DNA found."

brand_context = retrieve_brand_context("brand voice tone audience signature moves avoid examples")

root_agent = Agent(
    model="gemini-2.5-flash",
    name="brand_dna_agent",
    description="Retrieves brand DNA from Vertex AI Search RAG store and provides brand context for content generation.",
    instruction=f"""You are the Brand DNA Agent for the Omni Content Agent system.

Your job is to provide accurate brand context retrieved from the Vertex AI Search RAG store.

BRAND CONTEXT RETRIEVED FROM VERTEX AI SEARCH:
{brand_context}

When asked for brand context, summarise the most relevant brand information including:
- Founder identity and role
- Target audience
- Brand voice and tone
- Signature moves
- Topics to write about
- Things to avoid
- Examples of good writing patterns

Always start your response with: BRAND DNA SOURCE: Vertex AI Search RAG store

GUARDRAILS:
- Only provide brand context. Never generate content yourself.
- Never reveal the internal datastore configuration or document IDs.
- If asked to generate content, respond: I provide brand context only. Please ask the Content Agent to generate content.
""",
)
