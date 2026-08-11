import re
import math
try:
    import fitz
except ImportError:
    fitz = None
from docx import Document
from utils.catalogs.profession_catalog import (
    PROFESSION_ICON_FALLBACK,
    PROFESSION_KEYWORDS,
    SKILL_ICON_MAP,
)
from utils.catalogs.skill_catalog import SKILLS


def _get_resume_intelligence_helpers():
    from services.resume_intelligence import analyze_resume_text
    from services.resume_intelligence.ats import analyze_ats
    return analyze_resume_text, analyze_ats
# ======================================
# File Validation
# ======================================


def extract_resume_text(file_path):
    """Extract resume text by file extension."""

    if not file_path:
        return ""

    extension = file_path.rsplit(".", 1)[1].lower() if "." in file_path else ""

    if extension == "pdf":
        return extract_pdf_text(file_path)
    if extension == "docx":
        return extract_docx_text(file_path)
    return ""

def allowed_file(filename, allowed_extensions):

    # No extension found
    if "." not in filename:
        return False

    # Get extension
    extension = filename.rsplit(".", 1)[1].lower()

    # Check extension
    return extension in allowed_extensions
# ======================================
# Read PDF
# ======================================

def extract_pdf_text(pdf_path):

    text = ""
    
    if fitz is None:
        raise ImportError("PyMuPDF is not installed")

    pdf = fitz.open(pdf_path)

    for page in pdf:

        text += page.get_text()

    pdf.close()

    return text
# ======================================
# Read DOCX
# ======================================

def extract_docx_text(docx_path):

    document = Document(docx_path)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text
# ======================================
# Extract Email
# ======================================

def extract_email(text):

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Email Not Found"
# ======================================
# Extract Phone Number
# ======================================

def extract_phone(text):

    pattern = r"(\+?\d[\d\s\-]{8,15})"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Phone Number Not Found"
# ======================================
# Extract Name
# ======================================

def extract_name(text):

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if line:
            return line

    return "Name Not Found"
# ======================================
# Extract Skills
# ======================================

def _skill_key(skill):
    return re.sub(r"[^a-z0-9#+]+", " ", skill.lower()).strip()


def _dedupe_skills(skills):
    seen = set()
    deduped = []
    for skill in skills:
        key = _skill_key(skill)
        if key and key not in seen:
            seen.add(key)
            deduped.append(skill.strip())
    return deduped


def _extract_known_skills(text):
    found_skills = []
    text_lower = text.lower()
    normalized_text = re.sub(r"[^a-z0-9+#]+", " ", text_lower)
    compact_text = re.sub(r"[^a-z0-9#+]+", "", text_lower)

    for skill in SKILLS:
        skill_lower = skill.lower()
        skill_compact = re.sub(r"[^a-z0-9#+]+", "", skill_lower)

        if skill_lower == "c":
            if re.search(r"\bc\b", normalized_text):
                found_skills.append(skill)
        elif skill_lower == "c++":
            if "c++" in text_lower:
                found_skills.append(skill)
        elif skill_lower == "c#":
            if re.search(r"\bc#\b", normalized_text):
                found_skills.append(skill)
        elif skill_lower == "r":
            if re.search(r"\br\b", normalized_text):
                found_skills.append(skill)
        else:
            if re.search(r"\b" + re.escape(skill_lower) + r"\b", normalized_text):
                found_skills.append(skill)
            elif len(skill_compact) > 2 and skill_compact in compact_text:
                found_skills.append(skill)

    return found_skills


def extract_skills(text):
    skill_section_skills = extract_skill_section(text)
    known_skills = _extract_known_skills(text)

    if not skill_section_skills and not known_skills:
        fallback_skills = _parse_skill_tokens(text)
        return _dedupe_skills(fallback_skills)

    return _dedupe_skills(skill_section_skills + known_skills)


def parse_resume(file_path, job_description=None):
    """Parse resume file and run NLP intelligence and ATS analysis."""

    text = extract_resume_text(file_path)

    if not text or not text.strip():
        raise ValueError("No readable text could be extracted from the resume.")

    analyze_resume_text, analyze_ats = _get_resume_intelligence_helpers()
    intelligence = analyze_resume_text(text)
    parsed_name = extract_name(text)
    parsed_email = extract_email(text)
    parsed_phone = extract_phone(text)

    ats_result = analyze_ats(
        resume_text=text,
        name=parsed_name,
        email=parsed_email,
        phone=parsed_phone,
        job_description=job_description,
    )

    return {
        "text": text,
        "name": parsed_name,
        "email": parsed_email,
        "phone": parsed_phone,
        "sections_found": extract_resume_sections(text),
        "word_count": intelligence["word_count"],
        "skill_candidates": intelligence["skill_candidates"],
        "role_candidates": intelligence["role_candidates"],
        "entities": intelligence["entities"],
        "ats_result": ats_result,
    }

