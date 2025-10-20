"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, RefreshCw, Search, GitBranch, Clock, Star } from "lucide-react";

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string;
  language: string;
  stargazers_count: number;
  updated_at: string;
  html_url: string;
  private: boolean;
}

interface User {
  id: number;
  login: string;
  name: string;
  email: string;
  avatar_url: string;
}

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [filteredRepos, setFilteredRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchUser();
    fetchRepositories();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      const filtered = repositories.filter(
        (repo) =>
          repo.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          repo.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredRepos(filtered);
    } else {
      setFilteredRepos(repositories);
    }
  }, [searchQuery, repositories]);

  async function fetchUser() {
    try {
      const response = await fetch("/api/user");
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        router.push("/?error=not_authenticated");
      }
    } catch (error) {
      console.error("Failed to fetch user:", error);
      router.push("/?error=fetch_failed");
    }
  }

  async function fetchRepositories() {
    try {
      setLoading(true);
      const response = await fetch("/api/repositories");
      if (response.ok) {
        const data = await response.json();
        setRepositories(data.repositories || []);
        setFilteredRepos(data.repositories || []);
      }
    } catch (error) {
      console.error("Failed to fetch repositories:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSignOut() {
    await fetch("/api/auth/signout", { method: "POST" });
    router.push("/");
  }

  async function handleAnalyze(repo: Repository) {
    router.push(`/analyze?repo=${repo.full_name}`);
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                AutoRev Dashboard
              </h1>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="flex items-center gap-3">
                  <img
                    src={user.avatar_url}
                    alt={user.name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {user.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      @{user.login}
                    </p>
                  </div>
                </div>
              )}
              <button
                onClick={handleSignOut}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search repositories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <button
              onClick={fetchRepositories}
              disabled={loading}
              className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Repository List */}
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Loading repositories...</p>
          </div>
        ) : filteredRepos.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400">
              {searchQuery ? "No repositories found matching your search." : "No repositories found."}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredRepos.map((repo) => (
              <div
                key={repo.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      {repo.name}
                    </h3>
                    {repo.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {repo.description}
                      </p>
                    )}
                  </div>
                  {repo.private && (
                    <span className="px-2 py-1 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">
                      Private
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
                  {repo.language && (
                    <span className="flex items-center gap-1">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{
                          backgroundColor:
                            repo.language === "Python"
                              ? "#3572A5"
                              : repo.language === "JavaScript"
                              ? "#f1e05a"
                              : repo.language === "TypeScript"
                              ? "#2b7489"
                              : "#858585",
                        }}
                      />
                      {repo.language}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Star className="w-4 h-4" />
                    {repo.stargazers_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatDate(repo.updated_at)}
                  </span>
                </div>

                <button
                  onClick={() => handleAnalyze(repo)}
                  className="w-full px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <GitBranch className="w-5 h-5" />
                  Analyze Now
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
