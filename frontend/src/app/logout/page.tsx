"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function LogoutPage() {
  const { logout } = useAuth();

  useEffect(() => {
    logout();
  }, [logout]);

  return (
    <div className="text-center">
      <h1 className="text-2xl font-bold mb-4">Logging out...</h1>
      <p className="text-gray-600">You are being logged out. Please wait.</p>
    </div>
  );
}
