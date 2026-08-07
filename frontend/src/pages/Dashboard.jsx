/* Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement. */

import { useState, useMemo, useEffect, useCallback } from "react";
import { Icon } from "@iconify/react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler,
} from "chart.js";
import { Doughnut, Bar, Line } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler,
);

const INTENT_CATEGORIES = [
  "Technical Issues",
  "Billing & Payments",
  "Inquiry & Feedback",
  "Security Risks",
];

const PRIORITY_CATEGORIES = ["High", "Medium", "Low"];

function getRelativeTime(dateStr) {
  if (!dateStr) return "N/A";
  const diffMs = new Date() - new Date(dateStr);
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

function formatSourceName(sourceName) {
  if (!sourceName) return "r/unknown";
  const cleaned = sourceName.replace(/^(reddit_|r_)/i, "");
  return `r/${cleaned}`;
}

export default function Dashboard() {
  // Data States
  const [sources, setSources] = useState([]);
  const [posts, setPosts] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    positive: 0,
    negative: 0,
    neutral: 0,
    positivePct: 0,
    negativePct: 0,
    neutralPct: 0,
  });
  const [intentCounts, setIntentCounts] = useState({});
  const [timelineData, setTimelineData] = useState({
    labels: [],
    positive: [],
    negative: [],
    neutral: [],
  });

  // UI & Filter States
  const [filters, setFilters] = useState({
    subreddit: "all",
    sentiment: "all",
    intent: "all",
    priority: "all",
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const itemsPerPage = 5;

  // Add Source Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sourceFormData, setSourceFormData] = useState({
    name: "",
    url: "",
    is_active: true,
    fetch_interval_minutes: 30,
    last_fetched_at: "",
  });
  const [isSubmittingSource, setIsSubmittingSource] = useState(false);
  const [sourceError, setSourceError] = useState("");

  // React State for active HTML theme class
  const [theme, setTheme] = useState(() =>
    document.documentElement.classList.contains("dark") ? "dark" : "light",
  );

  // Listen for dark/light class changes on <html>
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const isDark = document.documentElement.classList.contains("dark");
      setTheme(isDark ? "dark" : "light");
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  // 1. Fetch Active Sources for Subreddit Dropdown (/api/sources)
  const fetchSources = useCallback(async () => {
    try {
      const res = await fetch("/api/sources");
      if (!res.ok) throw new Error("Failed to fetch sources");
      const data = await res.json();
      setSources(data.sources || []);
    } catch (err) {
      console.error("Error loading sources:", err);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // 2. Fetch KPI Statistics (/api/stats)
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const params = new URLSearchParams();
        if (filters.subreddit !== "all")
          params.append("source", filters.subreddit);

        const res = await fetch(`/api/stats?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch stats");
        const data = await res.json();

        setStats({
          total: data.total ?? 0,
          positive: data.positive ?? 0,
          negative: data.negative ?? 0,
          neutral: data.neutral ?? 0,
          positivePct: data.positivePct ?? 0,
          negativePct: data.negativePct ?? 0,
          neutralPct: data.neutralPct ?? 0,
        });
      } catch (err) {
        console.error("Error loading stats:", err);
      }
    };
    fetchStats();
  }, [filters.subreddit]);

  // 3. Fetch Intent Breakdown Chart Data (/api/stats/intents)
  useEffect(() => {
    const fetchIntents = async () => {
      try {
        const params = new URLSearchParams();
        if (filters.subreddit !== "all")
          params.append("source", filters.subreddit);
        if (filters.sentiment !== "all")
          params.append("sentiment", filters.sentiment);

        const res = await fetch(`/api/stats/intents?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch intents");
        const data = await res.json();
        setIntentCounts(data.breakdown || {});
      } catch (err) {
        console.error("Error loading intent breakdown:", err);
      }
    };
    fetchIntents();
  }, [filters.subreddit, filters.sentiment]);

  // 4. Fetch Timeline Trend Data (/api/stats/timeline)
  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const params = new URLSearchParams({ days: "7" });
        if (filters.subreddit !== "all")
          params.append("source", filters.subreddit);

        const res = await fetch(`/api/stats/timeline?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch timeline");
        const data = await res.json();

        if (data.days && Array.isArray(data.days)) {
          const labels = data.days.map((item) => {
            const d = new Date(item.date);
            return isNaN(d)
              ? item.date
              : d.toLocaleDateString("en-US", { weekday: "short" });
          });
          const positive = data.days.map((item) => item.positive ?? 0);
          const negative = data.days.map((item) => item.negative ?? 0);
          const neutral = data.days.map((item) => item.neutral ?? 0);

          setTimelineData({ labels, positive, negative, neutral });
        }
      } catch (err) {
        console.error("Error loading timeline:", err);
      }
    };
    fetchTimeline();
  }, [filters.subreddit]);

  // 5. Fetch Paginated Posts Table Data (/api/posts)
  useEffect(() => {
    const fetchPosts = async () => {
      setIsLoading(true);
      try {
        const params = new URLSearchParams({
          page: currentPage.toString(),
          limit: itemsPerPage.toString(),
        });

        if (filters.subreddit !== "all")
          params.append("source", filters.subreddit);
        if (filters.sentiment !== "all")
          params.append("sentiment", filters.sentiment);
        if (filters.priority !== "all")
          params.append("priority", filters.priority);
        if (filters.intent !== "all")
          params.append("intent", filters.intent);

        const res = await fetch(`/api/posts?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch posts");
        const data = await res.json();

        setPosts(data.items || []);
        setTotalPages(Math.ceil((data.total || 0) / itemsPerPage) || 1);
      } catch (err) {
        console.error("Error loading posts:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, [currentPage, filters]);

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  };

  const handleSourceInputChange = (field, value) => {
    setSourceFormData((prev) => ({ ...prev, [field]: value }));
  };

  const resetModalForm = () => {
    setSourceFormData({
      name: "",
      url: "",
      is_active: true,
      fetch_interval_minutes: 30,
      last_fetched_at: "",
    });
    setSourceError("");
    setIsSubmittingSource(false);
  };

  const handleAddSource = async (e) => {
    if (e) e.preventDefault();
    setSourceError("");

    if (!sourceFormData.name.trim() || !sourceFormData.url.trim()) {
      setSourceError("Name and URL are required fields.");
      return;
    }

    setIsSubmittingSource(true);

    try {
      const payload = {
        name: sourceFormData.name.trim(),
        url: sourceFormData.url.trim(),
        is_active: sourceFormData.is_active,
        fetch_interval_minutes: Number(sourceFormData.fetch_interval_minutes) || 30,
        last_fetched_at: sourceFormData.last_fetched_at
          ? new Date(sourceFormData.last_fetched_at).toISOString()
          : null,
      };

      const res = await fetch("/api/sources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to add new source.");
      }

      await fetchSources(); // Refresh sources list in dropdown
      resetModalForm();
      setIsModalOpen(false);
    } catch (err) {
      setSourceError(err.message || "An unexpected error occurred.");
    } finally {
      setIsSubmittingSource(false);
    }
  };

  const getVar = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  // Sentiment Doughnut Chart Config
  const sentimentChartData = useMemo(() => {
    const cardColor =
      getVar("--card") || (theme === "dark" ? "#131c2e" : "#ffffff");

    return {
      labels: ["Positive", "Negative", "Neutral"],
      datasets: [
        {
          data: [stats.positive, stats.negative, stats.neutral],
          backgroundColor: [
            getVar("--accent") || "#10b981",
            getVar("--negative-accent") || "#f43f5e",
            getVar("--muted-foreground") || "#64748b",
          ],
          borderWidth: 2,
          borderColor: cardColor,
          borderRadius: 5,
        },
      ],
    };
  }, [stats, theme]);

  // Intent Bar Chart Config
  const intentChartData = useMemo(() => {
    const labels =
      Object.keys(intentCounts).length > 0
        ? Object.keys(intentCounts)
        : INTENT_CATEGORIES;
    const dataValues =
      Object.keys(intentCounts).length > 0
        ? Object.values(intentCounts)
        : [0, 0, 0, 0];

    return {
      labels,
      datasets: [
        {
          label: "Post Count",
          data: dataValues,
          backgroundColor: getVar("--accent") || "#10b981",
          borderRadius: 6,
        },
      ],
    };
  }, [intentCounts, theme]);

  // Timeline Line Chart Config
  const timelineChartData = useMemo(() => {
    return {
      labels: timelineData.labels.length > 0 ? timelineData.labels : ["Mon"],
      datasets: [
        {
          label: "Positive",
          data: timelineData.positive.length > 0 ? timelineData.positive : [0],
          borderColor: getVar("--accent") || "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.12)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Negative",
          data: timelineData.negative.length > 0 ? timelineData.negative : [0],
          borderColor: getVar("--negative-accent") || "#f43f5e",
          backgroundColor: "rgba(244, 63, 94, 0.12)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Neutral",
          data: timelineData.neutral.length > 0 ? timelineData.neutral : [0],
          borderColor: getVar("--muted-foreground") || "#64748b",
          backgroundColor: "rgba(100, 116, 139, 0.12)",
          tension: 0.4,
          fill: true,
        },
      ],
    };
  }, [timelineData, theme]);

  return (
    <div className="p-4 md:p-6 lg:p-8 space-y-6 md:space-y-8 bg-[var(--background)] min-h-screen text-[var(--foreground)] transition-colors duration-200 overflow-x-hidden w-full max-w-full">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        {/* Total Posts */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Total Posts Analyzed
          </div>
          <div className="text-2xl md:text-3xl font-bold tracking-tight text-[var(--foreground)]">
            {stats.total.toLocaleString()}
          </div>
        </div>

        {/* Positive Sentiment */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Positive Sentiment
          </div>
          <div className="text-2xl md:text-3xl font-bold tracking-tight text-[var(--positive-text)]">
            {stats.positivePct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.positive} posts
          </div>
        </div>

        {/* Negative Sentiment */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Negative Sentiment
          </div>
          <div className="text-2xl md:text-3xl font-bold tracking-tight text-[var(--negative-text)]">
            {stats.negativePct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.negative} posts
          </div>
        </div>

        {/* Neutral Sentiment */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Neutral Sentiment
          </div>
          <div className="text-2xl md:text-3xl font-bold tracking-tight text-[var(--neutral-text)]">
            {stats.neutralPct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.neutral} posts
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Sentiment Distribution */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4">
          <h3 className="text-base font-bold text-[var(--foreground)]">
            Sentiment Distribution
          </h3>
          <div className="h-64 md:h-72 relative">
            <Doughnut
              key={theme}
              redraw={true}
              data={sentimentChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: "bottom",
                    labels: { color: getVar("--muted-foreground") },
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Intent Breakdown */}
        <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4">
          <h3 className="text-base font-bold text-[var(--foreground)]">
            Intent Breakdown
          </h3>
          <div className="h-64 md:h-72 relative">
            <Bar
              data={intentChartData}
              options={{
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: {
                    ticks: { color: getVar("--muted-foreground") },
                    grid: {
                      color: getVar("--chart-grid") || "rgba(0, 0, 0, 0.05)",
                    },
                  },
                  y: {
                    ticks: { color: getVar("--muted-foreground") },
                    grid: { display: false },
                  },
                },
              }}
            />
          </div>
        </div>
      </div>

      {/* Sentiment Timeline Chart */}
      <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4">
        <h3 className="text-base font-bold text-[var(--foreground)]">
          Sentiment Timeline (Last 7 Days)
        </h3>
        <div className="h-64 md:h-80 relative">
          <Line
            data={timelineChartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: "top",
                  labels: { color: getVar("--muted-foreground") },
                },
              },
              scales: {
                x: {
                  ticks: { color: getVar("--muted-foreground") },
                  grid: {
                    color: getVar("--chart-grid") || "rgba(0, 0, 0, 0.05)",
                  },
                },
                y: {
                  ticks: { color: getVar("--muted-foreground") },
                  grid: {
                    color: getVar("--chart-grid") || "rgba(0, 0, 0, 0.05)",
                  },
                },
              },
            }}
          />
        </div>
      </div>

      {/* Filter and Source Management Section */}
      <div className="p-4 md:p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4 md:space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-[var(--foreground)]">
            Posts Feed & Filters
          </h2>
          <button
            onClick={() => {
              resetModalForm();
              setIsModalOpen(true);
            }}
            className="px-4 py-2 bg-[var(--accent)] text-[var(--primary-foreground)] font-medium rounded-lg text-sm flex items-center gap-2 transition-transform active:scale-95 cursor-pointer hover:opacity-90 whitespace-nowrap"
          >
            <Icon icon="lucide:plus" className="w-4 h-4" />
            <span>Add Source</span>
          </button>
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {/* Subreddit / Source Filter */}
          <div>
            <label className="block text-xs font-semibold text-[var(--muted-foreground)] mb-2">
              Filter by Subreddit
            </label>
            <select
              value={filters.subreddit}
              onChange={(e) => handleFilterChange("subreddit", e.target.value)}
              className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="all">All Sources</option>
              {sources.map((src) => (
                <option key={src} value={src}>
                  {formatSourceName(src)}
                </option>
              ))}
            </select>
          </div>

          {/* Sentiment Filter */}
          <div>
            <label className="block text-xs font-semibold text-[var(--muted-foreground)] mb-2">
              Filter by Sentiment
            </label>
            <select
              value={filters.sentiment}
              onChange={(e) => handleFilterChange("sentiment", e.target.value)}
              className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>

          {/* Intent Filter */}
          <div>
            <label className="block text-xs font-semibold text-[var(--muted-foreground)] mb-2">
              Filter by Intent
            </label>
            <select
              value={filters.intent}
              onChange={(e) => handleFilterChange("intent", e.target.value)}
              className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="all">All Intents</option>
              {INTENT_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="block text-xs font-semibold text-[var(--muted-foreground)] mb-2">
              Filter by Priority
            </label>
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange("priority", e.target.value)}
              className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="all">All Priorities</option>
              {PRIORITY_CATEGORIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Posts Table - Fixed overflow */}
        <div className="overflow-x-auto border border-[var(--border)] rounded-lg">
          <div className="min-w-[768px]">
            <table className="w-full text-left border-collapse">
              <thead className="bg-[var(--muted)] border-b border-[var(--border)] text-xs uppercase font-semibold text-[var(--muted-foreground)]">
                <tr>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">Source</th>
                  <th className="p-3.5">Author</th>
                  <th className="p-3.5">Content</th>
                  <th className="p-3.5">Sentiment</th>
                  <th className="p-3.5">Intent</th>
                  <th className="p-3.5">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)] text-sm">
                {isLoading ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="p-6 text-center text-[var(--muted-foreground)]"
                    >
                      Loading posts...
                    </td>
                  </tr>
                ) : posts.length > 0 ? (
                  posts.map((post) => (
                    <tr
                      key={post.id}
                      onClick={() =>
                        post.url &&
                        window.open(post.url, "_blank", "noopener,noreferrer")
                      }
                      className="hover:bg-[var(--muted)]/50 transition-colors cursor-pointer"
                    >
                      <td className="p-3.5 text-[var(--muted-foreground)] whitespace-nowrap">
                        {getRelativeTime(post.fetched_at)}
                      </td>
                      <td className="p-3.5 font-semibold text-[var(--foreground)] whitespace-nowrap">
                        {formatSourceName(post.source_name)}
                      </td>
                      <td className="p-3.5 text-[var(--foreground)] whitespace-nowrap">
                        {post.author || "Anonymous"}
                      </td>
                      <td className="p-3.5 text-[var(--muted-foreground)] max-w-xs truncate">
                        {post.content && post.content.trim() !== ""
                          ? post.content
                          : post.title}
                      </td>
                      <td className="p-3.5 whitespace-nowrap">
                        <span
                          className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${
                            post.sentiment === "positive"
                              ? "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                              : post.sentiment === "negative"
                                ? "bg-[var(--negative-bg)] text-[var(--negative-text)]"
                                : "bg-[var(--neutral-bg)] text-[var(--neutral-text)]"
                          }`}
                        >
                          {post.sentiment || "neutral"}
                        </span>
                      </td>
                      <td className="p-3.5 whitespace-nowrap">
                        <span className="inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--neutral-bg)] text-[var(--neutral-text)]">
                          {post.intent_category || "General"}
                        </span>
                      </td>
                      <td className="p-3.5 whitespace-nowrap">
                        <span
                          className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold ${
                            post.priority === "High"
                              ? "bg-[var(--negative-bg)] text-[var(--negative-text)]"
                              : post.priority === "Medium"
                                ? "bg-[var(--medium-bg,#fef3c7)] text-[var(--medium-text,#b45309)]"
                                : "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                          }`}
                        >
                          {post.priority || "Low"}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={7}
                      className="p-6 text-center text-[var(--muted-foreground)]"
                    >
                      No posts matched the current filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-center gap-2 pt-2 flex-wrap">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[var(--muted)] transition-colors cursor-pointer"
          >
            <Icon icon="lucide:chevron-left" className="w-4 h-4" />
          </button>

          {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={`w-8 h-8 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                currentPage === page
                  ? "bg-[var(--accent)] border-[var(--accent)] text-[var(--primary-foreground)]"
                  : "border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] hover:bg-[var(--muted)]"
              }`}
            >
              {page}
            </button>
          ))}

          {totalPages > 7 && (
            <>
              <span className="text-[var(--muted-foreground)]">...</span>
              <button
                onClick={() => setCurrentPage(totalPages)}
                className={`w-8 h-8 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                  currentPage === totalPages
                    ? "bg-[var(--accent)] border-[var(--accent)] text-[var(--primary-foreground)]"
                    : "border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] hover:bg-[var(--muted)]"
                }`}
              >
                {totalPages}
              </button>
            </>
          )}

          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[var(--muted)] transition-colors cursor-pointer"
          >
            <Icon icon="lucide:chevron-right" className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Modal for Adding Source */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="relative w-full max-w-md bg-[var(--card)] border border-[var(--border)] rounded-xl p-6 shadow-2xl space-y-5">
            <button
              onClick={() => {
                resetModalForm();
                setIsModalOpen(false);
              }}
              className="absolute top-4 right-4 text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xl cursor-pointer"
            >
              &times;
            </button>

            <h3 className="text-lg font-bold text-[var(--foreground)]">
              Add New Source
            </h3>

            {sourceError && (
              <div className="p-3 text-xs font-semibold rounded-lg bg-[var(--negative-bg)] text-[var(--negative-text)] border border-[var(--negative-accent)]/20">
                {sourceError}
              </div>
            )}

            <form onSubmit={handleAddSource} className="space-y-4">
              {/* Name (Required) */}
              <div>
                <label className="block text-xs font-semibold text-[var(--foreground)] mb-1">
                  Source Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g., technology or vuejs"
                  value={sourceFormData.name}
                  onChange={(e) =>
                    handleSourceInputChange("name", e.target.value)
                  }
                  required
                  className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
                />
              </div>

              {/* URL (Required) */}
              <div>
                <label className="block text-xs font-semibold text-[var(--foreground)] mb-1">
                  Feed URL <span className="text-red-500">*</span>
                </label>
                <input
                  type="url"
                  placeholder="https://www.reddit.com/r/technology/.rss"
                  value={sourceFormData.url}
                  onChange={(e) =>
                    handleSourceInputChange("url", e.target.value)
                  }
                  required
                  className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
                />
              </div>

              {/* Fetch Interval Minutes (Optional) */}
              <div>
                <label className="block text-xs font-semibold text-[var(--foreground)] mb-1">
                  Fetch Interval (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  placeholder="30"
                  value={sourceFormData.fetch_interval_minutes}
                  onChange={(e) =>
                    handleSourceInputChange(
                      "fetch_interval_minutes",
                      e.target.value
                    )
                  }
                  className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
                />
              </div>

              {/* Last Fetched At (Optional) */}
              <div>
                <label className="block text-xs font-semibold text-[var(--foreground)] mb-1">
                  Initial Last Fetched Timestamp (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={sourceFormData.last_fetched_at}
                  onChange={(e) =>
                    handleSourceInputChange("last_fetched_at", e.target.value)
                  }
                  className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
                />
              </div>

              {/* Active Toggle (Optional) */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={sourceFormData.is_active}
                  onChange={(e) =>
                    handleSourceInputChange("is_active", e.target.checked)
                  }
                  className="w-4 h-4 rounded border-[var(--border)] text-[var(--accent)] focus:ring-[var(--accent)] cursor-pointer"
                />
                <label
                  htmlFor="is_active"
                  className="text-xs font-semibold text-[var(--foreground)] cursor-pointer"
                >
                  Enable source fetching immediately
                </label>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => {
                    resetModalForm();
                    setIsModalOpen(false);
                  }}
                  className="flex-1 py-2 px-4 rounded-lg border border-[var(--border)] bg-[var(--muted)] text-[var(--foreground)] text-sm font-semibold hover:opacity-90 transition-opacity cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingSource}
                  className="flex-1 py-2 px-4 rounded-lg bg-[var(--accent)] text-[var(--primary-foreground)] text-sm font-semibold hover:opacity-90 transition-opacity cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isSubmittingSource ? (
                    <span>Saving...</span>
                  ) : (
                    <>
                      <Icon icon="lucide:plus" className="w-4 h-4" />
                      <span>Add Source</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}