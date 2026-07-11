import axiosClient from "./client";
import type {
  VehicleResponse,
  VehicleCreatePayload,
  VehicleUpdatePayload,
} from "../types/vehicle";

export const getVehicle = async (
  vehicleId: string,
): Promise<VehicleResponse> => {
  const response = await axiosClient.get<VehicleResponse>(
    `/vehicles/${vehicleId}`,
  );
  return response.data;
};

export const listVehicles = async (): Promise<VehicleResponse[]> => {
  const response = await axiosClient.get<VehicleResponse[]>(`/vehicles/`);
  return response.data;
};

export const createVehicle = async (
  vehicleData: VehicleCreatePayload,
): Promise<VehicleResponse> => {
  const response = await axiosClient.post<VehicleResponse>(
    `/vehicles/`,
    vehicleData,
  );
  return response.data;
};

export const updateVehicle = async (
  vehicleId: string,
  vehicleData: VehicleUpdatePayload,
): Promise<VehicleResponse> => {
  const response = await axiosClient.patch<VehicleResponse>(
    `/vehicles/${vehicleId}`,
    vehicleData,
  );
  return response.data;
};

export const deleteVehicle = async (vehicleId: string) => {
  const response = await axiosClient.delete<null>(`/vehicles/${vehicleId}`);
  return response.status;
};
