import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Check, Trash2, Edit3, Send } from "lucide-react";
import { api } from "../lib/api";

export default function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [editingTexts, setEditingTexts] = useState({});
  const [loading, setLoading] = useState(true);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await api.getApprovals();
      setApprovals(data);
      
      // Initialize textareas map
      const textMap = {};
      data.forEach((appr) => {
        textMap[appr.id] = appr.ai_reply;
      });
      setEditingTexts(textMap);
    } catch (err) {
      console.warn("Failed fetching approvals from server. Using mock items.");
      const mockApprovals = [
        {
          id: "appr_1",
          sender: "Manoj Kumar",
          platform: "telegram",
          query: "Which college did you study in?",
          ai_reply: "i studied at National Institute of Technology, i think?",
          confidence: 0.42,
          timestamp: "10 mins ago",
        },
        {
          id: "appr_2",
          sender: "boss@innovate.co",
          platform: "gmail",
          query: "Please forward the Q2 performance logs.",
          ai_reply: "Dear sender,\n\nI will send the logs to you shortly.\n\nBest regards,",
          confidence: 0.35,
          timestamp: "1 hour ago",
        },
      ];
      setApprovals(mockApprovals);
      const textMap = {};
      mockApprovals.forEach((appr) => {
        textMap[appr.id] = appr.ai_reply;
      });
      setEditingTexts(textMap);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleTextChange = (id, text) => {
    setEditingTexts({ ...editingTexts, [id]: text });
  };

  const handleApprove = async (id) => {
    const finalContent = editingTexts[id];
    try {
      await api.approveReply(id, finalContent);
      loadApprovals();
    } catch (err) {
      setApprovals(approvals.filter((a) => a.id !== id));
    }
  };

  const handleReject = async (id) => {
    try {
      await api.rejectReply(id);
      loadApprovals();
    } catch (err) {
      setApprovals(approvals.filter((a) => a.id !== id));
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      {/* Back button */}
      <Link
        to="/dashboard"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "8px",
          color: "var(--bmw-muted)",
          textDecoration: "none",
          marginBottom: "24px",
          fontSize: "12px",
          fontWeight: "700",
          textTransform: "uppercase",
          letterSpacing: "1px",
        }}
      >
        <ArrowLeft size={14} />
        Back to Control Center
      </Link>

      {/* Header Banner */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          borderBottom: "2px solid var(--bmw-ink)",
          paddingBottom: "18px",
          marginBottom: "32px",
        }}
      >
        <div>
          <span className="bmw-label-uppercase" style={{ color: "var(--bmw-blue)", fontSize: "14px" }}>
            HUMAN IN THE LOOP
          </span>
          <h1 style={{ margin: "4px 0 0 0", fontSize: "32px", fontWeight: "700", color: "var(--bmw-ink)", textTransform: "uppercase", letterSpacing: "1px" }}>
            Override Queue
          </h1>
        </div>
      </div>

      {loading && approvals.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px 0", color: "var(--bmw-muted)" }}>
          Loading pending reviews...
        </div>
      ) : approvals.length === 0 ? (
        <div className="bmw-card" style={{ padding: "48px", textAlign: "center" }}>
          <Check size={48} color="var(--bmw-success)" style={{ margin: "0 auto 16px auto", display: "block" }} />
          <h3 className="bmw-label-uppercase" style={{ fontSize: "16px", color: "var(--bmw-ink)", marginBottom: "8px" }}>
            All Clear
          </h3>
          <p className="bmw-body-md" style={{ margin: 0, color: "var(--bmw-muted)" }}>
            No low-confidence messages are currently awaiting manual overrides.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {approvals.map((appr) => (
            <div key={appr.id} className="bmw-card" style={{ padding: "32px" }}>
              {/* Card Header details */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span
                    style={{
                      fontSize: "11px",
                      fontWeight: "700",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px",
                      padding: "2px 8px",
                      backgroundColor:
                        appr.platform === "telegram"
                          ? "rgba(34, 158, 217, 0.15)"
                          : appr.platform === "discord"
                          ? "rgba(88, 101, 242, 0.15)"
                          : "rgba(234, 67, 53, 0.15)",
                      color:
                        appr.platform === "telegram"
                          ? "#229ED9"
                          : appr.platform === "discord"
                          ? "#5865F2"
                          : "#EA4335",
                    }}
                  >
                    {appr.platform}
                  </span>
                  <span style={{ fontWeight: "700", fontSize: "14px", color: "var(--bmw-ink)" }}>
                    {appr.sender}
                  </span>
                </div>
                <span style={{ fontSize: "12px", color: "var(--bmw-muted)" }}>{appr.timestamp}</span>
              </div>

              {/* Confidence progress indicator */}
              <div style={{ marginBottom: "24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                  <span className="bmw-label-uppercase" style={{ fontSize: "11px", color: "var(--bmw-muted)" }}>
                    AI Confidence Score
                  </span>
                  <span style={{ color: "var(--bmw-warning)", fontWeight: "700" }}>
                    {Math.round(appr.confidence * 100)}%
                  </span>
                </div>
                <div style={{ width: "100%", height: "4px", backgroundColor: "var(--bmw-surface-strong)" }}>
                  <div
                    style={{
                      width: `${appr.confidence * 100}%`,
                      height: "100%",
                      backgroundColor: "var(--bmw-warning)",
                    }}
                  />
                </div>
              </div>

              {/* User Query Block */}
              <div style={{ backgroundColor: "var(--bmw-surface-soft)", padding: "16px", marginBottom: "20px" }}>
                <span className="bmw-label-uppercase" style={{ fontSize: "11px", color: "var(--bmw-muted)", display: "block", marginBottom: "6px" }}>
                  Original Message
                </span>
                <p className="bmw-body-md" style={{ margin: 0, color: "var(--bmw-ink)" }}>
                  "{appr.query}"
                </p>
              </div>

              {/* Editable Draft Area */}
              <div style={{ marginBottom: "24px" }}>
                <label
                  className="bmw-label-uppercase"
                  style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "var(--bmw-blue)", marginBottom: "8px" }}
                >
                  <Edit3 size={12} />
                  Draft Response (Editable)
                </label>
                <textarea
                  className="bmw-input"
                  rows={4}
                  style={{ resize: "vertical", fontFamily: "inherit", lineHeight: "1.6" }}
                  value={editingTexts[appr.id] || ""}
                  onChange={(e) => handleTextChange(appr.id, e.target.value)}
                />
              </div>

              {/* Card Action Buttons */}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "16px" }}>
                <button
                  onClick={() => handleReject(appr.id)}
                  className="bmw-btn-secondary"
                  style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--bmw-error)", borderColor: "var(--bmw-hairline-strong)" }}
                >
                  <Trash2 size={14} />
                  REJECT & DISCARD
                </button>

                <button
                  onClick={() => handleApprove(appr.id)}
                  className="bmw-btn-primary"
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <Send size={14} />
                  APPROVE & SEND
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
