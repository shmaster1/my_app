# SHAPP — Next.js Ecommerce UI

A production-ready Next.js frontend for the SHAPP ecommerce dashboard. Deployable on Vercel, connects to your Python backend.

## Quick Start

```bash
npm install
npm run dev
```

## Connect to Your Python Backend

1. Copy `.env.local.example` to `.env.local`
2. Set `NEXT_PUBLIC_API_URL` to your backend URL

```env
NEXT_PUBLIC_API_URL=https://your-python-api.com
```

## Deploy to Vercel

```bash
npm install -g vercel
vercel
```

Or connect your GitHub repo to Vercel and add the env variable in the Vercel dashboard.

## Backend API Contract

Your Python backend should expose these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products (supports `?search=`, `?category=`) |
| GET | `/products/:id` | Single product |
| GET | `/orders` | User orders |
| POST | `/orders` | Create order |
| GET | `/favorites` | User favorites |
| POST | `/favorites` | Add favorite |
| DELETE | `/favorites/:id` | Remove favorite |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |

### Product Schema
```json
{
  "id": 1,
  "name": "Aesthetic Tee",
  "price": 29.99,
  "stock": 5,
  "image": "https://...",
  "description": "Optional description"
}
```

## Project Structure

```
shapp-store/
├── pages/
│   ├── index.js          # Dashboard (product grid)
│   ├── products/[id].js  # Product detail
│   ├── orders.js
│   ├── favorites.js
│   ├── account.js
│   └── settings.js
├── components/
│   ├── Layout.js
│   ├── Sidebar.js
│   ├── Topbar.js
│   ├── ProductCard.js
│   ├── CartDrawer.js
│   └── CartContext.js
├── lib/
│   └── api.js            # Backend API calls + mock data
└── styles/
    └── globals.css
```

