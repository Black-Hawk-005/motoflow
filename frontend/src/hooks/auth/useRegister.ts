import { useMutation } from "@tanstack/react-query";
import { register } from "../../api/auth";

export const useRegister = () => {
  return useMutation({
    mutationFn: ({
      full_name,
      email,
      password,
      phone,
    }: {
      full_name: string;
      email: string;
      password: string;
      phone: string;
    }) => register({ full_name, email, password, phone }),
  });
};
