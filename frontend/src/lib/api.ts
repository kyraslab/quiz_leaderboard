import axios from "axios";
import Cookies from "js-cookie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove("token");
      window.location.href = "/login/";
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post("/auth/register/", data),
  loginWithUsername: (data: { username: string; password: string }) =>
    api.post("/auth/login/", data),
  logout: () => api.post("/auth/logout/"),
};

export const quizAPI = {
  getAllQuizzes: (
    activeOnly?: boolean,
    page?: number,
    pageSize: number = 10
  ) => {
    const params = new URLSearchParams();
    if (activeOnly) {
      params.set("active_only", "true");
    }
    if (page) {
      params.set("page", page.toString());
    }
    params.set("page_size", pageSize.toString());
    return api.get(`/api/quizzes/?${params.toString()}`);
  },
  getQuizById: (id: string) => api.get(`/api/quizzes/${id}`),
  submitQuizSession: (data: {
    user: string;
    quiz: string;
    score: number;
    user_start: string;
    user_end: string;
  }) => api.post("/api/quiz-sessions/", data),
};

export const leaderboardAPI = {
  getQuizLeaderboard: (quizId: string) => {
    return api.get(`/api/cached/leaderboard/quiz/${quizId}/`);
  },
  getSubjectLeaderboard: (bidang: string) => {
    return api.get(`/api/cached/leaderboard/subject/?bidang=${bidang}`);
  },
  getUserRank: (quizId: string) =>
    api.get(`/api/cached/leaderboard/quiz/${quizId}/user-performance/`),
};
