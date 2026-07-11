import { useQuery } from "@tanstack/react-query";
import { listVehicles } from "../../api/vehicle";

export const useVehicles = () => {
  return useQuery({
    queryKey: ["vehicles"],
    queryFn: listVehicles,
  });
};
