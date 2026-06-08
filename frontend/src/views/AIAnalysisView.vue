<template>
  <div class="ai-analysis-view">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">AI 交易分析</h1>
        <p class="text-gray-600">深度分析您的交易行为，发现优化机会</p>
      </div>

      <div class="mb-6 flex gap-4">
        <select
          v-model="analysisType"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="comprehensive">综合分析</option>
          <option value="performance">绩效分析</option>
          <option value="behavior">行为分析</option>
          <option value="risk">风险分析</option>
        </select>
        <button
          @click="runAnalysis"
          :disabled="loading"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <svg v-if="loading" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          {{ loading ? '分析中...' : '开始分析' }}
        </button>
      </div>

      <div v-if="analysisResult" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">总胜率</p>
                <p class="text-2xl font-bold" :class="analysisResult.performance.win_rate >= 50 ? 'text-green-600' : 'text-red-600'">
                  {{ analysisResult.performance.win_rate?.toFixed(1) }}%
                </p>
              </div>
              <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">盈亏比</p>
                <p class="text-2xl font-bold" :class="analysisResult.performance.profit_loss_ratio >= 1.5 ? 'text-green-600' : 'text-yellow-600'">
                  {{ analysisResult.performance.profit_loss_ratio?.toFixed(2) }}
                </p>
              </div>
              <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">夏普比率</p>
                <p class="text-2xl font-bold" :class="analysisResult.performance.sharpe_ratio >= 1 ? 'text-green-600' : 'text-yellow-600'">
                  {{ analysisResult.performance.sharpe_ratio?.toFixed(2) }}
                </p>
              </div>
              <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">最大回撤</p>
                <p class="text-2xl font-bold" :class="analysisResult.performance.max_drawdown <= 20 ? 'text-green-600' : 'text-red-600'">
                  {{ analysisResult.performance.max_drawdown?.toFixed(1) }}%
                </p>
              </div>
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">交易行为分析</h3>
            <div class="space-y-4">
              <div v-for="pattern in analysisResult.behavior.patterns" :key="pattern.name" class="flex items-center justify-between">
                <span class="text-gray-600">{{ pattern.name }}</span>
                <div class="flex items-center gap-2">
                  <div class="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      class="h-2 rounded-full"
                      :class="pattern.severity === 'good' ? 'bg-green-500' : pattern.severity === 'warning' ? 'bg-yellow-500' : 'bg-red-500'"
                      :style="{ width: pattern.value + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium" :class="pattern.severity === 'good' ? 'text-green-600' : pattern.severity === 'warning' ? 'text-yellow-600' : 'text-red-600'">
                    {{ pattern.value }}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">风险评估</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-gray-600">风险等级</span>
                <span
                  class="px-3 py-1 rounded-full text-sm font-medium"
                  :class="{
                    'bg-green-100 text-green-800': analysisResult.risk.level === 'low',
                    'bg-yellow-100 text-yellow-800': analysisResult.risk.level === 'medium',
                    'bg-red-100 text-red-800': analysisResult.risk.level === 'high'
                  }"
                >
                  {{ analysisResult.risk.level === 'low' ? '低' : analysisResult.risk.level === 'medium' ? '中' : '高' }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-gray-600">仓位集中度</span>
                <span class="font-medium">{{ analysisResult.risk.position_concentration?.toFixed(1) }}%</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-gray-600">杠杆使用率</span>
                <span class="font-medium">{{ analysisResult.risk.leverage_usage?.toFixed(1) }}x</span>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">AI 优化建议</h3>
          <div class="space-y-3">
            <div
              v-for="(suggestion, index) in analysisResult.suggestions"
              :key="index"
              class="flex items-start gap-3 p-4 bg-gray-50 rounded-lg"
            >
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                :class="suggestion.priority === 'high' ? 'bg-red-100' : suggestion.priority === 'medium' ? 'bg-yellow-100' : 'bg-green-100'"
              >
                <svg
                  class="w-4 h-4"
                  :class="suggestion.priority === 'high' ? 'text-red-600' : suggestion.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ suggestion.title }}</p>
                <p class="text-sm text-gray-600 mt-1">{{ suggestion.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">历史分析记录</h3>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">分析时间</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">类型</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">胜率</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">盈亏比</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-gray-500">夏普比率</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in analysisHistory" :key="record.id" class="border-b border-gray-100 hover:bg-gray-50">
                  <td class="py-3 px-4 text-sm text-gray-900">{{ formatDate(record.created_at) }}</td>
                  <td class="py-3 px-4 text-sm text-gray-600">{{ record.analysis_type }}</td>
                  <td class="py-3 px-4 text-sm" :class="record.win_rate >= 50 ? 'text-green-600' : 'text-red-600'">
                    {{ record.win_rate?.toFixed(1) }}%
                  </td>
                  <td class="py-3 px-4 text-sm text-gray-900">{{ record.profit_loss_ratio?.toFixed(2) }}</td>
                  <td class="py-3 px-4 text-sm text-gray-900">{{ record.sharpe_ratio?.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="text-center py-16">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">开始您的第一次 AI 分析</h3>
        <p class="text-gray-500">点击上方按钮，AI 将深度分析您的交易历史并提供个性化建议</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { aiService } from '../services/ai'
import type { AIAnalysis } from '../types'

const analysisType = ref('comprehensive')
const loading = ref(false)
const analysisResult = ref<AIAnalysis | null>(null)
const analysisHistory = ref<AIAnalysis[]>([])

const runAnalysis = async () => {
  loading.value = true
  try {
    const response = await aiService.analyzeTrading(analysisType.value)
    analysisResult.value = response.data
    await loadHistory()
  } catch (error) {
    console.error('分析失败:', error)
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  try {
    const response = await aiService.getAnalysisHistory()
    analysisHistory.value = response.data
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadHistory()
})
</script>
