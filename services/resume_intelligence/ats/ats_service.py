from services.resume_intelligence.ats.section_analyzer import (
    analyze_sections
)

from services.resume_intelligence.ats.content_analyzer import (
    analyze_content
)

from services.resume_intelligence.ats.keyword_analyzer import (
    analyze_keywords
)

from services.resume_intelligence.ats.scoring_engine import (
    analyze_contact_information,
    analyze_readability
)


def _get_rating(score):
    """Convert numerical ATS score into UI-friendly rating."""

    if score >= 90:
        return "Excellent"

    if score >= 80:
        return "Strong"

    if score >= 70:
        return "Good"

    if score >= 60:
        return "Needs Improvement"

    return "Weak"


def _build_recommendations(
    sections,
    content,
    keywords,
    contact,
    readability
):
    """Build deterministic recommendations from ATS evidence."""

    recommendations = []

    # Sections
    for section in sections["core_missing"]:

        recommendations.append(
            {
                "type": "structure",
                "priority": "high",
                "title": f"Add {section.title()} Section",
                "message":
                    f"Your resume does not appear to contain "
                    f"a clear {section} section."
            }
        )

    # Contact
    for item in contact["missing"]:

        recommendations.append(
            {
                "type": "contact",
                "priority": "high",
                "title": f"Add {item.title()}",
                "message":
                    f"Include your {item} so recruiters can "
                    f"identify and contact you."
            }
        )

    # Content feedback
    for message in content["feedback"]:

        recommendations.append(
            {
                "type": "content",
                "priority": "medium",
                "title": "Improve Resume Content",
                "message": message
            }
        )

    # JD gaps
    if (
        keywords["job_description_used"]
        and keywords["missing"]
    ):

        recommendations.append(
            {
                "type": "keywords",
                "priority": "high",
                "title": "Review Job-Specific Keywords",
                "message":
                    "Your resume may be missing relevant "
                    "skills or phrases found in the job description."
            }
        )

    # Readability
    for issue in readability["issues"]:

        recommendations.append(
            {
                "type": "readability",
                "priority": "medium",
                "title": "Improve ATS Readability",
                "message": issue
            }
        )

    return recommendations


def analyze_ats(
    resume_text,
    name=None,
    email=None,
    phone=None,
    job_description=None
):
    """
    Run complete ATS analysis.

    Final score: 0-100.
    """

    if not resume_text or not resume_text.strip():

        raise ValueError(
            "Resume text is required for ATS analysis."
        )

    sections = analyze_sections(
        resume_text
    )

    content = analyze_content(
        resume_text
    )

    keywords = analyze_keywords(
        resume_text,
        job_description
    )

    contact = analyze_contact_information(
        name=name,
        email=email,
        phone=phone
    )

    readability = analyze_readability(
        resume_text
    )

    total_score = (
        sections["score"]
        + content["score"]
        + keywords["score"]
        + contact["score"]
        + readability["score"]
    )

    total_score = round(
        min(total_score, 100),
        2
    )

    recommendations = (
        _build_recommendations(
            sections,
            content,
            keywords,
            contact,
            readability
        )
    )

    return {
        "ats_score":
            total_score,

        "rating":
            _get_rating(total_score),

        "breakdown": {
            "structure":
                sections["score"],

            "content":
                content["score"],

            "keywords":
                keywords["score"],

            "contact":
                contact["score"],

            "readability":
                readability["score"]
        },

        "sections":
            sections,

        "content":
            content,

        "keywords":
            keywords,

        "contact":
            contact,

        "readability":
            readability,

        "recommendations":
            recommendations
    }