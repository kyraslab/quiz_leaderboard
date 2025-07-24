"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { quizAPI } from "@/lib/api";
import { Quiz } from "@/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";

function QuizzesPageContent() {
  const [showActiveOnly, setShowActiveOnly] = useState(true);
  const {
    data: quizzes,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["quizzes", showActiveOnly],
    queryFn: () =>
      quizAPI.getAllQuizzes(showActiveOnly).then((res) => {
        console.log("API Response:", res.data);
        // Handle paginated response - extract results array
        if (res.data && res.data.results && Array.isArray(res.data.results)) {
          return res.data.results;
        }
        // If it's already an array, return as is
        if (Array.isArray(res.data)) {
          return res.data;
        }
        // If neither, return empty array
        return [];
      }),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-600">Loading quizzes...</p>
      </div>
    );
  }

  if (error) {
    console.error("Error loading quizzes:", error);
    return (
      <div className="text-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <h2 className="font-bold">Error Loading Quizzes</h2>
          <p>Unable to load quizzes. Please try again later.</p>
          <p className="text-sm mt-2">
            Error: {error instanceof Error ? error.message : "Unknown error"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Available Quizzes
        </h1>
        <p className="text-gray-600">Choose a quiz to test your knowledge</p>

        {/* Filter buttons */}
        <div className="mt-4 flex gap-2">
          <Button
            onClick={() => setShowActiveOnly(true)}
            variant={showActiveOnly ? "primary" : "secondary"}
            size="sm"
          >
            Active Quizzes
          </Button>
          <Button
            onClick={() => setShowActiveOnly(false)}
            variant={!showActiveOnly ? "primary" : "secondary"}
            size="sm"
          >
            All Quizzes
          </Button>
        </div>
      </div>

      {!quizzes || quizzes.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No Quizzes Available
            </h3>
            <p className="text-gray-500">
              {showActiveOnly
                ? "No active quizzes at the moment. Check back later!"
                : "No quizzes found."}
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.map((quiz: Quiz) => (
            <Link href={`/quizzes/${quiz.id}`}>
              <Card
                key={quiz.id}
                className="hover:shadow-lg hover:cursor-pointer transition-shadow"
              >
                <CardHeader>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {quiz.title}
                    </h3>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        quiz.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {quiz.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm">
                    {quiz.bidang_name} ({quiz.bidang})
                  </p>
                </CardHeader>
                <CardBody>
                  <div className="space-y-2 mb-4">
                    <div className="text-sm text-gray-500">
                      <strong>Start:</strong>{" "}
                      {new Date(quiz.start_date).toLocaleDateString()}{" "}
                      {new Date(quiz.start_date).toLocaleTimeString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      <strong>End:</strong>{" "}
                      {new Date(quiz.end_date).toLocaleDateString()}{" "}
                      {new Date(quiz.end_date).toLocaleTimeString()}
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function QuizzesPage() {
  return <QuizzesPageContent />;
}
