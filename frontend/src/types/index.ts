export interface User {
  id: string;
  username: string;
}

export interface Quiz {
  id: number;
  title: string;
  bidang: string;
  bidang_name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  already_attempted: boolean;
  attempt_details: QuizLeaderboardEntry | null;
}

export interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
}

export interface QuizSession {
  id: string;
  userId: string;
  quizId: string;
  score: number;
  startTime: string;
  endTime: string;
  createdAt: string;
}

export interface SubjectLeaderboardEntry {
  id: string;
  user_id: string;
  username: string;
  total_score: number;
  quiz_count: number;
  average_score: number;
  total_duration: number;
  average_duration: number;
}

export interface QuizLeaderboardEntry {
  id: string;
  user_id: string;
  username: string;
  score: number;
  quiz_count: number;
  duration: number;
}

export interface SubjectLeaderboard {
  bidang_name: string;
  leaderboard: SubjectLeaderboardEntry[];
}

export interface QuizLeaderboard {
  bidang_name: string;
  leaderboard: QuizLeaderboardEntry[];
}

export interface UserPerformance {
  quiz_id: number;
  quiz_title: string;
  user_performance: {
    user_id: number;
    username: string;
    session: {
      id: number;
      score: number;
      duration: number;
      user_start: string;
      user_end: string;
    };
    rank: number;
    total_participants: number;
  };
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
