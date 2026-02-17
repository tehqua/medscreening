/**
 * App.jsx
 *
 * Root component. Manages authentication state and switches between
 * the LoginPage and ChatPage based on whether the user has a valid session.
 */

import React, { useState, useCallback } from "react";
import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";
import { login, logout, isAuthenticated, getStoredPatientId } from "./services/api";

export default function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated);
  const [patientId, setPatientId] = useState(getStoredPatientId);

  const handleLogin = useCallback(async (id) => {
    const data = await login(id);
    setPatientId(data.patient_id);
    setAuthenticated(true);
  }, []);

  const handleLogout = useCallback(async () => {
    await logout();
    setAuthenticated(false);
    setPatientId("");
  }, []);

  if (!authenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <ChatPage patientId={patientId} onLogout={handleLogout} />;
}
