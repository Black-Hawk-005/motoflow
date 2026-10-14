import axios from "axios";

interface FastAPIValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  ctx?: { min_length?: number; max_length?: number; gt?: number };
}

interface FastAPIErrorBody {
  detail: string | FastAPIValidationError[];
}

const fieldLabel = (loc: (string | number)[]): string => {
  const name = String(loc[loc.length - 1]).replace(/_/g, " ");
  return name.charAt(0).toUpperCase() + name.slice(1);
};

const friendlyMessage = (d: FastAPIValidationError): string => {
  const label = fieldLabel(d.loc);
  if (d.type === "missing") return `${label} is required`;
  if (d.type === "string_too_short") {
    return d.ctx?.min_length === 1
      ? `${label} is required`
      : `${label} must be at least ${d.ctx?.min_length} characters`;
  }
  if (d.type === "string_too_long") {
    return `${label} must be at most ${d.ctx?.max_length} characters`;
  }
  if (d.type === "string_pattern_mismatch") {
    return label === "Phone"
      ? "Phone must be 10 to 15 digits, with an optional + at the start"
      : `${label} is not in a valid format`;
  }
  if (d.type === "greater_than") {
    return `${label} must be greater than ${d.ctx?.gt}`;
  }
  if (["int_parsing", "decimal_parsing", "float_parsing"].includes(d.type)) {
    return `${label} must be a number`;
  }
  if (d.type === "value_error" && label === "Email") {
    return "Enter a valid email address";
  }
  return `${label}: ${d.msg}`;
};

export const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError<FastAPIErrorBody>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map(friendlyMessage).join(", ");
  }
  return "Something went wrong";
};
