import { useQuery } from "@tanstack/react-query";
import { businessApi } from "../services/api";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

const PLAN_DETAILS = {
  starter: { price: "$99", calls: "200 AI conversations/mo", lines: "1 phone line" },
  growth: { price: "$199", calls: "Unlimited conversations", lines: "2 phone lines" },
  pro: { price: "$349", calls: "Unlimited conversations", lines: "3 phone lines + bilingual" },
};

export default function Billing() {
  const { data: business, isLoading } = useQuery({
    queryKey: ["business", BUSINESS_ID],
    queryFn: () => businessApi.get(BUSINESS_ID),
    retry: false,
  });

  if (isLoading) return <p className="loading-text">Loading...</p>;

  const plan = business?.plan ?? "starter";
  const details = PLAN_DETAILS[plan];

  return (
    <div className="page">
      <h1 className="page-title">Billing</h1>

      <div className="stat-card" style={{ maxWidth: 420, marginBottom: 24 }}>
        <p className="stat-label">Current Plan</p>
        <p className="stat-value" style={{ fontSize: 22, textTransform: "capitalize" }}>
          {plan} — {details.price}/mo
        </p>
        <p className="stat-sub" style={{ marginTop: 8 }}>{details.lines}</p>
        <p className="stat-sub">{details.calls}</p>
      </div>

      <div className="table-card" style={{ maxWidth: 420 }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Plan</th>
              <th>Price</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(["starter", "growth", "pro"] as const).map((p) => (
              <tr key={p}>
                <td style={{ textTransform: "capitalize", fontWeight: plan === p ? 700 : 400 }}>
                  {p} {plan === p && <span className="status-badge" style={{ background: "#6366f1", marginLeft: 6 }}>Current</span>}
                </td>
                <td>{PLAN_DETAILS[p].price}/mo</td>
                <td>
                  {plan !== p && (
                    <button className="btn-primary" style={{ padding: "5px 14px", fontSize: 13 }}>
                      Switch
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p style={{ marginTop: 20, fontSize: 13, color: "#9ca3af" }}>
        Billing managed via Stripe. Contact support to cancel.
      </p>
    </div>
  );
}
