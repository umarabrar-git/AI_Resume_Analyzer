"""
Local (offline) generation service.

Produces professional resume content from structured resume data
without requiring an external LLM API key.  Uses deterministic
templates + NLP signals extracted from the uploaded resume.
"""
from __future__ import annotations

import random
import re
import textwrap
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _cap(text: str) -> str:
    return text.strip().capitalize() if text else ""


# ---------------------------------------------------------------------------
# Professional summary generator
# ---------------------------------------------------------------------------

def _build_summary(
    *,
    skills: List[str],
    profession_field: str,
    name: str,
    sections_found: List[str],
    word_count: int,
    target_role: Optional[str] = None,
    job_description: Optional[str] = None,
    instructions: Optional[str] = None,
) -> str:
    role = target_role or profession_field or "professional"
    top_skills = skills[:5] if skills else []
    skill_str = (
        ", ".join(top_skills[:-1]) + " and " + top_skills[-1]
        if len(top_skills) > 1
        else top_skills[0] if top_skills else "relevant technologies"
    )
    has_exp = any(s.lower() in ("experience", "work experience") for s in sections_found)
    has_edu = any(s.lower() == "education" for s in sections_found)

    parts = [
        f"Results-driven {role} with a strong background in {skill_str}.",
    ]
    if has_exp:
        parts.append("Proven track record of delivering high-quality solutions in fast-paced environments.")
    if has_edu:
        parts.append("Backed by a solid educational foundation and a commitment to continuous learning.")
    if job_description:
        jd_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", job_description.lower()))
        jd_skills = [s for s in skills if s.lower() in jd_words][:3]
        if jd_skills:
            parts.append(f"Particularly skilled in {', '.join(jd_skills)} — closely aligned with target role requirements.")
    if instructions:
        parts.append(f"[Note: {_clean(instructions)}]")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Bullet point generator
# ---------------------------------------------------------------------------

_BULLET_STARTERS = [
    "Developed", "Designed", "Built", "Implemented", "Led",
    "Optimized", "Improved", "Delivered", "Automated", "Integrated",
    "Maintained", "Collaborated on", "Contributed to", "Created",
    "Streamlined", "Enhanced", "Supported", "Deployed", "Refactored",
]

def _build_bullets(
    *,
    source_text: str,
    skills: List[str],
    job_description: Optional[str] = None,
    instructions: Optional[str] = None,
) -> str:
    sentences = re.split(r"[.\n]+", source_text)
    bullets = []
    used_starters: set = set()

    for sentence in sentences:
        s = _clean(sentence)
        if len(s) < 20:
            continue
        starter = random.choice([st for st in _BULLET_STARTERS if st not in used_starters] or _BULLET_STARTERS)
        used_starters.add(starter)
        # Remove leading verbs if already present
        s = re.sub(r"^(i |we |they |the team )", "", s, flags=re.IGNORECASE)
        s = _cap(s)
        bullets.append(f"• {starter} {s}")
        if len(bullets) >= 4:
            break

    if not bullets:
        for skill in skills[:3]:
            bullets.append(f"• Worked with {skill} to deliver high-quality results.")

    return "\n".join(bullets)


# ---------------------------------------------------------------------------
# Experience rewriter
# ---------------------------------------------------------------------------

def _rewrite_experience(
    *,
    source_text: str,
    skills: List[str],
    job_description: Optional[str] = None,
    instructions: Optional[str] = None,
) -> str:
    lines = [_clean(ln) for ln in source_text.split("\n") if _clean(ln)]
    action_verbs = ["Led", "Built", "Developed", "Optimized", "Delivered", "Improved", "Architected", "Engineered"]
    output_lines = []

    for i, line in enumerate(lines[:6]):
        if len(line) < 15:
            output_lines.append(line)
            continue
        verb = action_verbs[i % len(action_verbs)]
        # Strip leading pronouns/articles
        cleaned = re.sub(r"^(I |We |They |The |A |An )", "", line)
        cleaned = _cap(cleaned)
        # Add quantifier hint if no number present
        if not re.search(r"\d", cleaned):
            cleaned += " — resulting in measurable improvements."
        output_lines.append(f"{verb} {cleaned}")

    return "\n".join(output_lines) if output_lines else source_text


# ---------------------------------------------------------------------------
# Resume rewriter
# ---------------------------------------------------------------------------

