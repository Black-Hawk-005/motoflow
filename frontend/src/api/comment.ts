import axiosClient from "./client";
import type { CommentCreatePayload, CommentResponse } from "../types/comment";

export const createComment = async (
  commentDetails: CommentCreatePayload,
): Promise<CommentResponse> => {
  const response = await axiosClient.post<CommentResponse>(
    "/comments/",
    commentDetails,
  );
  return response.data;
};

export const listComments = async (
  serviceRequestId: string,
): Promise<CommentResponse[]> => {
  const response = await axiosClient.get<CommentResponse[]>("/comments/", {
    params: { service_request_id: serviceRequestId },
  });
  return response.data;
};
