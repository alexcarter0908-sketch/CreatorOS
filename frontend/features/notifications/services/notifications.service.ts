import { apiClient } from "@/lib/api/client";
import type { AppNotification, NotificationListResponse } from "../types/notification.types";

export async function listNotifications(): Promise<NotificationListResponse> {
  const { data } = await apiClient.get<NotificationListResponse>("/api/v1/notifications");
  return data;
}

export async function markNotificationRead(id: string): Promise<AppNotification> {
  const { data } = await apiClient.post<AppNotification>(`/api/v1/notifications/${id}/read`);
  return data;
}

export async function markAllNotificationsRead(): Promise<void> {
  await apiClient.post("/api/v1/notifications/read-all");
}
