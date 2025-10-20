"use client";

import {
  Zap,
  Shield,
  GitBranch,
  Brain,
  Target,
  TrendingUp,
  Lock,
  Clock,
  CheckCircle2
} from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Deterministic & Repeatable",
    description: "Same commit hash + config = same results. Every step emits timestamped JSON/MD files for CI artifacts and complete auditability.",
    color: "text-yellow-500",
    bgColor: "bg-yellow-50 dark:bg-yellow-900/20"
  },
  {
    icon: Brain,
    title: "AI-Powered Patch Suggestions",
    description: "Optional AI integration with OpenAI, Anthropic Claude, or Google Gemini to draft patches. Re-analyzes only the diffs for rapid convergence.",
    color: "text-purple-500",
    bgColor: "bg-purple-50 dark:bg-purple-900/20"
  },
  {
    icon: Target,
    title: "Config-Driven Scoring",
    description: "Assigns Difficulty/Risk (1-5) and Value/Importance (1-5) scores with configurable weights. Estimates person-hours per finding.",
    color: "text-blue-500",
    bgColor: "bg-blue-50 dark:bg-blue-900/20"
  },
  {
    icon: Shield,
    title: "Security-First Analysis",
    description: "References OWASP guidance, runs Bandit and Semgrep security scanners. No shell injection—subprocess uses argument lists.",
    color: "text-red-500",
    bgColor: "bg-red-50 dark:bg-red-900/20"
  },
  {
    icon: GitBranch,
    title: "Delta-Optimized Reviews",
    description: "Re-reviews only changed files/hunks via Git history. Make changes → delta review → see only new issues for rapid iteration.",
    color: "text-green-500",
    bgColor: "bg-green-50 dark:bg-green-900/20"
  },
  {
    icon: TrendingUp,
    title: "Phased Improvement Plans",
    description: "Aggregates findings into 5 phases: Hygiene → Safety → Reliability → DevEx → Polish. Tag-based routing with rationale and best practices.",
    color: "text-indigo-500",
    bgColor: "bg-indigo-50 dark:bg-indigo-900/20"
  },
  {
    icon: Lock,
    title: "Multi-Language Support",
    description: "Uses Tree-sitter for parsing and Semgrep for cross-language rules. Supports Python, JavaScript, TypeScript, and more.",
    color: "text-cyan-500",
    bgColor: "bg-cyan-50 dark:bg-cyan-900/20"
  },
  {
    icon: Clock,
    title: "Fast & Efficient",
    description: "Analyze 1000+ files in under 30 seconds. Intelligent dependency ordering with topological sort for complex codebases.",
    color: "text-orange-500",
    bgColor: "bg-orange-50 dark:bg-orange-900/20"
  },
  {
    icon: CheckCircle2,
    title: "Production-Ready",
    description: "Pinned dependencies, comprehensive test suite (84%+ coverage), and extensive error handling. Ready for CI/CD integration.",
    color: "text-emerald-500",
    bgColor: "bg-emerald-50 dark:bg-emerald-900/20"
  }
];

export default function Features() {
  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Powerful Features for Modern Development
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            AutoVibe combines deterministic static analysis with AI-powered insights
            to deliver actionable code reviews that improve quality and velocity.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="group p-6 rounded-xl bg-gray-50 dark:bg-gray-800 hover:shadow-xl transition-all duration-300 border border-gray-200 dark:border-gray-700 hover:border-primary"
              >
                <div className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
            Ready to elevate your code quality?
          </p>
          <button className="px-8 py-4 bg-primary hover:bg-primary-dark text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
            Start Your Free Trial
          </button>
        </div>
      </div>
    </section>
  );
}
