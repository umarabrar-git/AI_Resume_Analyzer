from __future__ import annotations

from io import BytesIO
from typing import Callable, Dict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .report_data import ReportData


class PDFReportExporter:
    """
    Generates a real PDF report using ReportLab.

    Templates:
        professional
        modern
        minimal
        executive
        ai_insights
        career_analytics
    """

    SUPPORTED_TEMPLATES = {
        "professional",
        "modern",
        "minimal",
        "executive",
        "ai_insights",
        "career_analytics",
    }

    def export(
        self,
        report: ReportData,
        *,
        template: str = "professional",
    ) -> BytesIO:

        template = template.lower().strip()

        if template not in self.SUPPORTED_TEMPLATES:
            raise ValueError(
                f"Unsupported PDF template: {template}"
            )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=f"{report.name} - Resume Analysis Report",
            author="AI Resume Analyzer",
        )

        styles = self._build_styles(template)

        story = []

        story.extend(
            self._header(report, styles, template)
        )

        story.extend(
            self._score_overview(
                report,
                styles,
                template,
            )
        )

        story.extend(
            self._ats_breakdown(
                report,
                styles,
            )
        )

        story.extend(
            self._resume_metrics(
                report,
                styles,
            )
        )

        story.extend(
            self._skills_analysis(
                report,
                styles,
            )
        )

        story.extend(
            self._format_analysis(
                report,
                styles,
            )
        )

        story.extend(
            self._profile_analysis(
                report,
                styles,
            )
        )

        story.extend(
            self._recommendations(
                report,
                styles,
            )
        )

        document.build(story)

        buffer.seek(0)

        return buffer

    # =========================================================
    # STYLES
    # =========================================================

    def _build_styles(
        self,
        template: str,
    ) -> Dict[str, ParagraphStyle]:

        base = getSampleStyleSheet()

        accent = self._accent_color(template)

        return {
            "title": ParagraphStyle(
                "ReportTitle",
                parent=base["Title"],
                fontSize=22,
                leading=27,
                textColor=accent,
                alignment=TA_LEFT,
                spaceAfter=5,
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=base["Normal"],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#667085"),
                spaceAfter=12,
            ),
            "section": ParagraphStyle(
                "Section",
                parent=base["Heading2"],
                fontSize=13,
                leading=17,
                textColor=accent,
                spaceBefore=9,
                spaceAfter=7,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base["BodyText"],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#344054"),
            ),
            "small": ParagraphStyle(
                "Small",
                parent=base["BodyText"],
                fontSize=7.5,
                leading=10,
                textColor=colors.HexColor("#667085"),
            ),
            "metric": ParagraphStyle(
                "Metric",
                parent=base["BodyText"],
                fontSize=15,
                leading=18,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#101828"),
            ),
            "metric_label": ParagraphStyle(
                "MetricLabel",
                parent=base["BodyText"],
                fontSize=7.5,
                leading=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#667085"),
            ),
            "recommendation": ParagraphStyle(
                "Recommendation",
                parent=base["BodyText"],
                fontSize=9,
                leading=13,
                leftIndent=8,
                textColor=colors.HexColor("#344054"),
            ),
        }

    @staticmethod
    def _accent_color(
        template: str,
    ):
        colors_map = {
            "professional": "#1D4ED8",
            "modern": "#0F766E",
            "minimal": "#344054",
            "executive": "#7C3AED",
            "ai_insights": "#0369A1",
            "career_analytics": "#B45309",
        }

        return colors.HexColor(
            colors_map.get(
                template,
                "#1D4ED8",
            )
        )

    # =========================================================
    # HEADER
    # =========================================================

    def _header(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
        template: str,
    ):

        accent = self._accent_color(template)

        return [
            Paragraph(
                "Resume Analysis Report",
                styles["title"],
            ),
            Paragraph(
                f"<b>{self._escape(report.name)}</b>"
                f" &nbsp;•&nbsp; "
                f"{self._escape(report.profession_field)}",
                styles["subtitle"],
            ),
            HRFlowable(
                width="100%",
                thickness=1,
                color=accent,
                spaceAfter=12,
            ),
        ]

    # =========================================================
    # SCORE OVERVIEW
    # =========================================================

    def _score_overview(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
        template: str,
    ):

        data = [
            [
                Paragraph(
                    f"<b>{report.ats_score}</b>/100",
                    styles["metric"],
                ),
                Paragraph(
                    f"<b>{report.match_percentage}</b>%",
                    styles["metric"],
                ),
                Paragraph(
                    f"<b>{len(report.skills)}</b>",
                    styles["metric"],
                ),
                Paragraph(
                    f"<b>{report.profile_strength}</b>%",
                    styles["metric"],
                ),
            ],
            [
                Paragraph(
                    "ATS Score",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Job Match",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Skills Detected",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Profile Strength",
                    styles["metric_label"],
                ),
            ],
        ]

        table = Table(
            data,
            colWidths=[
                43 * mm,
                43 * mm,
                43 * mm,
                43 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#F8FAFC"),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        return [
            table,
            Spacer(1, 8),
            Paragraph(
                self._escape(report.resume_status),
                styles["small"],
            ),
        ]

    # =========================================================
    # ATS BREAKDOWN
    # =========================================================

    def _ats_breakdown(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        rows = [
            [
                Paragraph("<b>Area</b>", styles["body"]),
                Paragraph("<b>Score</b>", styles["body"]),
            ]
        ]

        mapping = [
            ("Structure", "structure"),
            ("Content", "content"),
            ("Keywords", "keywords"),
            ("Contact", "contact"),
            ("Readability", "readability"),
        ]

        for label, key in mapping:
            value = int(
                report.ats_breakdown.get(
                    key,
                    0,
                )
                or 0
            )

            rows.append(
                [
                    Paragraph(
                        label,
                        styles["body"],
                    ),
                    Paragraph(
                        f"{value}%",
                        styles["body"],
                    ),
                ]
            )

        table = Table(
            rows,
            colWidths=[
                135 * mm,
                35 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#F2F4F7"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "ATS Breakdown",
                styles["section"],
            ),
            table,
        ]

    # =========================================================
    # METRICS
    # =========================================================

    def _resume_metrics(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        data = [
            [
                Paragraph(
                    str(report.word_count),
                    styles["metric"],
                ),
                Paragraph(
                    str(report.page_count),
                    styles["metric"],
                ),
                Paragraph(
                    f"{report.reading_time} min",
                    styles["metric"],
                ),
                Paragraph(
                    f"{report.format_score}%",
                    styles["metric"],
                ),
            ],
            [
                Paragraph(
                    "Word Count",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Page Estimate",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Reading Time",
                    styles["metric_label"],
                ),
                Paragraph(
                    "Format Score",
                    styles["metric_label"],
                ),
            ],
        ]

        table = Table(
            data,
            colWidths=[
                43 * mm,
                43 * mm,
                43 * mm,
                43 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.white,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Resume Metrics",
                styles["section"],
            ),
            table,
        ]

    # =========================================================
    # SKILLS
    # =========================================================

    def _skills_analysis(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        matched = (
            ", ".join(report.matched_skills)
            if report.matched_skills
            else "None detected"
        )

        missing = (
            ", ".join(report.missing_skills)
            if report.missing_skills
            else "None detected"
        )

        detected = (
            ", ".join(report.skills)
            if report.skills
            else "None detected"
        )

        return [
            Paragraph(
                "Skills Analysis",
                styles["section"],
            ),
            Paragraph(
                f"<b>Detected:</b> "
                f"{self._escape(detected)}",
                styles["body"],
            ),
            Spacer(1, 4),
            Paragraph(
                f"<b>Matched:</b> "
                f"{self._escape(matched)}",
                styles["body"],
            ),
            Spacer(1, 4),
            Paragraph(
                f"<b>Missing:</b> "
                f"{self._escape(missing)}",
                styles["body"],
            ),
        ]

    # =========================================================
    # FORMAT
    # =========================================================

    def _format_analysis(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        rows = [
            [
                Paragraph(
                    "<b>Check</b>",
                    styles["body"],
                ),
                Paragraph(
                    "<b>Status</b>",
                    styles["body"],
                ),
                Paragraph(
                    "<b>Detail</b>",
                    styles["body"],
                ),
            ]
        ]

        for item in report.format_checks:

            label = getattr(
                item,
                "label",
                "",
            )

            passed = bool(
                getattr(
                    item,
                    "passed",
                    False,
                )
            )

            detail = getattr(
                item,
                "detail",
                "",
            )

            rows.append(
                [
                    Paragraph(
                        self._escape(label),
                        styles["body"],
                    ),
                    Paragraph(
                        "Passed" if passed else "Needs attention",
                        styles["body"],
                    ),
                    Paragraph(
                        self._escape(detail),
                        styles["small"],
                    ),
                ]
            )

        if len(rows) == 1:
            return []

        table = Table(
            rows,
            colWidths=[
                45 * mm,
                35 * mm,
                95 * mm,
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#F2F4F7"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Format Checker",
                styles["section"],
            ),
            table,
        ]

    # =========================================================
    # PROFILE
    # =========================================================

    def _profile_analysis(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        rows = []

        for item in report.profile_checklist:

            label = getattr(
                item,
                "label",
                "",
            )

            passed = bool(
                getattr(
                    item,
                    "passed",
                    False,
                )
            )

            rows.append(
                [
                    self._escape(label),
                    "Complete" if passed else "Missing",
                ]
            )

        if not rows:
            return []

        table = Table(
            [
                [
                    Paragraph(
                        "<b>Profile Item</b>",
                        styles["body"],
                    ),
                    Paragraph(
                        "<b>Status</b>",
                        styles["body"],
                    ),
                ]
            ]
            + [
                [
                    Paragraph(
                        label,
                        styles["body"],
                    ),
                    Paragraph(
                        status,
                        styles["body"],
                    ),
                ]
                for label, status in rows
            ],
            colWidths=[
                125 * mm,
                50 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#F2F4F7"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#E4E7EC"),
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        return [
            Paragraph(
                "Profile Completeness",
                styles["section"],
            ),
            table,
        ]

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    def _recommendations(
        self,
        report: ReportData,
        styles: Dict[str, ParagraphStyle],
    ):

        if not report.recommendations:
            return []

        elements = [
            Paragraph(
                "AI Recommendations",
                styles["section"],
            )
        ]

        for recommendation in report.recommendations:

            if isinstance(
                recommendation,
                dict,
            ):
                text = (
                    recommendation.get("message")
                    or recommendation.get("text")
                    or recommendation.get("recommendation")
                    or recommendation.get("title")
                    or str(recommendation)
                )
            else:
                text = str(
                    recommendation
                )

            elements.append(
                Paragraph(
                    "• "
                    + self._escape(text),
                    styles["recommendation"],
                )
            )

            elements.append(
                Spacer(1, 4)
            )

        return elements

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _escape(
        value: object,
    ) -> str:

        text = str(value or "")

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )


pdf_exporter = PDFReportExporter()