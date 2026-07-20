import apiClient from "@/lib/api/client";
import type { AutoTarget, CreateAutoTargetPayload } from "../types/target";

export async function listTargets(): Promise<AutoTarget[]> {
  const { data } = await apiClient.get<AutoTarget[]>("/api/v1/targets");
  return data;
}

export async function createTarget(payload: CreateAutoTargetPayload): Promise<AutoTarget> {
  const { data } = await apiClient.post<AutoTarget>("/api/v1/targets", payload);
  return data;
}

export async function deleteTarget(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/targets/${id}`);
}