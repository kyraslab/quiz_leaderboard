"use client";

import { useWebSocket } from "@/contexts/WebSocketContext";

export default function WebSocketStatus() {
  const { isConnected, lastMessage } = useWebSocket();

  return (
    <div className="fixed bottom-4 left-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm">
      <div className="flex items-center space-x-2 mb-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected ? "bg-green-500" : "bg-red-500"
          }`}
        ></div>
        <span className="text-sm font-medium">
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>
      {lastMessage && (
        <div className="text-xs text-gray-600">
          <div>Last: {lastMessage.type}</div>
          {lastMessage.message && (
            <div className="mt-1 text-gray-500 truncate">
              {lastMessage.message}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
