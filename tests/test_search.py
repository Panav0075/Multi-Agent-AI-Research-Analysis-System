from src.tools.knowledge_search import KnowledgeSearchTool


def test_search_finds_onboarding_document():
    tool = KnowledgeSearchTool("data/knowledge")
    results = tool.search(
        "Which onboarding tasks are repetitive and should be automated?",
        top_k=3,
    )
    assert results[0]["source"] == "onboarding-analysis.md"
