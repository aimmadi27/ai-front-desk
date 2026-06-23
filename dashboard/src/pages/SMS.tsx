import { useQuery } from "@tanstack/react-query";
import { sessionApi } from "../services/api";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

export default function SMS() {
  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["sessions", BUSINESS_ID],
    queryFn: () => sessionApi.list(BUSINESS_ID),
    retry: false,
  });

  const smsSessions = sessions.filter((s) => s.caller_number.startsWith("+") && !s.call_sid.startsWith("CA"));

  return (
    <div className="page">
      <h1 className="page-title">SMS Conversations</h1>

      {isLoading ? (
        <p className="loading-text">Loading...</p>
      ) : smsSessions.length === 0 ? (
        <p className="empty-text">No SMS conversations yet.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {smsSessions.map((s) => (
            <div key={s.call_sid} className="table-card" style={{ padding: 20 }}>
              <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14 }}>
                {s.caller_number}
                <span className="status-badge" style={{ background: "#6366f1", marginLeft: 10 }}>
                  {s.language === "es" ? "ES" : "EN"}
                </span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {s.messages.map((m, i) => (
                  <div
                    key={i}
                    style={{
                      alignSelf: m.role === "user" ? "flex-start" : "flex-end",
                      background: m.role === "user" ? "#f3f4f6" : "#6366f1",
                      color: m.role === "user" ? "#111" : "#fff",
                      padding: "8px 14px",
                      borderRadius: 12,
                      fontSize: 13,
                      maxWidth: "75%",
                    }}
                  >
                    {m.content}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
