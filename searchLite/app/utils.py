import re

def highlight_query_in_document(content, query):
    highlighted_content = content
    if query:
        highlighted_content = re.sub(rf'\b({query})\b', r'<span class="highlight">\1</span>', highlighted_content, flags=re.IGNORECASE)
    return highlighted_content
