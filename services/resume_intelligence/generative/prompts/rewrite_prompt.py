SYSTEM_PROMPT = """
You are an AI resume optimization assistant.

You may improve wording, organization and relevance, but you must
preserve candidate truth.

Never fabricate candidate facts.
Never add unsupported skills or experience.
Never create fake measurable achievements.
"""


def build_rewrite_prompt(
    resume_text: str,
    job_description: str | None = None,
    recommendations=None,
    instructions: str | None = None,
) -> str:

    recommendations = recommendations or []

    recommendation_text = "\n".join(
        f"- {item.get('title', 'Recommendation')}: "
        f"{item.get('action', item.get('message', ''))}"
        for item in recommendations
    )

    return f"""
Optimize the resume below.

RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description or "Not provided"}

ANALYSIS RECOMMENDATIONS:
{recommendation_text or "None"}

USER INSTRUCTIONS:
{instructions or "None"}

Requirements:
1. Preserve all factual candidate information.
2. Improve clarity and professional tone.
3. Improve ATS readability.
4. Address applicable recommendations.
5. Improve job alignment only using truthful existing evidence.
6. Do not invent qualifications or metrics.
7. Do not remove important factual information without reason.
8. Return only the improved resume content.
""".strip()