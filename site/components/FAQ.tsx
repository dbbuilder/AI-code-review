"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

const faqs = [
  {
    question: "What is AutoVibe?",
    answer: "AutoVibe is an AI-driven automated code review engine that analyzes your codebase, scores issues by difficulty/risk and value/importance, and provides a phased improvement plan. It combines deterministic static analysis with optional AI-powered insights to help you improve code quality systematically."
  },
  {
    question: "How does AutoVibe differ from other code review tools?",
    answer: "AutoVibe is deterministic and repeatable—same commit + config = same results. It provides weighted scoring on two dimensions (Difficulty/Risk and Value/Importance), phase-based improvement plans, and optional AI integration for patch suggestions. Unlike many tools, it supports delta-optimized reviews to analyze only changed code for rapid iteration."
  },
  {
    question: "Which programming languages are supported?",
    answer: "AutoVibe uses Tree-sitter for parsing and Semgrep for cross-language rules, supporting Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, and more. Language-specific tools like Flake8 and Bandit are used for Python, with extensibility for additional analyzers."
  },
  {
    question: "Do I need to use AI features?",
    answer: "No! AI integration is completely optional. AutoVibe works perfectly as a deterministic static analysis tool without any AI. When you do enable AI (OpenAI, Anthropic Claude, or Google Gemini), it only drafts patch suggestions—the core analysis remains deterministic."
  },
  {
    question: "How does the scoring system work?",
    answer: "AutoVibe assigns two scores (1-5) to each finding: Difficulty/Risk (based on complexity, coupling, security) and Value/Importance (based on impact, reliability, developer experience). Scores are config-driven with adjustable weights, and person-hour estimates are provided to help prioritize work."
  },
  {
    question: "What are the five phases in the improvement plan?",
    answer: "Phase 0: Repo Hygiene (formatting, dead code), Phase 1: Security & Safety (vulnerabilities, auth), Phase 2: Reliability & Performance (error handling, optimization), Phase 3: Developer Experience (tests, docs, typing), Phase 4: Product Polish (UX, observability). Findings are auto-routed based on tags."
  },
  {
    question: "Can I integrate AutoVibe into my CI/CD pipeline?",
    answer: "Yes! AutoVibe is designed for CI/CD integration. It emits timestamped JSON/MD artifacts for every stage, supports deterministic execution, and can fail builds based on threshold configurations. Run it as a step in GitHub Actions, GitLab CI, Jenkins, or any CI system."
  },
  {
    question: "How does delta review work?",
    answer: "Delta review uses Git history to detect changed files and hunks, then re-runs analysis only on those regions. This enables rapid iteration loops: make changes → delta review → see only new issues. Previous findings for unchanged code are preserved, making it perfect for pre-commit hooks."
  },
  {
    question: "Is my code secure with AutoVibe?",
    answer: "Yes. AutoVibe runs entirely in your environment (CLI or self-hosted worker). Code is never sent to AutoVibe servers. When you use AI features, only code snippets relevant to specific findings are sent to your chosen AI provider (OpenAI, Anthropic, or Gemini) with your API keys."
  },
  {
    question: "What kind of support do you offer?",
    answer: "Free tier includes community support via GitHub Discussions. Pro users get priority email support with 24-48 hour response time. Enterprise customers receive dedicated support, SLA guarantees, training, and custom integration assistance."
  },
  {
    question: "Can I customize the analysis rules?",
    answer: "Absolutely! You can add custom Semgrep rules, adjust scoring weights in config/engine.yaml, modify phase definitions, and configure which tools to run. Pro and Enterprise tiers offer advanced customization including custom AI prompts and integration of proprietary analyzers."
  },
  {
    question: "How do I get started?",
    answer: "For CLI: Install via pip, configure your .env with optional AI keys, and run 'crengine run --repo .' For the web platform: Sign up with GitHub, select a repository, and trigger an analysis. Both approaches provide the same deterministic, high-quality results."
  }
];

function FAQItem({ faq, isOpen, toggle }: { faq: typeof faqs[0]; isOpen: boolean; toggle: () => void }) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={toggle}
        className="w-full py-6 flex items-center justify-between text-left hover:text-primary transition-colors"
      >
        <span className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
          {faq.question}
        </span>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-primary flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="pb-6 pr-12">
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            {faq.answer}
          </p>
        </div>
      )}
    </div>
  );
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Everything you need to know about AutoVibe
          </p>
        </div>

        {/* FAQ List */}
        <div className="space-y-0">
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              faq={faq}
              isOpen={openIndex === index}
              toggle={() => setOpenIndex(openIndex === index ? null : index)}
            />
          ))}
        </div>

        {/* Still have questions CTA */}
        <div className="mt-16 text-center p-8 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-2xl">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Still have questions?
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Our team is here to help. Reach out anytime.
          </p>
          <button className="px-8 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200">
            Contact Support
          </button>
        </div>
      </div>
    </section>
  );
}
