import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Strategy, StrategyTemplate, BacktestResult } from '../services/strategy'
import { strategyService } from '../services/strategy'

export const useStrategyStore = defineStore('strategy', () => {
  const strategies = ref<Strategy[]>([])
  const templates = ref<StrategyTemplate[]>([])
  const currentStrategy = ref<Strategy | null>(null)
  const backtestResult = ref<BacktestResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadStrategies(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.getStrategies(params)
      if (response.success && response.data) {
        strategies.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载策略列表失败'
    } finally {
      loading.value = false
    }
  }

  async function loadStrategy(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.getStrategy(id)
      if (response.success && response.data) {
        currentStrategy.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载策略详情失败'
    } finally {
      loading.value = false
    }
  }

  async function createStrategy(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.createStrategy(data)
      if (response.success && response.data) {
        strategies.value.unshift(response.data)
        return response.data
      }
      throw new Error(response.message || '创建策略失败')
    } catch (e: any) {
      error.value = e.message || '创建策略失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateStrategy(id: number, data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.updateStrategy(id, data)
      if (response.success && response.data) {
        const index = strategies.value.findIndex(s => s.id === id)
        if (index !== -1) {
          strategies.value[index] = response.data
        }
        if (currentStrategy.value?.id === id) {
          currentStrategy.value = response.data
        }
        return response.data
      }
      throw new Error(response.message || '更新策略失败')
    } catch (e: any) {
      error.value = e.message || '更新策略失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteStrategy(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.deleteStrategy(id)
      if (response.success) {
        strategies.value = strategies.value.filter(s => s.id !== id)
        if (currentStrategy.value?.id === id) {
          currentStrategy.value = null
        }
      }
      return response
    } catch (e: any) {
      error.value = e.message || '删除策略失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadTemplates(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.getTemplates(params)
      if (response.success && response.data) {
        templates.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载策略模板失败'
    } finally {
      loading.value = false
    }
  }

  async function runBacktest(strategyId: number, params: any) {
    loading.value = true
    error.value = null
    try {
      const response = await strategyService.runBacktest(strategyId, params)
      if (response.success && response.data) {
        backtestResult.value = response.data
        return response.data
      }
      throw new Error(response.message || '回测失败')
    } catch (e: any) {
      error.value = e.message || '回测失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function toggleStrategy(id: number, active: boolean) {
    try {
      const response = await strategyService.toggleStrategy(id, active)
      if (response.success && response.data) {
        const index = strategies.value.findIndex(s => s.id === id)
        if (index !== -1) {
          strategies.value[index] = response.data
        }
        return response.data
      }
      throw new Error(response.message || '切换策略状态失败')
    } catch (e: any) {
      error.value = e.message || '切换策略状态失败'
      throw e
    }
  }

  return {
    strategies,
    templates,
    currentStrategy,
    backtestResult,
    loading,
    error,
    loadStrategies,
    loadStrategy,
    createStrategy,
    updateStrategy,
    deleteStrategy,
    loadTemplates,
    runBacktest,
    toggleStrategy
  }
})
