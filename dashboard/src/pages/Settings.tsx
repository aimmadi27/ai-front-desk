import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { businessApi } from "../services/api";
import type { Business } from "../types";

const BUSINESS_ID = import.meta.env.VITE_BUSINESS_ID || "default";

export default function Settings() {
  const qc = useQueryClient();
  const { data: business, isLoading } = useQuery({
    queryKey: ["business", BUSINESS_ID],
    queryFn: () => businessApi.get(BUSINESS_ID),
    retry: false,
  });

  const [form, setForm] = useState<Partial<Business>>({});
  const [saved, setSaved] = useState(false);

  const mutation = useMutation({
    mutationFn: (data: Partial<Business>) =>
      businessApi.update(BUSINESS_ID, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business", BUSINESS_ID] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  if (isLoading) return <p className="loading-text">Loading...</p>;

  return (
    <div className="page">
      <h1 className="page-title">Business Settings</h1>

      <form className="settings-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Business Name</label>
          <input
            type="text"
            defaultValue={business?.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
        </div>

        <div className="form-group">
          <label>Phone Number</label>
          <input
            type="text"
            defaultValue={business?.phone_number}
            onChange={(e) =>
              setForm((f) => ({ ...f, phone_number: e.target.value }))
            }
          />
        </div>

        <div className="form-group">
          <label>Owner Email</label>
          <input
            type="email"
            defaultValue={business?.owner_email}
            onChange={(e) =>
              setForm((f) => ({ ...f, owner_email: e.target.value }))
            }
          />
        </div>

        <div className="form-group">
          <label>Language</label>
          <select
            defaultValue={business?.language}
            onChange={(e) =>
              setForm((f) => ({ ...f, language: e.target.value }))
            }
          >
            <option value="en">English only</option>
            <option value="es">Spanish only</option>
            <option value="both">Bilingual (EN + ES)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Plan</label>
          <select
            defaultValue={business?.plan}
            onChange={(e) =>
              setForm((f) => ({ ...f, plan: e.target.value as Business["plan"] }))
            }
          >
            <option value="starter">Starter — $99/mo</option>
            <option value="growth">Growth — $199/mo</option>
            <option value="pro">Pro — $349/mo</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={mutation.isPending}>
          {mutation.isPending ? "Saving..." : saved ? "Saved!" : "Save Changes"}
        </button>
      </form>
    </div>
  );
}
