import { createI18n } from 'vue-i18n'
import zhCN from '../locales/zh-CN'
import enUS from '../locales/en-US'
import jaJP from '../locales/ja-JP'
import koKR from '../locales/ko-KR'
import frFR from '../locales/fr-FR'
import deDE from '../locales/de-DE'
import esES from '../locales/es-ES'
import ruRU from '../locales/ru-RU'

export const supportedLanguages = [
  { code: 'zh-CN', name: 'language.zhCN', flag: '🇨🇳' },
  { code: 'en-US', name: 'language.enUS', flag: '🇺🇸' },
  { code: 'ja-JP', name: 'language.jaJP', flag: '🇯🇵' },
  { code: 'ko-KR', name: 'language.koKR', flag: '🇰🇷' },
  { code: 'fr-FR', name: 'language.frFR', flag: '🇫🇷' },
  { code: 'de-DE', name: 'language.deDE', flag: '🇩🇪' },
  { code: 'es-ES', name: 'language.esES', flag: '🇪🇸' },
  { code: 'ru-RU', name: 'language.ruRU', flag: '🇷🇺' }
]

const savedLocale = localStorage.getItem('app-locale') || navigator.language || 'zh-CN'

// 确保语言代码在支持列表中
const getValidLocale = (locale: string): string => {
  const exactMatch = supportedLanguages.find(l => l.code === locale)
  if (exactMatch) return locale
  
  // 尝试匹配主语言代码（如 'zh' 匹配 'zh-CN'）
  const primaryLang = locale.split('-')[0]
  const partialMatch = supportedLanguages.find(l => l.code.startsWith(primaryLang))
  if (partialMatch) return partialMatch.code
  
  return 'zh-CN'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getValidLocale(savedLocale),
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP,
    'ko-KR': koKR,
    'fr-FR': frFR,
    'de-DE': deDE,
    'es-ES': esES,
    'ru-RU': ruRU
  }
})

export function setLocale(locale: string) {
  const validLocale = getValidLocale(locale)
  i18n.global.locale.value = validLocale
  localStorage.setItem('app-locale', validLocale)
  document.documentElement.lang = validLocale
}

export function getLocale(): string {
  return i18n.global.locale.value
}

export default i18n
