from datetime import datetime, timezone
import math

SEVERITY_LOOKUP = {
    "System Outages": 95.0,
    "Price Increases": 80.0,
    "PR Crises": 75,
    "Layoffs": 65,
    "Product Defects": 70,
    "Data Breaches": 90.0,
}

DECAY_COEFFICIENT = 0.02


def calculate_severity(vulnerability_type: str) -> float:

    return SEVERITY_LOOKUP.get(vulnerability_type, 50.0)


def calculate_volume_score(
    article_count: int = 1, source_tier: str = "standard"
) -> float:

    # source_tier could be tier1, tier2, or standard (tier3)

    baseline_score = 50
    multiplier = 1.0

    if article_count >= 3 and article_count <= 9:
        baseline_score = 75.0
    elif article_count >= 10:
        baseline_score = 90

    if source_tier.lower() == "tier1":
        multiplier = 1.5
    elif source_tier.lower() == "tier2":
        multiplier = 1.2

    return min(100.0, round(baseline_score * multiplier, 2))


def calculate_urgency(published_at: datetime | str, decay_rate: float = 0.05) -> float:

    now = datetime.now(timezone.utc)

    if isinstance(published_at, str):
        clean_str = published_at.replace("Z", "+00:00")
        pub_dt = datetime.fromisoformat(clean_str)
    else:
        pub_dt = published_at

    if pub_dt.tzinfo is None:
        pub_dt = pub_dt.replace(tzinfo=timezone.utc)

    hours_elapsed = (now - pub_dt).total_seconds() / 3600.0
    hours_elapsed = max(0.0, hours_elapsed)

    return round(100 * math.exp(-1 * decay_rate * hours_elapsed), 2)


def compute_opportunity_score(
    vulnerability_type: str, published_at: str | datetime, article_count: int = 1, source_tier: str = "standard"
) -> dict:

    severity = calculate_severity(vulnerability_type)
    volume = calculate_volume_score(article_count, source_tier)
    urgency = calculate_urgency(published_at, DECAY_COEFFICIENT)

    final_score = (0.4 * severity) + (0.3 * volume) + (0.3 * urgency)

    return {
        "opportunity_score": round(final_score, 2),
        "severity_score": severity,
        "volume_score": volume,
        "urgency_score": urgency,
        "priority_label": (
            "CRITICAL"
            if final_score >= 80
            else ("HIGH" if final_score >= 70 else "MEDIUM")
        ),
    }
