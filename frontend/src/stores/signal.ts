import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Signal, SignalReply, SignalParticipant, SignalQuality, MarketNews, MarketEvent, EconomicIndicator } from '@/types'
import { signalApi, marketApi } from '@/services/api'

export const useSignalStore = defineStore('signal', () => {
  const signals = ref<Signal[]>([])
  const currentSignal = ref<Signal | null>(null)
  const replies = ref<SignalReply[]>([])
  const participants = ref<SignalParticipant[]>([])
  const qualityScore = ref<SignalQuality | null>(null)
  const marketNews = ref<MarketNews[]>([])
  const marketEvents = ref<MarketEvent[]>([])
  const economicIndicators = ref<EconomicIndicator[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const sortedSignals = computed(() => {
    return [...signals.value].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  async function fetchSignals(limit = 20, message_type = '', market = '') {
    isLoading.value = true
    error.value = null
    try {
      const response = await signalApi.getSignals(limit, message_type, market)
      if (response.data.success && response.data.data) {
        signals.value = response.data.data
      }
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取信号列表失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSignalDetail(id: number) {
    isLoading.value = true
    error.value = null
    try {
      const [signalRes, repliesRes, participantsRes, qualityRes] = await Promise.all([
        signalApi.getSignalDetail(id),
        signalApi.getSignalReplies(id),
        signalApi.getSignalParticipants(id),
        signalApi.getSignalQuality(id)
      ])

      if (signalRes.data.success && signalRes.data.data) {
        currentSignal.value = signalRes.data.data
      }
      if (repliesRes.data.success && repliesRes.data.data) {
        replies.value = repliesRes.data.data
      }
      if (participantsRes.data.success && participantsRes.data.data) {
        participants.value = participantsRes.data.data
      }
      if (qualityRes.data.success && qualityRes.data.data) {
        qualityScore.value = qualityRes.data.data
      }
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取信号详情失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchReplies(signalId: number) {
    isLoading.value = true
    error.value = null
    try {
      const response = await signalApi.getSignalReplies(signalId)
      if (response.data.success && response.data.data) {
        replies.value = response.data.data
      }
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取评论失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createSignal(data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await signalApi.createSignal(data)
      if (response.data.success && response.data.data) {
        signals.value.unshift(response.data.data)
        return { success: true, signal: response.data.data }
      }
      return { success: false, message: response.data.message || '创建信号失败' }
    } catch (e: any) {
      error.value = e.response?.data?.message || '创建信号失败'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function addReply(signalId: number, content: string, parentId?: number) {
    try {
      const response = await signalApi.addReply(signalId, { content, parent_id: parentId })
      if (response.data.success && response.data.data) {
        replies.value.unshift(response.data.data)
        if (currentSignal.value) {
          currentSignal.value.reply_count++
        }
        return { success: true, reply: response.data.data }
      }
      return { success: false, message: response.data.message || '发布评论失败' }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message || '发布评论失败' }
    }
  }

  async function toggleFollow(signalId: number) {
    try {
      const response = await signalApi.toggleFollow(signalId)
      if (response.data.success) {
        const signal = signals.value.find(s => s.id === signalId)
        if (signal) {
          signal.is_following = response.data.is_following ?? !signal.is_following
          signal.participant_count += signal.is_following ? 1 : -1
        }
        if (currentSignal.value?.id === signalId) {
          currentSignal.value.is_following = response.data.is_following ?? !currentSignal.value.is_following
        }
        return { 
          success: true, 
          is_following: response.data.is_following,
          message: response.data.message
        }
      }
      return { success: false, message: response.data.message || '操作失败' }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message || '操作失败' }
    }
  }

  async function likeSignal(signalId: number) {
    try {
      const response = await signalApi.likeSignal(signalId)
      if (response.data.success) {
        const signal = signals.value.find(s => s.id === signalId)
        const likeData = response.data.data as any
        if (signal) {
          signal.is_liked = !signal.is_liked
          signal.likes = likeData?.likes ?? signal.likes + (signal.is_liked ? 1 : -1)
        }
        if (currentSignal.value?.id === signalId) {
          currentSignal.value.is_liked = !currentSignal.value.is_liked
          currentSignal.value.likes = likeData?.likes ?? currentSignal.value.likes + (currentSignal.value.is_liked ? 1 : -1)
        }
        return { success: true, likes: likeData?.likes }
      }
      return { success: false, message: response.data.message || '点赞失败' }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message || '点赞失败' }
    }
  }

  async function likeReply(signalId: number, replyId: number) {
    try {
      const response = await signalApi.likeReply(signalId, replyId)
      if (response.data.success) {
        const reply = replies.value.find(r => r.id === replyId)
        const likeData = response.data.data as any
        if (reply) {
          reply.is_liked = !reply.is_liked
          reply.likes = likeData?.likes ?? reply.likes + (reply.is_liked ? 1 : -1)
        }
        return { success: true, likes: likeData?.likes }
      }
      return { success: false, message: response.data.message || '点赞失败' }
    } catch (e: any) {
      return { success: false, message: e.response?.data?.message || '点赞失败' }
    }
  }

  async function fetchMarketNews(limit = 20) {
    isLoading.value = true
    error.value = null
    try {
      const response = await marketApi.getNews(limit)
      if (response.data.success && response.data.data) {
        marketNews.value = response.data.data
      }
      return marketNews.value
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取市场新闻失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMarketEvents(limit = 20) {
    isLoading.value = true
    error.value = null
    try {
      const response = await marketApi.getEvents(limit)
      if (response.data.success && response.data.data) {
        marketEvents.value = response.data.data
      }
      return marketEvents.value
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取市场事件失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchEconomicIndicators(limit = 20) {
    isLoading.value = true
    error.value = null
    try {
      const response = await marketApi.getIndicators(limit)
      if (response.data.success && response.data.data) {
        economicIndicators.value = response.data.data
      }
      return economicIndicators.value
    } catch (e: any) {
      error.value = e.response?.data?.message || '获取经济指标失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function clearCurrentSignal() {
    currentSignal.value = null
    replies.value = []
    participants.value = []
    qualityScore.value = null
  }

  return {
    signals,
    currentSignal,
    replies,
    participants,
    qualityScore,
    marketNews,
    marketEvents,
    economicIndicators,
    isLoading,
    error,
    sortedSignals,
    fetchSignals,
    fetchSignalDetail,
    fetchReplies,
    createSignal,
    addReply,
    toggleFollow,
    likeSignal,
    likeReply,
    fetchMarketNews,
    fetchMarketEvents,
    fetchEconomicIndicators,
    clearCurrentSignal
  }
})
