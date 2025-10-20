import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoRev - AI Driven Automated Code Review",
  description: "AutoRev - AI Driven Automated Code Review for Vibe Coding Quality. Deterministic, multi-language code analysis with AI-powered insights.",
  keywords: ["code review", "static analysis", "AI", "automation", "code quality", "security", "developer tools"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
