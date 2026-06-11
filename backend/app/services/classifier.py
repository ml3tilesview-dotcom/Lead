"""
Deterministic rule-based lead classifier for Phase 1.
No external AI API required.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ClassifierRule:
    pattern: str
    score: int
    intent: str
    product_interest: str | None = None
    mandatory_handoff: bool = False


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------
HOT_RULES: list[ClassifierRule] = [
    ClassifierRule(
        r"\b(book|schedule|request|want|need|get)\s+(a\s+)?(demo|demonstration)\b",
        85,
        "demo_request",
        mandatory_handoff=True,
    ),
    ClassifierRule(r"\bfree\s+trial\b", 80, "trial_request"),
    ClassifierRule(
        r"\b(pricing|price|prices|cost|costs|fee|fees|how\s+much|what('s|\s+is)\s+(it|the\s+cost|the\s+price))\b",
        80,
        "pricing_inquiry",
        mandatory_handoff=True,
    ),
    ClassifierRule(
        r"\b(quotation|quote|proposal|rfq)\b", 82, "quotation_request", mandatory_handoff=True
    ),
    ClassifierRule(
        r"\b(sales\s+call|speak\s+to\s+(sales|someone)|talk\s+to\s+(sales|a\s+person)|call\s+me|contact\s+me)\b",
        85,
        "sales_contact",
        mandatory_handoff=True,
    ),
    ClassifierRule(
        r"\b(buy|purchase|order|subscribe|sign\s+up|get\s+started|ready\s+to\s+(start|begin|use))\b",
        80,
        "purchase_intent",
        mandatory_handoff=True,
    ),
    ClassifierRule(
        r"\b(need\s+human|want\s+human|human\s+(support|help|agent)|speak\s+to\s+(a\s+person|someone|human|agent)|talk\s+to\s+(a\s+person|someone|human|agent))\b",
        90,
        "human_request",
        mandatory_handoff=True,
    ),
    ClassifierRule(
        r"\b(my\s+(phone|number|email|contact)\s+(is|:))\b",
        75,
        "contact_info_provided",
        mandatory_handoff=True,
    ),
]

WARM_RULES: list[ClassifierRule] = [
    ClassifierRule(
        r"\b(feature|features|functionality|capabilities|what\s+can)\b", 45, "feature_inquiry"
    ),
    ClassifierRule(
        r"\b(integrat|integration|connect|sync|api|webhook)\b", 50, "integration_inquiry"
    ),
    ClassifierRule(
        r"\b(shopify|woocommerce|magento|prestashop|opencart)\b",
        55,
        "ecommerce_integration",
        "ecommerce",
    ),
    ClassifierRule(
        r"\b(catalog|catalogue|product\s+(catalog|listing)|tile\s+(catalog|catalogue))\b",
        50,
        "catalog_request",
    ),
    ClassifierRule(
        r"\b(how\s+(does|do|many)|how\s+it\s+works|technical|specification|spec)\b",
        40,
        "technical_inquiry",
    ),
    ClassifierRule(
        r"\b(number\s+of\s+(store|stores|customer|customers|user|users|project|projects))\b",
        55,
        "scale_inquiry",
    ),
    ClassifierRule(r"\b(business|company|team|enterprise|b2b)\b", 38, "business_inquiry"),
    ClassifierRule(
        r"\b(requirement|requirements|use\s+case|workflow)\b", 45, "requirements_inquiry"
    ),
    ClassifierRule(
        r"\b(3d\s+(viewer|view|render|tile|tiles)|virtual\s+(tour|showroom)|tile\s+(design|visuali))\b",
        52,
        "product_feature_inquiry",
        "3d_viewer",
    ),
]

COLD_RULES: list[ClassifierRule] = [
    ClassifierRule(r"\b(interested|interest)\b", 20, "general_interest"),
    ClassifierRule(r"\btell\s+me\s+more\b", 18, "information_seeking"),
    ClassifierRule(
        r"\b(nice|cool|great|awesome|looks\s+good|impressive|love\s+(it|this|your))\b",
        12,
        "positive_comment",
    ),
    ClassifierRule(r"\b(hello|hi|hey|good\s+(morning|afternoon|evening))\b", 8, "greeting"),
    ClassifierRule(r"\b(what\s+(is|are)|can\s+you|could\s+you|do\s+you)\b", 15, "general_inquiry"),
]

NOT_LEAD_RULES: list[ClassifierRule] = [
    ClassifierRule(
        r"\b(job|career|position|vacancy|vacancies|hiring|apply\s+for|resume|cv|curriculum)\b",
        -50,
        "job_inquiry",
    ),
    ClassifierRule(
        r"\b(marketing\s+service|seo\s+service|link\s+build|guest\s+post|backlink|rank\s+your|traffic\s+to)\b",
        -60,
        "spam_marketing",
    ),
    ClassifierRule(
        r"\b(no\s+reply|auto[\s-]?reply|automated|do\s+not\s+reply|donotreply|noreply)\b",
        -80,
        "automated_message",
    ),
    ClassifierRule(r"\b(unsubscribe|remove\s+me|opt\s+out|stop\s+email)\b", -70, "unsubscribe"),
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def _match_rules(text: str, rules: list[ClassifierRule]) -> list[ClassifierRule]:
    matched = []
    for rule in rules:
        if re.search(rule.pattern, text, re.IGNORECASE):
            matched.append(rule)
    return matched


class LeadClassifier:
    """Deterministic lead classifier. No external service required."""

    def classify(
        self, message: str, contact_has_email: bool = False, contact_has_phone: bool = False
    ) -> "ClassificationResult":
        text = _normalize(message)

        hot_matches = _match_rules(text, HOT_RULES)
        warm_matches = _match_rules(text, WARM_RULES)
        cold_matches = _match_rules(text, COLD_RULES)
        not_lead_matches = _match_rules(text, NOT_LEAD_RULES)

        # Base score
        score = 0
        for rule in hot_matches:
            score += rule.score
        for rule in warm_matches:
            score += rule.score
        for rule in cold_matches:
            score += rule.score
        for rule in not_lead_matches:
            score += rule.score

        # Contact info bonus — if they provided info AND said something commercial, treat as hot
        if (contact_has_email or contact_has_phone) and (hot_matches or warm_matches):
            score += 15

        score = max(0, min(100, score))

        # Mandatory handoff check
        mandatory_handoff = any(r.mandatory_handoff for r in hot_matches)

        # Intent — pick highest-scoring matched intent
        all_matched = hot_matches + warm_matches + cold_matches + not_lead_matches
        primary_intent = "general_inquiry"
        if all_matched:
            primary_intent = max(all_matched, key=lambda r: abs(r.score)).intent

        # Product interest
        product_interest = None
        for rule in hot_matches + warm_matches:
            if rule.product_interest:
                product_interest = rule.product_interest
                break

        # Temperature
        if not_lead_matches and not hot_matches and not warm_matches and score <= 0:
            temperature = "not_lead"
            is_lead = False
        elif score >= 70:
            temperature = "hot"
            is_lead = True
        elif score >= 35:
            temperature = "warm"
            is_lead = True
        elif score >= 1:
            temperature = "cold"
            is_lead = True
        else:
            temperature = "not_lead"
            is_lead = False

        # Confidence — based on number of matched rules
        total_matches = (
            len(hot_matches) + len(warm_matches) + len(cold_matches) + len(not_lead_matches)
        )
        confidence = min(0.95, 0.5 + total_matches * 0.1)

        reason = _build_reason(hot_matches, warm_matches, cold_matches, not_lead_matches)
        handoff_reason = _build_handoff_reason(hot_matches) if mandatory_handoff else None

        return ClassificationResult(
            is_lead=is_lead,
            lead_temperature=temperature,
            intent=primary_intent,
            lead_score=score,
            confidence=round(confidence, 2),
            reason=reason,
            product_interest=product_interest,
            handoff_required=mandatory_handoff,
            handoff_reason=handoff_reason,
        )


def _build_reason(hot: list, warm: list, cold: list, not_lead: list) -> str:
    parts = []
    if hot:
        parts.append(f"Hot signals: {', '.join(r.intent for r in hot)}")
    if warm:
        parts.append(f"Warm signals: {', '.join(r.intent for r in warm)}")
    if cold:
        parts.append(f"Cold signals: {', '.join(r.intent for r in cold)}")
    if not_lead:
        parts.append(f"Not-lead signals: {', '.join(r.intent for r in not_lead)}")
    return "; ".join(parts) if parts else "No strong signals detected"


def _build_handoff_reason(hot: list) -> str:
    handoff_rules = [r for r in hot if r.mandatory_handoff]
    return "Mandatory handoff triggered by: " + ", ".join(r.intent for r in handoff_rules)


@dataclass
class ClassificationResult:
    is_lead: bool
    lead_temperature: str
    intent: str
    lead_score: int
    confidence: float
    reason: str
    product_interest: str | None
    handoff_required: bool
    handoff_reason: str | None
    conversation_summary: str | None = field(default=None)

    def to_schema(self) -> "LeadEvaluationSchema":  # noqa: F821
        from app.schemas.lead import LeadEvaluationSchema

        return LeadEvaluationSchema(
            is_lead=self.is_lead,
            lead_temperature=self.lead_temperature,
            intent=self.intent,
            lead_score=self.lead_score,
            confidence=self.confidence,
            reason=self.reason,
            product_interest=self.product_interest,
            conversation_summary=self.conversation_summary,
            handoff_required=self.handoff_required,
            handoff_reason=self.handoff_reason,
        )
