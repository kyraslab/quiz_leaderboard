"use client";

import { use } from "react";
import Cookies from "js-cookie";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { quizAPI, leaderboardAPI } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProtectedRoute from "@/components/ProtectedRoute";
import { Quiz, QuizLeaderboard, UserPerformance } from "@/types";

interface QuizPageProps {
  params: Promise<{
    id: string;
  }>;
}

function QuizPageContent({ params }: QuizPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();

  const { data: quiz, isLoading: quizLoading } = useQuery<Quiz>({
    queryKey: ["quiz", resolvedParams.id],
    queryFn: () =>
      quizAPI.getQuizById(resolvedParams.id).then((res) => res.data),
  });

  const { data: leaderboardData, isLoading: leaderboardLoading } =
    useQuery<QuizLeaderboard>({
      queryKey: ["leaderboard", "quiz", resolvedParams.id],
      queryFn: () =>
        leaderboardAPI
          .getQuizLeaderboard(resolvedParams.id)
          .then((res) => res.data),
    });

  const { data: userPerformance, isLoading: userPerformanceLoading } =
    useQuery<UserPerformance>({
      queryKey: ["userPerformance", "quiz", resolvedParams.id],
      queryFn: () =>
        leaderboardAPI.getUserRank(resolvedParams.id).then((res) => res.data),
      enabled: quiz?.already_attempted || false,
    });

  const isLoading = quizLoading || leaderboardLoading;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return "🥇";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return `#${rank}`;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {isLoading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading quiz details...</p>
        </div>
      ) : !quiz ? (
        <div className="text-center py-8">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Quiz not found
          </h3>
          <p className="text-gray-500">This quiz could not be found.</p>
        </div>
      ) : (
        <>
          <Card className="mb-8">
            <CardHeader>
              <h1 className="text-3xl text-center font-bold">{quiz.title}</h1>
            </CardHeader>
            <CardBody>
              {!quiz.is_active ? (
                <div className="text-center text-red-500 font-bold py-4">
                  This quiz is closed.
                </div>
              ) : quiz.already_attempted && quiz.attempt_details ? (
                <div>
                  <h3 className="text-xl font-bold text-center mb-4">
                    Your Performance
                  </h3>
                  <div className="flex justify-around text-center">
                    <div>
                      <p className="text-gray-500">Score</p>
                      <p className="text-2xl font-bold">
                        {quiz.attempt_details.score}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Time</p>
                      <p className="text-2xl font-bold">
                        {formatTime(quiz.attempt_details.duration)}
                      </p>
                    </div>
                    {userPerformance && (
                      <div>
                        <p className="text-gray-500">Rank</p>
                        <p className="text-2xl font-bold">
                          {getRankIcon(userPerformance.user_performance.rank)}
                        </p>
                        <p className="text-xs text-gray-400">
                          of{" "}
                          {userPerformance.user_performance.total_participants}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <Button
                  className="text-center w-full mb-4"
                  onClick={() => router.push(`/quizzes/${quiz.id}/submit`)}
                >
                  Submit My Performance
                </Button>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-2xl text-center font-bold">
                Top 20 Quiz Leaderboard
              </h2>
            </CardHeader>
            <CardBody>
              {!leaderboardData || leaderboardData.leaderboard.length === 0 ? (
                <div className="text-center py-8">
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">
                    No Results Yet
                  </h3>
                  <p className="text-gray-500">
                    Be the first to appear on the leaderboard!
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold">
                          Rank
                        </th>
                        <th className="text-left py-3 px-4 font-semibold">
                          Player
                        </th>
                        <th className="text-left py-3 px-4 font-semibold">
                          Score
                        </th>
                        <th className="text-left py-3 px-4 font-semibold">
                          Time
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {leaderboardData.leaderboard.map((entry, index) => (
                        <tr
                          key={entry.id}
                          className={`border-b border-gray-100 ${
                            index + 1 <= 3
                              ? "bg-yellow-50 hover:bg-yellow-100"
                              : ""
                          } ${
                            Cookies.get("username") === entry.username
                              ? "font-bold bg-blue-100 hover:bg-blue-200"
                              : "hover:bg-gray-50"
                          }`}
                        >
                          <td className="py-3 px-4">
                            <span className="flex items-center">
                              {getRankIcon(index + 1)}
                            </span>
                          </td>
                          <td className="py-3 px-4">{entry.username}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`font-bold ${
                                entry.score >= 90
                                  ? "text-green-600"
                                  : entry.score >= 70
                                  ? "text-yellow-600"
                                  : "text-red-600"
                              }`}
                            >
                              {entry.score}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {formatTime(entry.duration)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardBody>
          </Card>
        </>
      )}
    </div>
  );
}

export default function QuizPage({ params }: QuizPageProps) {
  return (
    <ProtectedRoute>
      <QuizPageContent params={params} />
    </ProtectedRoute>
  );
}
