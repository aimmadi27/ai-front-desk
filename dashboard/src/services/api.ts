import axios from "axios";
import type { Business, CallSession, DashboardStats } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const businessApi = {
  get: (id: string) =>
    api.get<Business>(`/businesses/${id}`).then((r) => r.data),

  update: (id: string, data: Partial<Business>) =>
    api.put<Business>(`/businesses/${id}`, data).then((r) => r.data),

  create: (data: Omit<Business, "id">) =>
    api.post<Business>("/businesses/", data).then((r) => r.data),
};

export const sessionApi = {
  list: (businessId: string) =>
    api
      .get<CallSession[]>(`/sessions?business_id=${businessId}`)
      .then((r) => r.data),

  get: (callSid: string) =>
    api.get<CallSession>(`/sessions/${callSid}`).then((r) => r.data),
};

export const statsApi = {
  get: (businessId: string) =>
    api
      .get<DashboardStats>(`/stats?business_id=${businessId}`)
      .then((r) => r.data),
};
