export interface CommentCreatePayload {
  service_request_id: string;
  message: string;
}

export interface CommentResponse {
  id: string;
  service_request_id: string;
  author_id: string;
  message: string;
  created_at: string;
}