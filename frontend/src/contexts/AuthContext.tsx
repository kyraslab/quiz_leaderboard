"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";
import { User } from "@/types";

interface JWTPayload {
  user_id: string;
  username: string;
  exp: number;
  iat: number;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string, username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const decodeTokenAndSetUser = (token: string, username: string) => {
    try {
      const decoded = jwtDecode<JWTPayload>(token);

      if (decoded.exp * 1000 < Date.now()) {
        console.log("Token is expired");
        Cookies.remove("token");
        setUser(null);
        setIsAuthenticated(false);
        return;
      }

      const userData: User = {
        id: decoded.user_id,
        username: username,
      };

      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Error decoding token:", error);
      Cookies.remove("token");
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    setIsLoading(true);
    const token = Cookies.get("token");
    const username = Cookies.get("username");

    if (token) {
      decodeTokenAndSetUser(token, username ? username : "");
    } else {
      setUser(null);
      setIsAuthenticated(false);
    }

    setIsLoading(false);
  }, []);

  const login = (token: string, username: string) => {
    decodeTokenAndSetUser(token, username);
    Cookies.set("token", token, { expires: 7 });
    Cookies.set("username", username, { expires: 7 });
  };

  const logout = () => {
    Cookies.remove("token");
    Cookies.remove("username");
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = "/";
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
