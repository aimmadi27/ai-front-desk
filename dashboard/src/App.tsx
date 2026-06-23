import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import CallLog from "./pages/CallLog";
import Bookings from "./pages/Bookings";
import SMS from "./pages/SMS";
import Settings from "./pages/Settings";
import Onboarding from "./pages/Onboarding";
import Billing from "./pages/Billing";
import "./App.css";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="layout">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/calls" element={<CallLog />} />
              <Route path="/bookings" element={<Bookings />} />
              <Route path="/sms" element={<SMS />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/onboarding" element={<Onboarding />} />
              <Route path="/billing" element={<Billing />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
