import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { businessApi } from "../services/api";
import type { Business, ServiceItem } from "../types";

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

const emptyService = (): ServiceItem => ({ name: "", duration_minutes: 60, price_usd: 0 });

export default function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: "",
    phone_number: "",
    owner_email: "",
    language: "en",
    plan: "starter" as Business["plan"],
    services: [emptyService()],
    hours: Object.fromEntries(DAYS.map((d) => [d, "9:00 AM - 6:00 PM"])),
  });

  const updateField = (field: string, value: unknown) =>
    setForm((f) => ({ ...f, [field]: value }));

  const updateService = (i: number, field: keyof ServiceItem, value: string | number) => {
    const services = form.services.map((s, idx) =>
      idx === i ? { ...s, [field]: value } : s
    );
    setForm((f) => ({ ...f, services }));
  };

  const addService = () =>
    setForm((f) => ({ ...f, services: [...f.services, emptyService()] }));

  const removeService = (i: number) =>
    setForm((f) => ({ ...f, services: f.services.filter((_, idx) => idx !== i) }));

  const updateHour = (day: string, value: string) =>
    setForm((f) => ({ ...f, hours: { ...f.hours, [day]: value } }));

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      await businessApi.create({
        ...form,
        calendar_id: undefined,
        stripe_customer_id: undefined,
        active: true,
      });
      navigate("/");
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Set Up Your Business</h1>
      <div className="onboarding-steps">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`step-dot ${step >= s ? "step-dot--active" : ""}`}>
            {s}
          </div>
        ))}
      </div>

      <div className="settings-form" style={{ maxWidth: 600 }}>
        {step === 1 && (
          <>
            <h2 className="section-title">Business Info</h2>
            <div className="form-group">
              <label>Business Name</label>
              <input value={form.name} onChange={(e) => updateField("name", e.target.value)} placeholder="Charlotte Cuts" />
            </div>
            <div className="form-group">
              <label>Phone Number (your existing number)</label>
              <input value={form.phone_number} onChange={(e) => updateField("phone_number", e.target.value)} placeholder="+17045551234" />
            </div>
            <div className="form-group">
              <label>Your Email</label>
              <input type="email" value={form.owner_email} onChange={(e) => updateField("owner_email", e.target.value)} placeholder="you@email.com" />
            </div>
            <div className="form-group">
              <label>Language</label>
              <select value={form.language} onChange={(e) => updateField("language", e.target.value)}>
                <option value="en">English only</option>
                <option value="es">Spanish only</option>
                <option value="both">Bilingual (EN + ES)</option>
              </select>
            </div>
            <button className="btn-primary" onClick={() => setStep(2)}>Next →</button>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="section-title">Services & Hours</h2>
            <div className="form-group">
              <label>Services</label>
              {form.services.map((svc, i) => (
                <div key={i} className="service-row">
                  <input placeholder="Service name" value={svc.name} onChange={(e) => updateService(i, "name", e.target.value)} />
                  <input type="number" placeholder="Min" value={svc.duration_minutes} onChange={(e) => updateService(i, "duration_minutes", Number(e.target.value))} style={{ width: 70 }} />
                  <input type="number" placeholder="$" value={svc.price_usd} onChange={(e) => updateService(i, "price_usd", Number(e.target.value))} style={{ width: 70 }} />
                  {form.services.length > 1 && (
                    <button className="btn-remove" onClick={() => removeService(i)}>✕</button>
                  )}
                </div>
              ))}
              <button className="btn-secondary" onClick={addService}>+ Add service</button>
            </div>

            <div className="form-group">
              <label>Business Hours</label>
              {DAYS.map((day) => (
                <div key={day} className="hours-row">
                  <span className="day-label">{day.slice(0, 3).toUpperCase()}</span>
                  <input
                    value={form.hours[day]}
                    onChange={(e) => updateHour(day, e.target.value)}
                    placeholder="9:00 AM - 6:00 PM or Closed"
                  />
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              <button className="btn-secondary" onClick={() => setStep(1)}>← Back</button>
              <button className="btn-primary" onClick={() => setStep(3)}>Next →</button>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h2 className="section-title">Choose a Plan</h2>
            {(["starter", "growth", "pro"] as Business["plan"][]).map((plan) => {
              const info = {
                starter: { price: "$99/mo", desc: "1 phone line · 200 AI conversations/mo · SMS" },
                growth: { price: "$199/mo", desc: "2 lines · Unlimited conversations · SMS + Email" },
                pro: { price: "$349/mo", desc: "3 lines · Bilingual · CRM sync · Analytics" },
              }[plan];
              return (
                <div
                  key={plan}
                  className={`plan-card ${form.plan === plan ? "plan-card--selected" : ""}`}
                  onClick={() => updateField("plan", plan)}
                >
                  <div className="plan-name">{plan.charAt(0).toUpperCase() + plan.slice(1)}</div>
                  <div className="plan-price">{info.price}</div>
                  <div className="plan-desc">{info.desc}</div>
                </div>
              );
            })}
            {error && <p style={{ color: "red", fontSize: 13 }}>{error}</p>}
            <div style={{ display: "flex", gap: 12 }}>
              <button className="btn-secondary" onClick={() => setStep(2)}>← Back</button>
              <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
                {loading ? "Saving..." : "Launch My AI Front Desk"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
