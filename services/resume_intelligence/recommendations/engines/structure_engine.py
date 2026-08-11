from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


CORE_SECTIONS = {
    "experience",
    "education",
    "skills"
}


SECTION_LABELS = {
    "summary": "Professional Summary",
    "experience": "Work Experience",
    "education": "Education",
    "skills": "Skills",
    "projects": "Projects",
    "certifications": "Certifications"
}


def generate_structure_recommendations(
    ats_result
):
    recommendations = []

    section_data = (
        ats_result.get(
            "sections",
            {}
        )
        or {}
    )

    missing = section_data.get(
        "missing",
        []
    ) or []

    for section in missing:

        label = SECTION_LABELS.get(
            section,
            section.replace(
                "_",
                " "
            ).title()
        )

        is_core = section in CORE_SECTIONS

        recommendations.append(
            RecommendationBuilder.build(
                category="structure",

                priority=(
                    "critical"
                    if is_core
                    else "medium"
                ),

                title=f"Add {label}",

                message=(
                    f"A clearly identifiable {label} "
                    "section was not detected in your resume."
                ),

                action=(
                    f"Create a clearly labeled {label} "
                    "section using a conventional heading."
                ),

                impact=(
                    "Improves resume organization, "
                    "ATS parsing and recruiter navigation."
                ),

                evidence={
                    "missing_section":
                        section,

                    "core_section":
                        is_core
                },

                tags=[
                    "ats",
                    "structure",
                    section
                ]
            )
        )

    return recommendations