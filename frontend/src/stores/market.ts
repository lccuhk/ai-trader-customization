import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MarketNews, MarketEvent, EconomicIndicator, MarketSentiment, MarketTicker } from '../services/market'
import { marketService } from '../services/market'

export const useMarketStore = defineStore('market', () => {
  const news = ref<MarketNews[]>([])
  const events = ref<MarketEvent[]>([])
  const indicators = ref<EconomicIndicator[]>([])
  const sentiment = ref<MarketSentiment | null>(null)
  const trending = ref<MarketTicker[]>([])
  const marketData = ref<MarketTicker[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadNews(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getNews(params)
      if (response.success && response.data) {
        news.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载市场新闻失败'
    } finally {
      loading.value = false
    }
  }

  async function loadEvents(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getEvents(params)
      if (response.success && response.data) {
        events.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载市场事件失败'
    } finally {
      loading.value = false
    }
  }

  async function loadIndicators(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getIndicators(params)
      if (response.success && response.data) {
        indicators.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载经济指标失败'
    } finally {
      loading.value = false
    }
  }

  async function loadSentiment() {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getSentiment()
      if (response.success && response.data) {
        sentiment.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载市场情绪失败'
    } finally {
      loading.value = false
    }
  }

  async function loadTrending(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getTrending(params)
      if (response.success && response.data) {
        trending.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载涨跌榜失败'
    } finally {
      loading.value = false
    }
  }

  async function loadMarketData(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await marketService.getMarketData(params)
      if (response.success && response.data) {
        marketData.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载市场数据失败'
    } finally {
      loading.value = false
    }
  }

  function updatePrices() {
    marketData.value.forEach(item => {
      const change = (Math.random() - 0.5) * 0.02 * item.price
      item.price = Math.max(0.0001, item.price + change)
      item.changePercent = item.changePercent + (Math.random() - 0.5) * 0.5
    })
  }

  return {
    news,
    events,
    indicators,
    sentiment,
    trending,
    marketData,
    loading,
    error,
    loadNews,
    loadEvents,
    loadIndicators,
    loadSentiment,
    loadTrending,
    loadMarketData,
    updatePrices
  }
})
