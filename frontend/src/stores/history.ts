import { defineStore } from 'pinia'
import { ref } from 'vue'

interface HistoryItem {
  id: string
  type: string
  title: string
  url: string
  timestamp: string
}

export const useHistoryStore = defineStore('history', () => {
  const history = ref<HistoryItem[]>(() => {
    const saved = localStorage.getItem('history')
    return saved ? JSON.parse(saved) : []
  })

  function saveHistory() {
    localStorage.setItem('history', JSON.stringify(history.value.slice(0, 100)))
  }

  function addHistoryItem(type: string, title: string, url: string) {
    const item: HistoryItem = {
      id: Date.now().toString(),
      type,
      title,
      url,
      timestamp: new Date().toISOString()
    }
    history.value.unshift(item)
    saveHistory()
  }

  function clearHistory() {
    history.value = []
    saveHistory()
  }

  function removeHistoryItem(id: string) {
    const index = history.value.findIndex(h => h.id === id)
    if (index >= 0) {
      history.value.splice(index, 1)
      saveHistory()
    }
  }

  return {
    history,
    addHistoryItem,
    clearHistory,
    removeHistoryItem
  }
})
