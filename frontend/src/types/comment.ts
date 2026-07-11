import type { User } from "./auth";

export interface CommentCreatePayload {
  service_request_id: string;
  message: string;
}

export interface CommentAuthor {
  id: string;
  full_name: string;
  role: User["role"];
}

export interface CommentResponse {
  id: string;
  service_request_id: string;
  author: CommentAuthor;
  message: string;
  created_at: string;
}
