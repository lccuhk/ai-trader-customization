import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'
import { notificationApi } from '@/services/api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.is_read).length
  )

  async function fetchNotifications(limit = 20) {
    isLoading.value = true
    error.value = null
    try {
      const response = await notificationApi.getNotifications(limit)
      if (response.data.success && response.data.notifications) {
        notifications.value = response.data.notifications
      }
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取通知失败'
    } finally {
      isLoading.value = false
    }
  }

  async function markAsRead(id: number) {
    try {
      const response = await notificationApi.markAsRead(id)
      if (response.data.success) {
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.is_read = true
        }
        return { success: true }
      }
      return { success: false, message: response.data.message }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message }
    }
  }

  async function markAllAsRead() {
    try {
      const response = await notificationApi.markAllAsRead()
      if (response.data.success) {
        notifications.value.forEach(n => n.is_read = true)
        return { success: true }
      }
      return { success: false, message: response.data.message }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message }
    }
  }

  function addNotification(notification: Notification) {
    notifications.value.unshift(notification)
  }

  return {
    notifications,
    isLoading,
    error,
    unreadCount,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    addNotification
  }
})
