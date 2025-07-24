# WebSocket Real-time Features

This frontend application includes real-time WebSocket functionality that provides live updates for leaderboards and quiz submissions.

## Features

### 🔄 Auto-refresh Leaderboards

- **Subject Leaderboards**: Automatically refresh when new quiz sessions are uploaded
- **Quiz Leaderboards**: Real-time updates for quiz-specific rankings
- **User Performance**: Live updates of user rankings and statistics

### 🔔 Real-time Notifications

- Quiz session upload notifications
- Leaderboard update alerts
- Connection status indicators
- Subscription confirmations

### 📡 Connection Management

- Automatic connection on authentication
- Reconnection with exponential backoff
- Graceful disconnection on logout
- Connection status visualization

## Implementation

### WebSocket Context (`src/contexts/WebSocketContext.tsx`)

The main WebSocket context provides:

- Connection management
- Message handling
- Notification system
- Subscription management

### Key Components

#### 1. Connection Status Indicators

Both leaderboard pages show:

- Live connection status (green/red dot)
- Last update timestamp
- Real-time connection state

#### 2. Auto-refresh Integration

- Uses React Query for data fetching
- Invalidates queries on WebSocket messages
- Automatic re-fetching of leaderboard data

#### 3. Quiz-specific Subscriptions

Quiz detail pages automatically:

- Subscribe to quiz-specific updates
- Unsubscribe when leaving the page
- Receive targeted notifications

## WebSocket Message Types

### Incoming Messages (from backend)

```typescript
{
  type: 'quiz_session_uploaded',
  data: { /* session data */ }
}

{
  type: 'leaderboard_updated',
  data: { /* leaderboard data */ }
}

{
  type: 'quiz_leaderboard_updated',
  data: { quiz_id: string, /* other data */ }
}

{
  type: 'subscription_confirmed',
  quiz_id: string,
  message: string
}
```

### Outgoing Messages (to backend)

```typescript
{
  type: 'subscribe_quiz',
  quiz_id: string
}

{
  type: 'unsubscribe_quiz',
  quiz_id: string
}
```

## Configuration

### Environment Variables

```bash
# WebSocket server URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# For production with HTTPS
NEXT_PUBLIC_WS_URL=wss://yourdomain.com
```

### Connection Parameters

- **Authentication**: JWT token passed as query parameter
- **Reconnection**: Exponential backoff (max 5 attempts)
- **Timeout**: Automatic reconnection on disconnect

## Usage Examples

### Basic WebSocket Hook Usage

```typescript
import { useWebSocket } from "@/contexts/WebSocketContext";

function MyComponent() {
  const { isConnected, lastMessage, showNotification } = useWebSocket();

  useEffect(() => {
    if (lastMessage?.type === "leaderboard_updated") {
      // Handle leaderboard update
      refreshData();
    }
  }, [lastMessage]);
}
```

### Quiz Subscription

```typescript
const { subscribeToQuiz, unsubscribeFromQuiz } = useWebSocket();

useEffect(() => {
  // Subscribe when component mounts
  subscribeToQuiz(quizId);

  return () => {
    // Unsubscribe when component unmounts
    unsubscribeFromQuiz(quizId);
  };
}, [quizId]);
```

### Manual Notifications

```typescript
const { showNotification } = useWebSocket();

// Show custom notification
showNotification("Custom message", "success");
```

## Integration Points

### 1. Leaderboard Pages

- `/leaderboard` - Subject leaderboards with live updates
- `/quizzes/[id]` - Quiz-specific leaderboards with subscription

### 2. Authentication Flow

- Connects on login
- Disconnects on logout
- Handles token expiration

### 3. Data Synchronization

- Integrates with React Query
- Invalidates cache on updates
- Triggers automatic refetching

## Troubleshooting

### Connection Issues

1. Check WebSocket URL in environment variables
2. Verify backend WebSocket server is running
3. Check browser console for connection errors
4. Ensure JWT token is valid

### Missing Updates

1. Verify subscription to correct channels
2. Check message handling in components
3. Ensure React Query keys match
4. Validate backend message broadcasting

### Performance Considerations

- WebSocket reconnection uses exponential backoff
- Notifications auto-dismiss after 5 seconds
- Query invalidation is throttled by React Query
- Connection status updates are optimized

## Backend Integration

This frontend works with a Django Channels WebSocket consumer that:

- Handles JWT authentication
- Manages group subscriptions
- Broadcasts leaderboard updates
- Supports quiz-specific channels

The WebSocket endpoint expects:

```
ws://localhost:8000/ws/leaderboard/?token=<jwt_token>
```
