import axiosClient from "./client";
import type {
  VehicleResponse,
  VehicleCreatePayload,
  VehicleUpdatePayload,
} from "../types/vehicle";

export const getVehicle = async (
  vehicle_id: string,
): Promise<VehicleResponse> => {
  const response = await axiosClient.get<VehicleResponse>(
    `/vehicles/${vehicle_id}`,
  );
  return response.data;
};

export const listVehicles = async (): Promise<VehicleResponse[]> => {
  const response = await axiosClient.get<VehicleResponse[]>(`/vehicles/`);
  return response.data;
};

export const createVehicle = async (
  vehicle_data: VehicleCreatePayload,
): Promise<VehicleResponse> => {
  const response = await axiosClient.post<VehicleResponse>(
    `/vehicles/`,
    vehicle_data,
  );
  return response.data;
};

export const updateVehicle = async (
  vehicle_id: string,
  vehicle_data: VehicleUpdatePayload,
): Promise<VehicleResponse> => {
  const response = await axiosClient.patch<VehicleResponse>(
    `/vehicles/${vehicle_id}`,
    vehicle_data,
  );
  return response.data;
};

export const deleteVehicle = async (vehicle_id: string) => {
  const response = await axiosClient.delete<null>(`/vehicles/${vehicle_id}`);
  return response.status;
};
