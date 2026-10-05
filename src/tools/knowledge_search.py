from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeSearchTool:
    def __init__(self, knowledge_path):
        self.knowledge_path = Path(knowledge_path)
        self.documents = self._load_documents()
        if not self.documents:
            raise ValueError(f"No knowledge documents found in {knowledge_path}")

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(
            [item["text"] for item in self.documents]
        )

    def _load_documents(self):
        documents = []
        for path in sorted(self.knowledge_path.glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            title = path.stem.replace("-", " ").title()

            match = re.search(r"^#\s+(.+)$", raw, flags=re.MULTILINE)
            if match:
                title = match.group(1).strip()

            text = re.sub(r"^#.*$", "", raw, flags=re.MULTILINE).strip()

            documents.append(
                {
                    "source": path.name,
                    "title": title,
                    "text": text,
                }
            )
        return documents

    def search(self, query, top_k=4):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        order = scores.argsort()[::-1][:top_k]

        results = []
        for idx in order:
            doc = self.documents[int(idx)]
            results.append(
                {
                    "source": doc["source"],
                    "title": doc["title"],
                    "passage": doc["text"],
                    "score": round(float(scores[int(idx)]), 6),
                }
            )
        return results
