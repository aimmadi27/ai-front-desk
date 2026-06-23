import { useQuery } from "@tanstack/react-query";
import { sessionApi } from "../services/api";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

const STATUS_COLORS: Record<string, string> = {
  completed: "#10b981",
  transferred: "#f59e0b",
  active: "#6366f1",
};

export default function CallLog() {
  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["sessions", BUSINESS_ID],
    queryFn: () => sessionApi.list(BUSINESS_ID),
    retry: false,
  });

  return (
    <div className="page">
      <h1 className="page-title">Call Log</h1>

      {isLoading ? (
        <p className="loading-text">Loading calls...</p>
      ) : sessions.length === 0 ? (
        <p className="empty-text">No calls recorded yet.</p>
      ) : (
        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Caller</th>
                <th>Language</th>
                <th>Status</th>
                <th>Messages</th>
                <th>Call SID</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.call_sid}>
                  <td>{s.caller_number}</td>
                  <td>{s.language === "es" ? "Spanish" : "English"}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ background: STATUS_COLORS[s.status] ?? "#ccc" }}
                    >
                      {s.status}
                    </span>
                  </td>
                  <td>{s.messages.length}</td>
                  <td className="mono">{s.call_sid}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
