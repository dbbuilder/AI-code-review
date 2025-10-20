# AutoVibe Landing Site

This is the landing page and marketing site for **AutoVibe** - AI Driven Automated Code Review for Vibe Coding Quality.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Deployment**: Vercel (recommended)

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the landing page.

### Build for Production

```bash
# Create optimized production build
npm run build

# Run production server
npm run start
```

## Project Structure

```
site/
├── app/                    # Next.js app router
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Main landing page
│   └── globals.css        # Global styles with Tailwind
├── components/            # React components
│   ├── Hero.tsx          # Hero section with branding
│   ├── Features.tsx      # Features showcase
│   ├── Pricing.tsx       # Pricing tiers
│   ├── FAQ.tsx           # FAQ accordion
│   └── Footer.tsx        # Footer with links
├── public/               # Static assets
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── next.config.mjs       # Next.js configuration
```

## Features

### Landing Page Sections

1. **Hero Section**
   - AutoVibe branding with gradient effects
   - Clear value proposition
   - CTA buttons for GitHub signup and demo
   - Trust indicators

2. **Features Showcase**
   - 9 key features with icons
   - Hover effects and animations
   - Detailed descriptions

3. **Pricing**
   - Three tiers: Free, Pro, Enterprise
   - Feature comparison
   - Highlighted "Most Popular" plan
   - Clear CTAs

4. **FAQ**
   - 12 frequently asked questions
   - Accordion UI for easy navigation
   - Support CTA

5. **Footer**
   - Brand identity
   - Social media links
   - Product, company, resources, and legal links
   - Copyright notice

## Customization

### Brand Colors

Edit `tailwind.config.ts` to change the primary and secondary colors:

```typescript
colors: {
  primary: {
    DEFAULT: "#6366f1",  // Indigo
    light: "#818cf8",
    dark: "#4f46e5",
  },
  secondary: {
    DEFAULT: "#8b5cf6",  // Purple
    light: "#a78bfa",
    dark: "#7c3aed",
  },
}
```

### Content

All content is embedded in the component files:
- Hero text: `components/Hero.tsx`
- Features: `components/Features.tsx` (see `features` array)
- Pricing: `components/Pricing.tsx` (see `plans` array)
- FAQ: `components/FAQ.tsx` (see `faqs` array)

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set root directory to `site`
4. Deploy

### Other Platforms

For Docker deployment:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

## License

Part of the code-review-engine project.

## Support

For questions or issues, please open an issue in the main repository.
