"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useWebSocket } from "@/contexts/WebSocketContext";

export default function LogoutPage() {
  const { logout } = useAuth();
  const { showNotification } = useWebSocket();

  useEffect(() => {
    showNotification("You have been logged out successfully", "info");
    logout();
  }, [logout, showNotification]);

  return (
    <div className="text-center">
      <h1 className="text-2xl font-bold mb-4">Logging out...</h1>
      <p className="text-gray-600">You are being logged out. Please wait.</p>
    </div>
  );
}
