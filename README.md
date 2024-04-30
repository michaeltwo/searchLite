

# SearchLite: A Lightweight Search Engine for Document Retrieval

SearchLite is a lightweight search engine designed to facilitate document retrieval based on free text queries. This project aims to provide a simple yet effective solution for searching through documents using natural language queries. It allows users to upload multiple documents of supported file types, search multiple queries, and filter the results. It also includes a document viewer that enables users to highlight terms in PDF documents.

## Features

Certainly! Here's the information in a formatted list:

- **Free Text Queries:** Users can enter natural language queries to search for relevant documents.
- **Document Indexing:** SearchLite indexes documents to enable efficient and quick retrieval of relevant content.
- **Responsive Interface:** The web-based interface allows users to interact with the search engine seamlessly across different devices.
- **Upload Multiple Documents:** Users can upload multiple documents of supported file types.
- **Search Multiple Queries:** Users can search multiple queries to find relevant documents.
- **Filter Search Results:** Users can filter search results based on specific criteria.
- **View Documents with Highlighted Terms:** Users can view documents with highlighted terms, particularly in PDF format.
- **Supports Various File Types:** SearchLite supports various file types, including PDF, DOCX, CSV, TXT, HTML, and images.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/sanket-dalvi/searchLite
   ```

2. Create two folders in the project root directory:

   - `corpus`: For storing uploaded documents.
   - `highlighted_pdfs`: For storing PDF documents with highlighted terms.

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Django development server:

   ```bash
   python manage.py runserver
   ```

5. Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Usage

1. **Homepage**: Access the homepage of the application.

2. **Upload**: Upload multiple documents of supported file types.

3. **Search**: Enter multiple queries to search for relevant documents.

4. **Results**: View search results and filter them based on specific criteria.

5. **Document Viewer**: View documents with highlighted terms in PDF format.

## Technologies Used

Certainly! Here's the list of technologies used in SearchLite in the requested format:

- **Python**
- **Django**
- **NLTK**
- **BeautifulSoup**
- **Pytesseract**
- **MongoDB** (for document storage and indexing)
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Django framework)
- **Document Processing**: Tokenization, Positional Indexing
- **Search Algorithms**: Phrase-based retrieval, Inverted Indexing

## Contributors

- [Alisha Bingewar](https://github.com/abingewar)
- [Animesh Patil](https://github.com/apatil2332)