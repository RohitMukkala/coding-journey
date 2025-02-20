import React, { createContext, useState, useContext, useEffect } from "react";
import axiosInstance from "../utils/axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const validateToken = async (token) => {
    try {
      const response = await axiosInstance.get("/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUser(response.data);
      return true;
    } catch (error) {
      console.error("Token validation error:", error);
      return false;
    }
  };

  const updateUser = async () => {
    try {
      const response = await axiosInstance.get("/me");
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error("Error updating user data:", error);
      return null;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        const isValid = await validateToken(token);
        setIsAuthenticated(isValid);
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (token) => {
    localStorage.setItem("token", token);
    const isValid = await validateToken(token);
    setIsAuthenticated(isValid);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, login, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
