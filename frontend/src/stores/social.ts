import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, UserProfile, DirectMessage, Conversation, Mention } from '../types'
import { socialService } from '../services/social'

export const useSocialStore = defineStore('social', () => {
  const userProfile = ref<UserProfile | null>(null)
  const followers = ref<User[]>([])
  const following = ref<User[]>([])
  const conversations = ref<Conversation[]>([])
  const messages = ref<DirectMessage[]>([])
  const mentions = ref<Mention[]>([])
  const searchResults = ref<User[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadUserProfile(userId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getUserProfile(userId)
      if (response.success && response.data) {
        userProfile.value = response.data.user
      }
      return response
    } catch (e: any) {
      error.value = e.message || '加载用户资料失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadFollowers(userId: number, params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getFollowers(userId, params)
      if (response.success && response.data) {
        followers.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载粉丝列表失败'
    } finally {
      loading.value = false
    }
  }

  async function loadFollowing(userId: number, params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getFollowing(userId, params)
      if (response.success && response.data) {
        following.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载关注列表失败'
    } finally {
      loading.value = false
    }
  }

  async function followUser(userId: number) {
    try {
      const response = await socialService.followUser(userId)
      if (response.success && userProfile.value && userProfile.value.id === userId) {
        userProfile.value.is_following = true
        if (userProfile.value.follower_count !== undefined) {
          userProfile.value.follower_count++
        }
      }
      return response
    } catch (e: any) {
      error.value = e.message || '关注失败'
      throw e
    }
  }

  async function unfollowUser(userId: number) {
    try {
      const response = await socialService.unfollowUser(userId)
      if (response.success && userProfile.value && userProfile.value.id === userId) {
        userProfile.value.is_following = false
        if (userProfile.value.follower_count !== undefined) {
          userProfile.value.follower_count--
        }
      }
      return response
    } catch (e: any) {
      error.value = e.message || '取消关注失败'
      throw e
    }
  }

  async function loadConversations() {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getConversations()
      if (response.success && response.data) {
        conversations.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载会话列表失败'
    } finally {
      loading.value = false
    }
  }

  async function loadMessages(otherUserId: number, params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getDirectMessages(otherUserId, params)
      if (response.success && response.data) {
        messages.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载消息失败'
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(receiverId: number, content: string) {
    try {
      const response = await socialService.sendDirectMessage({ receiver_id: receiverId, content })
      if (response.success && response.data) {
        messages.value.push(response.data)
      }
      return response
    } catch (e: any) {
      error.value = e.message || '发送消息失败'
      throw e
    }
  }

  async function loadMentions(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.getMentions(params)
      if (response.success && response.data) {
        mentions.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '加载提及失败'
    } finally {
      loading.value = false
    }
  }

  async function searchUsers(query: string, params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await socialService.searchUsers(query, params)
      if (response.success && response.data) {
        searchResults.value = response.data.items
      }
    } catch (e: any) {
      error.value = e.message || '搜索用户失败'
    } finally {
      loading.value = false
    }
  }

  function addMessage(message: DirectMessage) {
    messages.value.push(message)
    const convIndex = conversations.value.findIndex(c => c.user.id === message.sender_id)
    if (convIndex !== -1) {
      conversations.value[convIndex].last_message = {
        id: message.id,
        content: message.content,
        is_read: message.is_read,
        is_sent: false,
        created_at: message.created_at
      }
      conversations.value[convIndex].unread_count++
    }
  }

  return {
    userProfile,
    followers,
    following,
    conversations,
    messages,
    mentions,
    searchResults,
    loading,
    error,
    loadUserProfile,
    loadFollowers,
    loadFollowing,
    followUser,
    unfollowUser,
    loadConversations,
    loadMessages,
    sendMessage,
    loadMentions,
    searchUsers,
    addMessage
  }
})
