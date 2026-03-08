from __future__ import annotations

from core.models import ArticleDraft, QAResult
from core.utils import build_deterministic_id
from workers.qa.checks.citations import check_citations
from workers.qa.checks.safety import check_safety
from workers.qa.checks.style import check_style_and_structure


class QAPipeline:
    def evaluate(self, draft: ArticleDraft) -> QAResult:
        reasons: list[str] = []

        citation_passed, citation_details = check_citations(draft)
        if not citation_passed:
            reasons.append("CITATION_COVERAGE_FAILED")

        style_passed, style_details = check_style_and_structure(draft)
        if not style_passed:
            reasons.append("STYLE_OR_STRUCTURE_FAILED")

        safety_passed, safety_details = check_safety(draft)
        if not safety_passed:
            reasons.append("SAFETY_FAILED")

        report_id = build_deterministic_id("qa", draft.draft_id)
        return QAResult(
            report_id=report_id,
            draft_id=draft.draft_id,
            passed=citation_passed and style_passed and safety_passed,
            reason_codes=reasons,
            details={
                "citation": citation_details,
                "style": style_details,
                "safety": safety_details,
            },
        )
