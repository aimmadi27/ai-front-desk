import { useQuery } from "@tanstack/react-query";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import StatCard from "../components/StatCard";
import { statsApi } from "../services/api";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

const mockChartData = [
  { day: "Mon", calls: 12, bookings: 8 },
  { day: "Tue", calls: 19, bookings: 14 },
  { day: "Wed", calls: 9, bookings: 5 },
  { day: "Thu", calls: 22, bookings: 17 },
  { day: "Fri", calls: 30, bookings: 24 },
  { day: "Sat", calls: 35, bookings: 28 },
  { day: "Sun", calls: 14, bookings: 10 },
];

export default function Overview() {
  const { data: stats } = useQuery({
    queryKey: ["stats", BUSINESS_ID],
    queryFn: () => statsApi.get(BUSINESS_ID),
    retry: false,
  });

  const displayStats = stats ?? {
    calls_today: 0,
    bookings_today: 0,
    calls_this_month: 0,
    bookings_this_month: 0,
    missed_calls: 0,
  };

  return (
    <div className="page">
      <h1 className="page-title">Overview</h1>

      <div className="stat-grid">
        <StatCard label="Calls Today" value={displayStats.calls_today} />
        <StatCard label="Bookings Today" value={displayStats.bookings_today} accent />
        <StatCard label="Calls This Month" value={displayStats.calls_this_month} />
        <StatCard label="Missed Calls" value={displayStats.missed_calls} sub="needs follow-up" />
      </div>

      <div className="chart-card">
        <h2 className="chart-title">Calls & Bookings — Last 7 Days</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={mockChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="calls" stroke="#6366f1" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="bookings" stroke="#10b981" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
        <div className="chart-legend">
          <span className="legend-item legend-item--calls">Calls</span>
          <span className="legend-item legend-item--bookings">Bookings</span>
        </div>
      </div>
    </div>
  );
}
