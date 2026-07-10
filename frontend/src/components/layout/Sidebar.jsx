import React from "react";
import { NavLink } from "react-router-dom";
import { Sliders, ShieldAlert, Cpu, HeartPulse } from "lucide-react";

export default function Sidebar() {
  const linkStyle = ({ isActive }) => ({
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "14px 20px",
    color: isActive ? "var(--bmw-blue)" : "var(--bmw-muted)",
    textDecoration: "none",
    fontWeight: isActive ? "700" : "400",
    fontSize: "13px",
    textTransform: "uppercase",
    letterSpacing: "1.5px",
    borderLeft: isActive ? "4px solid var(--bmw-blue)" : "4px solid transparent",
    backgroundColor: isActive ? "var(--bmw-canvas)" : "transparent",
    transition: "all 0.2s ease",
  });

  return (
    <aside className="bmw-sidebar">
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <NavLink to="/dashboard" style={linkStyle}>
          <Sliders size={16} />
          Control Center
        </NavLink>

        <NavLink to="/arena" style={linkStyle}>
          <Cpu size={16} />
          Turing Arena
        </NavLink>

        <NavLink to="/approvals" style={linkStyle}>
          <ShieldAlert size={16} />
          Override Queue
        </NavLink>
      </div>

      {/* Corporate footer info at sidebar bottom */}
      <div
        style={{
          position: "absolute",
          bottom: "20px",
          left: "20px",
          right: "20px",
          borderTop: "1px solid var(--bmw-hairline)",
          paddingTop: "16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--bmw-muted)" }}>
          <HeartPulse size={12} />
          <span style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px" }}>
            Version 1.0-dev
          </span>
        </div>
      </div>
    </aside>
  );
}
