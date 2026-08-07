import { useState, useMemo, useEffect } from "react";
import { Icon } from "@iconify/react";

export default function CompetitiveIntel() {
  // --------------------------------------------------------------------------
  // STATE MANAGEMENT
  // --------------------------------------------------------------------------
  const [opportunities, setOpportunities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter dropdown state variables
  const [selectedCompetitor, setSelectedCompetitor] =
    useState("All Competitors");
  const [selectedVulnerability, setSelectedVulnerability] =
    useState("All Types");
  const [selectedPriority, setSelectedPriority] = useState("All Priorities");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal State (d1)
  const [selectedOpportunityModal, setSelectedOpportunityModal] =
    useState(null);

  // Toast Notification State
  const [toastMessage, setToastMessage] = useState(null);

  // --------------------------------------------------------------------------
  // HELPER UTILITIES
  // --------------------------------------------------------------------------
  const parseDepartments = (deptString) => {
    if (!deptString) return ["SALES"];
    return deptString
      .split("|")
      .map((d) => d.trim())
      .filter(Boolean);
  };

  const getScoreColorClasses = (score) => {
    if (score > 50) {
      return {
        text: "text-rose-500",
        bg: "bg-rose-500",
      };
    }
    if (score > 40) {
      return {
        text: "text-amber-500",
        bg: "bg-amber-500",
      };
    }
    return {
      text: "text-emerald-500",
      bg: "bg-emerald-500",
    };
  };

  // --------------------------------------------------------------------------
  // BACKEND API INTEGRATION: GET /api/vulnerabilities
  // --------------------------------------------------------------------------
  const fetchIntelData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/vulnerabilities");
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();

      const normalizedData = data.map((item) => {
        const matchedComps = item.matched_competitors || [];
        const formattedCompetitor =
          matchedComps.length > 0
            ? matchedComps
                .map((c) => c.charAt(0).toUpperCase() + c.slice(1))
                .join(", ")
            : item.competitor || "Unknown Competitor";

        const brief = item.action_brief || {};
        const scoring = item.opportunity_scoring || {};

        return {
          id: item.id || `opp-${Math.random().toString(36).substr(2, 9)}`,
          matchedCompetitorsList: matchedComps.map((c) => c.toLowerCase()),
          competitor: formattedCompetitor,
          vulnerabilityType: item.vulnerability_type || "General",
          priority: brief.urgency || scoring.priority_label || "Medium",
          priorityLabel: scoring.priority_label || "MEDIUM",
          title: brief.headline || item.title || "Untitled Opportunity",
          vulnerabilitySummary:
            brief.vulnerability_summary || "No summary provided.",
          opportunityScore: scoring.opportunity_score ?? 50,
          severityScore: scoring.severity_score ?? 0,
          volumeScore: scoring.volume_score ?? 0,
          urgencyScore: scoring.urgency_score ?? 0,
          targetDepartment: brief.target_department || "SALES",
          recommendedAction: brief.recommended_action || "No action specified.",
          urgency: brief.urgency || "Medium",
          factAudit: item.fact_audit || { is_passed: true, flagged_claims: [] },
          articleUrl:
            item.article_url ||
            item.url ||
            item.article?.url ||
            item.link ||
            null,
          source: item.source_name || item.source || "Processed at",
          timestamp: item.processed_at
            ? new Date(item.processed_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })
            : "Recently",
          acknowledged: item.acknowledged ?? false,
        };
      });

      setOpportunities(normalizedData);
    } catch (err) {
      console.error("Error fetching competitive intel:", err);
      setError("Failed to load competitive intelligence data from backend.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelData();
  }, []);

  // --------------------------------------------------------------------------
  // HANDLERS & API ACTIONS
  // --------------------------------------------------------------------------
  const handleAcknowledge = async (id, competitorName) => {
    setOpportunities((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, acknowledged: true } : item,
      ),
    );

    setToastMessage(`${competitorName} opportunity acknowledged`);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);

    try {
      await fetch(`/api/vulnerabilities/${id}/acknowledge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
    } catch (err) {
      console.error("Failed to sync acknowledgment with backend:", err);
    }
  };

  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((item) => {
      if (selectedCompetitor !== "All Competitors") {
        const target = selectedCompetitor.toLowerCase();
        const matchesCompList = item.matchedCompetitorsList.includes(target);
        const matchesCompString = item.competitor
          .toLowerCase()
          .includes(target);
        if (!matchesCompList && !matchesCompString) return false;
      }
      if (
        selectedVulnerability !== "All Types" &&
        item.vulnerabilityType.toLowerCase() !==
          selectedVulnerability.toLowerCase()
      ) {
        return false;
      }
      if (
        selectedPriority !== "All Priorities" &&
        item.priority.toLowerCase() !== selectedPriority.toLowerCase()
      ) {
        return false;
      }
      if (searchQuery.trim() !== "") {
        const query = searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(query);
        const matchesCompetitor = item.competitor.toLowerCase().includes(query);
        const matchesAction = item.recommendedAction
          .toLowerCase()
          .includes(query);
        const matchesSummary = item.vulnerabilitySummary
          .toLowerCase()
          .includes(query);
        if (
          !matchesTitle &&
          !matchesCompetitor &&
          !matchesAction &&
          !matchesSummary
        )
          return false;
      }
      return true;
    });
  }, [
    opportunities,
    selectedCompetitor,
    selectedVulnerability,
    selectedPriority,
    searchQuery,
  ]);

  const criticalCount = useMemo(
    () =>
      opportunities.filter(
        (o) => o.priority.toLowerCase() === "critical" && !o.acknowledged,
      ).length,
    [opportunities],
  );

  const avgScore = useMemo(() => {
    if (opportunities.length === 0) return 0;
    const total = opportunities.reduce(
      (acc, curr) => acc + curr.opportunityScore,
      0,
    );
    return Math.round(total / opportunities.length);
  }, [opportunities]);

  return (
    <div className="p-8 space-y-6 bg-[var(--background)] min-h-screen text-[var(--foreground)] relative">
      {/* HEADER BAR */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Competitive Intelligence Command Center
          </h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            AI-detected competitor vulnerabilities, scored and ready to act on
          </p>
        </div>
        <button
          onClick={fetchIntelData}
          disabled={isLoading}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors self-start md:self-auto cursor-pointer"
        >
          <Icon
            icon="lucide:refresh-cw"
            className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`}
          />
          <span>Refresh Feed</span>
        </button>
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
                {criticalCount}{" "}
                {criticalCount === 1
                  ? "opportunity needs"
                  : "opportunities need"}{" "}
                action now
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
              Live Sync
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
          <div className="text-xl font-bold mt-2.5">{opportunities.length}</div>
          <span className="inline-block text-xs text-[var(--positive-text)] font-semibold bg-[var(--positive-bg)] px-2 py-0.5 rounded-md">
            Active Feed
          </span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Avg Opportunity Score
          </span>
          <div className="text-xl font-bold mt-2.5">{avgScore}</div>
          <span className="text-xs text-[var(--muted-foreground)]">
            out of 100
          </span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Top Vulnerability
          </span>
          <div className="text-xl font-bold truncate mt-2.5">
            Product Defects
          </div>
          <span className="text-xs text-[var(--muted-foreground)]">
            Primary market factor
          </span>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-1">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            Acknowledged
          </span>
          <div className="text-xl font-bold mt-2.5">
            {opportunities.filter((o) => o.acknowledged).length}
          </div>
          <span className="text-xs text-[var(--muted-foreground)]">
            processed by team
          </span>
        </div>
      </div>

      {/* FILTER BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
            Competitor
          </label>
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
            <option value="Touchbistro">TouchBistro</option>
            <option value="Spoton">SpotOn</option>
            <option value="Stripe">Stripe</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
            Vulnerability Type
          </label>
          <select
            value={selectedVulnerability}
            onChange={(e) => setSelectedVulnerability(e.target.value)}
            className="w-full px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="All Types">All Types</option>
            <option value="System Outages">System Outages</option>
            <option value="Price Increases">Price Increases</option>
            <option value="PR Crises">PR Crises</option>
            <option value="Layoffs">Layoffs</option>
            <option value="Product Defects">Product Defects</option>
            <option value="Data Breaches">Data Breaches</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
            Priority (Urgency)
          </label>
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
          <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
            Search
          </label>
          <div className="relative">
            <Icon
              icon="lucide:search"
              className="w-4 h-4 absolute left-3 top-2.5 text-[var(--muted-foreground)]"
            />
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
        <div className="text-center py-12 text-sm text-[var(--muted-foreground)] flex items-center justify-center gap-2">
          <Icon icon="lucide:loader-2" className="w-4 h-4 animate-spin" />
          Fetching live competitive vulnerabilities...
        </div>
      ) : error ? (
        <div className="text-center py-12 text-sm text-rose-500">{error}</div>
      ) : filteredOpportunities.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[var(--border)] rounded-xl space-y-2">
          <p className="font-semibold text-[var(--foreground)]">
            No opportunities found
          </p>
          <p className="text-xs text-[var(--muted-foreground)]">
            Try adjusting your active filters or clear search query.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredOpportunities.map((item) => {
            const scoreColors = getScoreColorClasses(item.opportunityScore);
            return (
              <div
                key={item.id}
                className={`p-6 rounded-xl border bg-[var(--card)] shadow-xs space-y-4 flex flex-col justify-between transition-opacity ${
                  item.acknowledged
                    ? "opacity-60 border-[var(--border)]"
                    : "border-[var(--border)]"
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-base">
                        {item.competitor}
                      </span>
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-[var(--muted)] text-[var(--muted-foreground)]">
                        {item.vulnerabilityType}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-extrabold tracking-wider px-2 py-0.5 rounded-md uppercase shrink-0 ${
                        item.urgency.toLowerCase() === "critical"
                          ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                          : item.urgency.toLowerCase() === "high"
                            ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                            : "bg-slate-500/10 text-slate-500 border border-slate-500/20"
                      }`}
                    >
                      {item.urgency}
                    </span>
                  </div>

                  <h3 className="font-semibold text-sm leading-snug">
                    {item.title}
                  </h3>

                  <div className="space-y-1.5 pt-1">
                    <div className="flex justify-between items-center text-[10px] font-bold uppercase text-[var(--muted-foreground)]">
                      <span>Opportunity Score</span>
                      <span
                        className={`${scoreColors.text} font-extrabold text-xs`}
                      >
                        {item.opportunityScore}/100
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-[var(--muted)] rounded-full overflow-hidden">
                      <div
                        className={`h-full ${scoreColors.bg} rounded-full transition-all duration-300`}
                        style={{ width: `${item.opportunityScore}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-1 gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {parseDepartments(item.targetDepartment).map(
                        (dept, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20"
                          >
                            {dept}
                          </span>
                        ),
                      )}
                    </div>
                    {!item.factAudit.is_passed && (
                      <span className="text-[10px] font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1 bg-amber-500/10 px-2 py-0.5 rounded">
                        <Icon
                          icon="lucide:alert-triangle"
                          className="w-3 h-3"
                        />
                        Fact Flagged
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-[var(--muted-foreground)] bg-[var(--muted)]/50 p-3 rounded-lg leading-relaxed">
                    <strong className="text-[var(--foreground)]">
                      Action:
                    </strong>{" "}
                    {item.recommendedAction}
                  </p>
                </div>

                <div className="space-y-3 pt-2">
                  <div className="text-[11px] text-[var(--muted-foreground)]">
                    {item.source} · {item.timestamp}
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setSelectedOpportunityModal(item)}
                      className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors cursor-pointer"
                    >
                      <Icon icon="lucide:eye" className="w-4 h-4" />
                      <span>View Details</span>
                    </button>

                    <button
                      onClick={() =>
                        handleAcknowledge(item.id, item.competitor)
                      }
                      disabled={item.acknowledged}
                      className={`flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors ${
                        item.acknowledged
                          ? "bg-[var(--muted)] text-[var(--muted-foreground)] cursor-not-allowed"
                          : "bg-emerald-600 hover:bg-emerald-700 text-white cursor-pointer"
                      }`}
                    >
                      <Icon icon="lucide:check" className="w-4 h-4" />
                      <span>
                        {item.acknowledged ? "Acknowledged" : "Acknowledge"}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* TOAST NOTIFICATION POPUP */}
      {toastMessage && (
        <div className="fixed bottom-6 left-6 z-[110] flex items-center gap-2.5 px-4 py-3 bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-xl animate-in fade-in slide-in-from-bottom-3 duration-200">
          <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center text-white shrink-0">
            <Icon icon="lucide:check" className="w-3.5 h-3.5 stroke-[3]" />
          </div>
          <span className="text-xs font-bold text-emerald-800 dark:text-emerald-400">
            {toastMessage}
          </span>
        </div>
      )}

      {/* VIEW DETAILS MODAL POPUP (d1) */}
      {selectedOpportunityModal && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/60 backdrop-blur-xs p-4 pt-20 pb-12 overflow-y-auto">
          <div className="bg-[var(--card)] border border-[var(--border)] text-[var(--foreground)] w-full max-w-xl rounded-2xl shadow-2xl p-6 relative space-y-5 animate-in fade-in zoom-in-95 duration-150 my-auto">
            {/* MODAL HEADER */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base font-bold text-[var(--foreground)]">
                    {selectedOpportunityModal.competitor}
                  </h2>
                  <span className="text-xs px-2 py-0.5 rounded bg-[var(--muted)] text-[var(--muted-foreground)] font-semibold">
                    {selectedOpportunityModal.vulnerabilityType}
                  </span>
                </div>
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  Processed {selectedOpportunityModal.timestamp}
                </p>
              </div>
              <button
                onClick={() => setSelectedOpportunityModal(null)}
                className="p-1 rounded-lg text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)] transition-colors cursor-pointer"
              >
                <Icon icon="lucide:x" className="w-5 h-5" />
              </button>
            </div>

            {/* ACTION BRIEF HEADLINE */}
            <div className="p-3.5 rounded-xl bg-[var(--muted)]/50 border border-[var(--border)]">
              <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                EXECUTIVE HEADLINE
              </span>
              <p className="text-xs font-semibold leading-relaxed text-[var(--foreground)]">
                {selectedOpportunityModal.title}
              </p>
            </div>

            {/* METRICS & METADATA GRID WITH DIRECT ARTICLE LINK */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-xl bg-[var(--muted)]/20 border border-[var(--border)] text-xs">
              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-0.5">
                  URGENCY
                </span>
                <span
                  className={`text-[10px] font-extrabold tracking-wider px-2 py-0.5 rounded-md uppercase inline-block ${
                    selectedOpportunityModal.urgency.toLowerCase() ===
                    "critical"
                      ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                      : selectedOpportunityModal.urgency.toLowerCase() ===
                          "high"
                        ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                        : "bg-slate-500/10 text-slate-500 border border-slate-500/20"
                  }`}
                >
                  {selectedOpportunityModal.urgency}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-0.5">
                  OPPORTUNITY SCORE
                </span>
                <span
                  className={`${
                    getScoreColorClasses(
                      selectedOpportunityModal.opportunityScore,
                    ).text
                  } font-extrabold text-xs`}
                >
                  {selectedOpportunityModal.opportunityScore}/100
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-1">
                  DEPARTMENTS
                </span>
                <div className="flex flex-wrap gap-1">
                  {parseDepartments(
                    selectedOpportunityModal.targetDepartment,
                  ).map((dept, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 inline-block"
                    >
                      {dept}
                    </span>
                  ))}
                </div>
              </div>


              {/* DIRECT SOURCE ARTICLE LINK GRID ITEM */}
              <div>
                <span className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase block mb-0.5">
                  SOURCE ARTICLE
                </span>
                {selectedOpportunityModal.articleUrl ? (
                  <a
                    href={selectedOpportunityModal.articleUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 hover:underline"
                  >
                    <span>Read Article</span>
                    <Icon
                      icon="lucide:external-link"
                      className="w-3 h-3 shrink-0"
                    />
                  </a>
                ) : (
                  <span className="text-[10px] text-[var(--muted-foreground)]">
                    Unavailable
                  </span>
                )}
              </div>
            </div>

            {/* ACTION BRIEF FIELDS */}
            <div className="space-y-4 text-xs">
              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  VULNERABILITY SUMMARY
                </h4>
                <p className="text-[var(--foreground)] leading-relaxed">
                  {selectedOpportunityModal.vulnerabilitySummary}
                </p>
              </div>

              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  RECOMMENDED ACTION
                </h4>
                <p className="text-[var(--foreground)] leading-relaxed bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl">
                  {selectedOpportunityModal.recommendedAction}
                </p>
              </div>

              {/* FACT AUDIT STATUS */}
              <div>
                <h4 className="text-[10px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase mb-1">
                  STAGE 3 FACT AUDIT STATUS
                </h4>
                {selectedOpportunityModal.factAudit.is_passed ? (
                  <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    <Icon
                      icon="lucide:check-circle"
                      className="w-4 h-4 shrink-0"
                    />
                    <span>
                      Audit Passed — Vulnerability Summary supported by source article.
                    </span>
                  </div>
                ) : (
                  <div className="space-y-2 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-500">
                    <div className="flex items-center gap-2 font-semibold">
                      <Icon
                        icon="lucide:alert-octagon"
                        className="w-4 h-4 shrink-0"
                      />
                      <span>
                        Audit Flagged — Contradicted / Unverified Claims
                        Detected:
                      </span>
                    </div>
                    <ul className="list-disc list-inside space-y-1 text-[11px] pl-2 text-[var(--foreground)]">
                      {selectedOpportunityModal.factAudit.flagged_claims?.map(
                        (claim, idx) => (
                          <li key={idx} className="leading-snug">
                            "{claim}"
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
