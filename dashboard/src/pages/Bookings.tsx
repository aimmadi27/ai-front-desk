import { useQuery } from "@tanstack/react-query";
import { sessionApi } from "../services/api";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

export default function Bookings() {
  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["sessions", BUSINESS_ID],
    queryFn: () => sessionApi.list(BUSINESS_ID),
    retry: false,
  });

  const bookings = sessions.filter((s) =>
    s.messages.some(
      (m) => m.role === "model" && m.content.toLowerCase().includes("confirm")
    )
  );

  return (
    <div className="page">
      <h1 className="page-title">Bookings</h1>

      {isLoading ? (
        <p className="loading-text">Loading...</p>
      ) : bookings.length === 0 ? (
        <p className="empty-text">No bookings yet — they'll appear here once the AI confirms appointments.</p>
      ) : (
        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Language</th>
                <th>Confirmed By AI</th>
                <th>Call SID</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((s) => {
                const confirm = s.messages.find(
                  (m) => m.role === "model" && m.content.toLowerCase().includes("confirm")
                );
                return (
                  <tr key={s.call_sid}>
                    <td>{s.caller_number}</td>
                    <td>{s.language === "es" ? "Spanish" : "English"}</td>
                    <td style={{ fontSize: 13, maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {confirm?.content.slice(0, 80)}…
                    </td>
                    <td className="mono">{s.call_sid}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
