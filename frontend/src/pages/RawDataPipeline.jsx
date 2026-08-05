import { useState, useMemo, useEffect } from "react";
import { Icon } from "@iconify/react";

// ============================================================================
// MOCK API DATA STRUCTURE
// Matching screenshot layout & API backend specifications
// Expected Endpoint: GET /api/v1/raw-pipeline/articles
// ============================================================================
const MOCK_RAW_ARTICLES = [
  {
    id: "raw-101",
    title: "Square payment processing down for 6+ hours nationwide",
    source: "Fundus",
    published: "4h ago",
    matchedEntity: "Square",
    matchedContext: "payment outage",
    preFilterStatus: "Pass", // Options: 'Pass' | 'Fail'
    rawUrl: "https://example.com/news/square-outage-6h",
    contentSnippet: "Square merchants experienced nationwide payment processing downtime lasting over 6 hours during peak business hours...",
    rawJson: { feed_id: "rss_fundus_091", word_count: 642, confidence_score: 0.96 }
  },
  {
    id: "raw-102",
    title: "Clover investigating possible customer data exposure",
    source: "Google News",
    published: "6h ago",
    matchedEntity: "Clover",
    matchedContext: "data breach",
    preFilterStatus: "Pass",
    rawUrl: "https://example.com/news/clover-data-investigation",
    contentSnippet: "Security researchers identified unencrypted API responses from Clover merchant portals, prompting an internal audit...",
    rawJson: { feed_id: "gn_tech_4821", word_count: 512, confidence_score: 0.91 }
  },
  {
    id: "raw-103",
    title: "Toast raises subscription fees 15% for restaurant tier",
    source: "Fundus",
    published: "1d ago",
    matchedEntity: "Toast",
    matchedContext: "price increase",
    preFilterStatus: "Pass",
    rawUrl: "https://example.com/news/toast-fee-hike-restaurant",
    contentSnippet: "Toast announced updated pricing tiers for restaurant partners, introducing a mandatory 15% base fee increase effective next month...",
    rawJson: { feed_id: "rss_fundus_104", word_count: 420, confidence_score: 0.88 }
  },
  {
    id: "raw-104",
    title: "Local coffee shop switches to new POS system, cites ease of use",
    source: "Reddit RSS",
    published: "9h ago",
    matchedEntity: "—",
    matchedContext: "—",
    preFilterStatus: "Fail",
    failureReason: "No target competitor entity detected in article content.",
    rawUrl: "https://reddit.com/r/smallbusiness/comments/pos_switch",
    contentSnippet: "We decided to switch our shop POS setup after struggling with slow terminal updates...",
    rawJson: { feed_id: "reddit_sb_392", word_count: 180, confidence_score: 0.21 }
  },
  {
    id: "raw-105",
    title: "Lightspeed expands retail inventory tools across North America",
    source: "Google News",
    published: "1d ago",
    matchedEntity: "Lightspeed",
    matchedContext: "product update",
    preFilterStatus: "Pass",
    rawUrl: "https://example.com/news/lightspeed-inventory-update",
    contentSnippet: "Lightspeed Commerce announced new multi-location inventory sync capabilities targeting mid-market retailers...",
    rawJson: { feed_id: "gn_retail_891", word_count: 730, confidence_score: 0.94 }
  },
  {
    id: "raw-106",
    title: "General discussion on payment hardware reliability",
    source: "Reddit RSS",
    published: "2d ago",
    matchedEntity: "—",
    matchedContext: "—",
    preFilterStatus: "Fail",
    failureReason: "Generic content; lacks actionable competitive intelligence metrics.",
    rawUrl: "https://reddit.com/r/hardware/comments/payment_terminals",
    contentSnippet: "Looking for opinions on overall terminal lifespan when running high volume customer taps daily...",
    rawJson: { feed_id: "reddit_hw_110", word_count: 240, confidence_score: 0.15 }
  }
];

