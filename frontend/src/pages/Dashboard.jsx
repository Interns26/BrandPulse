import { useState, useMemo, useEffect } from "react";
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

const INITIAL_POSTS = [
  {
    id: 1,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    source: "reactjs",
    author: "CodeMaster92",
    content:
      "Just encountered an API timeout issue when fetching data from the platform. Has anyone else experienced this? Really impacting production.",
    sentiment: "negative",
    intent: "Technical Issues",
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    source: "saas",
    author: "StartupGuy",
    content:
      "The new dashboard update is absolutely fantastic! The UX improvements are really noticeable. Great work by the team!",
    sentiment: "positive",
    intent: "Inquiry & Feedback",
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    source: "technology",
    author: "SecurityNerd",
    content:
      "Security advisory: Found potential vulnerability in version 2.1. Recommend immediate patching before deploying to production.",
    sentiment: "neutral",
    intent: "Security Risks",
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
    source: "webdev",
    author: "FullStackDev",
    content:
      "Can anyone clarify the pricing tiers? The documentation seems outdated and I'm confused about which plan fits our needs.",
    sentiment: "neutral",
    intent: "Billing & Payments",
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 10 * 60 * 60 * 1000),
    source: "reactjs",
    author: "ProDeveloper",
    content:
      "Switched to your platform last month and the performance improvements are remarkable. Highly recommend to anyone on the fence.",
    sentiment: "positive",
    intent: "Inquiry & Feedback",
  },
  {
    id: 6,
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
    source: "saas",
    author: "DataAnalyst",
    content:
      "The API documentation could be much better. Spent 3 hours trying to integrate a simple endpoint. Very frustrating experience.",
    sentiment: "negative",
    intent: "Technical Issues",
  },
  {
    id: 7,
    timestamp: new Date(Date.now() - 14 * 60 * 60 * 1000),
    source: "technology",
    author: "TechWriter",
    content:
      "Interesting implementation of OAuth 2.0 in their latest release. Seems well thought out and follows industry standards.",
    sentiment: "positive",
    intent: "Inquiry & Feedback",
  },
  {
    id: 8,
    timestamp: new Date(Date.now() - 16 * 60 * 60 * 1000),
    source: "webdev",
    author: "NewUser",
    content:
      "Just noticed the billing page shows incorrect charges for last month. This needs to be reviewed urgently.",
    sentiment: "negative",
    intent: "Billing & Payments",
  },
  {
    id: 9,
    timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000),
    source: "reactjs",
    author: "OpenSourceFan",
    content:
      "Love that they support open standards. Makes integration with our existing toolchain seamless.",
    sentiment: "positive",
    intent: "Inquiry & Feedback",
  },
  {
    id: 10,
    timestamp: new Date(Date.now() - 20 * 60 * 60 * 1000),
    source: "saas",
    author: "QAEngineer",
    content:
      "Found a critical security issue in the authentication flow. Reported through their responsible disclosure program.",
    sentiment: "neutral",
    intent: "Security Risks",
  },
];

function getRelativeTime(date) {
  const diffMs = new Date() - new Date(date);
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Date(date).toLocaleDateString();
}

