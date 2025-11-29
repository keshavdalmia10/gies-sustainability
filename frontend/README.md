# Gies Sustainability Dashboard - Frontend

## React + TypeScript + Vite Frontend

Modern dashboard for the Gies Sustainability Impact project with three persona-based views.

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server (proxies to backend on localhost:8000)
npm run dev

# Visit: http://localhost:3000
```

## Features

- **Landing Page**: Hero section with persona selection
- **Donor View**: Filterable impact cards with funding metrics ✅
- **Dean View**: Strategic analysis dashboard (coming soon)
- **Student View**: Faculty mentor search (coming soon)

## Tech Stack

- React 18 with TypeScript
- Vite for fast development
- Axios for API calls
- Lucide React for icons
- CSS with design tokens

## Project Structure

```
src/
├── components/
│   └── Layout.tsx        # Header, nav, footer
├── pages/
│   ├── HomePage.tsx      # Landing with personas
│   ├── DonorView.tsx     # Impact cards view ✅
│   ├── DeanView.tsx      # Strategic dashboard
│   ├── StudentView.tsx   # Faculty search
│   └── ImpactCardDetail.tsx
├── services/
│   └── api.ts            # Axios configuration
└── index.css             # Global styles & design tokens
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Backend Integration

The Vite dev server proxies `/api/*` requests to `http://localhost:8000` where your FastAPI backend runs.

Make sure your backend is running:
```bash
cd ../backend
uvicorn app.main:app --reload
```

## What's Implemented

✅ Project setup & configuration
✅ Global design system
✅ Layout with navigation
✅ Homepage with persona cards
✅ Donor view with impact card grid
✅ API integration layer
⬜ Dean view (strategic analysis)
⬜ Student view (faculty search)
⬜ Impact card detail page

## Next Steps

1. Start backend: `cd ../backend && uvicorn app.main:app --reload`
2. Generate impact cards: `python scripts/generate_sdg7_cards.py`
3. Start frontend: `npm install && npm run dev`
4. Visit: http://localhost:3000
