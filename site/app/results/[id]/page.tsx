"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft,
  Download,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2,
  TrendingUp,
  Shield,
  Zap,
  Code,
  FileText,
} from "lucide-react";

interface Finding {
  id: string;
  file: string;
  line: number;
  severity: "critical" | "high" | "medium" | "low" | "info";
  rule: string;
  message: string;
  difficulty: number;
  value: number;
  phase: number;
}

interface AnalysisResult {
  id: string;
  repository: string;
  branch: string;
  status: "completed" | "running" | "failed";
  startedAt: string;
  completedAt: string;
  findings: Finding[];
  summary: {
    totalFindings: number;
    bySeverity: Record<string, number>;
    byPhase: Record<string, number>;
    estimatedEffort: number;
  };
}

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string | null>(null);
  const [selectedPhase, setSelectedPhase] = useState<number | null>(null);

  useEffect(() => {
    fetchResults();
  }, [analysisId]);

  async function fetchResults() {
    try {
      setLoading(true);
      const response = await fetch(`/api/analysis/${analysisId}`);

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        // Mock data for demo
        setResult({
          id: analysisId,
          repository: "example/repo",
          branch: "main",
          status: "completed",
          startedAt: new Date(Date.now() - 300000).toISOString(),
          completedAt: new Date().toISOString(),
          findings: generateMockFindings(),
          summary: {
            totalFindings: 45,
            bySeverity: { critical: 3, high: 8, medium: 15, low: 12, info: 7 },
            byPhase: { "0": 10, "1": 8, "2": 12, "3": 10, "4": 5 },
            estimatedEffort: 24.5,
          },
        });
      }
    } catch (error) {
      console.error("Failed to fetch results:", error);
    } finally {
      setLoading(false);
    }
  }

  function generateMockFindings(): Finding[] {
    const findings: Finding[] = [];
    const severities: Finding["severity"][] = ["critical", "high", "medium", "low", "info"];
    const files = [
      "src/main.py",
      "src/api/routes.py",
      "src/utils/helpers.py",
      "tests/test_api.py",
      "config/settings.py",
    ];

    for (let i = 0; i < 20; i++) {
      findings.push({
        id: `finding_${i}`,
        file: files[Math.floor(Math.random() * files.length)],
        line: Math.floor(Math.random() * 200) + 1,
        severity: severities[Math.floor(Math.random() * severities.length)],
        rule: `Rule ${100 + i}`,
        message: `Sample finding message ${i + 1}`,
        difficulty: Math.floor(Math.random() * 5) + 1,
        value: Math.floor(Math.random() * 5) + 1,
        phase: Math.floor(Math.random() * 5),
      });
    }

    return findings.sort((a, b) => {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    });
  }

  function getSeverityIcon(severity: string) {
    switch (severity) {
      case "critical":
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case "high":
        return <AlertCircle className="w-5 h-5 text-orange-600" />;
      case "medium":
        return <Info className="w-5 h-5 text-yellow-600" />;
      case "low":
        return <Info className="w-5 h-5 text-blue-600" />;
      default:
        return <CheckCircle2 className="w-5 h-5 text-gray-600" />;
    }
  }

  function getPhaseIcon(phase: number) {
    const icons = [
      <Zap key="0" className="w-5 h-5" />,
      <Shield key="1" className="w-5 h-5" />,
      <TrendingUp key="2" className="w-5 h-5" />,
      <Code key="3" className="w-5 h-5" />,
      <FileText key="4" className="w-5 h-5" />,
    ];
    return icons[phase] || icons[0];
  }

  const phaseNames = [
    "Repo Hygiene",
    "Security & Safety",
    "Reliability & Performance",
    "Developer Experience",
    "Product Polish",
  ];

  const filteredFindings = result?.findings.filter((finding) => {
    if (selectedSeverity && finding.severity !== selectedSeverity) return false;
    if (selectedPhase !== null && finding.phase !== selectedPhase) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading results...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400">Analysis not found</p>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => router.push("/dashboard")}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Analysis Results
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {result.repository} • {result.branch}
              </p>
            </div>
            <button className="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors flex items-center gap-2">
              <Download className="w-5 h-5" />
              Export Report
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Total Findings
            </h3>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {result.summary.totalFindings}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Critical/High
            </h3>
            <p className="text-3xl font-bold text-red-600">
              {result.summary.bySeverity.critical + result.summary.bySeverity.high}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Estimated Effort
            </h3>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {result.summary.estimatedEffort}h
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Status
            </h3>
            <p className="text-3xl font-bold text-green-600">Complete</p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Filters
          </h2>
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Severity
              </label>
              <div className="flex gap-2">
                {["critical", "high", "medium", "low", "info"].map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setSelectedSeverity(selectedSeverity === sev ? null : sev)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      selectedSeverity === sev
                        ? "bg-primary text-white"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phase
              </label>
              <div className="flex gap-2">
                {[0, 1, 2, 3, 4].map((phase) => (
                  <button
                    key={phase}
                    onClick={() => setSelectedPhase(selectedPhase === phase ? null : phase)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      selectedPhase === phase
                        ? "bg-primary text-white"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    Phase {phase}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Findings List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Findings ({filteredFindings?.length || 0})
            </h2>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredFindings?.map((finding) => (
              <div key={finding.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {getSeverityIcon(finding.severity)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 text-xs font-semibold bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                        {finding.severity.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {phaseNames[finding.phase]}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Difficulty: {finding.difficulty}/5 • Value: {finding.value}/5
                      </span>
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                      {finding.rule}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {finding.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 font-mono">
                      {finding.file}:{finding.line}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
