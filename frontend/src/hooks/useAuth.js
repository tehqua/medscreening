/**
 * useAuth.js
 *
 * Manages authentication state across the application.
 * Components use this hook to access login / logout and the current user.
 */

import { useState, useCallback } from "react";
import { login as apiLogin, logout as apiLogout, isAuthenticated, getStoredPatientId } from "../services/api";

export function useAuth() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated);
  const [patientId, setPatientId] = useState(getStoredPatientId);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (id) => {
    setLoading(true);
    setError("");
    try {
      const data = await apiLogin(id);
      setPatientId(data.patient_id);
      setAuthenticated(true);
    } catch (err) {
      setError(err.message || "Login failed. Check your Patient ID.");
      setAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setAuthenticated(false);
    setPatientId("");
  }, []);

  return { authenticated, patientId, login, logout, error, loading };
}
