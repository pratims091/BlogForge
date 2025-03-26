from typing import List, Any


def format_sources_text(source_documents: List[Any]) -> str:
    """
    Format source documents as text.

    Args:
        source_documents: List of source documents

    Returns:
        str: Formatted source text
    """
    if not source_documents:
        return ""

    unique_sources = set()
    for doc in source_documents:
        source_url = doc.metadata.get("source", "")
        if source_url and source_url not in unique_sources:
            unique_sources.add(source_url)

    if not unique_sources:
        return ""

    sources_text = "\n\n📚 Sources:\n"
    for i, source in enumerate(list(unique_sources)[:3]):  # Limit to 3 sources
        sources_text += f"• {source}\n"

    if len(unique_sources) > 3:
        sources_text += f"• ...and {len(unique_sources) - 3} more sources\n"

    return sources_text
