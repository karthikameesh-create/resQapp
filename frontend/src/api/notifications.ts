import api from "./client";

export interface Notification {
  id: number;
  user_id: number;
  incident_id: number | null;
  type: string;
  title: string;
  message: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationCount {
  unread_count: number;
}

export async function getNotifications(
  options?: {
    unreadOnly?: boolean;
    limit?: number;
  }
): Promise<Notification[]> {
  const response = await api.get<Notification[]>(
    "/notifications",
    {
      params: {
        unread_only:
          options?.unreadOnly ?? false,
        limit: options?.limit ?? 50,
      },
    }
  );

  return response.data;
}

export async function getUnreadNotifications(): Promise<
  Notification[]
> {
  const response = await api.get<Notification[]>(
    "/notifications/unread"
  );

  return response.data;
}

export async function getUnreadCount(): Promise<number> {
  const response =
    await api.get<NotificationCount>(
      "/notifications/unread-count"
    );

  return response.data.unread_count;
}

export async function markNotificationAsRead(
  notificationId: number
): Promise<Notification> {
  const response =
    await api.put<Notification>(
      `/notifications/${notificationId}/read`
    );

  return response.data;
}

export async function markAllNotificationsAsRead(): Promise<number> {
  const response =
    await api.put<NotificationCount>(
      "/notifications/read-all"
    );

  return response.data.unread_count;
}