import { useState, useMemo, useEffect } from "react";
import { Icon } from "@iconify/react";

// ============================================================================
// ENRICHED DUMMY API DATA STRUCTURE
// Unique fields added for every opportunity card to support the modal details
// Expected backend endpoint: GET /api/v1/competitor-intel
// ============================================================================
const DUMMY_OPPORTUNITIES = [
  {
    id: "opp-1",
    competitor: "Square",
    vulnerabilityType: "System Outages",
    priority: "Critical",
    title: "Square payment processing down for 6+ hours nationwide",
    opportunityScore: 94,
    tag: "SALES",
    alertSent: true,
    recommendedAction: "Reach out to affected Square merchants in the region with a same-day migration offer.",
    source: "TechCrunch",
    timestamp: "3h ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Merchants unable to process transactions during peak hours; high switching intent window.",
    targetAudience: "Small-to-mid retail merchants currently on Square",
    suggestedOutreachMessage: '"Hi [Name], we noticed today\'s Square outage may have disrupted your sales. Our POS platform guarantees 99.99% uptime with a dedicated failover line — happy to set up a same-day account so you\'re covered before your next rush."',
  },
  {
    id: "opp-2",
    competitor: "Clover",
    vulnerabilityType: "Data Breach",
    priority: "Critical",
    title: "Clover investigating possible customer data exposure",
    opportunityScore: 89,
    tag: "MARKETING",
    alertSent: true,
    recommendedAction: "Publish a security trust-center blog post and run paid social to affected merchant segment.",
    source: "Krebs on Security",
    timestamp: "5h ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Security vulnerabilities drive decision-makers to seek SOC2-certified enterprise alternatives immediately.",
    targetAudience: "Multi-location hospitality groups concerned about PCI compliance",
    suggestedOutreachMessage: '"Hi [Name], customer trust is paramount. While recent industry headlines highlight security vulnerabilities, our architecture ensures end-to-end tokenization and zero data liability. Let\'s review your compliance setup today."',
  },
  {
    id: "opp-3",
    competitor: "Toast",
    vulnerabilityType: "Price Hikes",
    priority: "High",
    title: "Toast introduces mandatory 0.99% fee on online ordering platforms",
    opportunityScore: 82,
    tag: "SALES",
    alertSent: true,
    recommendedAction: "Launch 'No Hidden Fee Guarantee' campaign targeting Toast restaurant partners.",
    source: "Restaurant Business",
    timestamp: "1d ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Surprise transaction fees directly cut into merchant margins, causing public operator pushback.",
    targetAudience: "Independent full-service and quick-service restaurant owners",
    suggestedOutreachMessage: '"Hi [Name], tired of unexpected transaction fees shrinking your margins? Switch to our flat-rate processing plan with 0% online ordering markups guaranteed for 24 months."',
  },
  {
    id: "opp-4",
    competitor: "Lightspeed",
    vulnerabilityType: "Layoffs",
    priority: "Medium",
    title: "Lightspeed cuts 10% of support and customer success workforce",
    opportunityScore: 68,
    tag: "SALES",
    alertSent: false,
    recommendedAction: "Target enterprise accounts emphasizing 24/7 dedicated account management SLAs.",
    source: "Bloomberg",
    timestamp: "2d ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Support cutbacks lead to increased ticket resolution times and merchant dissatisfaction.",
    targetAudience: "Mid-market retail chains relying heavily on dedicated account support",
    suggestedOutreachMessage: '"Hi [Name], when systems need attention, waiting hours for support isn\'t an option. We offer guaranteed 2-minute phone response times and dedicated US-based account managers."',
  },
  {
    id: "opp-5",
    competitor: "Square",
    vulnerabilityType: "PR Crisis",
    priority: "Medium",
    title: "Merchant complaints spike regarding unexpected risk account holds",
    opportunityScore: 61,
    tag: "MARKETING",
    alertSent: false,
    recommendedAction: "Promote instant settlement guarantees and transparent risk review procedures.",
    source: "Reddit /r/smallbusiness",
    timestamp: "2d ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Arbitrary account holds disrupt merchant cash flow, prompting urgent platform switches.",
    targetAudience: "High-volume e-commerce and omnichannel sellers",
    suggestedOutreachMessage: '"Hi [Name], cash flow is the heartbeat of your business. Our transparent underwriting ensures no arbitrary holds and next-day payout guarantees."',
  },
  {
    id: "opp-6",
    competitor: "Toast",
    vulnerabilityType: "System Outages",
    priority: "Low",
    title: "Minor API latency issues reported during dinner rush hour",
    opportunityScore: 35,
    tag: "PRODUCT",
    alertSent: false,
    recommendedAction: "Monitor status page; defer outbound messaging unless outage escalates.",
    source: "StatusPage",
    timestamp: "3d ago",
    acknowledged: false,
    // Detailed Modal Fields
    rationale: "Minor latency observed; potential indicator of underlying infrastructure instability.",
    targetAudience: "High-volume dinner-only dining establishments",
    suggestedOutreachMessage: '"Hi [Name], offline resilience matters most when your dining room is full. See how our local network fallback keeps orders firing even when internet connectivity degrades."',
  },
];

