/**
 * LoginPage.jsx
 *
 * Patient login screen. Accepts the Patient ID in the format
 * FirstName###_LastName###_uuid (validated by the backend).
 */

import React, { useState } from "react";

const styles = {
  root: {
    position: "relative",
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "1rem",
    overflow: "hidden",
  },

  // Subtle mesh background
  bg: {
    position: "absolute",
    inset: 0,
    background:
      "radial-gradient(ellipse 80% 60% at 20% 10%, rgba(204,251,241,0.55) 0%, transparent 60%)," +
      "radial-gradient(ellipse 60% 60% at 80% 80%, rgba(224,242,254,0.45) 0%, transparent 60%)," +
      "linear-gradient(160deg, #f0fdf9 0%, #f8fafc 50%, #eff6ff 100%)",
    zIndex: 0,
  },

  card: {
    position: "relative",
    zIndex: 1,
    width: "100%",
    maxWidth: "420px",
    background: "rgba(255,255,255,0.82)",
    backdropFilter: "blur(18px)",
    WebkitBackdropFilter: "blur(18px)",
    border: "1px solid rgba(255,255,255,0.75)",
    borderRadius: "1.75rem",
    padding: "2.5rem 2.25rem 2rem",
    boxShadow:
      "0 4px 32px -6px rgba(15,23,42,0.10), 0 1px 4px rgba(15,23,42,0.04)",
    animation: "fadeUp 0.45s ease both",
  },

  logoWrap: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginBottom: "2rem",
    gap: "0.5rem",
  },

  logoIcon: {
    width: "3.25rem",
    height: "3.25rem",
    borderRadius: "0.875rem",
    background: "linear-gradient(135deg, #ccfbf1 0%, #ffffff 100%)",
    border: "1px solid rgba(20,184,166,0.2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "0.5rem",
    boxShadow: "0 2px 8px rgba(13,148,136,0.12)",
  },

  logoIconSymbol: {
    fontSize: "1.75rem",
    color: "#0f766e",
  },

  logoTitle: {
    fontFamily: "var(--font-display)",
    fontSize: "2rem",
    fontWeight: 400,
    color: "#0f172a",
    letterSpacing: "-0.02em",
  },

  logoSubtitle: {
    fontFamily: "var(--font-display)",
    fontStyle: "italic",
    fontSize: "0.8125rem",
    color: "#0d9488",
    letterSpacing: "0.08em",
  },

  tagline: {
    fontSize: "0.875rem",
    color: "#64748b",
    textAlign: "center",
    lineHeight: 1.6,
    maxWidth: "280px",
    margin: "0 auto 1.75rem",
  },

  fieldGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
    marginBottom: "0.75rem",
  },

  label: {
    fontSize: "0.7rem",
    fontWeight: 600,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: "#475569",
    paddingLeft: "0.25rem",
  },

  inputWrap: {
    position: "relative",
    display: "flex",
    alignItems: "center",
  },

  inputIcon: {
    position: "absolute",
    left: "0.875rem",
    color: "#0d9488",
    fontSize: "1.25rem",
    pointerEvents: "none",
  },

  input: {
    width: "100%",
    padding: "0.8rem 1rem 0.8rem 2.75rem",
    fontSize: "0.9375rem",
    fontFamily: "var(--font-body)",
    fontWeight: 500,
    color: "#0f172a",
    background: "rgba(255,255,255,0.85)",
    border: "1px solid #e2e8f0",
    borderRadius: "0.75rem",
    outline: "none",
    transition: "border-color 220ms ease, box-shadow 220ms ease",
    boxShadow: "0 1px 3px rgba(15,23,42,0.04)",
  },

  inputFocusBorder: "1px solid #14b8a6",
  inputFocusShadow: "0 0 0 3px rgba(20,184,166,0.12), 0 1px 3px rgba(15,23,42,0.04)",

  button: {
    width: "100%",
    padding: "0.875rem 1rem",
    marginTop: "0.5rem",
    fontSize: "0.9375rem",
    fontWeight: 600,
    fontFamily: "var(--font-body)",
    color: "#ffffff",
    background: "linear-gradient(135deg, #0f766e 0%, #0d9488 60%, #14b8a6 100%)",
    border: "none",
    borderRadius: "0.875rem",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.5rem",
    boxShadow: "0 4px 14px rgba(13,148,136,0.38)",
    transition: "opacity 200ms ease, transform 200ms ease, box-shadow 200ms ease",
  },

  buttonDisabled: {
    opacity: 0.65,
    cursor: "not-allowed",
    transform: "none",
  },

  forgotLink: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.35rem",
    marginTop: "0.75rem",
    fontSize: "0.875rem",
    fontWeight: 500,
    color: "#64748b",
    textDecoration: "none",
    cursor: "pointer",
    background: "none",
    border: "none",
    transition: "color 150ms ease",
  },

  divider: {
    height: "1px",
    background: "#f1f5f9",
    margin: "1.25rem 0",
  },

  footer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.625rem",
  },

  badge: {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.375rem",
    padding: "0.25rem 0.75rem",
    borderRadius: "9999px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    fontSize: "0.7rem",
    fontWeight: 700,
    color: "#475569",
    letterSpacing: "0.04em",
  },

  badgeIcon: {
    fontSize: "0.875rem",
    color: "#22c55e",
  },

  footerText: {
    fontSize: "0.6875rem",
    color: "#94a3b8",
    textAlign: "center",
    lineHeight: 1.5,
  },

  errorBox: {
    padding: "0.625rem 0.875rem",
    borderRadius: "0.625rem",
    background: "rgba(254,242,242,0.9)",
    border: "1px solid #fecaca",
    fontSize: "0.8125rem",
    color: "#dc2626",
    marginBottom: "0.5rem",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
  },
};

