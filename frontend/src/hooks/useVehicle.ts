import { useQuery } from "@tanstack/react-query";
import { getVehicle } from "../api/vehicle";

export const useVehicle = (vehicle_id: string) => {
  return useQuery({
    queryKey: ["vehicles", vehicle_id],
    queryFn: () => getVehicle(vehicle_id),
  });
};
