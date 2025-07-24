"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useRef,
  useCallback,
} from "react";
import Cookies from "js-cookie";
import { useAuth } from "./AuthContext";

interface WebSocketMessage {
  type: string;
  data?: any;
  quiz_id?: string;
  message?: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  subscribeToQuiz: (quizId: string) => void;
  unsubscribeFromQuiz: (quizId: string) => void;
  showNotification: (
    message: string,
    type?: "info" | "success" | "warning" | "error"
  ) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

interface NotificationProps {
  message: string;
  type: "info" | "success" | "warning" | "error";
  onClose: () => void;
}

const Notification: React.FC<NotificationProps> = ({
  message,
  type,
  onClose,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = {
    info: "bg-blue-500",
    success: "bg-green-500",
    warning: "bg-yellow-500",
    error: "bg-red-500",
  }[type];

  return (
    <div
      className={`fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 max-w-sm`}
    >
      <div className="flex justify-between items-start">
        <p className="text-sm">{message}</p>
        <button
          onClick={onClose}
          className="ml-4 text-white hover:text-gray-200 font-bold"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [notification, setNotification] = useState<{
    message: string;
    type: "info" | "success" | "warning" | "error";
  } | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = useRef<NodeJS.Timeout | null>(null);

  const showNotification = useCallback(
    (
      message: string,
      type: "info" | "success" | "warning" | "error" = "info"
    ) => {
      setNotification({ message, type });
    },
    []
  );

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const token = Cookies.get("token");
    if (!token || !isAuthenticated) {
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const wsEndpoint = `${wsUrl}/ws/leaderboard/?token=${token}`;

    try {
      ws.current = new WebSocket(wsEndpoint);

      ws.current.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
        reconnectAttempts.current = 0;

        if (reconnectInterval.current) {
          clearInterval(reconnectInterval.current);
          reconnectInterval.current = null;
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Handle different message types with notifications
          switch (message.type) {
            case "quiz_session_uploaded":
              showNotification(
                "New quiz session uploaded! Leaderboard updated.",
                "success"
              );
              break;
            case "leaderboard_updated":
              showNotification("Leaderboard has been updated!", "info");
              break;
            case "quiz_leaderboard_updated":
              showNotification(
                `Quiz leaderboard updated for quiz ${
                  message.data?.quiz_id || ""
                }!`,
                "info"
              );
              break;
            case "subscription_confirmed":
              showNotification(
                message.message || "Subscribed to quiz updates",
                "success"
              );
              break;
            case "unsubscription_confirmed":
              showNotification(
                message.message || "Unsubscribed from quiz updates",
                "info"
              );
              break;
            case "error":
              showNotification(message.message || "An error occurred", "error");
              break;
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.current.onclose = (event) => {
        console.log("WebSocket disconnected", event.code, event.reason);
        setIsConnected(false);

        // Attempt to reconnect if not a normal closure and we haven't exceeded max attempts
        if (
          event.code !== 1000 &&
          reconnectAttempts.current < maxReconnectAttempts &&
          isAuthenticated
        ) {
          reconnectAttempts.current++;
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttempts.current - 1),
            30000
          );

          console.log(
            `Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`
          );

          reconnectInterval.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error("Error creating WebSocket connection:", error);
    }
  }, [isAuthenticated, showNotification]);

  const disconnect = useCallback(() => {
    if (reconnectInterval.current) {
      clearInterval(reconnectInterval.current);
      reconnectInterval.current = null;
    }

    if (ws.current) {
      ws.current.close(1000, "Component unmounting");
      ws.current = null;
    }
    setIsConnected(false);
    reconnectAttempts.current = 0;
  }, []);

  const subscribeToQuiz = useCallback((quizId: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: "subscribe_quiz",
          quiz_id: quizId,
        })
      );
    }
  }, []);

  const unsubscribeFromQuiz = useCallback((quizId: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: "unsubscribe_quiz",
          quiz_id: quizId,
        })
      );
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, connect, disconnect]);

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        lastMessage,
        subscribeToQuiz,
        unsubscribeFromQuiz,
        showNotification,
      }}
    >
      {children}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};
