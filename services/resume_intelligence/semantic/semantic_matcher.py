from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None
    util = None

from services.resume_intelligence.config import SEMANTIC_MATCH_THRESHOLD, SEMANTIC_MODEL


@lru_cache(maxsize=1)
def get_semantic_model():
    """Load and cache the sentence-transformer model."""

    if SentenceTransformer is None or util is None:
        raise RuntimeError("sentence-transformers is not installed. Run: pip install sentence-transformers torch")

    return SentenceTransformer(SEMANTIC_MODEL)


def encode_texts(texts):
    """Encode multiple texts efficiently."""

    if not texts:
        return None

    model = get_semantic_model()

    return model.encode(texts, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False)


def calculate_similarity(first_text, second_text):
    """Return semantic similarity from 0 to 100."""

    if not first_text or not second_text:
        return 0.0

    embeddings = encode_texts([first_text, second_text])

    score = float(util.cos_sim(embeddings[0], embeddings[1]).item())
    score = max(0.0, min(1.0, score))

    return round(score * 100, 2)


def match_candidates(resume_candidates, job_candidates, threshold=SEMANTIC_MATCH_THRESHOLD):
    """Match job-description candidates to the most semantically similar resume candidate."""

    resume_candidates = list(dict.fromkeys(resume_candidates or []))
    job_candidates = list(dict.fromkeys(job_candidates or []))

    if not job_candidates:
        return {"matched": [], "missing": [], "match_percentage": 0.0}

    if not resume_candidates:
        return {"matched": [], "missing": job_candidates, "match_percentage": 0.0}

    resume_embeddings = encode_texts(resume_candidates)
    job_embeddings = encode_texts(job_candidates)
    similarity_matrix = util.cos_sim(job_embeddings, resume_embeddings)

    matched = []
    missing = []

    for job_index, job_candidate in enumerate(job_candidates):
        scores = similarity_matrix[job_index]
        best_index = int(scores.argmax().item())
        best_score = float(scores[best_index].item())

        if best_score >= threshold:
            matched.append(
                {
                    "job_candidate": job_candidate,
                    "resume_candidate": resume_candidates[best_index],
                    "similarity": round(best_score * 100, 2),
                }
            )
        else:
            missing.append(job_candidate)

    match_percentage = len(matched) / len(job_candidates) * 100
    return {"matched": matched, "missing": missing, "match_percentage": round(match_percentage, 2)}
