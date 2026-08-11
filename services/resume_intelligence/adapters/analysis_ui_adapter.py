from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class ChecklistItem:
    label: str
    passed: bool


@dataclass(frozen=True)
class FormatCheckItem:
    label: str
    detail: str
    passed: bool


class AnalysisUIAdapter:
    """
    Converts Resume Intelligence output into a stable UI contract.

    Important:
    - Raw ATS component points are normalized to percentages.
    - No fake chart scores are generated.
    - Format checks are derived from actual ATS evidence.
    - Existing Jinja components remain independent of backend internals.
    """

    DEFAULT_ROLE = "General Professional"

    SECTION_LABELS = {
        "summary": "Summary",
        "professional_summary": "Summary",
        "profile": "Summary",
        "objective": "Summary",

        "experience": "Experience",
        "work_experience": "Experience",
        "employment": "Experience",

        "education": "Education",

        "skills": "Skills",
        "technical_skills": "Skills",
        "core_skills": "Skills",

        "projects": "Projects",

        "certifications": "Certifications",
        "certificates": "Certifications",

        "languages": "Languages",

        "achievements": "Achievements",
        "awards": "Achievements",

        "contact": "Contact",
    }

    # =========================================================
    # PUBLIC API
    # =========================================================

    def build(
        self,
        analysis_result: Optional[Mapping[str, Any]],
        *,
        resume_text: str = "",
        job_description: str = "",
    ) -> Dict[str, Any]:

        result = self._mapping(
            analysis_result
        )

        # Unwrap if the workflow wrapped the result under "analysis_result"
        if isinstance(result.get("analysis_result"), dict):
            result = result["analysis_result"]

        # Also check for "raw" sibling that contains the flat values
        raw = self._mapping(result.get("raw"))

        # -----------------------------------------------------
        # Main result areas
        # -----------------------------------------------------

        ats = self._first_mapping(
            result,
            "ats",
            "ats_result",
            "ats_analysis",
        )

        match = self._first_mapping(
            result,
            "job_match",
            "matching",
            "match",
            "match_result",
        )

        resume = self._first_mapping(
            result,
            "resume",
            "resume_analysis",
            "nlp",
            "resume_data",
        )

        semantic = self._first_mapping(
            result,
            "semantic",
            "semantic_analysis",
        )

        # -----------------------------------------------------
        # ATS overall
        # -----------------------------------------------------

        ats_score = self._normalize_percentage(
            self._first_value(
                ats,
                "ats_score",
                "overall_score",
                "score",
                default=self._first_value(
                    raw,
                    "ats_score",
                    default=0,
                ),
            )
        )

        # -----------------------------------------------------
        # ATS sub-analysis
        # -----------------------------------------------------

        sections_result = self._first_mapping(
            ats,
            "sections",
        )

        content_result = self._first_mapping(
            ats,
            "content",
        )

        keyword_result = self._first_mapping(
            ats,
            "keywords",
        )

        contact_result = self._first_mapping(
            ats,
            "contact",
        )

        readability_result = self._first_mapping(
            ats,
            "readability",
        )

        ats_breakdown = {
            "structure":
                self._component_percentage(
                    sections_result
                ),

            "content":
                self._component_percentage(
                    content_result
                ),

            "keywords":
                self._component_percentage(
                    keyword_result
                ),

            "contact":
                self._component_percentage(
                    contact_result
                ),

            "readability":
                self._component_percentage(
                    readability_result
                ),
        }

        # Compatibility with current ats-chart.js.
        ats_breakdown["sections"] = (
            ats_breakdown["structure"]
        )

        ats_breakdown["formatting"] = (
            ats_breakdown["structure"]
        )

        # -----------------------------------------------------
        # Job matching
        # -----------------------------------------------------

        match_percentage = self._extract_match_percentage(
            match=match,
            keywords=keyword_result,
        )
        # Fall back to raw when structured sub-objects are empty
        if not match_percentage:
            match_percentage = self._normalize_percentage(
                self._first_value(raw, "match_percentage", default=0)
            )

        matched_skills = self._string_list(
            self._first_value(
                match,
                "matched_skills",
                "matched_required",
                "matched",
                default=self._first_value(
                    keyword_result,
                    "matched",
                    default=self._first_value(raw, "matched_skills", default=[]),
                ),
            )
        )

        missing_skills = self._string_list(
            self._first_value(
                match,
                "missing_skills",
                "missing_required",
                "missing",
                "skill_gaps",
                default=self._first_value(
                    keyword_result,
                    "missing",
                    default=self._first_value(raw, "missing_skills", default=[]),
                ),
            )
        )

        # -----------------------------------------------------
        # Skills
        # -----------------------------------------------------

        raw_skills = self._first_value(
            resume,
            "skills",
            "detected_skills",
            "extracted_skills",
            default=None,
        )

        if raw_skills is None:
            raw_skills = self._first_value(
                result,
                "skills",
                "detected_skills",
                default=None,
            )

        # ATS keyword candidates are a useful final fallback.
        if raw_skills is None:
            raw_skills = self._first_value(
                keyword_result,
                "resume_candidates",
                default=self._first_value(raw, "skills", default=[]),
            )

        skills = self._string_list(
            raw_skills
        )

        skill_labels, skill_scores = (
            self._build_skill_chart_data(
                raw_skills=raw_skills,
                skills=skills,
                semantic=semantic,
                result=result,
            )
        )

        # -----------------------------------------------------
        # Role / profession
        # -----------------------------------------------------

        profession_field = self._profession(
            result,
            resume,
        )

        # -----------------------------------------------------
        # Sections
        # -----------------------------------------------------

        sections_found = self._sections(
            result=result,
            resume=resume,
            ats_sections=sections_result,
        )

        # -----------------------------------------------------
        # Resume metrics
        # -----------------------------------------------------

        word_count = self._word_count(
            resume_text,
            content_result,
        )

        reading_time = (
            max(
                1,
                math.ceil(
                    word_count / 200
                ),
            )
            if word_count
            else 0
        )

        page_count = self._page_estimate(
            word_count
        )

        # -----------------------------------------------------
        # Profile completeness
        # -----------------------------------------------------

        profile_checklist = (
            self._profile_checklist(
                sections_found
            )
        )

        profile_strength = (
            self._profile_strength(
                profile_checklist
            )
        )

        resume_status = (
            self._resume_status(
                ats_score,
                profile_strength,
            )
        )

        # -----------------------------------------------------
        # Format checker
        # -----------------------------------------------------

        format_checks = self._build_format_checks(
            sections=sections_result,
            contact=contact_result,
            readability=readability_result,
            content=content_result,
        )

        format_score = self._format_score(
            format_checks
        )

        # -----------------------------------------------------
        # Recommendations
        # -----------------------------------------------------

        recommendations = self._first_value(
            result,
            "recommendations",
            default=None,
        )

        if recommendations is None:
            recommendations = self._first_value(
                ats,
                "recommendations",
                default=[],
            )

        # -----------------------------------------------------
        # Final stable UI contract
        # -----------------------------------------------------

        return {
            # ATS
            "ats_score":
                ats_score,

            "ats_rating":
                self._first_value(
                    ats,
                    "rating",
                    default="",
                ),

            "ats_breakdown":
                ats_breakdown,

            # Matching
            "match_percentage":
                match_percentage,

            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            # Skills
            "skills":
                skills,

            "skill_labels":
                skill_labels,

            "skill_scores":
                skill_scores,

            # Role
            "profession_field":
                profession_field,

            # Resume insight
            "resume_status":
                resume_status,

            "sections_found":
                sections_found,

            "page_count":
                page_count,

            "word_count":
                word_count,

            "reading_time":
                reading_time,

            "profile_strength":
                profile_strength,

            "profile_checklist":
                profile_checklist,

            # Format checker
            "format_score":
                format_score,

            "format_checks":
                format_checks,

            # Recommendations
            "recommendations":
                recommendations or [],

            # Preserve original AI result
            "analysis_result":
                dict(result),

            # Preview data
            "text":
                resume_text or "",

            "job_description":
                job_description or "",
        }

    # =========================================================
    # ATS SCORE NORMALIZATION
    # =========================================================

    @staticmethod
    def _component_percentage(
        component: Mapping[str, Any]
    ) -> int:
        """
        Convert component points to 0-100.

        Examples:
            20/25 -> 80
            12/15 -> 80
             8/10 -> 80
        """

        if not component:
            return 0

        try:
            score = float(
                component.get(
                    "score",
                    0
                )
            )

            maximum = float(
                component.get(
                    "max_score",
                    0
                )
            )

        except (TypeError, ValueError):
            return 0

        if maximum <= 0:
            return 0

        percentage = (
            score / maximum
        ) * 100

        return int(
            round(
                max(
                    0,
                    min(
                        percentage,
                        100
                    )
                )
            )
        )

    @staticmethod
    def _normalize_percentage(
        value: Any
    ) -> int:

        try:
            number = float(value)

        except (TypeError, ValueError):
            return 0

        if 0 < number <= 1:
            number *= 100

        return int(
            round(
                max(
                    0,
                    min(
                        number,
                        100
                    )
                )
            )
        )

    # =========================================================
    # MATCHING
    # =========================================================

    def _extract_match_percentage(
        self,
        *,
        match: Mapping[str, Any],
        keywords: Mapping[str, Any],
    ) -> int:

        value = self._first_value(
            match,
            "match_percentage",
            "match_score",
            "overall_score",
            "percentage",
            "score",
            default=None,
        )

        if value is None:
            value = self._first_value(
                keywords,
                "match_percentage",
                default=0,
            )

        return self._normalize_percentage(
            value
        )

    # =========================================================
    # FORMAT CHECKER
    # =========================================================

    def _build_format_checks(
        self,
        *,
        sections: Mapping[str, Any],
        contact: Mapping[str, Any],
        readability: Mapping[str, Any],
        content: Mapping[str, Any],
    ) -> List[FormatCheckItem]:

        checks: List[FormatCheckItem] = []

        # -----------------------------------------------------
        # Core section structure
        # -----------------------------------------------------

        core_missing = self._string_list(
            sections.get(
                "core_missing",
                []
            )
        )

        if core_missing:
            detail = (
                "Missing core section(s): "
                + ", ".join(
                    item.title()
                    for item in core_missing
                )
                + "."
            )

            checks.append(
                FormatCheckItem(
                    label="Core resume sections",
                    detail=detail,
                    passed=False,
                )
            )

        else:
            checks.append(
                FormatCheckItem(
                    label="Core resume sections",
                    detail=(
                        "Experience, education and skills "
                        "sections were detected."
                    ),
                    passed=True,
                )
            )

        # -----------------------------------------------------
        # Contact information
        # -----------------------------------------------------

        missing_contact = self._string_list(
            contact.get(
                "missing",
                []
            )
        )

        if missing_contact:
            checks.append(
                FormatCheckItem(
                    label="Contact information",
                    detail=(
                        "Missing: "
                        + ", ".join(
                            item.title()
                            for item
                            in missing_contact
                        )
                        + "."
                    ),
                    passed=False,
                )
            )

        else:
            checks.append(
                FormatCheckItem(
                    label="Contact information",
                    detail=(
                        "Name, email and phone information "
                        "were detected."
                    ),
                    passed=True,
                )
            )

        # -----------------------------------------------------
        # ATS readability
        # -----------------------------------------------------

        readability_issues = (
            self._string_list(
                readability.get(
                    "issues",
                    []
                )
            )
        )

        if readability_issues:
            checks.append(
                FormatCheckItem(
                    label="ATS readability",
                    detail=(
                        readability_issues[0]
                    ),
                    passed=False,
                )
            )

        else:
            checks.append(
                FormatCheckItem(
                    label="ATS readability",
                    detail=(
                        "No text-level ATS readability "
                        "issues were detected."
                    ),
                    passed=True,
                )
            )

        # -----------------------------------------------------
        # Readable text extraction
        # -----------------------------------------------------

        try:
            word_count = int(
                content.get(
                    "word_count",
                    0
                )
            )
        except (TypeError, ValueError):
            word_count = 0

        enough_text = word_count >= 100

        checks.append(
            FormatCheckItem(
                label="Readable text extraction",
                detail=(
                    f"{word_count} readable words were "
                    f"extracted from the resume."
                    if enough_text
                    else
                    "Very little readable text was extracted; "
                    "the file may be difficult for ATS parsing."
                ),
                passed=enough_text,
            )
        )

        # -----------------------------------------------------
        # Section detectability
        # -----------------------------------------------------

        detected = self._mapping(
            sections.get(
                "detected",
                {}
            )
        )

        detected_count = sum(
            1
            for value in detected.values()
            if bool(value)
        )

        section_detectable = (
            detected_count >= 3
        )

        checks.append(
            FormatCheckItem(
                label="Section detectability",
                detail=(
                    f"{detected_count} standard resume "
                    f"sections were recognized."
                ),
                passed=section_detectable,
            )
        )

        return checks

    @staticmethod
    def _format_score(
        checks: List[FormatCheckItem]
    ) -> int:
        """
        UI pass percentage based only on actual checks.
        """

        if not checks:
            return 0

        passed = sum(
            1
            for check in checks
            if check.passed
        )

        return int(
            round(
                (
                    passed /
                    len(checks)
                ) * 100
            )
        )

    # =========================================================
    # SKILL CHART
    # =========================================================

    def _build_skill_chart_data(
        self,
        *,
        raw_skills: Any,
        skills: List[str],
        semantic: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> tuple[List[str], List[int]]:

        score_map: Dict[str, int] = {}

        # Scores attached directly to skills.
        if isinstance(
            raw_skills,
            (list, tuple)
        ):

            for item in raw_skills:

                if not isinstance(
                    item,
                    Mapping
                ):
                    continue

                name = (
                    item.get("name")
                    or item.get("skill")
                    or item.get("label")
                )

                if not name:
                    continue

                value = (
                    item.get("score")
                    or item.get("confidence")
                    or item.get("strength")
                )

                if value is None:
                    continue

                score_map[
                    str(name).casefold()
                ] = self._normalize_percentage(
                    value
                )

        semantic_scores = (
            self._first_value(
                semantic,
                "skill_scores",
                "skill_strengths",
                default={},
            )
        )

        self._merge_skill_scores(
            score_map,
            semantic_scores,
        )

        root_scores = self._first_value(
            result,
            "skill_scores",
            "skill_strengths",
            default={},
        )

        self._merge_skill_scores(
            score_map,
            root_scores,
        )

        # Keep only five skills in chart.
        labels = skills[:5]

        values = [
            score_map.get(
                skill.casefold(),
                0
            )
            for skill in labels
        ]

        # Rank only when actual scores exist.
        if any(values):

            ranked = sorted(
                zip(
                    labels,
                    values
                ),
                key=lambda item: item[1],
                reverse=True,
            )

            labels = [
                item[0]
                for item in ranked
            ]

            values = [
                item[1]
                for item in ranked
            ]

        return labels, values

    def _merge_skill_scores(
        self,
        target: Dict[str, int],
        values: Any,
    ) -> None:

        if isinstance(
            values,
            Mapping
        ):

            for name, score in values.items():

                if isinstance(
                    score,
                    Mapping
                ):

                    score = (
                        score.get("score")
                        or score.get("confidence")
                        or score.get("strength")
                    )

                if score is None:
                    continue

                target[
                    str(name).casefold()
                ] = self._normalize_percentage(
                    score
                )

            return

        if isinstance(
            values,
            (list, tuple)
        ):

            for item in values:

                if not isinstance(
                    item,
                    Mapping
                ):
                    continue

                name = (
                    item.get("name")
                    or item.get("skill")
                    or item.get("label")
                )

                score = (
                    item.get("score")
                    or item.get("confidence")
                    or item.get("strength")
                )

                if (
                    not name
                    or score is None
                ):
                    continue

                target[
                    str(name).casefold()
                ] = self._normalize_percentage(
                    score
                )

    # =========================================================
    # PROFESSION
    # =========================================================

    def _profession(
        self,
        result: Mapping[str, Any],
        resume: Mapping[str, Any],
    ) -> str:

        value = self._first_value(
            resume,
            "profession_field",
            "profession",
            "detected_role",
            "primary_role",
            "role",
            default=None,
        )

        if value is None:
            value = self._first_value(
                result,
                "profession_field",
                "profession",
                "detected_role",
                "primary_role",
                "role",
                default=None,
            )

        if not value:
            return self.DEFAULT_ROLE

        if isinstance(
            value,
            Mapping
        ):
            value = (
                value.get("name")
                or value.get("role")
                or value.get("label")
            )

        return (
            str(value).strip()
            if value
            else self.DEFAULT_ROLE
        )

    # =========================================================
    # SECTIONS
    # =========================================================

    def _sections(
        self,
        *,
        result: Mapping[str, Any],
        resume: Mapping[str, Any],
        ats_sections: Mapping[str, Any],
    ) -> List[str]:

        raw = self._first_value(
            resume,
            "sections_found",
            "sections",
            default=None,
        )

        if raw is None:
            raw = ats_sections.get(
                "detected"
            )

        if raw is None:
            raw = self._first_value(
                result,
                "sections_found",
                default=[],
            )

        sections: List[Any] = []

        if isinstance(
            raw,
            Mapping
        ):

            sections = [
                key
                for key, value
                in raw.items()
                if self._section_present(
                    value
                )
            ]

        elif isinstance(
            raw,
            (list, tuple, set)
        ):
            sections = list(raw)

        normalized = []
        seen = set()

        for section in sections:

            if isinstance(
                section,
                Mapping
            ):
                section = (
                    section.get("name")
                    or section.get("section")
                    or section.get("label")
                )

            if not section:
                continue

            key = (
                str(section)
                .strip()
                .casefold()
            )

            label = (
                self.SECTION_LABELS.get(
                    key,
                    key.replace(
                        "_",
                        " "
                    ).title(),
                )
            )

            identity = label.casefold()

            if identity in seen:
                continue

            seen.add(identity)
            normalized.append(label)

        return normalized

    @staticmethod
    def _section_present(
        value: Any
    ) -> bool:

        if isinstance(
            value,
            Mapping
        ):

            for key in (
                "found",
                "present",
                "detected",
            ):
                if key in value:
                    return bool(
                        value[key]
                    )

        return bool(value)

    # =========================================================
    # RESUME INSIGHTS
    # =========================================================

    @staticmethod
    def _word_count(
        resume_text: str,
        content: Mapping[str, Any],
    ) -> int:

        try:
            stored_count = int(
                content.get(
                    "word_count",
                    0
                )
            )
        except (TypeError, ValueError):
            stored_count = 0

        if stored_count > 0:
            return stored_count

        return len(
            (resume_text or "").split()
        )

    @staticmethod
    def _page_estimate(
        word_count: int
    ) -> int:

        if word_count <= 0:
            return 0

        return max(
            1,
            math.ceil(
                word_count / 500
            ),
        )

    def _profile_checklist(
        self,
        sections: List[str],
    ) -> List[ChecklistItem]:

        normalized = {
            item.casefold()
            for item in sections
        }

        def has(
            *names: str
        ) -> bool:

            return any(
                name.casefold()
                in normalized
                for name in names
            )

        return [
            ChecklistItem(
                "Professional summary",
                has("Summary"),
            ),
            ChecklistItem(
                "Work experience",
                has("Experience"),
            ),
            ChecklistItem(
                "Education",
                has("Education"),
            ),
            ChecklistItem(
                "Skills",
                has("Skills"),
            ),
            ChecklistItem(
                "Projects / achievements",
                has(
                    "Projects",
                    "Achievements",
                ),
            ),
        ]

    @staticmethod
    def _profile_strength(
        checklist: List[ChecklistItem]
    ) -> int:

        if not checklist:
            return 0

        passed = sum(
            item.passed
            for item in checklist
        )

        return int(
            round(
                passed
                / len(checklist)
                * 100
            )
        )

    @staticmethod
    def _resume_status(
        ats_score: int,
        profile_strength: int,
    ) -> str:

        combined = (
            ats_score * 0.65
            + profile_strength * 0.35
        )

        if combined >= 85:
            return "Excellent"

        if combined >= 70:
            return "Strong"

        if combined >= 55:
            return "Good"

        if combined >= 40:
            return "Needs Polish"

        return "Needs Improvement"

    # =========================================================
    # GENERIC HELPERS
    # =========================================================

    @staticmethod
    def _mapping(
        value: Any
    ) -> Mapping[str, Any]:

        return (
            value
            if isinstance(
                value,
                Mapping
            )
            else {}
        )

    def _first_mapping(
        self,
        source: Mapping[str, Any],
        *keys: str,
    ) -> Mapping[str, Any]:

        value = self._first_value(
            source,
            *keys,
            default={},
        )

        return self._mapping(
            value
        )

    @staticmethod
    def _first_value(
        source: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:

            if key not in source:
                continue

            value = source[key]

            if value is not None:
                return value

        return default

    @staticmethod
    def _string_list(
        values: Any
    ) -> List[str]:

        if not values:
            return []

        if isinstance(
            values,
            Mapping
        ):
            values = list(
                values.keys()
            )

        elif isinstance(
            values,
            str
        ):
            values = [values]

        if not isinstance(
            values,
            (list, tuple, set)
        ):
            return []

        result: List[str] = []
        seen = set()

        for value in values:

            if isinstance(
                value,
                Mapping
            ):
                value = (
                    value.get("name")
                    or value.get("skill")
                    or value.get("label")
                )

            if not value:
                continue

            text = str(
                value
            ).strip()

            if not text:
                continue

            identity = text.casefold()

            if identity in seen:
                continue

            seen.add(identity)
            result.append(text)

        return result