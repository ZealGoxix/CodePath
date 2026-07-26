"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob
import string

# Common filler words that carry no topic meaning. Ignoring these keeps
# relevance based on real content words (auth, database, token) instead of
# matching on words like "the" or "is" that appear in every document.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "to", "of", "in", "on", "for", "and", "or", "but",
    "if", "then", "there", "here", "any", "some", "how", "what", "which",
    "who", "when", "where", "why", "i", "you", "it", "this", "that", "these",
    "those", "my", "your", "with", "as", "at", "by", "from", "into", "about",
    "can", "will", "would", "should", "could", "me", "we", "they", "them",
    "docs", "doc", "documentation", "mention", "mentioned",
}


class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Tokenization helper
    # -----------------------------------------------------------

    def tokenize(self, text):
        """
        Split text into lowercase words, stripping surrounding punctuation.
        Example: "POST /api/login." -> ["post", "api/login"]
        Shared by build_index and score_document so they agree on words.
        """
        tokens = []
        for raw in text.lower().split():
            word = raw.strip(string.punctuation)
            if word:
                tokens.append(word)
        return tokens

    def query_terms(self, query):
        """
        The meaningful content words in a query: tokenized, with stopwords
        removed. These are the only words that count toward relevance.
        Example: "How do I connect to the database?" -> {"connect", "database"}
        """
        return {word for word in self.tokenize(query) if word not in STOPWORDS}

    def split_paragraphs(self, text):
        """
        Break a document into paragraphs on blank lines. Paragraphs are the
        unit of retrieval, so a snippet is one focused section rather than a
        whole file. Blank/whitespace-only chunks are dropped.
        """
        paragraphs = []
        for chunk in text.split("\n\n"):
            cleaned = chunk.strip()
            if cleaned:
                paragraphs.append(cleaned)
        return paragraphs

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        TODO (Phase 1):
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        for filename, text in documents:
            # Use a set so each file is recorded once per word.
            for word in set(self.tokenize(text)):
                if word not in index:
                    index[word] = []
                index[word].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        query_words = self.query_terms(query)
        text_words = set(self.tokenize(text))
        # Score = how many distinct content words from the query appear here.
        # Stopwords are excluded, so filler words never inflate the score.
        return len(query_words & text_words)

    def retrieve(self, query, top_k=3):
        """
        Select up to top_k relevant *paragraphs* (not whole documents).

        Pipeline:
        1. Use the index to find candidate files sharing a query content word.
        2. Split each candidate into paragraphs and score each paragraph.
        3. Keep only paragraphs with a positive score (the guardrail), sort by
           score descending, and return the best top_k as (filename, text).

        If the query has no meaningful content words, or no paragraph matches,
        this returns an empty list so the caller refuses to answer.
        """
        terms = self.query_terms(query)
        # Guardrail: a query of only filler words gives us nothing to match on.
        if not terms:
            return []

        # Use the index to find candidate files: any doc with a query term.
        candidates = set()
        for word in terms:
            for filename in self.index.get(word, []):
                candidates.add(filename)

        # Score each paragraph inside the candidate documents.
        scored = []
        for filename, text in self.documents:
            if filename not in candidates:
                continue
            for paragraph in self.split_paragraphs(text):
                score = self.score_document(query, paragraph)
                # Guardrail: drop paragraphs with no content-word overlap.
                if score > 0:
                    scored.append((score, filename, paragraph))

        # Sort by score descending, then return top_k as (filename, text).
        scored.sort(key=lambda item: item[0], reverse=True)
        results = [(filename, paragraph) for _score, filename, paragraph in scored]
        return results[:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
