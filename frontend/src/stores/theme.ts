import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

type Theme = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'auto')

  function applyTheme(theme: Theme) {
    const root = document.documentElement
    
    let effectiveTheme = theme
    if (theme === 'auto') {
      effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    if (effectiveTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    localStorage.setItem('theme', theme)
  }

  function setTheme(theme: Theme) {
    currentTheme.value = theme
    applyTheme(theme)
  }

  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  function toggleTheme() {
    const themes: Theme[] = ['light', 'dark', 'auto']
    const currentIndex = themes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  return {
    currentTheme,
    setTheme,
    toggleTheme
  }
})