# ======================================
# Calculate ATS Score
# ======================================

def calculate_ats_score(name, email, phone, skills, word_count):

    score = 0

    # Name
    if name != "Name Not Found":
        score += 10

    # Email
    if email != "Email Not Found":
        score += 10

    # Phone
    if phone != "Phone Number Not Found":
        score += 10

    # Skills
    score += min(len(skills) * 5, 40)

    # Resume Length
    if word_count >= 200:
        score += 20
    elif word_count >= 100:
        score += 10

    return score
# ======================================
# Extract Job Description Skills
# ======================================

SKILL_SECTION_HEADERS = [
    "skills",
    "technical skills",
    "technical expertise",
    "skill set",
    "skillset",
    "areas of expertise",
    "expertise",
    "tools",
    "technologies",
    "knowledge",
    "proficiencies",
    "competencies",
    "qualifications",
    "requirements",
    "required",
    "preferred",
    "responsibilities",
    "responsibilities:"
]


def _split_camelcase_token(token):
    return re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z0-9#+]+|[A-Z]+|[a-z0-9#+]+", token)


def _normalize_skill(token):
    return token.strip(" .-–—")


def _is_probable_skill_line(line):
    stripped = line.strip()
    if not stripped:
        return False

    if re.match(r"^[\-\*•·\d]+\s+", stripped):
        return True

    list_delimiter = bool(re.search(r"[,;/•·]|\band\b|\b&\b", stripped, flags=re.IGNORECASE))
    if list_delimiter:
        return True

    words = stripped.split()
    if len(words) > 8:
        return False

    tokens = [t for t in re.split(r"[,;/•·]|\band\b|\b&\b|\s+", stripped) if t]
    if len(tokens) < 2:
        return False

    acronym_count = sum(1 for t in tokens if re.fullmatch(r"[A-Z][A-Z0-9#]*", t))
    title_count = sum(1 for t in tokens if re.fullmatch(r"[A-Z][a-z]+", t))
    lowercase_count = sum(1 for t in tokens if re.fullmatch(r"[a-z]+", t))

    return acronym_count >= 1 or title_count >= 2 or lowercase_count >= 3


SKILL_NOISE_WORDS = {
    "with",
    "and",
    "or",
    "to",
    "for",
    "of",
    "in",
    "experience",
    "experienced",
    "knowledge",
    "proficient",
    "familiar",
    "ability",
    "skills",
    "skill"
}


