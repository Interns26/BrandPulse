import { useState, useMemo, useEffect } from "react";
import { Icon } from "@iconify/react";

export default function RawDataPipeline() {
  // --------------------------------------------------------------------------
  // STATE MANAGEMENT
  // --------------------------------------------------------------------------
  const [articles, setArticles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState(null);

  // Filters State
  const [selectedSource, setSelectedSource] = useState("All Sources");
  const [selectedStatus, setSelectedStatus] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  // Table Interaction State
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 4;

  // --------------------------------------------------------------------------
  // BACKEND API INTEGRATION: GET /api/articles
  // --------------------------------------------------------------------------
  const fetchPipelineArticles = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/articles");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const rawArticles = Array.isArray(data) ? data : [];

      // Map backend Article schema to UI model
      const normalizedData = rawArticles.map((item) => {
        const isPass = Boolean(item.vulnerability_processed);
        const hasCompetitors =
          Array.isArray(item.matched_competitors) &&
          item.matched_competitors.length > 0;
        const hasContexts =
          Array.isArray(item.matched_contexts) &&
          item.matched_contexts.length > 0;

        return {
          id: item.id || `raw-${Math.random().toString(36).substring(2, 9)}`,
          title: item.title || "Untitled Ingestion Record",
          source: item.source_name || "RSS Feed",
          published: item.published_at
            ? new Date(item.published_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
                year: "numeric",
              })
            : "Recently",
          matchedEntity: hasCompetitors
            ? item.matched_competitors.join(", ")
            : "—",
          matchedContext: hasContexts ? item.matched_contexts.join(", ") : "—",
          preFilterStatus: isPass ? "Pass" : "Fail",
          failureReason: isPass
            ? null
            : "Filtered out before AI vulnerability processing.",
          rawUrl: item.url || "#",
          contentSnippet: item.content || "No snippet available.",
          rawJson: item,
        };
      });

      setArticles(normalizedData);
    } catch (err) {
      console.error("Error fetching raw articles:", err);
      setError("Failed to load raw pipeline data from backend.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPipelineArticles();
  }, []);

  // --------------------------------------------------------------------------
  // TRIGGER MANUAL FETCH CYCLE
  // --------------------------------------------------------------------------
  const handleTriggerFetchCycle = async () => {
    setIsFetching(true);
    try {
      await fetch("/api/articles/trigger-fetch", { method: "POST" });
      await fetchPipelineArticles();
    } catch (err) {
      console.error("Failed to trigger fetch cycle:", err);
    } finally {
      setIsFetching(false);
    }
  };

  // Dynamic Sources List
  const availableSources = useMemo(() => {
    const sourcesSet = new Set(articles.map((item) => item.source));
    return ["All Sources", ...Array.from(sourcesSet)];
  }, [articles]);

  // --------------------------------------------------------------------------
  // FILTERING & PAGINATION LOGIC
  // --------------------------------------------------------------------------
  const filteredArticles = useMemo(() => {
    return articles.filter((item) => {
      if (selectedSource !== "All Sources" && item.source !== selectedSource)
        return false;
      if (selectedStatus !== "All" && item.preFilterStatus !== selectedStatus)
        return false;
      if (searchQuery.trim() !== "") {
        const query = searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(query);
        const matchesEntity = item.matchedEntity.toLowerCase().includes(query);
        const matchesContext = item.matchedContext
          .toLowerCase()
          .includes(query);
        const matchesSource = item.source.toLowerCase().includes(query);
        if (
          !matchesTitle &&
          !matchesEntity &&
          !matchesContext &&
          !matchesSource
        )
          return false;
      }
      return true;
    });
  }, [articles, selectedSource, selectedStatus, searchQuery]);

  // --------------------------------------------------------------------------
  // DYNAMICALLY DERIVED METRICS
  // --------------------------------------------------------------------------
  const totalArticlesCount = articles.length;
  const passCount = useMemo(
    () => articles.filter((a) => a.preFilterStatus === "Pass").length,
    [articles]
  );
  const passRate = useMemo(
    () =>
      totalArticlesCount > 0
        ? Math.round((passCount / totalArticlesCount) * 100)
        : 0,
    [passCount, totalArticlesCount]
  );

  // Pagination Math
  const totalPages = Math.ceil(filteredArticles.length / itemsPerPage) || 1;
  const paginatedArticles = useMemo(() => {
    const startIdx = (currentPage - 1) * itemsPerPage;
    return filteredArticles.slice(startIdx, startIdx + itemsPerPage);
  }, [filteredArticles, currentPage, itemsPerPage]);

  const handleRowClick = (url) => {
    if (url && url !== "#") {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="p-8 space-y-6 bg-[var(--background)] min-h-screen text-[var(--foreground)]">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Raw Data Pipeline Monitor
          </h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            Transparency into articles fetched before they reach the AI pipeline
          </p>
        </div>
      </div>

      {/* KPI STAT CARDS SECTION */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            ARTICLES FETCHED
          </span>
          <div className="text-3xl font-bold">{totalArticlesCount}</div>
          <div>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">
              ↑ Google News + TechCrunch POS
            </span>
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            PRE-FILTER PASS RATE
          </span>
          <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {passRate}%
          </div>
          <div className="text-xs text-[var(--muted-foreground)]">
            {passCount} of {totalArticlesCount} passed
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            SENT TO VULNERABILITY PIPELINE
          </span>
          <div className="text-3xl font-bold">{passCount}</div>
          <div className="text-xs text-[var(--muted-foreground)]">
            processed by vulnerability classifier
          </div>
        </div>

        <div className="p-5 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-2">
          <span className="text-[11px] font-bold tracking-wider uppercase text-[var(--muted-foreground)]">
            LAST FETCH CYCLE
          </span>
          <div className="text-3xl font-bold">Active</div>
          <div className="text-xs text-[var(--muted-foreground)]">
            runs every 30 min
          </div>
        </div>
      </div>

      {/* MAIN MONITOR TABLE CONTAINER */}
      <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h2 className="text-base font-bold text-[var(--foreground)]">
            Raw RSS Data Pipeline Monitor
          </h2>
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

          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-[var(--muted-foreground)] uppercase">
              Filter Status
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
          <div className="py-12 text-center text-sm text-[var(--muted-foreground)] flex items-center justify-center gap-2">
            <Icon icon="lucide:loader-2" className="w-4 h-4 animate-spin" />
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
                  <th className="py-3 px-4">TITLE</th>
                  <th className="py-3 px-4">SOURCE</th>
                  <th className="py-3 px-4">PUBLISHED</th>
                  <th className="py-3 px-4">MATCHED RIVALS</th>
                  <th className="py-3 px-4">MATCHED CONTEXT</th>
                  <th className="py-3 px-4 text-right">FILTER STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)] text-xs">
                {paginatedArticles.map((row) => {
                  const isPass = row.preFilterStatus === "Pass";

                  return (
                    <tr
                      key={row.id}
                      onClick={() => handleRowClick(row.rawUrl)}
                      className="group hover:bg-[var(--muted)]/40 transition-colors cursor-pointer"
                    >
                      <td className="py-4 px-4 font-semibold text-[var(--foreground)] max-w-xs md:max-w-md">
                        <div
                          className="truncate flex items-center gap-1.5"
                          title={row.title}
                        >
                          <span>{row.title}</span>
                          <Icon
                            icon="lucide:external-link"
                            className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-[var(--muted-foreground)] shrink-0"
                          />
                        </div>
                      </td>

                      <td className="py-4 px-4 text-[var(--muted-foreground)] font-medium">
                        {row.source}
                      </td>

                      <td className="py-4 px-4 text-[var(--muted-foreground)] whitespace-nowrap">
                        {row.published}
                      </td>

                      <td className="py-4 px-4 font-medium text-[var(--foreground)]">
                        {row.matchedEntity}
                      </td>

                      <td className="py-4 px-4 text-[var(--muted-foreground)]">
                        {row.matchedContext}
                      </td>

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