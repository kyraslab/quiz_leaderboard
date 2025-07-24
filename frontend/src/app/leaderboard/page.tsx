"use client";

import { useState, useEffect } from "react";
import Cookies from "js-cookie";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { leaderboardAPI } from "@/lib/api";
import { SubjectLeaderboardEntry, SubjectLeaderboard } from "@/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useWebSocket } from "@/contexts/WebSocketContext";

enum BidangEnum {
  AST = "AST",
  BIO = "BIO",
  EKO = "EKO",
  FIS = "FIS",
  GEO = "GEO",
  INF = "INF",
  KBM = "KBM",
  KIM = "KIM",
  MAT = "MAT",
}

const subjects = [
  { bidang: BidangEnum.AST, bidang_name: "Astronomi" },
  { bidang: BidangEnum.BIO, bidang_name: "Biologi" },
  { bidang: BidangEnum.EKO, bidang_name: "Ekonomi" },
  { bidang: BidangEnum.FIS, bidang_name: "Fisika" },
  { bidang: BidangEnum.GEO, bidang_name: "Geografi" },
  { bidang: BidangEnum.INF, bidang_name: "Informatika" },
  { bidang: BidangEnum.KBM, bidang_name: "Kebumian" },
  { bidang: BidangEnum.KIM, bidang_name: "Kimia" },
  { bidang: BidangEnum.MAT, bidang_name: "Matematika" },
];

function LeaderboardPageContent() {
  const [selectedSubject, setSelectedSubject] = useState<BidangEnum>(
    subjects[0].bidang
  );
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const { isConnected, lastMessage, showNotification } = useWebSocket();
  const queryClient = useQueryClient();

  const { data: subjectLeaderboard, isLoading: subjectLoading } = useQuery({
    queryKey: ["leaderboard", "subject", selectedSubject],
    queryFn: () =>
      leaderboardAPI
        .getSubjectLeaderboard(selectedSubject!)
        .then((res) => res.data),
    enabled: !!selectedSubject,
  });

  // Handle WebSocket messages for auto-refresh
  useEffect(() => {
    if (lastMessage) {
      const shouldRefresh =
        lastMessage.type === "leaderboard_updated" ||
        lastMessage.type === "quiz_session_uploaded" ||
        lastMessage.type === "quiz_leaderboard_updated";

      if (shouldRefresh) {
        // Invalidate and refetch leaderboard data
        queryClient.invalidateQueries({
          queryKey: ["leaderboard", "subject", selectedSubject],
        });
        setLastUpdate(new Date());

        console.log(
          "Leaderboard auto-refreshed due to WebSocket message:",
          lastMessage.type
        );
      }
    }
  }, [lastMessage, queryClient, selectedSubject]);

  const isLoading = subjectLoading;
  const leaderboardData: SubjectLeaderboard | undefined = subjectLeaderboard;

  const handleSubjectChange = (bidang: BidangEnum) => {
    setSelectedSubject(bidang);
  };

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
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Leaderboard</h1>

        <div className="flex flex-wrap gap-2 mb-4">
          {subjects.map((subject) => (
            <Button
              key={subject.bidang}
              onClick={() => handleSubjectChange(subject.bidang)}
              variant={
                selectedSubject === subject.bidang ? "primary" : "secondary"
              }
              size="sm"
            >
              {subject.bidang_name}
            </Button>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Top 20 Leaderboard</h2>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? "bg-green-500" : "bg-red-500"
                  }`}
                ></div>
                <span>{isConnected ? "Live Updates" : "Disconnected"}</span>
              </div>
              <div className="text-xs">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardBody>
          {!selectedSubject ? (
            <div className="text-center py-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Select a Subject
              </h3>
              <p className="text-gray-500">
                Choose a subject above to view the leaderboard.
              </p>
            </div>
          ) : isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading leaderboard...</p>
            </div>
          ) : !leaderboardData || leaderboardData.leaderboard.length === 0 ? (
            <div className="text-center py-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                No Results Yet
              </h3>
              <p className="text-gray-500">No results for this subject yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-center py-3 px-4 font-semibold">
                      Rank
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Player
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Total Score
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Average Score
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Total Time
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Avg Time
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboardData.leaderboard.map(
                    (entry: SubjectLeaderboardEntry, index: number) => (
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
                        <td className="text-center py-3 px-4">
                          <span className="flex items-center">
                            {getRankIcon(index + 1)}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          {entry.username}
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className="font-bold text-blue-600">
                            {entry.total_score}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span
                            className={`font-bold ${
                              entry.average_score >= 90
                                ? "text-green-600"
                                : entry.average_score >= 70
                                ? "text-yellow-600"
                                : "text-red-600"
                            }`}
                          >
                            {entry.average_score.toFixed(1)}
                          </span>
                        </td>
                        <td className="text-center py-3 px-4 text-sm text-gray-600">
                          {formatTime(entry.total_duration)}
                        </td>
                        <td className="text-center py-3 px-4 text-sm text-gray-600">
                          {formatTime(entry.average_duration)}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

export default function LeaderboardPage() {
  return (
    <ProtectedRoute>
      <LeaderboardPageContent />
    </ProtectedRoute>
  );
}
