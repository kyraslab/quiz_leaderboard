# Quiz Leaderboard Frontend

A Next.js frontend application for a quiz platform with real-time leaderboards and WebSocket notifications.

## Features

- 🏆 **Real-time Leaderboards** - Live updates via WebSocket
- 🔐 **Authentication** - JWT-based login/logout system
- 📊 **Subject & Quiz Rankings** - Multiple leaderboard views
- 🔔 **Live Notifications** - Real-time updates and alerts
- 📱 **Responsive Design** - Works on desktop and mobile
- ⚡ **Auto-refresh** - Automatic data updates on changes

## Getting Started

### Prerequisites

- Node.js 18+
- npm/yarn/pnpm
- Backend API server running

### Installation

1. Clone and install dependencies:

```bash
npm install
```

2. Set up environment variables:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## WebSocket Integration

This application includes real-time WebSocket functionality for live leaderboard updates. See [WEBSOCKET_DOCS.md](./WEBSOCKET_DOCS.md) for detailed documentation.

### Key Features:

- ✅ Auto-refresh leaderboards on new submissions
- ✅ Real-time notifications for updates
- ✅ Connection status indicators
- ✅ Automatic reconnection with backoff
- ✅ Quiz-specific subscriptions

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **Authentication**: JWT with js-cookie
- **WebSocket**: Native WebSocket API
- **HTTP Client**: Axios
- **TypeScript**: Full type safety

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── leaderboard/       # Subject leaderboards
│   ├── quizzes/           # Quiz pages and submissions
│   ├── login/             # Authentication pages
│   └── logout/
├── components/            # Reusable UI components
│   ├── ui/                # Basic UI components
│   ├── Navbar.tsx         # Navigation component
│   └── ProtectedRoute.tsx # Auth guard component
├── contexts/              # React Context providers
│   ├── AuthContext.tsx    # Authentication state
│   └── WebSocketContext.tsx # WebSocket management
├── lib/                   # Utilities and API clients
│   └── api.ts             # HTTP API client
└── types/                 # TypeScript type definitions
    └── index.ts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

| Variable              | Description          | Example                 |
| --------------------- | -------------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL`  | WebSocket server URL | `ws://localhost:8000`   |

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Other Platforms

```bash
npm run build
npm run start
```

Ensure WebSocket URLs use `wss://` for HTTPS deployments.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Documentation](https://tanstack.com/query)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Tailwind CSS](https://tailwindcss.com/docs)
