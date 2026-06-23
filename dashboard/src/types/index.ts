export interface ServiceItem {
  name: string;
  duration_minutes: number;
  price_usd: number;
}

export interface Business {
  id: string;
  name: string;
  phone_number: string;
  owner_email: string;
  services: ServiceItem[];
  hours: Record<string, string>;
  language: string;
  calendar_id?: string;
  stripe_customer_id?: string;
  plan: "starter" | "growth" | "pro";
  active: boolean;
}

export interface Message {
  role: "user" | "model";
  content: string;
}

export interface CallSession {
  call_sid: string;
  business_id: string;
  caller_number: string;
  messages: Message[];
  language: string;
  status: "active" | "completed" | "transferred";
}

export interface DashboardStats {
  calls_today: number;
  bookings_today: number;
  calls_this_month: number;
  bookings_this_month: number;
  missed_calls: number;
}
