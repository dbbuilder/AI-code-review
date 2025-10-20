# Enhancing AutoRev UI with Tailwind UI & shadcn/ui

## Overview

This guide shows how to enhance the AutoRev interface with Tailwind UI components and shadcn/ui for a more polished, professional look.

---

## GitHub OAuth Callback URL

When setting up GitHub OAuth, use this callback URL:

```
https://autorev.servicevision.io/api/auth/github/callback
```

**Steps to create GitHub OAuth App:**
1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: **AutoRev**
   - Homepage URL: **https://autorev.servicevision.io**
   - Authorization callback URL: **https://autorev.servicevision.io/api/auth/github/callback**
4. Click "Register application"
5. Copy Client ID and Client Secret
6. Add to Vercel environment variables

---

## Adding shadcn/ui Components

shadcn/ui is a collection of re-usable components built with Radix UI and Tailwind CSS.

### Step 1: Install shadcn/ui

```bash
cd site
npx shadcn-ui@latest init
```

Answer the prompts:
- **Style**: Default
- **Base color**: Slate
- **CSS variables**: Yes

This creates `components/ui/` directory and updates `tailwind.config.ts`.

### Step 2: Add Components

Install individual components as needed:

```bash
# Button component
npx shadcn-ui@latest add button

# Card component
npx shadcn-ui@latest add card

# Dialog (Modal) component
npx shadcn-ui@latest add dialog

# Dropdown Menu
npx shadcn-ui@latest add dropdown-menu

# Tabs component
npx shadcn-ui@latest add tabs

# Badge component
npx shadcn-ui@latest add badge

# Alert component
npx shadcn-ui@latest add alert

# Input component
npx shadcn-ui@latest add input

# Select component
npx shadcn-ui@latest add select

# Checkbox component
npx shadcn-ui@latest add checkbox

# Radio Group component
npx shadcn-ui@latest add radio-group

# Toast (notifications)
npx shadcn-ui@latest add toast

# Tooltip
npx shadcn-ui@latest add tooltip

# Progress bar
npx shadcn-ui@latest add progress

# Skeleton loader
npx shadcn-ui@latest add skeleton

# Avatar
npx shadcn-ui@latest add avatar

# Separator
npx shadcn-ui@latest add separator
```

### Step 3: Update Components to Use shadcn/ui

#### Example: Hero Component with shadcn Button

```typescript
import { Button } from "@/components/ui/button";
import { Github } from "lucide-react";

// Replace old button with:
<Button
  onClick={handleGitHubSignIn}
  className="px-8 py-4"
  size="lg"
>
  <Github className="w-5 h-5 mr-2" />
  Sign in with GitHub
</Button>
```

#### Example: Dashboard with shadcn Card

```typescript
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

<Card className="hover:shadow-lg transition-shadow">
  <CardHeader>
    <div className="flex justify-between items-start">
      <CardTitle>{repo.name}</CardTitle>
      {repo.private && <Badge variant="secondary">Private</Badge>}
    </div>
    <CardDescription className="line-clamp-2">
      {repo.description}
    </CardDescription>
  </CardHeader>
  <CardContent>
    <Button className="w-full" onClick={() => handleAnalyze(repo)}>
      Analyze Now
    </Button>
  </CardContent>
</Card>
```

#### Example: FAQ with shadcn Accordion

```bash
npx shadcn-ui@latest add accordion
```

```typescript
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

<Accordion type="single" collapsible className="w-full">
  {faqs.map((faq, index) => (
    <AccordionItem key={index} value={`item-${index}`}>
      <AccordionTrigger>{faq.question}</AccordionTrigger>
      <AccordionContent>{faq.answer}</AccordionContent>
    </AccordionItem>
  ))}
</Accordion>
```

---

## Adding Tailwind UI Components

Tailwind UI is a premium component library. You'll need a license ($299 one-time or $24/month).

### Step 1: Get Tailwind UI Access

1. Purchase license at: https://tailwindui.com/pricing
2. Access components at: https://tailwindui.com/components

### Step 2: Install Dependencies

Tailwind UI components may require additional packages:

```bash
cd site
npm install @headlessui/react @heroicons/react
```

### Step 3: Copy Components

Browse Tailwind UI components and copy the code directly into your project:

#### Example: Pricing Section

From: https://tailwindui.com/components/marketing/sections/pricing

Copy the entire component code and adapt to AutoRev:

```typescript
// components/PricingTailwindUI.tsx
import { CheckIcon } from '@heroicons/react/20/solid'

const tiers = [
  // ... your pricing data
]

export default function PricingTailwindUI() {
  return (
    <div className="bg-white py-24 sm:py-32">
      {/* Tailwind UI pricing grid code */}
    </div>
  )
}
```