export default function RawDataPipeline() {
  // --------------------------------------------------------------------------
  // STATE MANAGEMENT
  // --------------------------------------------------------------------------
  const [articles, setArticles] = useState(MOCK_RAW_ARTICLES);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState(null);

  // Filters State
  const [selectedSource, setSelectedSource] = useState("All Sources");
  const [selectedStatus, setSelectedStatus] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  // Table Interaction State
  const [expandedRowId, setExpandedRowId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 4;

  // --------------------------------------------------------------------------
  // BACKEND API INTEGRATION PLACEHOLDERS
  // --------------------------------------------------------------------------
  useEffect(() => {
    /*
      BACKEND INTEGRATION POINT 1: Initial Ingestion Data Fetch
      
      async function fetchPipelineArticles() {
        setIsLoading(true);
        try {
          // Pass active filters directly to API query parameters if server-side filtering is preferred:
          // const res = await fetch(`/api/v1/raw-pipeline/articles?source=${selectedSource}&status=${selectedStatus}&q=${searchQuery}`);
          const res = await fetch('/api/v1/raw-pipeline/articles');
          const data = await res.json();
          setArticles(data.articles);
        } catch (err) {
          setError("Failed to load raw pipeline data.");
        } finally {
          setIsLoading(false);
        }
      }
      fetchPipelineArticles();
    */
  }, []);

  // Trigger Manual Ingestion Fetch
  const handleTriggerFetchCycle = async () => {
    setIsFetching(true);
    /*
      BACKEND INTEGRATION POINT 2: Trigger Manual Fetch Cycle
      
      try {
        const res = await fetch('/api/v1/raw-pipeline/trigger-fetch', { method: 'POST' });
        const result = await res.json();
        // Refresh articles list after fetch completes
      } catch (err) {
        console.error("Failed to trigger fetch cycle", err);
      }
    */
    setTimeout(() => {
      setIsFetching(false);
    }, 1200);
  };

  // Dynamic Sources List (combines default choices with dynamic sources from data)
  const availableSources = useMemo(() => {
    const sourcesSet = new Set(articles.map((item) => item.source));
    return ["All Sources", ...Array.from(sourcesSet)];
  }, [articles]);

  // --------------------------------------------------------------------------
  // FILTERING & PAGINATION LOGIC
  // --------------------------------------------------------------------------
  const filteredArticles = useMemo(() => {
    return articles.filter((item) => {
      // 1. Source Dropdown Filter
      if (selectedSource !== "All Sources" && item.source !== selectedSource) {
        return false;
      }
      // 2. Pre-filter Status Dropdown Filter
      if (selectedStatus !== "All" && item.preFilterStatus !== selectedStatus) {
        return false;
      }
      // 3. Keyword Free-Text Search Filter
      if (searchQuery.trim() !== "") {
        const query = searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(query);
        const matchesEntity = item.matchedEntity.toLowerCase().includes(query);
        const matchesContext = item.matchedContext.toLowerCase().includes(query);
        const matchesSource = item.source.toLowerCase().includes(query);
        if (!matchesTitle && !matchesEntity && !matchesContext && !matchesSource) {
          return false;
        }
      }
      return true;
    });
  }, [articles, selectedSource, selectedStatus, searchQuery]);

  // Pagination Math
  const totalPages = Math.ceil(filteredArticles.length / itemsPerPage) || 1;
  const paginatedArticles = useMemo(() => {
    const startIdx = (currentPage - 1) * itemsPerPage;
    return filteredArticles.slice(startIdx, startIdx + itemsPerPage);
  }, [filteredArticles, currentPage, itemsPerPage]);

  const toggleRowExpand = (id) => {
    setExpandedRowId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="p-8 space-y-6 bg-[var(--background)] min-h-screen text-[var(--foreground)]">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Raw Data Pipeline Monitor</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            Transparency into articles fetched before they reach the AI pipeline
          </p>
        </div>
      </div>

      {/* KPI STAT CARDS SECTION */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Articles Fetched */}
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            ARTICLES FETCHED (24H)
          </span>
          <div className="text-3xl font-bold">8</div>
          <div>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">
              ↑ Fundus + Google News + Reddit
            </span>
          </div>
        </div>

        {/* Card 2: Pre-filter Pass Rate */}
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            PRE-FILTER PASS RATE
          </span>
          <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">75%</div>
          <div className="text-xs text-[var(--muted-foreground)]">6 of 8 passed</div>
        </div>

        {/* Card 3: Sent to AI Pipeline */}
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            SENT TO AI PIPELINE
          </span>
          <div className="text-3xl font-bold">6</div>
          <div className="text-xs text-[var(--muted-foreground)]">awaiting / processed by Basim's stages</div>
        </div>

        {/* Card 4: Last Fetch Cycle */}
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            LAST FETCH CYCLE
          </span>
          <div className="text-3xl font-bold">4m ago</div>
          <div className="text-xs text-[var(--muted-foreground)]">runs every 30 min</div>
        </div>
      </div>

      {/* MAIN MONITOR TABLE CONTAINER */}
      <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-6">
        {/* Card Header & Trigger Button */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h2 className="text-base font-bold text-[var(--foreground)]">Raw RSS Data Pipeline Monitor</h2>
          <button
            onClick={handleTriggerFetchCycle}
            disabled={isFetching}
            className="flex items-center justify-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--muted)] transition-colors self-start sm:self-auto"
          >
            <Icon
              icon="lucide:refresh-cw"
              className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`}
            />
            <span>{isFetching ? "Triggering..." : "Trigger Fetch Cycle"}</span>
          </button>
        </div>

        {/* TOP FILTER BAR */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Dropdown 1: Filter by Source */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
              Filter by Source
            </label>
            <select
              value={selectedSource}
              onChange={(e) => {
                setSelectedSource(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              {availableSources.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
          </div>

          {/* Dropdown 2: Pre-filter Status */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
              Pre-filter Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              <option value="All">All</option>
              <option value="Pass">Pass</option>
              <option value="Fail">Fail</option>
            </select>
          </div>

          {/* Keyword Free-Text Search */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
              Keyword Search
            </label>
            <input
              type="text"
              placeholder="Search title or content..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            />
          </div>
        </div>

        {/* DATA DISPLAY TABLE */}
        {isLoading ? (
          <div className="py-12 text-center text-sm text-[var(--muted-foreground)]">
            Loading pipeline ingestion data...
          </div>
        ) : error ? (
          <div className="py-12 text-center text-sm text-rose-500">{error}</div>
        ) : paginatedArticles.length === 0 ? (
          <div className="py-12 text-center text-sm text-[var(--muted-foreground)] border border-dashed border-[var(--border)] rounded-xl">
            No pipeline items match the active filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)] text-[10px] font-bold uppercase tracking-wider text-[var(--muted-foreground)]">
                  <th className="py-3 px-2 w-8"></th>
                  <th className="py-3 px-4">TITLE</th>
                  <th className="py-3 px-4">SOURCE</th>
                  <th className="py-3 px-4">PUBLISHED</th>
                  <th className="py-3 px-4">MATCHED ENTITY</th>
                  <th className="py-3 px-4">MATCHED CONTEXT</th>
                  <th className="py-3 px-4 text-right">PRE-FILTER</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)] text-xs">
                {paginatedArticles.map((row) => {
                  const isExpanded = expandedRowId === row.id;
                  const isPass = row.preFilterStatus === "Pass";

                  return (
                    <tr key={row.id} className="group hover:bg-[var(--muted)]/40 transition-colors">
                      {/* Chevron expand trigger */}
                      <td className="py-4 px-2">
                        <button
                          onClick={() => toggleRowExpand(row.id)}
                          className="p-1 rounded-md text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
                        >
                          <Icon
                            icon="lucide:chevron-right"
                            className={`w-4 h-4 transition-transform duration-200 ${
                              isExpanded ? "rotate-90" : ""
                            }`}
                          />
                        </button>
                      </td>

                      {/* Title Column */}
                      <td className="py-4 px-4 font-semibold text-[var(--foreground)] max-w-xs md:max-w-md">
                        <div className="truncate" title={row.title}>
                          {row.title}
                        </div>
                      </td>

                      {/* Source Column */}
                      <td className="py-4 px-4 text-[var(--muted-foreground)] font-medium">
                        {row.source}
                      </td>

                      {/* Published Column */}
                      <td className="py-4 px-4 text-[var(--muted-foreground)] whitespace-nowrap">
                        {row.published}
                      </td>

                      {/* Matched Entity Column */}
                      <td className="py-4 px-4 font-medium text-[var(--foreground)]">
                        {row.matchedEntity}
                      </td>

                      {/* Matched Context Column */}
                      <td className="py-4 px-4 text-[var(--muted-foreground)]">
                        {row.matchedContext}
                      </td>

                      {/* Pre-filter Status Badge */}
                      <td className="py-4 px-4 text-right whitespace-nowrap">
                        <span
                          className={`inline-block px-2.5 py-0.5 text-[11px] font-bold rounded-md ${
                            isPass
                              ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                              : "bg-rose-500/10 text-rose-500"
                          }`}
                        >
                          {row.preFilterStatus}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* EXPANDABLE DETAIL DRAWER (RENDERED WHEN ROW IS CLICKED) */}
        {expandedRowId && (
          <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--muted)]/30 text-xs space-y-3 animate-in fade-in duration-150">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[var(--foreground)]">
                Raw Ingestion Snippet Details
              </span>
              <button
                onClick={() => setExpandedRowId(null)}
                className="text-[11px] text-[var(--muted-foreground)] hover:underline"
              >
                Close details
              </button>
            </div>
            {(() => {
              const activeRow = articles.find((a) => a.id === expandedRowId);
              if (!activeRow) return null;
              return (
                <div className="space-y-2">
                  <p className="text-[var(--muted-foreground)] leading-relaxed">
                    <strong className="text-[var(--foreground)]">Snippet:</strong>{" "}
                    {activeRow.contentSnippet}
                  </p>
                  {activeRow.failureReason && (
                    <p className="text-rose-500 font-medium">
                      <strong>Filter Rejection Reason:</strong> {activeRow.failureReason}
                    </p>
                  )}
                  <div className="pt-2">
                    <span className="text-[10px] font-bold uppercase text-[var(--muted-foreground)] block mb-1">
                      Raw Data Payload
                    </span>
                    <pre className="p-3 rounded-lg bg-[var(--card)] border border-[var(--border)] text-[11px] text-[var(--muted-foreground)] overflow-x-auto font-mono">
                      {JSON.stringify(activeRow.rawJson, null, 2)}
                    </pre>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* PAGINATION CONTROLS */}
        <div className="flex items-center justify-center gap-2 pt-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={`w-7 h-7 flex items-center justify-center text-xs font-semibold rounded-md transition-colors ${
                currentPage === page
                  ? "bg-[var(--foreground)] text-[var(--background)] font-bold"
                  : "bg-[var(--card)] border border-[var(--border)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]"
              }`}
            >
              {page}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}