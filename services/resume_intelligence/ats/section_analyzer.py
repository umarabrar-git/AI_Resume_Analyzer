import re


SECTION_PATTERNS = {
    "summary": [
        r"\bprofessional summary\b",
        r"\bcareer summary\b",
        r"\bsummary\b",
        r"\bprofile\b",
        r"\bobjective\b"
    ],

    "experience": [
        r"\bwork experience\b",
        r"\bprofessional experience\b",
        r"\bemployment history\b",
        r"\bexperience\b"
    ],

    "education": [
        r"\beducation\b",
        r"\bacademic background\b",
        r"\bacademic qualifications\b",
        r"\bqualifications\b"
    ],

    "skills": [
        r"\btechnical skills\b",
        r"\bprofessional skills\b",
        r"\bcore competencies\b",
        r"\bskills\b"
    ],

    "projects": [
        r"\bprojects\b",
        r"\bprofessional projects\b",
        r"\bacademic projects\b"
    ],

    "certifications": [
        r"\bcertifications\b",
        r"\bcertificates\b",
        r"\blicenses\b"
    ]
}


CORE_SECTIONS = {
    "experience",
    "education",
    "skills"
}


def detect_sections(text):
    """Detect common ATS resume sections."""

    text = text or ""

    detected = {}

    for section, patterns in SECTION_PATTERNS.items():

        found = any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )
            for pattern in patterns
        )

        detected[section] = found

    return detected


def analyze_sections(text):
    """
    Score resume structure out of 25.
    """

    detected = detect_sections(text)

    score = 0

    # Core sections carry more weight.
    weights = {
        "experience": 7,
        "education": 6,
        "skills": 5,
        "summary": 3,
        "projects": 2,
        "certifications": 2
    }

    missing = []

    for section, weight in weights.items():

        if detected.get(section):
            score += weight

        else:
            missing.append(section)

    return {
        "score": min(score, 25),
        "max_score": 25,
        "detected": detected,
        "missing": missing,
        "core_missing": [
            section
            for section in CORE_SECTIONS
            if not detected.get(section)
        ]
    }