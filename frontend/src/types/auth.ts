export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: "customer" | "admin" | "mechanic";
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  phone: string;
}
