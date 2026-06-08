<template>
  <div class="ai-strategies-view">
    <div class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">AI 策略中心</h1>
        <p class="text-gray-600">生成智能交易策略，回测历史表现</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-6">生成新策略</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">交易品种</label>
                <select
                  v-model="strategyForm.symbol"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="BTC">BTC/USDT</option>
                  <option value="ETH">ETH/USDT</option>
                  <option value="BNB">BNB/USDT</option>
                  <option value="SOL">SOL/USDT</option>
                  <option value="XRP">XRP/USDT</option>
                  <option value="AAPL">AAPL</option>
                  <option value="GOOGL">GOOGL</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">策略类型</label>
                <select
                  v-model="strategyForm.strategy_type"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="trend_following">趋势跟踪</option>
                  <option value="mean_reversion">均值回归</option>
                  <option value="breakout">突破策略</option>
                  <option value="arbitrage">套利策略</option>
                  <option value="grid">网格交易</option>
                  <option value="martingale">马丁格尔</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">时间周期</label>
                <select
                  v-model="strategyForm.timeframe"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="1m">1分钟</option>
                  <option value="5m">5分钟</option>
                  <option value="15m">15分钟</option>
                  <option value="1h">1小时</option>
                  <option value="4h">4小时</option>
                  <option value="1d">1天</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">风险等级</label>
                <select
                  v-model="strategyForm.risk_level"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">保守</option>
                  <option value="medium">稳健</option>
                  <option value="high">激进</option>
                </select>
              </div>
            </div>
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">策略描述（可选）</label>
              <textarea
                v-model="strategyForm.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="描述您的策略思路..."
              ></textarea>
            </div>
            <div class="flex gap-4">
              <button
                @click="generateStrategy"
                :disabled="generating"
                class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <svg v-if="generating" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {{ generating ? 'AI 生成中...' : '生成策略' }}
              </button>
              <button
                @click="showBacktestModal = true"
                :disabled="!generatedStrategy"
                class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                回测策略
              </button>
            </div>
          </div>

          <div v-if="generatedStrategy" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">AI 生成的策略</h3>
              <span
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="{
                  'bg-green-100 text-green-800': generatedStrategy.status === 'active',
                  'bg-yellow-100 text-yellow-800': generatedStrategy.status === 'testing',
                  'bg-gray-100 text-gray-800': generatedStrategy.status === 'inactive'
                }"
              >
                {{ generatedStrategy.status === 'active' ? '运行中' : generatedStrategy.status === 'testing' ? '测试中' : '已停止' }}
              </span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-sm text-gray-500">预期年化收益</p>
                <p class="text-xl font-bold text-green-600">+{{ generatedStrategy.expected_return?.toFixed(1) }}%</p>
              </div>
              <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-sm text-gray-500">最大回撤</p>
                <p class="text-xl font-bold text-red-600">{{ generatedStrategy.max_drawdown?.toFixed(1) }}%</p>
              </div>
              <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-sm text-gray-500">胜率</p>
                <p class="text-xl font-bold text-blue-600">{{ generatedStrategy.win_rate?.toFixed(1) }}%</p>
              </div>
            </div>
            <div class="p-4 bg-blue-50 rounded-lg mb-4">
              <h4 class="font-medium text-blue-900 mb-2">策略逻辑</h4>
              <p class="text-sm text-blue-800">{{ generatedStrategy.parameters?.logic }}</p>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-2">入场条件</h4>
              <ul class="text-sm text-gray-600 space-y-1">
                <li v-for="(condition, index) in generatedStrategy.parameters?.entry_conditions" :key="index">
                  • {{ condition }}
                </li>
              </ul>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg mt-4">
              <h4 class="font-medium text-gray-900 mb-2">出场条件</h4>
              <ul class="text-sm text-gray-600 space-y-1">
                <li v-for="(condition, index) in generatedStrategy.parameters?.exit_conditions" :key="index">
                  • {{ condition }}
                </li>
              </ul>
            </div>
            <div class="flex gap-4 mt-6">
              <button
                @click="saveStrategy"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存策略
              </button>
              <button
                @click="activateStrategy(generatedStrategy)"
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                激活运行
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">我的策略</h3>
            <div class="space-y-3">
              <div
                v-for="strategy in strategies"
                :key="strategy.id"
                @click="selectStrategy(strategy)"
                class="p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
                :class="{ 'border-blue-500 bg-blue-50': selectedStrategy?.id === strategy.id }"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="font-medium text-gray-900">{{ strategy.symbol }}</span>
                  <span
                    class="px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-green-100 text-green-800': strategy.status === 'active',
                      'bg-yellow-100 text-yellow-800': strategy.status === 'testing',
                      'bg-gray-100 text-gray-800': strategy.status === 'inactive'
                    }"
                  >
                    {{ strategy.status === 'active' ? '运行中' : strategy.status === 'testing' ? '测试中' : '已停止' }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 mb-2">{{ strategy.strategy_type }}</p>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-green-600">+{{ strategy.expected_return?.toFixed(1) }}%</span>
                  <span class="text-gray-400">{{ formatDate(strategy.created_at) }}</span>
                </div>
              </div>
            </div>
            <div v-if="strategies.length === 0" class="text-center py-8 text-gray-500">
              暂无策略，开始生成第一个吧
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedStrategy" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">策略回测结果</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="p-4 bg-gray-50 rounded-lg text-center">
            <p class="text-sm text-gray-500">总收益</p>
            <p class="text-2xl font-bold" :class="selectedStrategy.backtest_result?.total_return >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ selectedStrategy.backtest_result?.total_return >= 0 ? '+' : '' }}{{ selectedStrategy.backtest_result?.total_return?.toFixed(1) }}%
            </p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg text-center">
            <p class="text-sm text-gray-500">年化收益</p>
            <p class="text-2xl font-bold" :class="selectedStrategy.backtest_result?.annualized_return >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ selectedStrategy.backtest_result?.annualized_return >= 0 ? '+' : '' }}{{ selectedStrategy.backtest_result?.annualized_return?.toFixed(1) }}%
            </p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg text-center">
            <p class="text-sm text-gray-500">最大回撤</p>
            <p class="text-2xl font-bold text-red-600">{{ selectedStrategy.backtest_result?.max_drawdown?.toFixed(1) }}%</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg text-center">
            <p class="text-sm text-gray-500">夏普比率</p>
            <p class="text-2xl font-bold text-blue-600">{{ selectedStrategy.backtest_result?.sharpe_ratio?.toFixed(2) }}</p>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-500">交易次数</p>
            <p class="text-xl font-bold text-gray-900">{{ selectedStrategy.backtest_result?.total_trades }}</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-500">胜率</p>
            <p class="text-xl font-bold" :class="selectedStrategy.backtest_result?.win_rate >= 50 ? 'text-green-600' : 'text-red-600'">
              {{ selectedStrategy.backtest_result?.win_rate?.toFixed(1) }}%
            </p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-500">盈亏比</p>
            <p class="text-xl font-bold text-gray-900">{{ selectedStrategy.backtest_result?.profit_loss_ratio?.toFixed(2) }}</p>
          </div>
        </div>
      </div>

      <div v-if="showBacktestModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">回测设置</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">回测开始日期</label>
              <input
                v-model="backtestForm.start_date"
                type="date"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">回测结束日期</label>
              <input
                v-model="backtestForm.end_date"
                type="date"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">初始资金 (USDT)</label>
              <input
                v-model.number="backtestForm.initial_capital"
                type="number"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="10000"
              />
            </div>
          </div>
          <div class="flex gap-4 mt-6">
            <button
              @click="showBacktestModal = false"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              取消
            </button>
            <button
              @click="runBacktest"
              :disabled="backtesting"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ backtesting ? '回测中...' : '开始回测' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { aiService } from '../services/ai'
import type { AIStrategy } from '../types'

const generating = ref(false)
const backtesting = ref(false)
const showBacktestModal = ref(false)
const generatedStrategy = ref<AIStrategy | null>(null)
const selectedStrategy = ref<AIStrategy | null>(null)
const strategies = ref<AIStrategy[]>([])

const strategyForm = ref({
  symbol: 'BTC',
  strategy_type: 'trend_following',
  timeframe: '1h',
  risk_level: 'medium',
  description: ''
})

const backtestForm = ref({
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  initial_capital: 10000
})

const generateStrategy = async () => {
  generating.value = true
  try {
    const response = await aiService.generateStrategy(strategyForm.value)
    generatedStrategy.value = response.data
  } catch (error) {
    console.error('生成策略失败:', error)
  } finally {
    generating.value = false
  }
}

const runBacktest = async () => {
  if (!generatedStrategy.value) return
  backtesting.value = true
  try {
    const response = await aiService.runBacktest(generatedStrategy.value.id, backtestForm.value)
    generatedStrategy.value = response.data
    selectedStrategy.value = response.data
    showBacktestModal.value = false
    await loadStrategies()
  } catch (error) {
    console.error('回测失败:', error)
  } finally {
    backtesting.value = false
  }
}

const saveStrategy = async () => {
  if (!generatedStrategy.value) return
  try {
    await aiService.saveStrategy(generatedStrategy.value)
    await loadStrategies()
    alert('策略保存成功')
  } catch (error) {
    console.error('保存策略失败:', error)
  }
}

const activateStrategy = async (strategy: AIStrategy) => {
  try {
    const response = await aiService.activateStrategy(strategy.id)
    strategy.status = response.data.status
    await loadStrategies()
  } catch (error) {
    console.error('激活策略失败:', error)
  }
}

const selectStrategy = (strategy: AIStrategy) => {
  selectedStrategy.value = strategy
}

const loadStrategies = async () => {
  try {
    const response = await aiService.getStrategies()
    strategies.value = response.data
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadStrategies()
})
</script>
