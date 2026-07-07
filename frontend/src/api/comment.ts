import axiosClient from "./client";
import type { CommentCreatePayload, CommentResponse } from "../types/comment";

export const create_comment = async (
  comment_details: CommentCreatePayload,
): Promise<CommentResponse> => {
  const response = await axiosClient.post<CommentResponse>(
    "/comments/",
    comment_details,
  );
  return response.data;
};

export const list_comments = async (
  service_request_id: string,
): Promise<CommentResponse[]> => {
  const response = await axiosClient.get<CommentResponse[]>("/comments/", {
    params: { service_request_id },
  });
  return response.data;
};
