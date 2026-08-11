import re


def analyze_contact_information(
    name=None,
    email=None,
    phone=None
):
    """
    Contact/completeness score.

    Maximum: 15.
    """

    score = 0

    missing = []

    if name:
        score += 5
    else:
        missing.append("name")

    if email:
        score += 5
    else:
        missing.append("email")

    if phone:
        score += 5
    else:
        missing.append("phone")

    return {
        "score": score,
        "max_score": 15,
        "missing": missing
    }


def analyze_readability(text):
    """
    Basic text-level ATS readability checks.

    Maximum: 10.

    File-layout analysis will later be able to extend this.
    """

    text = text or ""

    score = 10

    issues = []

    # Excessive symbol usage can indicate parsing problems.
    symbol_count = len(
        re.findall(
            r"[★◆●■►▶✓✔❖]",
            text
        )
    )

    if symbol_count > 20:

        score -= 2

        issues.append(
            "Resume contains excessive decorative symbols."
        )

    # Extremely long lines may indicate extraction/layout problems.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    long_lines = [
        line
        for line in lines
        if len(line) > 250
    ]

    if len(long_lines) >= 5:

        score -= 2

        issues.append(
            "Some resume content may be difficult "
            "for parsers to interpret."
        )

    # Basic extraction quality.
    if len(text.split()) < 100:

        score -= 4

        issues.append(
            "Very little readable text was extracted."
        )

    return {
        "score": max(score, 0),
        "max_score": 10,
        "issues": issues
    }