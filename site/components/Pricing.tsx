"use client";

import { Check, Sparkles, Zap, Building2 } from "lucide-react";

const plans = [
  {
    name: "Free",
    icon: Zap,
    price: "$0",
    period: "forever",
    description: "Perfect for individual developers and open source projects",
    features: [
      "Up to 10 repositories",
      "Max repo size: 500MB",
      "Max analysis time: 5 minutes",
      "Basic static analysis (Flake8, Bandit, Semgrep)",
      "Deterministic scoring",
      "Phased improvement plans",
      "JSON/Markdown reports",
      "Community support"
    ],
    cta: "Start Free",
    highlighted: false,
    popular: false
  },
  {
    name: "Pro",
    icon: Sparkles,
    price: "$29",
    period: "per month",
    description: "For professional developers and small teams",
    features: [
      "Unlimited repositories",
      "Max repo size: 2GB",
      "Max analysis time: 15 minutes",
      "All static analysis tools",
      "AI-powered patch suggestions (OpenAI, Anthropic, Gemini)",
      "Delta-optimized re-reviews",
      "GitHub Codespaces integration",
      "Advanced metrics & trends",
      "Priority email support",
      "Custom Semgrep rules",
      "Configurable scoring weights"
    ],
    cta: "Start Pro Trial",
    highlighted: true,
    popular: true
  },
  {
    name: "Enterprise",
    icon: Building2,
    price: "Custom",
    period: "contact us",
    description: "For organizations with advanced security and compliance needs",
    features: [
      "Everything in Pro",
      "Unlimited repo size",
      "Unlimited analysis time",
      "Self-hosted deployment option",
      "SSO/SAML authentication",
      "Advanced security scans (SAST, secrets detection)",
      "Custom AI model integration",
      "Dedicated support & SLA",
      "Training & onboarding",
      "Custom integrations",
      "Volume pricing discounts",
      "Contract & invoice billing"
    ],
    cta: "Contact Sales",
    highlighted: false,
    popular: false
  }
];

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-gradient-to-br from-gray-50 to-indigo-50 dark:from-gray-900 dark:to-indigo-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Choose the plan that fits your needs. Upgrade or downgrade anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            return (
              <div
                key={index}
                className={`relative rounded-2xl p-8 ${
                  plan.highlighted
                    ? "bg-primary text-white shadow-2xl scale-105 z-10"
                    : "bg-white dark:bg-gray-800 shadow-lg"
                } transition-all duration-300 hover:shadow-2xl`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-secondary text-white px-4 py-1 rounded-full text-sm font-semibold shadow-md">
                      Most Popular
                    </span>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <div className="flex items-center justify-center mb-4">
                    <div
                      className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        plan.highlighted
                          ? "bg-white/20"
                          : "bg-primary/10"
                      }`}
                    >
                      <Icon
                        className={`w-6 h-6 ${
                          plan.highlighted ? "text-white" : "text-primary"
                        }`}
                      />
                    </div>
                  </div>
                  <h3
                    className={`text-2xl font-bold mb-2 ${
                      plan.highlighted ? "text-white" : "text-gray-900 dark:text-white"
                    }`}
                  >
                    {plan.name}
                  </h3>
                  <p
                    className={`text-sm mb-4 ${
                      plan.highlighted ? "text-white/90" : "text-gray-600 dark:text-gray-400"
                    }`}
                  >
                    {plan.description}
                  </p>
                  <div className="mb-2">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.price !== "Custom" && (
                      <span
                        className={`text-sm ml-2 ${
                          plan.highlighted ? "text-white/80" : "text-gray-500"
                        }`}
                      >
                        {plan.period}
                      </span>
                    )}
                  </div>
                </div>

                {/* Features List */}
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-start gap-3">
                      <Check
                        className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                          plan.highlighted ? "text-white" : "text-green-500"
                        }`}
                      />
                      <span
                        className={`text-sm ${
                          plan.highlighted ? "text-white/90" : "text-gray-600 dark:text-gray-300"
                        }`}
                      >
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <button
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${
                    plan.highlighted
                      ? "bg-white text-primary hover:bg-gray-100"
                      : "bg-primary text-white hover:bg-primary-dark"
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            );
          })}
        </div>

        {/* Bottom Note */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            All plans include 14-day free trial. No credit card required.
          </p>
        </div>
      </div>
    </section>
  );
}
