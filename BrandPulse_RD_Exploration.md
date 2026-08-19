# BrandPulse R&D Exploration
### Finding BrandPulse's Next Strategic Direction

Prepared as a research/architecture exploration — team: Momina + Ismail

---

## 1. Where BrandPulse Is Today

BrandPulse currently does one thing very well: it turns raw external signals (Reddit posts, competitor news via RSS) into **structured, scored intelligence**.

**Current data flow:**
```
Reddit / Competitor News (RSS)
        ↓
   Ingestion + Cleaning
        ↓
   PostgreSQL (raw storage)
        ↓
AI Pipeline: Sentiment/Intent (customer) | Vulnerability Classification (competitor)
        ↓
   Opportunity Scoring (severity + volume + urgency)
        ↓
   SLM Action Brief (department routing, recommended action, outreach copy)
        ↓
   Fact Audit (NLI check against source article)
        ↓
   FastAPI → Dashboard
```

**What BrandPulse already knows how to do, technically:**
- Zero-shot/NLI classification (vulnerability type detection)
- Deterministic multi-factor scoring with time-decay (opportunity score)
- Conditional local SLM generation (action briefs)
- Grounding/fact-verification of generated text against source documents
- Scheduled batch pipeline orchestration

**Where it currently stops:** BrandPulse produces a *recommendation* (an action brief) and then the loop ends. Nothing closes back — there's no mechanism to know whether a detected opportunity or a generated recommendation was actually good. This is the single biggest structural gap, and it's the thing that shapes almost every direction below.

**Current limitations (from the README and prior scoping):**
- Single-shot scoring — no feedback signal, no learning over time
- Extraction reliability issues (Cloudflare blocks, DNS failures, paywalls)
- No historical baseline — every article is scored in isolation, with no notion of "is this vulnerability type more or less severe than usual for this competitor"
- No outcome data of any kind exists yet, for anything

---

## 2. Competitive Landscape Research

### Rival IQ (acquired by NetBase Quid)
Rival IQ is fundamentally a **benchmarking and analytics** tool, not a decisioning tool. It ingests competitors' public social media activity and website content, and its "AI" is mostly pattern/anomaly detection on top of that: boosted-post detection (ML classifier estimating whether a competitor's organic post was paid promotion), engagement benchmarking against a custom competitive set, and estimated impression modeling. It tells you *what happened* and *how you compare*, but it does not decide *what to do about it* — that step is left entirely to the human analyst. Its intelligence is also social/content-only; it has no sense of your own customers' sentiment or intent, so it can't connect "competitor did X" to "our customers are reacting to X."

Newer entrants in the same space (RivalSweeper, Rivalize, RivalOut, Rival Radar) are converging on the same idea BrandPulse already has — detect competitor signals (pricing, hiring, product changes) and assign an AI-scored significance rating — but nearly all of them stop at the *alert*, not the *action*. A few (Rival Radar, aimed at B2B sales) go one step further into auto-generated "battle cards" for sales reps, which is conceptually close to your `action_brief`, but it's static reference material, not a personalized recommendation tied to a specific customer segment.

### GoHighLevel (GHL)
GHL is the opposite end of the spectrum: it's an execution and automation platform (CRM + funnels + email/SMS + calling), with AI layered on for content generation, conversational lead-qualification, and workflow-building assistance ("describe the workflow in plain English and it builds it"). Its AI is almost entirely **generative and reactive** — it responds to inbound leads, drafts follow-ups, and auto-builds automations from natural-language descriptions. It is not built around *external* competitive or market signals at all; its trigger events are internal (a lead replied, a form was submitted, a review came in). There is no equivalent of "a competitor raised prices, therefore act."

### The gap between them
Neither platform — nor most of the adjacent tools surveyed (Optimove, Braze, Pega, CleverTap for next-best-action; Klue/Crayon-style battle-card tools) — actually connects **external competitive/market signal detection** to **individualized customer-level action**. The industry pattern is a hard split:
- Competitive intelligence tools (Rival IQ, Rivalize, etc.) → detect signals, stop at alerting/reporting
- Marketing/CRM automation platforms (GHL, Braze, Optimove) → personalize and execute, but only react to *internal* customer behavior, not *external* market events
- Enterprise "next-best-action" engines (Pega, Optimove) do the closest thing to what a closed-loop BrandPulse could become, but they require large historical interaction datasets, are enterprise-priced, and are generic (not built around a competitor-vulnerability trigger)

