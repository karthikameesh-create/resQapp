import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getNotifications,
  getUnreadCount,
  markAllNotificationsAsRead,
  markNotificationAsRead,
  type Notification,
} from "../../api/notifications";

import PriorityBadge from "../status/PriorityBadge";

function formatNotificationTime(
  date: string
) {
  const created = new Date(date);
  const now = new Date();

  const diffMs = now.getTime() - created.getTime();
  const diffMinutes = Math.floor(
    diffMs / 60000
  );

  if (diffMinutes < 1) {
    return "Just now";
  }

  if (diffMinutes < 60) {
    return `${diffMinutes} min ago`;
  }

  const diffHours = Math.floor(
    diffMinutes / 60
  );

  if (diffHours < 24) {
    return `${diffHours} hr ago`;
  }

  return created.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
}

function getNotificationClass(
  notification: Notification
) {
  const priority =
    notification.priority.toLowerCase();

  if (priority === "critical") {
    return "notification-critical";
  }

  if (priority === "high") {
    return "notification-high";
  }

  return "notification-default";
}

interface NotificationCenterProps {
  compact?: boolean;
}

export default function NotificationCenter({
  compact = false,
}: NotificationCenterProps) {
  const navigate = useNavigate();

  const [notifications, setNotifications] =
    useState<Notification[]>([]);

  const [unreadCount, setUnreadCount] =
    useState(0);

  const [open, setOpen] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function loadNotificationData() {
    try {
      setError("");

      const [items, count] =
        await Promise.all([
          getNotifications({
            limit: 50,
          }),
          getUnreadCount(),
        ]);

      setNotifications(items);
      setUnreadCount(count);
    } catch {
      setError(
        "Unable to load notifications."
      );
    }
  }

  useEffect(() => {
    loadNotificationData();

    const interval =
      window.setInterval(
        async () => {
          try {
            const count =
              await getUnreadCount();

            setUnreadCount(count);
          } catch {
            // Preserve the existing count if polling fails.
          }
        },
        10000
      );

    return () =>
      window.clearInterval(interval);
  }, []);

  async function handleOpen() {
    setOpen((current) => !current);

    if (!open) {
      setLoading(true);

      try {
        const items =
          await getNotifications({
            limit: 50,
          });

        setNotifications(items);
      } catch {
        setError(
          "Unable to load notifications."
        );
      } finally {
        setLoading(false);
      }
    }
  }

  async function handleMarkAsRead(
    notification: Notification
  ) {
    if (!notification.is_read) {
      try {
        const updated =
          await markNotificationAsRead(
            notification.id
          );

        setNotifications((current) =>
          current.map((item) =>
            item.id === updated.id
              ? updated
              : item
          )
        );

        setUnreadCount((current) =>
          Math.max(0, current - 1)
        );
      } catch {
        setError(
          "Unable to update notification."
        );
        return;
      }
    }

    if (notification.incident_id) {
      setOpen(false);

      navigate(
        `/incidents/${notification.incident_id}`
      );
    }
  }

  async function handleMarkAllAsRead() {
    try {
      await markAllNotificationsAsRead();

      setNotifications((current) =>
        current.map((notification) => ({
          ...notification,
          is_read: true,
        }))
      );

      setUnreadCount(0);
    } catch {
      setError(
        "Unable to mark notifications as read."
      );
    }
  }

  return (
    <div
      className={[
        "notification-center",
        compact
          ? "notification-center-compact"
          : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <button
        className="notification-trigger"
        type="button"
        aria-label="Notifications"
        onClick={handleOpen}
      >
        <span className="notification-bell">
          🔔
        </span>

        {unreadCount > 0 && (
          <span className="notification-count">
            {unreadCount > 99
              ? "99+"
              : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <>
          <button
            className="notification-overlay"
            type="button"
            aria-label="Close notifications"
            onClick={() => setOpen(false)}
          />

          <div className="notification-dropdown">
            <div className="notification-dropdown-header">
              <div>
                <h3>Notifications</h3>

                <span>
                  {unreadCount} unread
                </span>
              </div>

              <button
                type="button"
                className="notification-mark-all"
                disabled={unreadCount === 0}
                onClick={
                  handleMarkAllAsRead
                }
              >
                Mark all as read
              </button>
            </div>

            {error && (
              <div className="notification-error">
                {error}
              </div>
            )}

            <div className="notification-list">
              {loading ? (
                <div className="notification-empty">
                  Loading notifications...
                </div>
              ) : notifications.length ===
                0 ? (
                <div className="notification-empty">
                  <div className="notification-empty-icon">
                    ✓
                  </div>

                  <strong>
                    You're all caught up
                  </strong>

                  <span>
                    No notifications yet.
                  </span>
                </div>
              ) : (
                notifications.map(
                  (notification) => (
                    <button
                      type="button"
                      key={notification.id}
                      className={[
                        "notification-item",
                        !notification.is_read
                          ? "notification-unread"
                          : "",
                        getNotificationClass(
                          notification
                        ),
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      onClick={() =>
                        handleMarkAsRead(
                          notification
                        )
                      }
                    >
                      <div className="notification-item-top">
                        <div>
                          <strong>
                            {notification.title}
                          </strong>

                          <span>
                            {formatNotificationTime(
                              notification.created_at
                            )}
                          </span>
                        </div>

                        <PriorityBadge
                          priority={
                            notification.priority
                          }
                        />
                      </div>

                      <p>
                        {notification.message}
                      </p>

                      {!notification.is_read && (
                        <span className="notification-new-dot" />
                      )}
                    </button>
                  )
                )
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}