"""
AI Career Assistant — context-aware response engine.

Answers user questions about their resume, ATS score, skills,
job search, and career advice using the session resume data.
Works fully offline without an LLM API key.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

_INTENT_PATTERNS = [
    ("ats", [r"ats", r"applicant tracking", r"score", r"ats score"]),
    ("skills", [r"skill", r"technology", r"tech stack", r"programming", r"language"]),
    ("missing", [r"missing", r"gap", r"lack", r"need", r"add", r"improve"]),
    ("summary", [r"summary", r"profile", r"objective", r"about me", r"professional summary"]),
    ("experience", [r"experience", r"work", r"job", r"role", r"career", r"bullet"]),
    ("cover_letter", [r"cover letter", r"covering letter", r"application letter"]),
    ("format", [r"format", r"formatting", r"layout", r"design", r"template", r"readability"]),
    ("keywords", [r"keyword", r"phrase", r"term", r"buzzword"]),
    ("salary", [r"salary", r"pay", r"compensation", r"wage", r"earn"]),
    ("interview", [r"interview", r"question", r"prepare", r"preparation", r"tips"]),
    ("help", [r"help", r"what can you", r"how do you", r"commands", r"options"]),
    ("greeting", [r"^(hi|hello|hey|good morning|good evening|howdy)\b"]),
]


def _detect_intent(message: str) -> str:
    msg = message.lower().strip()
    for intent, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, msg):
                return intent
    return "general"


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _resp_greeting(data: Dict) -> str:
    name = data.get("name", "")
    name_part = f", {name.split()[0]}" if name and name != "Name Not Found" else ""
    ats = data.get("ats_score", 0)
    if ats:
        return (
            f"Hi{name_part}! 👋 Your resume is currently loaded and scored **{ats}/100** ATS. "
            "Ask me anything — skills, improvements, cover letters, interview tips, or career advice."
        )
    return (
        f"Hi{name_part}! 👋 I'm your AI Career Assistant. Upload a resume to unlock personalized insights, "
        "or ask me anything about resume writing, job search, or career growth."
    )


def _resp_ats(data: Dict) -> str:
    ats = data.get("ats_score", 0)
    if not ats:
        return (
            "Upload your resume first to get a full ATS score breakdown. "
            "ATS (Applicant Tracking System) scores measure how well your resume "
            "parses through automated screening software used by most employers."
        )
    rating = (
        "excellent 🟢" if ats >= 80
        else "good 🟡" if ats >= 60
        else "needs improvement 🔴"
    )
    sections = data.get("sections_found", [])
    section_str = ", ".join(sections[:4]) if sections else "none detected"
    return (
        f"Your resume scores **{ats}/100** — {rating}.\n\n"
        f"**Sections detected:** {section_str}\n\n"
        "To push your score above 80, ensure you have clear section headers, "
        "measurable achievements, and role-specific keywords aligned with the job description."
    )


def _resp_skills(data: Dict) -> str:
    skills = data.get("skills", [])
    if not skills:
        return (
            "No skills were detected yet. Upload your resume or ensure your "
            "Skills section uses a standard header like **Skills** or **Technical Skills**."
        )
    top = skills[:8]
    return (
        f"I detected **{len(skills)} skills** in your resume:\n\n"
        f"**Top skills:** {', '.join(top)}"
        + (f" and {len(skills) - 8} more." if len(skills) > 8 else ".")
        + "\n\nThese are matched against a catalog of 500+ industry-standard skills. "
        "Add skills you have that aren't listed to strengthen your profile."
    )


def _resp_missing(data: Dict) -> str:
    missing = data.get("missing_skills", [])
    matched = data.get("matched_skills", [])
    match_pct = data.get("match_percentage", 0)
    if not missing and not matched:
        return (
            "Upload your resume with a job description to see a full skill gap analysis. "
            "I'll compare your resume skills against the JD requirements and tell you exactly what to add."
        )
    parts = []
    if missing:
        parts.append(f"**Missing skills ({len(missing)}):** {', '.join(missing[:8])}")
    if matched:
        parts.append(f"**Matched skills ({len(matched)}):** {', '.join(matched[:8])}")
    if match_pct:
        parts.append(f"**Job match:** {match_pct}%")
    parts.append(
        "\n💡 **Tip:** Add the missing skills to your resume if you genuinely have them. "
        "Even listing them in a short 'Additional Skills' section can meaningfully raise your match score."
    )
    return "\n\n".join(parts)


def _resp_summary(data: Dict) -> str:
    skills = data.get("skills", [])[:4]
    field = data.get("profession_field", "Professional")
    has_resume = bool(data.get("text") or data.get("ats_score"))
    if not has_resume:
        return (
            "Upload your resume and I'll generate a tailored professional summary for you. "
            "Or ask me to generate one by providing your skills and target role."
        )
    skill_str = ", ".join(skills) if skills else "your core competencies"
    return (
        f"Here's a sample professional summary for you:\n\n"
        f"*\"Results-driven {field} with expertise in {skill_str}. "
        "Proven ability to deliver impactful solutions in collaborative, fast-paced environments. "
        "Passionate about continuous growth and committed to exceeding expectations.\"*\n\n"
        "Go to the **Resume Creation** page to generate a fully customised version using your complete resume data."
    )


def _resp_cover_letter(data: Dict) -> str:
    return (
        "I can generate a professional cover letter for you!\n\n"
        "Head to the **Resume Creation** page → **AI Tools** tab → **Cover Letter Generator**. "
        "It'll use your uploaded resume data and the job description to create a personalised letter.\n\n"
        "Or tell me the target role and company here and I'll draft one right now."
    )


def _resp_format(data: Dict) -> str:
    format_score = data.get("format_score", 0)
    format_checks = data.get("format_checks", [])
    if not format_score and not format_checks:
        return (
            "Upload your resume to get a full format analysis. "
            "I check for ATS readability, consistent fonts, section headers, contact info, and more."
        )
    passed = [fc for fc in format_checks if getattr(fc, "passed", fc.get("passed", False) if isinstance(fc, dict) else False)]
    failed = [fc for fc in format_checks if not getattr(fc, "passed", fc.get("passed", True) if isinstance(fc, dict) else True)]
    lines = [f"**Format score:** {format_score}/100"]
    if failed:
        issues = [getattr(f, "label", f.get("label", "")) for f in failed[:3]]
        lines.append(f"**Issues to fix:** {', '.join(issues)}")
    if passed:
        ok = [getattr(p, "label", p.get("label", "")) for p in passed[:3]]
        lines.append(f"**Passing:** {', '.join(ok)}")
    lines.append("\nSee the full breakdown on the **Resume Analysis** page → Format Checker.")
    return "\n\n".join(lines)


def _resp_keywords(data: Dict) -> str:
    skills = data.get("skills", [])
    job_desc = data.get("job_description", "")
    if not job_desc:
        return (
            "To optimise for keywords, paste the job description when uploading your resume. "
            "I'll identify which keywords from the JD are present in your resume "
            "and which ones you should add."
        )
    matched = data.get("matched_skills", [])
    missing = data.get("missing_skills", [])
    lines = ["Here's your keyword alignment:"]
    if matched:
        lines.append(f"✅ **Present:** {', '.join(matched[:6])}")
    if missing:
        lines.append(f"❌ **Missing:** {', '.join(missing[:6])}")
    lines.append("\nWeave the missing keywords naturally into your experience bullet points.")
    return "\n".join(lines)


def _resp_salary(data: Dict) -> str:
    field = data.get("profession_field", "your field")
    skills = data.get("skills", [])
    high_value = [s for s in skills if s.lower() in {
        "machine learning", "deep learning", "pytorch", "tensorflow", "aws", "kubernetes",
        "docker", "react", "node.js", "django", "flask", "sql", "python", "java"
    }]
    base = "I don't have access to live salary data, but here are general benchmarks:\n\n"
    lines = [base]
    lines.append(f"**{field}** salaries typically range from **$50k–$150k+** depending on seniority and location.")
    if high_value:
        lines.append(f"Your skills in **{', '.join(high_value[:3])}** are high-demand and command premium compensation.")
    lines.append("\nCheck **LinkedIn Salary**, **Glassdoor**, or **levels.fyi** for real-time data in your market.")
    return "\n".join(lines)


def _resp_interview(data: Dict) -> str:
    skills = data.get("skills", [])[:3]
    field = data.get("profession_field", "your field")
    skill_str = ", ".join(skills) if skills else "your core skills"
    return (
        f"Here are key interview prep tips for a **{field}** role:\n\n"
        f"1. **STAR method** — Structure answers as: Situation → Task → Action → Result\n"
        f"2. **Know your tech** — Be ready to deep-dive on {skill_str}\n"
        f"3. **Research the company** — Understand their product, culture and recent news\n"
        f"4. **Quantify impact** — Replace 'I worked on X' with 'I improved X by Y%'\n"
        f"5. **Prepare questions** — Ask about team structure, tech stack, and growth opportunities\n\n"
        "Want me to generate mock interview questions for your specific role?"
    )


def _resp_help(data: Dict) -> str:
    has_resume = bool(data.get("ats_score") or data.get("text"))
    lines = [
        "Here's what I can help you with:\n",
        "📊 **ATS Score** — Understand your resume's ATS compatibility",
        "🎯 **Skills Analysis** — Review detected skills and gaps",
        "✍️ **Summary Generator** — Create a professional summary",
        "📝 **Cover Letter** — Draft a tailored cover letter",
        "🔑 **Keywords** — Align your resume to the job description",
        "📐 **Formatting** — Check ATS readability and structure",
        "💰 **Salary** — General compensation benchmarks",
        "🎤 **Interview Tips** — Prepare for your next interview",
    ]
    if not has_resume:
        lines.append("\n💡 Upload your resume first to unlock personalised insights.")
    return "\n".join(lines)


def _resp_general(message: str, data: Dict) -> str:
    return (
        f"I understand you're asking about: *\"{message[:80]}\"*\n\n"
        "I'm your AI Career Assistant focused on resume and career topics. "
        "I can help with ATS scores, skills analysis, professional summaries, "
        "cover letters, keywords, formatting, salary benchmarks, and interview prep.\n\n"
        "Type **help** to see everything I can do!"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_assistant_response(
    message: str,
    resume_data: Dict[str, Any],
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    """
    Return a context-aware assistant response.

    Args:
        message: The user's message.
        resume_data: Flattened session context from build_session_context().
        conversation_history: Optional list of {"role": ..., "content": ...} dicts.

    Returns:
        Markdown-formatted response string.
    """
    if not message or not message.strip():
        return _resp_help(resume_data)

    intent = _detect_intent(message)

    handlers = {
        "greeting":     lambda: _resp_greeting(resume_data),
        "ats":          lambda: _resp_ats(resume_data),
        "skills":       lambda: _resp_skills(resume_data),
        "missing":      lambda: _resp_missing(resume_data),
        "summary":      lambda: _resp_summary(resume_data),
        "cover_letter": lambda: _resp_cover_letter(resume_data),
        "format":       lambda: _resp_format(resume_data),
        "keywords":     lambda: _resp_keywords(resume_data),
        "salary":       lambda: _resp_salary(resume_data),
        "interview":    lambda: _resp_interview(resume_data),
        "help":         lambda: _resp_help(resume_data),
        "experience":   lambda: (
            "Head to the **Resume Creation** page → **AI Tools** to rewrite your experience bullets with AI. "
            "Or paste a specific experience paragraph here and I'll suggest improvements."
        ),
        "general":      lambda: _resp_general(message, resume_data),
    }

    return handlers.get(intent, handlers["general"])()
