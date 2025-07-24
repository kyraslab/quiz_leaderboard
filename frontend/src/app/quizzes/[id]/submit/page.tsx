"use client";

import { useState, use } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { quizAPI } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";

interface SubmitQuizPageProps {
  params: Promise<{
    id: string;
  }>;
}

function SubmitQuizPageContent({ params }: SubmitQuizPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { user } = useAuth();

  const [score, setScore] = useState<number>(0);
  const [userStart, setUserStart] = useState<string>("");
  const [userEnd, setUserEnd] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitSessionMutation = useMutation({
    mutationFn: quizAPI.submitQuizSession,
    onSuccess: () => {
      setIsSubmitting(false);
      router.push(`/quizzes/${resolvedParams.id}`);
    },
    onError: (error) => {
      setIsSubmitting(false);
      console.error("Failed to submit quiz session:", error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      console.error("User not authenticated");
      return;
    }

    if (!userStart || !userEnd) {
      alert("Please fill in both start and end times");
      return;
    }

    setIsSubmitting(true);

    submitSessionMutation.mutate({
      user: user.id,
      quiz: resolvedParams.id,
      score: score,
      user_start: userStart,
      user_end: userEnd,
    });
  };

  const getCurrentDateTime = () => {
    const now = new Date();
    return now.toISOString().slice(0, 16); // Format for datetime-local input
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <h1 className="text-2xl font-bold text-center">
            Submit Quiz Session
          </h1>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="score"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Score (0-100)
              </label>
              <input
                type="number"
                id="score"
                min="0"
                max="100"
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label
                htmlFor="userStart"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Start Time
              </label>
              <input
                type="datetime-local"
                id="userStart"
                value={userStart}
                onChange={(e) => setUserStart(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <button
                type="button"
                onClick={() => setUserStart(getCurrentDateTime())}
                className="mt-1 text-sm text-blue-600 hover:text-blue-800"
              >
                Set to current time
              </button>
            </div>

            <div>
              <label
                htmlFor="userEnd"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                End Time
              </label>
              <input
                type="datetime-local"
                id="userEnd"
                value={userEnd}
                onChange={(e) => setUserEnd(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <button
                type="button"
                onClick={() => setUserEnd(getCurrentDateTime())}
                className="mt-1 text-sm text-blue-600 hover:text-blue-800"
              >
                Set to current time
              </button>
            </div>

            <div className="flex space-x-4">
              <Button
                type="button"
                onClick={() => router.push(`/quizzes/${resolvedParams.id}`)}
                variant="secondary"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting} className="flex-1">
                {isSubmitting ? "Submitting..." : "Submit Quiz Session"}
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}

export default function SubmitQuizPage({ params }: SubmitQuizPageProps) {
  return (
    <ProtectedRoute>
      <SubmitQuizPageContent params={params} />
    </ProtectedRoute>
  );
}
