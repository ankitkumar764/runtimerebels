import React from "react";
import { useNavigate } from "react-router-dom";
import { Bot, Zap, ShieldCheck, ArrowRight, MessageSquare, Mail, MessageCircle } from "lucide-react";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{ 
      minHeight: "100vh", 
      backgroundColor: "var(--bmw-canvas)",
      color: "var(--bmw-ink)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "60px 24px",
      boxSizing: "border-box"
    }}>
      {/* Brand Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "40px" }}>
        <div style={{
          width: "44px",
          height: "44px",
          borderRadius: "50%",
          border: "2px solid var(--bmw-blue)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--bmw-blue)",
          fontWeight: "800",
          fontSize: "20px",
        }}>
          D
        </div>
        <div>
          <span className="bmw-label-uppercase" style={{ fontSize: "18px", letterSpacing: "2.5px" }}>
            DIGITAL TWIN
          </span>
          <span style={{ fontSize: "18px", fontWeight: "300", color: "var(--bmw-muted)", marginLeft: "8px" }}>
            | Autopilot
          </span>
        </div>
      </div>

      {/* Main Hero Container */}
      <div style={{ 
        maxWidth: "960px", 
        width: "100%", 
        textAlign: "center", 
        margin: "40px 0",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "24px"
      }}>
        <div style={{ 
          fontSize: "12px", 
          fontWeight: "700", 
          color: "var(--bmw-blue)", 
          letterSpacing: "3px", 
          textTransform: "uppercase" 
        }}>
          Now in Development • Version 1.0-dev
        </div>
        
        <h1 style={{ 
          fontSize: "48px", 
          fontWeight: "800", 
          lineHeight: "1.15", 
          margin: 0,
          letterSpacing: "-0.5px",
          color: "var(--bmw-ink)"
        }}>
          Your AI Twin. <span style={{ color: "var(--bmw-blue)" }}>Always On.</span> Always You.
        </h1>

        <p className="bmw-body-md" style={{ 
          maxWidth: "680px", 
          fontSize: "18px", 
          color: "var(--bmw-body)",
          margin: "0 auto 16px auto",
          lineHeight: "1.6"
        }}>
          Train an AI clone on your chat history. It replies to your messages on Telegram, Discord, and Email — exactly like you would. Only when you're unavailable. Instantly silent when you flip it off.
        </p>

        <button 
          className="bmw-btn-primary" 
          onClick={() => navigate("/upload")}
          style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "10px", 
            padding: "16px 36px", 
            fontSize: "14px",
            boxShadow: "0 4px 14px rgba(28, 105, 212, 0.2)"
          }}
        >
          🚀 Get Started <ArrowRight size={16} />
        </button>
      </div>

      {/* Supported Platforms */}
      <div style={{ maxWidth: "800px", width: "100%", textAlign: "center", margin: "40px 0" }}>
        <h3 className="bmw-label-uppercase" style={{ fontSize: "12px", color: "var(--bmw-muted)", marginBottom: "20px" }}>
          Supported Platforms
        </h3>
        <div style={{ 
          display: "flex", 
          justifyContent: "center", 
          gap: "16px", 
          flexWrap: "wrap" 
        }}>
          {[
            { name: "Telegram", icon: <MessageCircle size={20} />, color: "#0088cc" },
            { name: "Discord", icon: <MessageSquare size={20} />, color: "#5865F2" },
            { name: "Email", icon: <Mail size={20} />, color: "#EA4335" },
            { name: "WhatsApp", icon: <MessageSquare size={20} />, color: "#25D366" },
          ].map((platform) => (
            <div 
              key={platform.name} 
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "12px 24px",
                border: "1px solid var(--bmw-hairline)",
                backgroundColor: "var(--bmw-surface-card)",
                fontWeight: "600",
                fontSize: "14px",
              }}
            >
              <span style={{ color: platform.color }}>{platform.icon}</span>
              <span>{platform.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div style={{ 
        maxWidth: "960px", 
        width: "100%", 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", 
        gap: "24px",
        margin: "40px 0"
      }}>
        {[
          {
            title: "🧠 Trained on You",
            desc: "Upload your chat exports from WhatsApp or Telegram to train your clone. It absorbs your tone, slang, catchphrases, and typing patterns.",
            icon: <Bot size={24} color="var(--bmw-blue)" />
          },
          {
            title: "🔌 24/7 Autopilot",
            desc: "Enable autopilot lockouts or global kill switches. The clone takes over instantly when you go idle, responding with simulated keypress delays.",
            icon: <Zap size={24} color="var(--bmw-blue)" />
          },
          {
            title: "🔒 Human Override",
            desc: "Replies with low-confidence scores (<60%) are automatically queued for approval. Edit and approve them before they are dispatched.",
            icon: <ShieldCheck size={24} color="var(--bmw-blue)" />
          }
        ].map((feat, index) => (
          <div key={index} className="bmw-card" style={{ display: "flex", flexDirection: "column", gap: "16px", margin: 0 }}>
            <div>{feat.icon}</div>
            <h4 className="bmw-label-uppercase" style={{ fontSize: "14px", color: "var(--bmw-ink)", margin: 0 }}>
              {feat.title}
            </h4>
            <p className="bmw-body-sm" style={{ margin: 0, lineHeight: "1.5" }}>
              {feat.desc}
            </p>
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer style={{ 
        width: "100%", 
        textAlign: "center", 
        borderTop: "1px solid var(--bmw-hairline)", 
        paddingTop: "24px", 
        marginTop: "40px" 
      }}>
        <p className="bmw-body-sm" style={{ margin: 0 }}>
          © 2026 Digital Twin Autopilot. Built with corporate BMW design styling.
        </p>
      </footer>
    </div>
  );
}
