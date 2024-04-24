from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['SearchLite']  # Replace 'your_database_name' with your actual database name
postings_collection = db['Postings']  # Collection to store postings

def update_postings(doc_id, cleaned_text):
    """
    Update postings for each term in the cleaned text.

    Args:
        doc_id (str): The document ID.
        cleaned_text (list): The list of cleaned terms from the document.
    """
    for position, term in enumerate(cleaned_text):
        postings = postings_collection.find_one({"term": term})
        if postings is None:
            postings = {"term": term, "positions": {doc_id: [position]}}
        else:
            positions = postings.get("positions", {})
            positions[doc_id] = positions.get(doc_id, []) + [position]
            postings["positions"] = positions
        postings_collection.replace_one({"term": term}, postings, upsert=True)

def get_term_postings(term):
    """
    Get the postings for a given term.

    Args:
        term (str): The term to get postings for.

    Returns:
        dict: The postings for the term.
    """
    try:
        term_postings = postings_collection.find_one({"term": term})["positions"]
        return term_postings
    except:
        return None