export default function LoginPage({ onLogin }) {
  const [patientId, setPatientId] = useState("");
  const [focused, setFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!patientId.trim() || loading) return;

    setLoading(true);
    setError("");
    try {
      await onLogin(patientId.trim());
    } catch (err) {
      setError(err.message || "Invalid Patient ID. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.root}>
      <div style={styles.bg} />

      <div style={styles.card} className="fade-up">
        {/* Logo area */}
        <div style={styles.logoWrap}>
          <div style={styles.logoIcon}>
            <span
              className="material-symbols-outlined"
              style={styles.logoIconSymbol}
            >
              medical_services
            </span>
          </div>
          <span style={styles.logoTitle}>MedScreening</span>
          <span style={styles.logoSubtitle}>Patient Portal</span>
        </div>

        <p style={styles.tagline}>
          Welcome back. Please enter your details to access your AI health
          summary.
        </p>

        <form onSubmit={handleSubmit}>
          {error && (
            <div style={styles.errorBox}>
              <span className="material-symbols-outlined" style={{ fontSize: "1rem" }}>
                error
              </span>
              {error}
            </div>
          )}

          <div style={styles.fieldGroup}>
            <label style={styles.label} htmlFor="patient-id">
              Patient ID
            </label>
            <div style={styles.inputWrap}>
              <span
                className="material-symbols-outlined"
                style={styles.inputIcon}
              >
                id_card
              </span>
              <input
                id="patient-id"
                type="text"
                value={patientId}
                placeholder="e.g. Adam631_Cronin387_aff8f143..."
                autoComplete="off"
                required
                style={{
                  ...styles.input,
                  ...(focused
                    ? {
                        border: styles.inputFocusBorder,
                        boxShadow: styles.inputFocusShadow,
                      }
                    : {}),
                }}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                onChange={(e) => setPatientId(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !patientId.trim()}
            style={{
              ...styles.button,
              ...(loading || !patientId.trim() ? styles.buttonDisabled : {}),
            }}
            onMouseEnter={(e) => {
              if (!loading && patientId.trim()) {
                e.currentTarget.style.opacity = "0.9";
                e.currentTarget.style.transform = "translateY(-1px)";
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "1";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            {loading ? (
              <>
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: "1.1rem", animation: "spin 1s linear infinite" }}
                >
                  progress_activity
                </span>
                Verifying...
              </>
            ) : (
              <>
                Secure Login
                <span className="material-symbols-outlined" style={{ fontSize: "1.1rem" }}>
                  arrow_forward
                </span>
              </>
            )}
          </button>

          <button type="button" style={styles.forgotLink}>
            <span className="material-symbols-outlined" style={{ fontSize: "1rem", color: "#94a3b8" }}>
              help
            </span>
            Help: Forgot ID?
          </button>
        </form>

        <div style={styles.divider} />

        <div style={styles.footer}>
          <span style={styles.badge}>
            <span className="material-symbols-outlined" style={styles.badgeIcon}>
              lock
            </span>
            256-bit SSL Encrypted
          </span>
          <p style={styles.footerText}>
            Authorized Patient Use Only.
            <br />
            <span style={{ color: "#64748b", cursor: "pointer" }}>Privacy Policy</span>
            {" · "}
            <span style={{ color: "#64748b", cursor: "pointer" }}>Terms of Service</span>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