#### Example: Feature Sections

From: https://tailwindui.com/components/marketing/sections/feature-sections

Choose a layout (alternating features, offset grid, etc.) and adapt.

#### Example: Stats Section

From: https://tailwindui.com/components/marketing/sections/stats

Perfect for the results dashboard summary cards:

```typescript
import { ArrowUpIcon } from '@heroicons/react/20/solid'

const stats = [
  { id: 1, name: 'Total Findings', value: '45' },
  { id: 2, name: 'Critical/High', value: '11', change: '+4.5%', changeType: 'negative' },
  { id: 3, name: 'Estimated Effort', value: '24.5h' },
]

export default function StatsDashboard() {
  // Tailwind UI stats implementation
}
```

---

## Recommended Component Updates

### 1. Hero Section

**Current**: Basic gradient background
**Enhanced**:
- shadcn Button for CTAs
- Tailwind UI "Split with image" hero pattern
- Animated background with particles.js
- Featured logos section

### 2. Features Section

**Current**: Grid of cards
**Enhanced**:
- Tailwind UI "Alternating side-by-side" layout
- shadcn Tabs to organize features by category
- Animated icons with Framer Motion
- Screenshots/mockups of features

### 3. Pricing Section

**Current**: Basic cards
**Enhanced**:
- Tailwind UI pricing component with hover effects
- shadcn RadioGroup for billing period toggle (Monthly/Yearly)
- Comparison table with tooltips
- "Most Popular" badge with shadcn Badge

### 4. Dashboard

**Current**: Repository list
**Enhanced**:
- shadcn Command palette (Cmd+K) for quick search
- shadcn DataTable with sorting/filtering
- shadcn DropdownMenu for repo actions
- shadcn Toast notifications for success/errors

### 5. Results Page

**Current**: Basic findings list
**Enhanced**:
- shadcn Tabs for different views (List, Chart, Timeline)
- shadcn Sheet (slide-over) for finding details
- Tailwind UI "Stacked list" for findings
- Chart.js or Recharts for visualizations

### 6. FAQ Section

**Current**: Custom accordion
**Enhanced**:
- shadcn Accordion component
- Search bar to filter questions
- shadcn Dialog for detailed answers

---

## Complete shadcn/ui Setup Example

### Update `tailwind.config.ts`

After running `npx shadcn-ui@latest init`, your config will look like:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
```

### Update `app/globals.css`

Add CSS variables:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 239 84% 67%;
    --primary-foreground: 210 40% 98%;
    --secondary: 272 51% 71%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 239 84% 67%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 239 84% 67%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 272 51% 71%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 239 84% 67%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## Installation Commands Summary

```bash
# 1. Initialize shadcn/ui
npx shadcn-ui@latest init

# 2. Install commonly used components
npx shadcn-ui@latest add button card dialog dropdown-menu tabs badge alert input select toast tooltip progress skeleton avatar separator accordion

# 3. Install Headless UI & Heroicons for Tailwind UI
npm install @headlessui/react @heroicons/react

# 4. Install additional animation/chart libraries (optional)
npm install framer-motion recharts

# 5. Install icons (optional, if not using Lucide)
npm install @radix-ui/react-icons
```

---

## Quick Wins for Visual Enhancement

### 1. Add shadcn Button to Hero

Replace the basic `<button>` in `Hero.tsx` with shadcn Button.

### 2. Use shadcn Card for Repository List

Replace the div cards in `Dashboard.tsx` with shadcn Card components.

### 3. Add shadcn Toast for Notifications

Show success/error toasts when actions complete.

### 4. Use shadcn Dialog for Confirmations

Replace browser `alert()` with shadcn Dialog for better UX.

### 5. Add shadcn Progress for Analysis

Replace the custom progress bar with shadcn Progress component.

---

## Resources

- **shadcn/ui Docs**: https://ui.shadcn.com
- **shadcn/ui GitHub**: https://github.com/shadcn-ui/ui
- **Tailwind UI**: https://tailwindui.com
- **Headless UI**: https://headlessui.com
- **Heroicons**: https://heroicons.com
- **Lucide Icons**: https://lucide.dev

---

## Next Steps

1. ✅ Deploy current AutoRev site
2. ⏳ Setup GitHub OAuth credentials
3. ⏳ Initialize shadcn/ui in the project
4. ⏳ Replace basic components with shadcn versions
5. ⏳ Add Tailwind UI patterns (if purchased)
6. ⏳ Test responsiveness and accessibility
7. ⏳ Optimize performance

---

**Status**: Guide Complete | Ready for UI Enhancement
