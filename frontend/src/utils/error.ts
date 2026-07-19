import axios from "axios";

interface FastAPIValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

interface FastAPIErrorBody {
  detail: string | FastAPIValidationError[];
}

export const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError<FastAPIErrorBody>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  }
  return "Something went wrong";
};