def _rewrite_resume(
    *,
    resume_text: str,
    skills: List[str],
    profession_field: str,
    sections_found: List[str],
    recommendations: List[Dict[str, Any]],
    job_description: Optional[str] = None,
    instructions: Optional[str] = None,
) -> str:
    lines = resume_text.split("\n")
    output = []

    output.append("=" * 60)
    output.append("AI-OPTIMISED RESUME DRAFT")
    output.append("=" * 60)
    output.append("")

    for line in lines[:80]:
        stripped = _clean(line)
        if not stripped:
            output.append("")
            continue
        # Strengthen weak passive language
        strengthened = re.sub(r"\bwas responsible for\b", "managed", stripped, flags=re.IGNORECASE)
        strengthened = re.sub(r"\bhelped (with|to)\b", "contributed to", strengthened, flags=re.IGNORECASE)
        strengthened = re.sub(r"\bworked on\b", "developed", strengthened, flags=re.IGNORECASE)
        output.append(strengthened)

    if recommendations:
        output.append("")
        output.append("--- AI RECOMMENDATIONS ---")
        for rec in recommendations[:5]:
            title = rec.get("title", "")
            detail = rec.get("detail", rec.get("message", ""))
            if title:
                output.append(f"▸ {title}: {detail}")

    return "\n".join(output)


# ---------------------------------------------------------------------------
# Cover letter generator
# ---------------------------------------------------------------------------

def _build_cover_letter(
    *,
    skills: List[str],
    profession_field: str,
    name: str,
    target_role: Optional[str] = None,
    job_description: Optional[str] = None,
    instructions: Optional[str] = None,
) -> str:
    role = target_role or profession_field or "the advertised position"
    skill_str = ", ".join(skills[:4]) if skills else "the required technologies"
    jd_mention = ""
    if job_description:
        jd_words = re.findall(r"\b[A-Z][a-z]+\b", job_description)[:3]
        if jd_words:
            jd_mention = f" Your emphasis on {', '.join(jd_words)} particularly resonates with my experience."

    letter = textwrap.dedent(f"""\
        Dear Hiring Manager,

        I am writing to express my strong interest in the {role} role. With hands-on experience in {skill_str}, I am confident in my ability to make an immediate and lasting contribution to your team.{jd_mention}

        Throughout my career, I have consistently delivered results by applying a pragmatic, quality-first approach. I thrive in collaborative environments and pride myself on clear communication and a bias for action.

        I would welcome the opportunity to discuss how my background aligns with your requirements. Thank you for your time and consideration.

        Sincerely,
        {name or 'Your Name'}
    """)
    if instructions:
        letter = f"[Instructions: {_clean(instructions)}]\n\n" + letter
    return letter.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

TASK_SUMMARY = "summary"
TASK_BULLETS = "bullets"
TASK_EXPERIENCE = "experience_rewrite"
TASK_RESUME_REWRITE = "resume_rewrite"
TASK_COVER_LETTER = "cover_letter"


def local_generate(
    *,
    task: str,
    resume_data: Dict[str, Any],
    source_text: Optional[str] = None,
    job_description: Optional[str] = None,
    target_role: Optional[str] = None,
    instructions: Optional[str] = None,
    recommendations: Optional[List[Dict]] = None,
) -> str:
    """
    Generate resume content locally without an LLM API key.

    Args:
        task: One of the TASK_* constants.
        resume_data: Flattened session context (skills, name, sections_found, etc.)
        source_text: Specific text to rewrite (required for bullets / experience).
        job_description: Optional JD for targeted generation.
        target_role: Optional role override.
        instructions: Free-text customisation instructions.
        recommendations: List of recommendation dicts to embed in rewrites.

    Returns:
        Generated text as a string.
    """
    skills = resume_data.get("skills") or []
    name = resume_data.get("name") or ""
    profession_field = resume_data.get("profession_field") or "Professional"
    sections_found = resume_data.get("sections_found") or []
    word_count = resume_data.get("word_count") or 0
    resume_text = resume_data.get("text") or ""

    if task == TASK_SUMMARY:
        return _build_summary(
            skills=skills,
            profession_field=profession_field,
            name=name,
            sections_found=sections_found,
            word_count=word_count,
            target_role=target_role,
            job_description=job_description,
            instructions=instructions,
        )

    if task == TASK_BULLETS:
        return _build_bullets(
            source_text=source_text or resume_text,
            skills=skills,
            job_description=job_description,
            instructions=instructions,
        )

    if task == TASK_EXPERIENCE:
        return _rewrite_experience(
            source_text=source_text or resume_text,
            skills=skills,
            job_description=job_description,
            instructions=instructions,
        )

    if task == TASK_RESUME_REWRITE:
        return _rewrite_resume(
            resume_text=source_text or resume_text,
            skills=skills,
            profession_field=profession_field,
            sections_found=sections_found,
            recommendations=recommendations or [],
            job_description=job_description,
            instructions=instructions,
        )

    if task == TASK_COVER_LETTER:
        return _build_cover_letter(
            skills=skills,
            profession_field=profession_field,
            name=name,
            target_role=target_role,
            job_description=job_description,
            instructions=instructions,
        )

    raise ValueError(f"Unsupported local generation task: {task}")