This is the real whitespace: **"when something changes in the market, which of our specific customers does it matter to, and what's worth doing about it" is not something any of these tools do end-to-end.** That's a genuine, defensible research angle for BrandPulse, distinct from "wrap an LLM around campaign copy."

---

## 3. AI/ML Directions Considered

For each direction: Problem/value, novelty, the actual ML problem, data needed, evaluation method, feasibility, and product fit.

### A. Customer–Vulnerability Relevance Matching (Audience Discovery grounded in your own data)
- **Problem/value:** Right now, when a competitor vulnerability is detected, the `target_department` is generic ("Marketing," "Sales"). It doesn't say *which* customers this actually matters to. You already have Sprint-1 sentiment+intent data per customer post — that's an untapped signal.
- **Novelty:** This forces you to learn how to connect two previously separate subsystems (customer intelligence + competitor intelligence) that currently don't talk to each other at all.
- **ML problem:** Given a vulnerability event (type + competitor + text) and a corpus of customer posts (with sentiment/intent), retrieve/rank which customer segments or individual posts are most relevant/likely to react — essentially a semantic relevance + intent-matching task (embedding similarity + intent-category filtering), not a black-box classifier.
- **Data required:** Your existing Sprint 1 sentiment/intent post data and Sprint 2 vulnerability data — nothing new needed. This is the most data-feasible direction by far.
- **Evaluation:** Precision/recall against a small hand-labeled validation set (you and Ismail label "is this post relevant to this vulnerability?" for ~100-200 pairs) — a legitimate, gradeable ML evaluation exercise.
- **Feasibility:** High. Sentence embeddings (e.g. a small sentence-transformer) + cosine similarity + intent filtering is buildable in days, not weeks.
- **Product fit:** Strong — it's the connective tissue your two existing pipelines are missing, and it's a prerequisite for almost every other direction below (you can't target a campaign, predict outcomes, or rank opportunities well without knowing who a signal is relevant to).

### B. Opportunity Ranking / Prioritization Across Time (Anomaly & Change Detection)
- **Problem/value:** Every article is currently scored in isolation with static weights. Analysts actually care about *change*: is this competitor's vulnerability rate spiking? Is this a one-off, or the fourth outage this month?
- **Novelty:** Moves opportunity scoring from a single-article calculation to a **time-series/statistical** problem — genuinely different ML/stats territory (baselines, z-scores, rolling windows) from anything currently in the pipeline.
- **ML problem:** Given a history of vulnerability events per competitor, detect anomalies/trend shifts (e.g., rolling frequency + severity vs. historical baseline) and re-rank current opportunities by "how unusual is this," not just "how severe is this in isolation."
- **Data required:** Needs weeks of accumulated `vulnerability_results` history to have any baseline — you have some of this once Sprint 2 has been running a while, but not on day one.
- **Evaluation:** Backtestable against your own accumulated data (does the anomaly flag correlate with genuinely notable events?) — objective and code-checkable without needing human labels.
- **Feasibility:** Medium — the modeling is simple (rolling stats, not deep learning) but requires a few weeks of real data first to be meaningful, so it's more of a Sprint 3.5 than something demoable immediately.
- **Product fit:** Strong long-term differentiator, weak short-term demo (nothing to show until data accumulates).

### C. Campaign/Outreach Generation ("AI Campaign Copilot" — the direction already explored with you)
- **Problem/value:** Turns a recommendation into ready-to-review outreach content.
- **Novelty:** Low from an ML standpoint — it's SLM prompting + reused fact-auditing, not new modeling technique.
- **ML problem:** Generative (LLM/SLM), not predictive — there's no actual "model" being trained or evaluated statistically.
- **Data required:** None beyond what exists.
- **Evaluation:** Subjective (human review of quality) — hard to evaluate "objectively," which was flagged earlier as a real weakness of this direction as a research exercise.
- **Feasibility:** High.
- **Product fit:** Good for demo polish, weak as R&D — it's real product work, but it doesn't teach you a new ML technique, and per your own constraint ("generate marketing copy with an LLM" is explicitly the kind of generic feature to avoid), this direction alone doesn't satisfy the assignment's intent.

### D. Campaign Outcome Prediction / Uplift Modeling
- **Problem/value:** Predict whether a given campaign/action would actually work, and for whom — the "genuinely interesting ML" part of campaign management.
- **Novelty:** High — causal inference / uplift modeling is graduate-level ML territory, a real learning opportunity.
- **ML problem:** Given treatment (campaign sent) vs. control (not sent) outcomes, estimate individual treatment effect (uplift) rather than raw conversion probability.
- **Data required:** Requires actual campaign outcome data (sent/not-sent, converted/not-converted) at meaningful volume — you have **zero** campaigns run, let alone paired treatment/control outcomes. This is not buildable in any near-term sprint, as flagged earlier.
- **Evaluation:** Needs real experiments (A/B), which you can't run without a live audience.
- **Feasibility:** Very low right now. This is the direction to *design for* but not *build* yet.
- **Product fit:** Excellent eventually, not viable as this sprint's deliverable.

### E. Competitor Behavior Prediction (Forecasting)
- **Problem/value:** Predict when a competitor is likely to have another vulnerability event, based on historical patterns (e.g., "Competitor X tends to have pricing issues quarterly").
- **Novelty:** Genuine time-series forecasting problem.
- **ML problem:** Sequence/frequency forecasting per competitor.
- **Data required:** Same issue as (B) — needs real accumulated history across many competitors to be meaningful; with only a handful of tracked competitors and a few weeks of data, this will be statistically thin.
- **Evaluation:** Backtesting, but weak with small-N competitor history.
- **Feasibility:** Low near-term for the same reason as B/D — not enough historical depth yet.
- **Product fit:** Interesting later, not now.

### F. Knowledge Graph / Relationship Modeling
- **Problem/value:** Model relationships between competitors, vulnerability types, departments, and customer segments explicitly, enabling multi-hop queries ("which competitors have had the most price-related issues affecting price-sensitive customers in the last quarter").
- **Novelty:** Different technical skill entirely (graph modeling, not classification/generation) — a real new area for the team.
- **ML problem:** Less "ML," more structured knowledge representation + graph queries; could incorporate embeddings for entity linking.
- **Data required:** Your existing relational data, restructured — feasible with what you have.
- **Evaluation:** Harder to evaluate "objectively" — more of an infrastructure/analytics capability than a testable model.
- **Feasibility:** Medium, but scope is fuzzy and it risks becoming a large infrastructure project rather than a research finding.
- **Product fit:** Nice-to-have analytics layer, not a strong standalone direction.

---

## 4. Recommended Strategic Directions (Top 3)

### Direction 1 — Customer-Vulnerability Relevance Engine *(Recommended)*
- **Problem:** BrandPulse detects competitor vulnerabilities but has no way to say which of your actual customers/segments the event is relevant to — it routes to a generic department, not a specific audience.
- **Proposed solution:** Build a relevance-matching layer that links each detected vulnerability to the customer posts/segments (from your existing sentiment+intent data) most likely to care, using semantic similarity plus intent-category filtering, and surface a ranked "who this affects" list alongside the existing opportunity score.
- **AI/ML technique:** Sentence embeddings (e.g. a small open sentence-transformer) for semantic similarity between vulnerability context and customer post content, combined with rule-based intent-category filtering; optionally a lightweight learned re-ranker if you have time.
- **Required data:** 100% available today — your existing Sprint 1 (customer posts/intent/sentiment) and Sprint 2 (vulnerability results) tables. No new data collection needed.
- **Expected value:** Turns "Marketing should look at this" into "these 40 posts, from customers showing price-sensitive intent, are the ones this actually matters to" — a materially more useful and specific output, and the connective layer that any future campaign/targeting feature will need anyway.
- **Research/learning opportunity:** Real, hands-on embedding-based retrieval + evaluation methodology (precision/recall against a labeled set you build yourselves) — a legitimate, gradeable ML exercise with an objective metric.
- **Prototype complexity:** Low-medium. Buildable by 2 people in roughly a week, cleanly scoped, and it doesn't require inventing new data.

### Direction 2 — Opportunity Anomaly & Trend Detection
- **Problem:** Every vulnerability is scored in isolation; there's no sense of whether a signal is a routine blip or a real trend shift for a competitor.
- **Proposed solution:** Layer a rolling-baseline/anomaly-detection stage on top of the existing opportunity scorer that compares current signals against each competitor's historical pattern and flags genuine deviations.
- **AI/ML technique:** Time-series statistics (rolling mean/std, z-scores) — simple, interpretable, no deep learning required.
- **Required data:** Weeks of accumulated `vulnerability_results` — partially available now, will improve as Sprint 2 keeps running.
- **Expected value:** Reduces alert fatigue and surfaces genuinely notable shifts instead of treating every article the same.
- **Research/learning opportunity:** Real statistical modeling and backtesting methodology.
- **Prototype complexity:** Medium — simple math, but needs real historical depth to demo convincingly, so it's better framed as a "Sprint 3.5" once more data exists.

### Direction 3 — Closed-Loop Campaign System (Copilot + outcome logging, ML deferred)
- **Problem:** Recommendations currently dead-end; there's no mechanism to ever learn whether they worked.
- **Proposed solution:** Build the scoped "AI Campaign Copilot" MVP already discussed (generate a draft campaign from an opportunity, fact-audited, human-approved) — but treat its real R&D value as **instrumentation**: log every campaign's outcome from day one (even manually entered), so a future sprint has the paired treatment/outcome data that Direction 4-style uplift modeling would need.
- **AI/ML technique:** SLM generation + fact-audit reuse (near-term); uplift modeling deferred until outcome data exists.
- **Required data:** None near-term; sets up future data collection.
- **Expected value:** Strong demo value now; sets up the *only* path to genuinely interesting predictive ML later.
- **Research/learning opportunity:** Limited near-term (mostly engineering, as flagged earlier) — the learning payoff is deferred.
- **Prototype complexity:** Low-medium, already scoped in detail in your earlier planning.

---

## 5. Recommendation

**Direction 1 (Customer–Vulnerability Relevance Engine) is the strongest next step**, for a specific reason: it's the only direction that is simultaneously (a) buildable right now with zero new data, (b) a genuine ML exercise with an objective evaluation method you control, and (c) a structural improvement that every other direction — campaign targeting, anomaly detection, future uplift modeling — will eventually depend on. It directly attacks BrandPulse's biggest actual limitation (customer intelligence and competitor intelligence are two disconnected pipelines) rather than adding a new surface feature on top of an unconnected foundation.

Direction 3 (Campaign Copilot) is worth doing in parallel or right after — it's good product/demo value and, critically, if you log outcomes from day one, it's what makes Direction "uplift modeling" (the most research-worthy direction of all) actually possible in a future sprint. Direction 2 (anomaly detection) is the right long-term differentiator but is data-starved today — worth designing for, not building yet.

**Suggested sequencing for a 2-person team:**
1. Now: Direction 1 (relevance engine) — real ML, no data blockers, ~1 week
2. Next: Direction 3 (campaign copilot), built *on top of* Direction 1's output (so campaigns can be audience-targeted using the relevance engine, not generic) — and instrumented to log outcomes
3. Later (next semester/sprint, once outcome + historical data exists): Direction 2 (anomaly detection) and eventually true uplift modeling on the campaign outcome data you've been quietly collecting since step 2

This sequencing means the "campaign management" idea doesn't disappear — it gets absorbed into a stronger foundation, and the eventual uplift-modeling/next-best-action capability (the thing that would genuinely differentiate BrandPulse from Rival IQ-style alerting tools and GHL-style generic automation) becomes buildable instead of hand-waved.
