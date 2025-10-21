"use client";

import { ArrowRight, Code2, Sparkles, Github } from "lucide-react";

export default function Hero() {
  const handleGitHubSignIn = () => {
    window.location.href = "/api/auth/github";
  };

  const handleTryDemo = () => {
    // Navigate to analyze page with a demo repo pre-filled
    window.location.href = "/analyze?repo=https://github.com/dbbuilder/SQLExtract";
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-secondary/20 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Logo/Brand */}
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <Code2 className="w-16 h-16 text-primary" />
              <Sparkles className="w-8 h-8 text-secondary absolute -top-2 -right-2 animate-pulse" />
            </div>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-6">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
              AutoRev
            </span>
          </h1>

          <p className="text-2xl md:text-3xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
            AI Driven Automated Code Review
          </p>

          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-12 max-w-3xl mx-auto">
            for Vibe Coding Quality
          </p>

          {/* Value Proposition */}
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            Deterministic, repeatable code analysis with AI-powered insights.
            Analyze your codebase, score issues by difficulty and value,
            and receive a phased improvement plan—all in seconds.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={handleTryDemo}
              className="group px-8 py-4 bg-primary hover:bg-primary-dark text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              Try Demo Now (No Login Required)
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={handleGitHubSignIn}
              className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:text-primary dark:hover:text-primary font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border-2 border-gray-300 dark:border-gray-600 hover:border-primary flex items-center gap-2"
            >
              <Github className="w-5 h-5" />
              Sign in with GitHub
            </button>
          </div>

          {/* Public Access Notice */}
          <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            🎉 Now publicly accessible! Try analyzing public repositories without signing in.
            <br />
            Sign in with GitHub for private repositories and advanced features.
          </p>

          {/* Trust Indicators */}
          <div className="mt-16 flex flex-wrap justify-center gap-8 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Multi-Language Support</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>AI-Powered Insights</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Deterministic Results</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>GitHub Integration</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
