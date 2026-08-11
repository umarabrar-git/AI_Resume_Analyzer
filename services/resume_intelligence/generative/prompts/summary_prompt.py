SYSTEM_PROMPT = """
You are a professional resume writing assistant.

Your job is to improve resume content using only information
supported by the candidate's supplied resume and context.

Rules:
- Never invent employment, education, certifications or skills.
- Never invent numbers, percentages, revenue or achievements.
- Never claim expertise that is not supported by the source.
- Keep language professional and concise.
- Use ATS-friendly wording naturally.
- Do not keyword-stuff.
- Do not include explanations unless requested.
"""


def build_summary_prompt(
    resume_text: str,
    target_role: str | None = None,
    job_description: str | None = None,
    instructions: str | None = None,
) -> str:

    return f"""
Create a concise professional resume summary.

TARGET ROLE:
{target_role or "Not specified"}

JOB DESCRIPTION:
{job_description or "Not provided"}

CANDIDATE RESUME:
{resume_text}

ADDITIONAL INSTRUCTIONS:
{instructions or "None"}

Requirements:
1. Use only supported candidate information.
2. Focus on the most relevant strengths.
3. Avoid first-person pronouns.
4. Avoid generic filler.
5. Keep the summary approximately 2-4 sentences.
6. Do not invent metrics or qualifications.
7. Return only the finished professional summary.
""".strip()