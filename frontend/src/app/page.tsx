"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-teal-800 mb-4">
          Welcome to Sparing Mingguan
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Test your knowledge, compete with others, and climb the leaderboard!
        </p>

        {isAuthenticated ? (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-8">
            Welcome back, {user?.username}! Ready for your next challenge?
          </div>
        ) : (
          <div className="space-x-4">
            <Link href="/register">
              <Button variant="primary" size="lg">
                Get Started
              </Button>
            </Link>
          </div>
        )}
      </div>

      <Card>
        <CardHeader className="">
          <h2 className="text-2xl font-bold text-teal-600 text-center">
            How it works
          </h2>
        </CardHeader>
        <CardBody>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 font-bold">1</span>
              </div>
              <h4 className="font-semibold mb-2 text-green-600">Sign Up</h4>
              <p className="text-sm text-gray-600">
                Create your account to get started
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 font-bold">2</span>
              </div>
              <h4 className="font-semibold mb-2 text-green-600">Choose Quiz</h4>
              <p className="text-sm text-gray-600">
                Browse and select a quiz to take
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 font-bold">3</span>
              </div>
              <h4 className="font-semibold mb-2 text-green-600">Take Quiz</h4>
              <p className="text-sm text-gray-600">
                Answer questions and submit your results
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 font-bold">4</span>
              </div>
              <h4 className="font-semibold mb-2 text-green-600">Compete</h4>
              <p className="text-sm text-gray-600">
                See your ranking on the leaderboard
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
