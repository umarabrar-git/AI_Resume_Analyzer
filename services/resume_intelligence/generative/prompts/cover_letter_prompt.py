SYSTEM_PROMPT = """
You create professional cover letters grounded in candidate-provided
resume information.

Never fabricate candidate history or qualifications.
Do not claim experience that cannot be supported by the resume.
"""


def build_cover_letter_prompt(
    resume_text: str,
    job_description: str | None = None,
    target_role: str | None = None,
    instructions: str | None = None,
) -> str:

    return f"""
Write a professional cover letter.

TARGET ROLE:
{target_role or "Not specified"}

JOB DESCRIPTION:
{job_description or "Not provided"}

CANDIDATE RESUME:
{resume_text}

ADDITIONAL INSTRUCTIONS:
{instructions or "None"}

Requirements:
1. Ground candidate claims in the supplied resume.
2. Explain relevant value without exaggeration.
3. Use a professional and natural tone.
4. Avoid generic filler.
5. Do not invent company-specific facts not supplied above.
6. Do not invent candidate achievements.
7. Keep the letter concise.
8. Return only the cover letter.
""".strip()