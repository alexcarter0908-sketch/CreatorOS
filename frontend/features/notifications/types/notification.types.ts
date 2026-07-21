export interface AppNotification {
  id: string;
  type: string;
  title: string;
  message: string | null;
  workflow_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: AppNotification[];
  unread_count: number;
}
