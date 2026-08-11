import re


ACTION_VERBS = {
    "achieved",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "directed",
    "drove",
    "executed",
    "generated",
    "implemented",
    "improved",
    "increased",
    "launched",
    "led",
    "managed",
    "optimized",
    "organized",
    "reduced",
    "resolved",
    "streamlined",
    "supervised",
    "trained"
}


def _count_action_verbs(text):
    text_lower = (text or "").lower()

    return sum(
        1
        for verb in ACTION_VERBS
        if re.search(
            rf"\b{re.escape(verb)}\b",
            text_lower
        )
    )


def _count_quantified_achievements(text):
    """
    Detect achievement-style numbers such as:
    25%, $50K, 10 employees, 200 customers.
    """

    patterns = [
        r"\b\d+(?:\.\d+)?%",
        r"[$£€]\s?\d+(?:[,.]\d+)*(?:\s?[KMB])?",
        r"\b\d+(?:[,.]\d+)*\+?\s+"
        r"(?:users|clients|customers|employees|projects|"
        r"teams|members|sales|cases|patients|students)\b"
    ]

    matches = []

    for pattern in patterns:

        matches.extend(
            re.findall(
                pattern,
                text or "",
                flags=re.IGNORECASE
            )
        )

    return len(matches)


def analyze_content(text):
    """
    Analyze general resume content quality.

    Maximum: 25 points.
    """

    text = text or ""

    words = text.split()

    word_count = len(words)

    action_verb_count = _count_action_verbs(
        text
    )

    quantified_count = (
        _count_quantified_achievements(
            text
        )
    )

    score = 0

    feedback = []

    # Resume length/content density: max 8.
    if 300 <= word_count <= 1000:
        score += 8

    elif 200 <= word_count < 300:
        score += 6
        feedback.append(
            "Resume content may be slightly brief."
        )

    elif 1000 < word_count <= 1300:
        score += 6
        feedback.append(
            "Resume may benefit from more concise content."
        )

    elif word_count >= 100:
        score += 3
        feedback.append(
            "Review resume length and content density."
        )

    else:
        feedback.append(
            "Resume contains very limited readable content."
        )

    # Action-oriented language: max 8.
    if action_verb_count >= 8:
        score += 8

    elif action_verb_count >= 5:
        score += 6

    elif action_verb_count >= 2:
        score += 4

    else:
        feedback.append(
            "Use stronger action-oriented language "
            "in experience descriptions."
        )

    # Quantified achievements: max 9.
    if quantified_count >= 5:
        score += 9

    elif quantified_count >= 3:
        score += 7

    elif quantified_count >= 1:
        score += 4

    else:
        feedback.append(
            "Add measurable achievements where appropriate."
        )

    return {
        "score": min(score, 25),
        "max_score": 25,
        "word_count": word_count,
        "action_verbs": action_verb_count,
        "quantified_achievements": quantified_count,
        "feedback": feedback
    }