import { defineStore } from 'pinia'
import { ref } from 'vue'

interface FavoriteSignal {
  id: number
  title: string
  agent_name: string
  added_at: string
}

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<FavoriteSignal[]>(() => {
    const saved = localStorage.getItem('favorites')
    return saved ? JSON.parse(saved) : []
  })

  function saveFavorites() {
    localStorage.setItem('favorites', JSON.stringify(favorites.value))
  }

  function toggleFavorite(signalId: number, title: string, agentName: string) {
    const index = favorites.value.findIndex(f => f.id === signalId)
    if (index >= 0) {
      favorites.value.splice(index, 1)
    } else {
      favorites.value.unshift({
        id: signalId,
        title,
        agent_name: agentName,
        added_at: new Date().toISOString()
      })
    }
    saveFavorites()
  }

  function isFavorite(signalId: number) {
    return favorites.value.some(f => f.id === signalId)
  }

  function clearFavorites() {
    favorites.value = []
    saveFavorites()
  }

  return {
    favorites,
    toggleFavorite,
    isFavorite,
    clearFavorites
  }
})
