import { createContext, useContext, useEffect, useState, useCallback } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("taskflow_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("taskflow_token");
    if (!token) {
      setLoading(false);
      return;
    }
    client
      .get("/auth/me")
      .then((res) => {
        setUser(res.data);
        localStorage.setItem("taskflow_user", JSON.stringify(res.data));
      })
      .catch(() => {
        localStorage.removeItem("taskflow_token");
        localStorage.removeItem("taskflow_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const res = await client.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("taskflow_token", res.data.access_token);
    localStorage.setItem("taskflow_user", JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data.user;
  }, []);

  const register = useCallback(async (email, username, password) => {
    const res = await client.post("/auth/register", { email, username, password });
    localStorage.setItem("taskflow_token", res.data.access_token);
    localStorage.setItem("taskflow_user", JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("taskflow_token");
    localStorage.removeItem("taskflow_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
