"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { WebSocketProvider } from "@/contexts/WebSocketContext";
import Navbar from "@/components/Navbar";
import { useState } from "react";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WebSocketProvider>
          <div className="min-h-screen bg-teal-50">
            <Navbar />
            <main className="container mx-auto px-4 py-8">{children}</main>
          </div>
        </WebSocketProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