export default function CompetitiveIntel() {
  // --------------------------------------------------------------------------
  // STATE MANAGEMENT
  // --------------------------------------------------------------------------
  const [opportunities, setOpportunities] = useState(DUMMY_OPPORTUNITIES);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filter dropdown state variables
  const [selectedCompetitor, setSelectedCompetitor] = useState("All Competitors");
  const [selectedVulnerability, setSelectedVulnerability] = useState("All Types");
  const [selectedPriority, setSelectedPriority] = useState("All Priorities");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal State
  const [selectedOpportunityModal, setSelectedOpportunityModal] = useState(null);

  // Toast Notification State
  const [toastMessage, setToastMessage] = useState(null);

  // --------------------------------------------------------------------------
  // BACKEND API INTEGRATION PLACEHOLDERS
  // --------------------------------------------------------------------------
  useEffect(() => {
    // BACKEND INTEGRATION POINT: Fetch Initial Data
    /*
    async function fetchIntelData() {
      setIsLoading(true);
      try {
        const response = await fetch('/api/v1/competitor-intel');
        const data = await response.json();
        setOpportunities(data);
      } catch (err) {
        setError("Failed to fetch competitive intelligence data.");
      } finally {
        setIsLoading(false);
      }
    }
    fetchIntelData();
    */
  }, []);

  // Dynamic Filtering Logic
  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((item) => {
      if (selectedCompetitor !== "All Competitors" && item.competitor !== selectedCompetitor) return false;
      if (selectedVulnerability !== "All Types" && item.vulnerabilityType !== selectedVulnerability) return false;
      if (selectedPriority !== "All Priorities" && item.priority !== selectedPriority) return false;
      if (searchQuery.trim() !== "") {
        const query = searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(query);
        const matchesCompetitor = item.competitor.toLowerCase().includes(query);
        const matchesAction = item.recommendedAction.toLowerCase().includes(query);
        const matchesSource = item.source.toLowerCase().includes(query);
        if (!matchesTitle && !matchesCompetitor && !matchesAction && !matchesSource) return false;
      }
      return true;
    });
  }, [opportunities, selectedCompetitor, selectedVulnerability, selectedPriority, searchQuery]);

  // --------------------------------------------------------------------------
  // HANDLERS
  // --------------------------------------------------------------------------
  const handleAcknowledge = (id, competitorName) => {
    // BACKEND INTEGRATION POINT: Update Acknowledge Status
    /*
    await fetch(`/api/v1/competitor-intel/${id}/acknowledge`, { method: 'POST' });
    */
    setOpportunities((prev) =>
      prev.map((item) => (item.id === id ? { ...item, acknowledged: true } : item))
    );

    // Trigger Toast Notification
    setToastMessage(`${competitorName} opportunity acknowledged`);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const criticalCount = useMemo(
    () => opportunities.filter((o) => o.priority === "Critical" && !o.acknowledged).length,
    [opportunities]
  );

  return (
    <div className="p-8 space-y-6 bg-[var(--background)] min-h-screen text-[var(--foreground)] relative">
      {/* HEADER BAR */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Competitive Intelligence Command Center</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            AI-detected competitor vulnerabilities, scored and ready to act on
          </p>
        </div>
      </div>

      {/* CRITICAL ALERT BANNER */}
      {criticalCount > 0 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-500">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-full bg-rose-500/20 text-rose-500 shrink-0">
              <Icon icon="lucide:zap" className="w-5 h-5 fill-current" />
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider block leading-none">
                Critical Alerts
              </span>
              <span className="text-base font-bold text-[var(--foreground)]">
                {criticalCount} {criticalCount === 1 ? "opportunity needs" : "opportunities need"} action now
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-[var(--muted-foreground)]">
            <span className="flex items-center gap-1.5">
              <Icon icon="lucide:slack" className="w-3.5 h-3.5" />
              Auto-dispatched to #sales-alerts
            </span>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--positive-bg)] text-[var(--positive-text)] font-medium text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
              Auto-refresh 30s
            </span>
          </div>
        </div>
      )}

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Opportunities Tracked
          </span>
          <div className="text-3xl font-bold">{opportunities.length}</div>
          <span className="inline-block text-xs text-[var(--positive-text)] font-semibold bg-[var(--positive-bg)] px-2 py-0.5 rounded-md">
            ↑ 6 new today
          </span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Avg Opportunity Score
          </span>
          <div className="text-3xl font-bold">71</div>
          <span className="text-xs text-[var(--muted-foreground)]">out of 100</span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Top Vulnerability
          </span>
          <div className="text-2xl font-bold truncate">System Outages</div>
          <span className="text-xs text-[var(--muted-foreground)]">7 mentions this week</span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Slack Alerts Sent
          </span>
          <div className="text-3xl font-bold">3</div>
          <span className="text-xs text-[var(--muted-foreground)]">since Monday</span>
        </div>
      </div>

      {/* FILTER BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">Competitor</label>
          <select
            value={selectedCompetitor}
            onChange={(e) => setSelectedCompetitor(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="All Competitors">All Competitors</option>
            <option value="Square">Square</option>
            <option value="Toast">Toast</option>
            <option value="Clover">Clover</option>
            <option value="Lightspeed">Lightspeed</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">Vulnerability Type</label>
          <select
            value={selectedVulnerability}
            onChange={(e) => setSelectedVulnerability(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="All Types">All Types</option>
            <option value="System Outages">System Outages</option>
            <option value="Price Hikes">Price Hikes</option>
            <option value="PR Crisis">PR Crisis</option>
            <option value="Layoffs">Layoffs</option>
            <option value="Data Breach">Data Breach</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">Priority</label>
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="All Priorities">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">Search</label>
          <div className="relative">
            <Icon icon="lucide:search" className="w-4 h-4 absolute left-3 top-2.5 text-[var(--muted-foreground)]" />
            <input
              type="text"
              placeholder="Search opportunities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
      </div>

      {/* OPPORTUNITY CARDS LIST */}
      {isLoading ? (
        <div className="text-center py-12 text-sm text-[var(--muted-foreground)]">Loading intelligence feed...</div>
      ) : error ? (
        <div className="text-center py-12 text-sm text-rose-500">{error}</div>
      ) : filteredOpportunities.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[var(--border)] rounded-xl space-y-2">
          <p className="font-semibold text-[var(--foreground)]">No opportunities found</p>
          <p className="text-xs text-[var(--muted-foreground)]">Try adjusting your active filters or clear search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredOpportunities.map((item) => (
            <div
              key={item.id}
              className={`p-6 rounded-xl border bg-[var(--card)] shadow-xs space-y-4 flex flex-col justify-between transition-opacity ${
                item.acknowledged ? "opacity-60 border-[var(--border)]" : "border-[var(--border)]"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base">{item.competitor}</span>
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-[var(--muted)] text-[var(--muted-foreground)]">
                      {item.vulnerabilityType}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-extrabold tracking-wider px-2 py-0.5 rounded-md uppercase ${
                      item.priority === "Critical"
                        ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                        : item.priority === "High"
                        ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                        : "bg-slate-500/10 text-slate-500 border border-slate-500/20"
                    }`}
                  >
                    {item.priority}
                  </span>
                </div>

                <h3 className="font-semibold text-sm leading-snug">{item.title}</h3>

                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center text-[10px] font-bold uppercase text-[var(--muted-foreground)]">
                    <span>Opportunity Score</span>
                    <span className="text-rose-500 font-extrabold text-xs">{item.opportunityScore}/100</span>
                  </div>
                  <div className="w-full h-1.5 bg-[var(--muted)] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-rose-500 rounded-full transition-all duration-300"
                      style={{ width: `${item.opportunityScore}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400">
                    {item.tag}
                  </span>
                  {item.alertSent && (
                    <span className="text-[11px] text-[var(--muted-foreground)] flex items-center gap-1">
                      <Icon icon="lucide:send" className="w-3 h-3" />
                      Alert sent
                    </span>
                  )}
                </div>

                <p className="text-xs text-[var(--muted-foreground)] bg-[var(--muted)]/50 p-3 rounded-lg leading-relaxed">
                  <strong className="text-[var(--foreground)]">Action:</strong> {item.recommendedAction}
                </p>
              </div>

              <div className="space-y-3 pt-2">
                <div className="text-[11px] text-[var(--muted-foreground)]">
                  {item.source} · {item.timestamp}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {/* View Details Button */}
                  <button
                    onClick={() => setSelectedOpportunityModal(item)}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors"
                  >
                    <Icon icon="lucide:eye" className="w-4 h-4" />
                    <span>View Details</span>
                  </button>

                  {/* Acknowledge Button */}
                  <button
                    onClick={() => handleAcknowledge(item.id, item.competitor)}
                    disabled={item.acknowledged}
                    className={`flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors ${
                      item.acknowledged
                        ? "bg-[var(--muted)] text-[var(--muted-foreground)] cursor-not-allowed"
                        : "bg-emerald-600 hover:bg-emerald-700 text-white"
                    }`}
                  >
                    <Icon icon="lucide:check" className="w-4 h-4" />
                    <span>{item.acknowledged ? "Acknowledged" : "Acknowledge"}</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ==================================================================== */}
      {/* 1. TOAST NOTIFICATION POPUP (MATCHING SCREENSHOT image_432ae7.png)   */}
      {/* ==================================================================== */}
      {toastMessage && (
        <div className="fixed bottom-6 left-6 z-50 flex items-center gap-2.5 px-4 py-3 bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-xl animate-in fade-in slide-in-from-bottom-3 duration-200">
          <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center text-white shrink-0">
            <Icon icon="lucide:check" className="w-3.5 h-3.5 stroke-[3]" />
          </div>
          <span className="text-xs font-bold text-emerald-800 dark:text-emerald-400">
            {toastMessage}
          </span>
        </div>
      )}

      {/* ==================================================================== */}
      {/* 2. VIEW DETAILS MODAL POPUP (MATCHING SCREENSHOT image_432b00.jpg)  */}
      {/* ==================================================================== */}
      {selectedOpportunityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
          <div className="bg-[var(--card)] border border-[var(--border)] text-[var(--foreground)] w-full max-w-lg rounded-2xl shadow-2xl p-6 relative space-y-5 animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-bold text-[var(--foreground)]">
                  {selectedOpportunityModal.competitor} — {selectedOpportunityModal.vulnerabilityType}
                </h2>
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  {selectedOpportunityModal.title}
                </p>
              </div>
              <button
                onClick={() => setSelectedOpportunityModal(null)}
                className="p-1 rounded-lg text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)] transition-colors"
              >
                <Icon icon="lucide:x" className="w-5 h-5" />
              </button>
            </div>

            {/* Metadata Grid (Priority, Opportunity Score, Department, Source) */}
            <div className="grid grid-cols-2 gap-4 py-2 border-y border-[var(--border)] text-xs">
              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                  PRIORITY
                </span>
                <span
                  className={`text-[10px] font-extrabold tracking-wider px-2 py-0.5 rounded-md uppercase inline-block ${
                    selectedOpportunityModal.priority === "Critical"
                      ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                      : selectedOpportunityModal.priority === "High"
                      ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                      : "bg-slate-500/10 text-slate-500 border border-slate-500/20"
                  }`}
                >
                  {selectedOpportunityModal.priority}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                  OPPORTUNITY SCORE
                </span>
                <span className="text-rose-500 font-extrabold text-xs">
                  {selectedOpportunityModal.opportunityScore}/100
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                  DEPARTMENT
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400 inline-block">
                  {selectedOpportunityModal.tag}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                  SOURCE
                </span>
                <span className="text-[var(--foreground)] font-medium">
                  {selectedOpportunityModal.source}, {selectedOpportunityModal.timestamp}
                </span>
              </div>
            </div>

            {/* Content Sections matching prototype */}
            <div className="space-y-4 text-xs">
              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  RATIONALE
                </h4>
                <p className="text-[var(--foreground)] leading-relaxed">
                  {selectedOpportunityModal.rationale}
                </p>
              </div>

              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  ACTION ITEM
                </h4>
                <p className="text-[var(--foreground)] leading-relaxed">
                  {selectedOpportunityModal.recommendedAction}
                </p>
              </div>

              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  TARGET AUDIENCE
                </h4>
                <p className="text-[var(--foreground)] leading-relaxed">
                  {selectedOpportunityModal.targetAudience}
                </p>
              </div>

              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  SUGGESTED OUTREACH MESSAGE
                </h4>
                <div className="p-3.5 rounded-xl bg-[var(--muted)]/50 border border-[var(--border)] text-[var(--muted-foreground)] italic leading-relaxed">
                  {selectedOpportunityModal.suggestedOutreachMessage}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}