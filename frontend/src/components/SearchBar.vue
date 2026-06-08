<template>
  <div class="search-bar">
    <input
      v-model="searchQuery"
      type="text"
      placeholder="搜索信号、新闻、市场..."
      class="search-input"
      @input="handleSearch"
      @focus="isFocused = true"
      @blur="handleBlur"
    />
    <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
    <div v-if="isFocused && searchQuery" class="search-suggestions">
      <div v-if="suggestions.length > 0" class="suggestion-list">
        <div v-for="item in suggestions" :key="item.id" class="suggestion-item" @click="handleSuggestionClick(item)">
          <span class="suggestion-type">{{ item.type }}</span>
          <span class="suggestion-title">{{ item.title }}</span>
        </div>
      </div>
      <div v-else class="no-results">没有找到相关结果</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const isFocused = ref(false)

const suggestions = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  const mockSuggestions = [
    { id: 1, type: '信号', title: 'NVDA 突破分析', url: '/signal/1' },
    { id: 2, type: '信号', title: 'AAPL 买入机会', url: '/signal/2' },
    { id: 3, type: '新闻', title: '美联储利率决议前瞻', url: '/market' },
    { id: 4, type: '新闻', title: 'AI 芯片需求暴涨', url: '/market' },
    { id: 5, type: '市场', title: 'BTC 减半行情', url: '/market' }
  ]
  return mockSuggestions.filter(item => 
    item.title.toLowerCase().includes(query)
  ).slice(0, 5)
})

function handleSearch() {
  console.log('搜索:', searchQuery.value)
}

function handleSuggestionClick(item: any) {
  searchQuery.value = ''
  isFocused.value = false
  router.push(item.url)
}

function handleBlur() {
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}
</script>

<style scoped>
.search-bar {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.suggestion-list {
  padding: 8px;
}

.suggestion-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  gap: 12px;
  align-items: center;
  transition: background 0.2s;
}

.suggestion-item:hover {
  background: var(--bg-secondary);
}

.suggestion-type {
  background: var(--accent-color);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.suggestion-title {
  color: var(--text-primary);
  font-size: 14px;
}

.no-results {
  padding: 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}
</style>
