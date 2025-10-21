"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, Play, Settings, GitBranch, AlertCircle, CheckCircle2 } from "lucide-react";

function AnalyzePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlRepo = searchParams.get("repo");

  const [repoUrl, setRepoUrl] = useState(urlRepo || "");
  const [selectedPreset, setSelectedPreset] = useState("comprehensive");
  const [selectedBranch, setSelectedBranch] = useState("main");
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

  const presets = [
    {
      id: "security",
      name: "Security-Focused",
      description: "Prioritizes security vulnerabilities and SAST findings",
    },
    {
      id: "performance",
      name: "Performance",
      description: "Focuses on performance bottlenecks and optimization opportunities",
    },
    {
      id: "comprehensive",
      name: "Comprehensive",
      description: "Balanced analysis across all dimensions (recommended)",
    },
  ];

  const branches = ["main", "master", "develop", "staging"];

  async function handleAnalyze() {
    setAnalyzing(true);
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          return 95;
        }
        return prev + 5;
      });
    }, 500);

    try {
      // TODO: Implement actual API call to trigger analysis
      const response = await fetch("/api/analysis/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository: repoUrl,
          preset: selectedPreset,
          branch: selectedBranch,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        clearInterval(interval);
        setProgress(100);

        // Redirect to results page
        setTimeout(() => {
          router.push(`/results/${data.analysisId}`);
        }, 1000);
      } else {
        throw new Error("Analysis failed");
      }
    } catch (error) {
      clearInterval(interval);
      setAnalyzing(false);
      setProgress(0);
      alert("Analysis failed. Please try again.");
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          {/* Repository Info */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Configure Analysis
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Analyze any public GitHub repository without signing in!
            </p>
          </div>

          {/* Configuration */}
          <div className="space-y-8">
            {/* Repository URL Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
                GitHub Repository URL
              </label>
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent font-mono"
              />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Enter any public GitHub repository URL (e.g., https://github.com/dbbuilder/SQLExtract)
              </p>
            </div>
            {/* Preset Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
                <Settings className="w-5 h-5 inline mr-2" />
                Analysis Preset
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {presets.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => setSelectedPreset(preset.id)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      selectedPreset === preset.id
                        ? "border-primary bg-primary/5"
                        : "border-gray-300 dark:border-gray-600 hover:border-primary/50"
                    }`}
                  >
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                      {preset.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {preset.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Branch Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
                <GitBranch className="w-5 h-5 inline mr-2" />
                Branch
              </label>
              <select
                value={selectedBranch}
                onChange={(e) => setSelectedBranch(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                {branches.map((branch) => (
                  <option key={branch} value={branch}>
                    {branch}
                  </option>
                ))}
              </select>
            </div>

            {/* Info Box */}
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  <p className="font-semibold mb-1">Analysis Details:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Estimated time: 2-5 minutes</li>
                    <li>No login required for public repositories</li>
                    <li>Results persist in our database</li>
                    <li>Bookmark the results URL to access later</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {analyzing && (
              <div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <span>Analyzing...</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  {progress < 30 && "Cloning repository..."}
                  {progress >= 30 && progress < 60 && "Running static analysis..."}
                  {progress >= 60 && progress < 90 && "Scoring findings..."}
                  {progress >= 90 && "Generating report..."}
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="flex-1 px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {analyzing ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Start Analysis
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <AnalyzePageContent />
    </Suspense>
  );
}
