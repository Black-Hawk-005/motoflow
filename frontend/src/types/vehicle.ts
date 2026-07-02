export interface VehicleResponse {
  id: string;
  customer_id: string;
  make: string;
  model: string;
  year: number;
  license_plate: string;
}

export interface VehicleCreatePayload {
  make: string;
  model: string;
  year: number;
  license_plate: string;
}

export interface VehicleUpdatePayload {
  make?: string;
  model?: string;
  year?: number;
  license_plate?: string;
}
