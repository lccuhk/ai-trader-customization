import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RiskMetric, RiskAlert, RiskSettings } from '../services/risk'
import { riskService } from '../services/risk'

export const useRiskStore = defineStore('risk', () => {
  const metrics = ref<RiskMetric[]>([])
  const alerts = ref<RiskAlert[]>([])
  const settings = ref<RiskSettings | null>(null)
  const exposure = ref<{ symbol: string; percentage: number; value: number }[]>([])
  const riskScore = ref(0)
  const activeAlertsCount = ref(0)
  const triggeredToday = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadDashboard() {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.getDashboard()
      if (response.success && response.data) {
        metrics.value = response.data.metrics
        exposure.value = response.data.exposure
        activeAlertsCount.value = response.data.activeAlerts
        triggeredToday.value = response.data.triggeredToday
        riskScore.value = response.data.riskScore
      }
    } catch (e: any) {
      error.value = e.message || '加载风险仪表盘失败'
    } finally {
      loading.value = false
    }
  }

  async function loadAlerts(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.getAlerts(params)
      if (response.success && response.data) {
        alerts.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载风险预警失败'
    } finally {
      loading.value = false
    }
  }

  async function createAlert(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.createAlert(data)
      if (response.success && response.data) {
        alerts.value.unshift(response.data)
        return response.data
      }
      throw new Error(response.message || '创建预警失败')
    } catch (e: any) {
      error.value = e.message || '创建预警失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateAlert(id: number, data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.updateAlert(id, data)
      if (response.success && response.data) {
        const index = alerts.value.findIndex(a => a.id === id)
        if (index !== -1) {
          alerts.value[index] = response.data
        }
        return response.data
      }
      throw new Error(response.message || '更新预警失败')
    } catch (e: any) {
      error.value = e.message || '更新预警失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteAlert(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.deleteAlert(id)
      if (response.success) {
        alerts.value = alerts.value.filter(a => a.id !== id)
      }
      return response
    } catch (e: any) {
      error.value = e.message || '删除预警失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadSettings() {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.getSettings()
      if (response.success && response.data) {
        settings.value = response.data
      }
    } catch (e: any) {
      error.value = e.message || '加载风险设置失败'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await riskService.updateSettings(data)
      if (response.success && response.data) {
        settings.value = response.data
        return response.data
      }
      throw new Error(response.message || '更新设置失败')
    } catch (e: any) {
      error.value = e.message || '更新设置失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    metrics,
    alerts,
    settings,
    exposure,
    riskScore,
    activeAlertsCount,
    triggeredToday,
    loading,
    error,
    loadDashboard,
    loadAlerts,
    createAlert,
    updateAlert,
    deleteAlert,
    loadSettings,
    updateSettings
  }
})