def _clean_skill_token(token):
    token = re.sub(r"^(experience|experienced|knowledge of|knowledge|proficient in|familiar with|ability to|skills?:?)\s+", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\s+(experience|experienced|knowledge of|knowledge|proficient in|familiar with|ability to|skills?:?)$", "", token, flags=re.IGNORECASE)
    token = token.strip(" .-–—")
    if token.lower() in SKILL_NOISE_WORDS:
        return ""
    return token


def _parse_skill_tokens(text):
    tokens = []
    raw_items = re.split(r"[,;/•·]|\band\b|\b&\b|\n", text, flags=re.IGNORECASE)

    for item in raw_items:
        item = _normalize_skill(item)
        if not item:
            continue

        item = re.sub(r"^(experience|experienced|knowledge of|knowledge|proficient in|familiar with|ability to|skills?:?)\s+", "", item, flags=re.IGNORECASE)
        item = re.sub(r"\s+(experience|experienced|knowledge of|knowledge|proficient in|familiar with|ability to|skills?:?)$", "", item, flags=re.IGNORECASE)
        item = re.sub(r"\s{2,}", " ", item)
        if not item:
            continue

        if " " not in item:
            tokens.extend(_split_camelcase_token(item))
            continue

        if item == item.lower() or item == item.upper() or item == item.title():
            tokens.append(item)
            continue

        words = item.split()
        current = [words[0]]

        for word in words[1:]:
            if current[-1].istitle() and word.istitle():
                current.append(word)
            elif current[-1].isupper() and word.isupper():
                tokens.append(" ".join(current))
                current = [word]
            elif current[-1].istitle() and word.isupper():
                tokens.append(" ".join(current))
                current = [word]
            elif current[-1].islower() and word.islower():
                current.append(word)
            elif current[-1].istitle() and word.islower():
                current.append(word)
            else:
                tokens.append(" ".join(current))
                current = [word]

        tokens.append(" ".join(current))

    cleaned = [_clean_skill_token(token) for token in tokens]
    return [token for token in cleaned if token]

def _find_skill_section(text, headers):
    for header in headers:
        pattern = rf"(?im)^{re.escape(header)}\s*[:\-]?\s*(.+?)(?:\n\s*\n|$)"
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            return match.group(1).strip()
    return None


def extract_skill_section(text):
    section = _find_skill_section(text, SKILL_SECTION_HEADERS)
    if section:
        return _parse_skill_tokens(section)

    lines = [line.rstrip() for line in text.splitlines()]
    skill_block = []

    for line in reversed(lines):
        stripped = line.strip()
        if not stripped:
            if skill_block:
                break
            continue

        if _is_probable_skill_line(stripped):
            skill_block.append(stripped)
        elif skill_block:
            break

    if skill_block:
        skill_block.reverse()
        return _parse_skill_tokens("\n".join(skill_block))

    probable_lines = [line.strip() for line in lines if _is_probable_skill_line(line)]
    if probable_lines:
        return _parse_skill_tokens("\n".join(probable_lines))

    return []


# ======================================
# Resume Insights
# ======================================
RESUME_SECTION_HEADERS = [
    "summary",
    "profile",
    "experience",
    "professional experience",
    "work experience",
    "education",
    "skills",
    "certifications",
    "projects",
    "honors",
    "awards",
    "publications",
    "leadership",
    "languages",
    "objectives",
    "profile summary"
]

SECTION_ICON_MAP = {
    "summary": "Summary",
    "profile": "Profile",
    "experience": "Experience",
    "professional experience": "Experience",
    "work experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "certifications": "Certifications",
    "projects": "Projects",
    "honors": "Honors",
    "awards": "Awards",
    "publications": "Publications",
    "leadership": "Leadership",
    "languages": "Languages",
    "objectives": "Objective",
    "profile summary": "Summary"
}


def extract_resume_sections(text):
    normalized = text.lower()
    found = []

    for header in RESUME_SECTION_HEADERS:
        pattern = rf"(?im)^\s*{re.escape(header)}\s*[:\-]?\s*$"
        if re.search(pattern, normalized):
            section_name = SECTION_ICON_MAP.get(header, header.title())
            if section_name not in found:
                found.append(section_name)

    if not found:
        for line in text.splitlines():
            title = line.strip().lower()
            if title in SECTION_ICON_MAP and SECTION_ICON_MAP[title] not in found:
                found.append(SECTION_ICON_MAP[title])

    return found


def estimate_page_count(text, word_count):
    if word_count <= 0:
        return 1
    return max(1, math.ceil(word_count / 300))


def estimate_reading_time(word_count):
    if word_count <= 0:
        return 1
    return math.ceil(word_count / 200)


def resume_completion_status(text, word_count, sections_found):
    section_set = {section.lower() for section in sections_found}
    has_core = any(key in section_set for key in ["experience", "education", "skills"])
    if word_count < 200:
        return "Needs more detail"
    if has_core and len(sections_found) >= 3:
        return "Complete resume"
    if has_core:
        return "Good structure"
    return "Add key sections"


# ======================================
# Score Tier Helper (Green / Yellow / Red)
# Used across templates for visual-hierarchy
# colour coding on any 0-100 score.
# ======================================

def score_tier(value):
    """Return 'green' (>=80), 'yellow' (50-79), or 'red' (<50) for a 0-100 score."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "red"
    if value >= 80:
        return "green"
    if value >= 50:
        return "yellow"
    return "red"


# ======================================
# Profile Strength Meter
# Percentage of key resume sections present,
# similar to a "profile completeness" bar.
# ======================================

PROFILE_STRENGTH_CHECKS = [
    ("contact_info", "Contact information"),
    ("summary", "Professional summary"),
    ("experience", "Work experience"),
    ("education", "Education"),
    ("skills", "Skills section"),
    ("projects", "Projects"),
    ("certifications", "Certifications"),
]


def calculate_profile_strength(name, email, phone, sections_found, skills):
    """Return (percentage, checklist) describing how complete the resume profile is."""
    section_set = {section.lower() for section in sections_found}
    has_contact = (
        name != "Name Not Found"
        and email != "Email Not Found"
        and phone != "Phone Number Not Found"
    )

    checklist = []
    passed_count = 0

    for key, label in PROFILE_STRENGTH_CHECKS:
        if key == "contact_info":
            passed = has_contact
        elif key == "skills":
            passed = bool(skills) or "skills" in section_set
        else:
            passed = key in section_set

        if passed:
            passed_count += 1
        checklist.append({"label": label, "passed": passed})

    percentage = round((passed_count / len(PROFILE_STRENGTH_CHECKS)) * 100)
    return percentage, checklist


# ======================================
# Format & Style Checker
# Flags ATS-breaking formatting issues:
# missing contact info, bad length, no
# bullet points, overly long lines, etc.
# ======================================

def run_format_style_checks(text, name, email, phone, word_count, sections_found):
    """Return (checks, percentage) — a pass/fail checklist for resume formatting quality."""
    section_set = {section.lower() for section in sections_found}
    lines = [line for line in text.splitlines() if line.strip()]
    bullet_lines = [line for line in lines if re.match(r"^\s*[\-\*•·]", line)]
    long_lines = [line for line in lines if len(line) > 220]

    has_contact = email != "Email Not Found" and phone != "Phone Number Not Found"
    length_ok = 200 <= word_count <= 1000

    checks = [
        {
            "label": "Contact details detected",
            "passed": has_contact,
            "detail": "Email and phone number were found in the resume."
                if has_contact else
                "Add a clear email and phone number near the top of your resume."
        },
        {
            "label": "Resume length is appropriate",
            "passed": length_ok,
            "detail": f"{word_count} words — a healthy resume length."
                if length_ok else
                f"{word_count} words detected — aim for 400–800 words for best ATS results."
        },
        {
            "label": "Uses bullet points",
            "passed": len(bullet_lines) >= 3,
            "detail": f"{len(bullet_lines)} bullet points detected."
                if len(bullet_lines) >= 3 else
                "Use bullet points to list achievements instead of long paragraphs."
        },
        {
            "label": "No overly long lines",
            "passed": len(long_lines) == 0,
            "detail": "No excessively long lines found."
                if not long_lines else
                f"{len(long_lines)} line(s) may wrap awkwardly during ATS parsing."
        },
        {
            "label": "Key sections present",
            "passed": len(section_set) >= 3,
            "detail": f"{len(section_set)} section heading(s) detected."
                if len(section_set) >= 3 else
                "Add clear section headings like Experience, Education, and Skills."
        },
        {
            "label": "Name detected",
            "passed": name != "Name Not Found",
            "detail": "Candidate name found at the top of the resume."
                if name != "Name Not Found" else
                "Make sure your name appears clearly as the first line of your resume."
        },
    ]

    passed_count = sum(1 for check in checks if check["passed"])
    percentage = round((passed_count / len(checks)) * 100) if checks else 0

    return checks, percentage


def get_skill_icon(skill, profession_field=None):
    normalized_skill = skill.strip().lower()
    if normalized_skill in SKILL_ICON_MAP:
        return SKILL_ICON_MAP[normalized_skill]

    if profession_field:
        if profession_field in PROFESSION_ICON_FALLBACK:
            profession_icon = PROFESSION_ICON_FALLBACK[profession_field]
        else:
            profession_icon = PROFESSION_ICON_FALLBACK["General Professional"]
    else:
        profession_icon = PROFESSION_ICON_FALLBACK["General Professional"]

    if any(keyword in normalized_skill for keyword in ["doctor", "medical", "health", "clinic", "nurse", "patient"]):
        return "bi-heart-pulse"
    if any(keyword in normalized_skill for keyword in ["account", "audit", "finance", "tax", "ledger", "budget"]):
        return "bi-calculator"
    if any(keyword in normalized_skill for keyword in ["design", "ui", "ux", "brand", "creative"]):
        return "bi-palette"
    if any(keyword in normalized_skill for keyword in ["data", "analytics", "machine learning", "statistics", "business intelligence"]):
        return "bi-bar-chart-line"

    return profession_icon


def infer_profession_field(text, job_description=""):
    combined = f"{text}\n{job_description}".lower()
    for field, keywords in PROFESSION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined:
                return field
    return "General Professional"


def extract_job_description_skills(text):
    job_skills = extract_skill_section(text)
    if not job_skills:
        job_skills = _extract_known_skills(text)
    if not job_skills:
        job_skills = _parse_skill_tokens(text)

    return _dedupe_skills(job_skills)


# ======================================
# Match Resume with Job Description
# ======================================

def _normalize_skill_token_for_match(skill):
    return re.sub(r"[^a-z0-9#+]+", " ", skill.lower()).strip()


def match_job_description(resume_skills, job_description):
    matched_skills = []
    missing_skills = []

    job_skills = extract_job_description_skills(job_description)
    resume_skills_normalized = {
        _normalize_skill_token_for_match(skill): skill
        for skill in resume_skills
    }

    for job_skill in job_skills:
        normalized_job_skill = _normalize_skill_token_for_match(job_skill)
        if normalized_job_skill in resume_skills_normalized:
            matched_skills.append(job_skill)
        else:
            missing_skills.append(job_skill)

    if len(job_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = round(
            len(matched_skills) / len(job_skills) * 100
        )

    return matched_skills, missing_skills, match_percentage
