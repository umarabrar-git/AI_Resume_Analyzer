SYSTEM_PROMPT = """
You are an expert resume editor.

Rewrite experience content without changing the underlying facts.

Never invent:
- employers
- job titles
- dates
- responsibilities
- technologies
- achievements
- percentages
- financial figures
- team sizes

Improve clarity, impact and ATS readability while preserving truth.
"""


def build_experience_prompt(
    source_text: str,
    resume_text: str,
    job_description: str | None = None,
    instructions: str | None = None,
) -> str:

    return f"""
Rewrite the following resume experience content.

SOURCE EXPERIENCE:
{source_text}

FULL RESUME CONTEXT:
{resume_text}

JOB DESCRIPTION:
{job_description or "Not provided"}

ADDITIONAL INSTRUCTIONS:
{instructions or "None"}

Requirements:
1. Preserve factual meaning.
2. Use concise professional language.
3. Prefer action-oriented wording where appropriate.
4. Improve relevance to the job description only when supported.
5. Do not invent metrics.
6. Do not invent responsibilities.
7. Return only the rewritten experience content.
""".strip()