export default function Dashboard() {
  const [posts, setPosts] = useState(INITIAL_POSTS);
  const [filters, setFilters] = useState({
    subreddit: "all",
    sentiment: "all",
    intent: "all",
  });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSubreddit, setNewSubreddit] = useState("");

  // 1. React State to track the active HTML theme class
  const [theme, setTheme] = useState(() =>
    document.documentElement.classList.contains("dark") ? "dark" : "light",
  );

  // 2. Listen for class changes on <html> (document.documentElement)
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

  const filteredPosts = useMemo(() => {
    return posts.filter((post) => {
      const subredditMatch =
        filters.subreddit === "all" || post.source === filters.subreddit;
      const sentimentMatch =
        filters.sentiment === "all" || post.sentiment === filters.sentiment;
      const intentMatch =
        filters.intent === "all" || post.intent === filters.intent;
      return subredditMatch && sentimentMatch && intentMatch;
    });
  }, [posts, filters]);

  const stats = useMemo(() => {
    const total = filteredPosts.length;
    const positive = filteredPosts.filter(
      (p) => p.sentiment === "positive",
    ).length;
    const negative = filteredPosts.filter(
      (p) => p.sentiment === "negative",
    ).length;
    const neutral = filteredPosts.filter(
      (p) => p.sentiment === "neutral",
    ).length;
    const baseTotal = total || 1;

    return {
      total,
      positive,
      negative,
      neutral,
      positivePct: Math.round((positive / baseTotal) * 100),
      negativePct: Math.round((negative / baseTotal) * 100),
      neutralPct: Math.round((neutral / baseTotal) * 100),
    };
  }, [filteredPosts]);

  const totalPages = Math.ceil(filteredPosts.length / itemsPerPage) || 1;
  const paginatedPosts = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredPosts.slice(start, start + itemsPerPage);
  }, [filteredPosts, currentPage]);

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  };

  const handleAddSource = () => {
    if (!newSubreddit.trim()) return;
    const sourceKey = newSubreddit.trim().toLowerCase().replace(/^r\//, "");

    const newPosts = [
      {
        id: Date.now(),
        timestamp: new Date(),
        source: sourceKey,
        author: `User${Math.floor(Math.random() * 9000 + 1000)}`,
        content: `Sample post from r/${sourceKey}. Dynamic feed addition active.`,
        sentiment: "positive",
        intent: "Inquiry & Feedback",
      },
    ];

    setPosts((prev) => [...prev, ...newPosts]);
    setNewSubreddit("");
    setIsModalOpen(false);
  };

  // Dynamic Theme Palette from CSS Variables
  const getVar = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

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
          borderRadius: 5
        },
      ],
    };
  }, [stats, theme]);

  const intentCounts = useMemo(() => {
    const counts = {};
    INTENT_CATEGORIES.forEach((cat) => {
      counts[cat] = filteredPosts.filter((p) => p.intent === cat).length;
    });
    return counts;
  }, [filteredPosts]);

  const intentChartData = {
    labels: Object.keys(intentCounts),
    datasets: [
      {
        label: "Post Count",
        data: Object.values(intentCounts),
        backgroundColor: getVar("--accent") || "#10b981",
        borderRadius: 6,
      },
    ],
  };

  const timelineChartData = {
    labels: ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"],
    datasets: [
      {
        label: "Positive",
        data: [220, 160, 248, 206, 222, 237, 226],
        borderColor: getVar("--accent") || "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.12)",
        tension: 0.4,
        fill: true,
      },
      {
        label: "Negative",
        data: [134, 90, 153, 148, 112, 157, 81],
        borderColor: getVar("--negative-accent") || "#f43f5e",
        backgroundColor: "rgba(244, 63, 94, 0.12)",
        tension: 0.4,
        fill: true,
      },
      {
        label: "Neutral",
        data: [177, 188, 112, 125, 157, 114, 148],
        borderColor: getVar("--muted-foreground") || "#64748b",
        backgroundColor: "rgba(100, 116, 139, 0.12)",
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div className="p-8 space-y-8 bg-[var(--background)] min-h-screen text-[var(--foreground)] transition-colors duration-200">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Posts */}
        <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Total Posts Analyzed
          </div>
          <div className="text-3xl font-bold tracking-tight text-[var(--foreground)]">
            {stats.total.toLocaleString()}
          </div>
          <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-[var(--positive-bg)] text-[var(--positive-text)] w-fit">
            <Icon icon="lucide:arrow-up" className="w-3 h-3" />
            <span>12.5% vs last week</span>
          </div>
        </div>

        {/* Positive Sentiment */}
        <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Positive Sentiment
          </div>
          <div className="text-3xl font-bold tracking-tight text-[var(--positive-text)]">
            {stats.positivePct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.positive} posts
          </div>
        </div>

        {/* Negative Sentiment */}
        <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Negative Sentiment
          </div>
          <div className="text-3xl font-bold tracking-tight text-[var(--negative-text)]">
            {stats.negativePct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.negative} posts
          </div>
        </div>

        {/* Neutral Sentiment */}
        <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs flex flex-col justify-between space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
            Neutral Sentiment
          </div>
          <div className="text-3xl font-bold tracking-tight text-[var(--neutral-text)]">
            {stats.neutralPct}%
          </div>
          <div className="text-sm text-[var(--muted-foreground)]">
            {stats.neutral} posts
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="p-6 rounded-xl border border-border bg-card shadow-xs space-y-4">
          <h3 className="text-base font-bold text-foreground">
            Sentiment Distribution
          </h3>
          <div className="h-72 relative">
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
        <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4">
          <h3 className="text-base font-bold text-[var(--foreground)]">
            Intent Breakdown
          </h3>
          <div className="h-72 relative">
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
      <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-4">
        <h3 className="text-base font-bold text-[var(--foreground)]">
          Sentiment Timeline (Last 7 Days)
        </h3>
        <div className="h-80 relative">
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
      <div className="p-6 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-xs space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[var(--foreground)]">
            Posts Feed & Filters
          </h2>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 bg-[var(--accent)] text-[var(--primary-foreground)] font-medium rounded-lg text-sm flex items-center gap-2 transition-transform active:scale-95 cursor-pointer hover:opacity-90"
          >
            <Icon icon="lucide:plus" className="w-4 h-4" />
            <span>Add Source</span>
          </button>
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              <option value="reactjs">r/reactjs</option>
              <option value="saas">r/saas</option>
              <option value="technology">r/technology</option>
              <option value="webdev">r/webdev</option>
            </select>
          </div>

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
        </div>

        {/* Posts Table */}
        <div className="overflow-x-auto border border-[var(--border)] rounded-lg">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[var(--muted)] border-b border-[var(--border)] text-xs uppercase font-semibold text-[var(--muted-foreground)]">
              <tr>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">Source</th>
                <th className="p-3.5">Author</th>
                <th className="p-3.5">Content</th>
                <th className="p-3.5">Sentiment</th>
                <th className="p-3.5">Intent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)] text-sm">
              {paginatedPosts.length > 0 ? (
                paginatedPosts.map((post) => (
                  <tr
                    key={post.id}
                    className="hover:bg-[var(--muted)]/50 transition-colors"
                  >
                    <td className="p-3.5 text-[var(--muted-foreground)]">
                      {getRelativeTime(post.timestamp)}
                    </td>
                    <td className="p-3.5 font-semibold text-[var(--foreground)]">
                      r/{post.source}
                    </td>
                    <td className="p-3.5 text-[var(--foreground)]">
                      {post.author}
                    </td>
                    <td className="p-3.5 text-[var(--muted-foreground)] max-w-xs truncate">
                      {post.content}
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${
                          post.sentiment === "positive"
                            ? "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                            : post.sentiment === "negative"
                              ? "bg-[var(--negative-bg)] text-[var(--negative-text)]"
                              : "bg-[var(--neutral-bg)] text-[var(--neutral-text)]"
                        }`}
                      >
                        {post.sentiment}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className="inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--neutral-bg)] text-[var(--neutral-text)]">
                        {post.intent}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={6}
                    className="p-6 text-center text-[var(--muted-foreground)]"
                  >
                    No posts matched the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[var(--muted)] transition-colors cursor-pointer"
          >
            <Icon icon="lucide:chevron-left" className="w-4 h-4" />
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
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
          <div className="relative w-full max-w-md bg-[var(--card)] border border-[var(--border)] rounded-xl p-6 shadow-2xl space-y-6">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xl cursor-pointer"
            >
              &times;
            </button>
            <h3 className="text-lg font-bold text-[var(--foreground)]">
              Add New Source
            </h3>
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-[var(--foreground)]">
                Subreddit Name
              </label>
              <input
                type="text"
                placeholder="e.g., vuejs, python, learnprogramming"
                value={newSubreddit}
                onChange={(e) => setNewSubreddit(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddSource()}
                className="w-full p-2.5 rounded-lg border border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)] text-sm focus:outline-none focus:border-[var(--accent)]"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="flex-1 py-2 px-4 rounded-lg border border-[var(--border)] bg-[var(--muted)] text-[var(--foreground)] text-sm font-semibold hover:opacity-90 transition-opacity cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAddSource}
                className="flex-1 py-2 px-4 rounded-lg bg-[var(--accent)] text-[var(--primary-foreground)] text-sm font-semibold hover:opacity-90 transition-opacity cursor-pointer flex items-center justify-center gap-2"
              >
                <Icon icon="lucide:plus" className="w-4 h-4" />
                <span>Add Source</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
