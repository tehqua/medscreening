/**
 * TopBar.jsx
 *
 * Header bar for the chat dashboard.
 * Shows system status, the patient's short ID, help button and avatar.
 */

import React from "react";
import { shortPatientId, patientInitials } from "../services/api";

const s = {
  bar: {
    height: "3.75rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 2rem",
    background: "rgba(255,255,255,0.72)",
    backdropFilter: "blur(14px)",
    WebkitBackdropFilter: "blur(14px)",
    borderBottom: "1px solid rgba(226,232,240,0.6)",
    flexShrink: 0,
    zIndex: 10,
  },

  status: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
  },

  dot: {
    width: "0.5rem",
    height: "0.5rem",
    borderRadius: "9999px",
    background: "#22c55e",
    animation: "pulse 2s ease infinite",
  },

  statusLabel: {
    fontSize: "0.6875rem",
    fontWeight: 600,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: "#64748b",
  },

  right: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
  },

  pidBadge: {
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
    padding: "0.3rem 0.75rem",
    background: "rgba(255,255,255,0.55)",
    border: "1px solid rgba(226,232,240,0.7)",
    borderRadius: "9999px",
    boxShadow: "0 1px 3px rgba(15,23,42,0.04)",
  },

  pidText: {
    fontSize: "0.8125rem",
    fontFamily: "monospace",
    color: "#475569",
    fontWeight: 500,
  },

  helpBtn: {
    padding: "0.35rem",
    border: "none",
    background: "transparent",
    color: "#94a3b8",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    borderRadius: "9999px",
    transition: "color 140ms ease, background 140ms ease",
  },

  avatar: {
    width: "2.125rem",
    height: "2.125rem",
    borderRadius: "9999px",
    background: "linear-gradient(135deg, #14b8a6, #3b82f6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#ffffff",
    fontSize: "0.75rem",
    fontWeight: 700,
    boxShadow: "0 2px 6px rgba(20,184,166,0.35)",
    flexShrink: 0,
    cursor: "default",
    userSelect: "none",
  },
};

export default function TopBar({ patientId }) {
  return (
    <header style={s.bar}>
      <div style={s.status}>
        <div style={s.dot} />
        <span style={s.statusLabel}>System Active</span>
      </div>

      <div style={s.right}>
        <div style={s.pidBadge}>
          <span className="material-symbols-outlined" style={{ fontSize: "1rem", color: "#94a3b8" }}>
            badge
          </span>
          <span style={s.pidText}>{shortPatientId(patientId)}</span>
        </div>

        <button
          style={s.helpBtn}
          title="Help"
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "#0d9488";
            e.currentTarget.style.background = "rgba(204,251,241,0.3)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "#94a3b8";
            e.currentTarget.style.background = "transparent";
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: "1.25rem" }}>
            help
          </span>
        </button>

        <div style={s.avatar} title={patientId}>
          {patientInitials(patientId)}
        </div>
      </div>
    </header>
  );
}
