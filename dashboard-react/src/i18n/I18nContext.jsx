import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { translations, LANGUAGES, LANGUAGE_LABELS } from './translations'

const I18nContext = createContext(null)

// Helper function to get nested translation by dot notation key
const getNestedValue = (obj, path) => {
  return path.split('.').reduce((acc, part) => {
    return acc && acc[part] !== undefined ? acc[part] : undefined
  }, obj)
}

export function I18nProvider({ children }) {
  // Initialize language from localStorage or default to French
  const [language, setLanguageState] = useState(() => {
    const stored = localStorage.getItem('synapsix_language')
    return stored && Object.values(LANGUAGES).includes(stored) ? stored : LANGUAGES.FR
  })

  // Persist language preference
  useEffect(() => {
    localStorage.setItem('synapsix_language', language)
    // Update document language attribute
    document.documentElement.lang = language
  }, [language])

  // Set language with validation
  const setLanguage = useCallback((lang) => {
    if (Object.values(LANGUAGES).includes(lang)) {
      setLanguageState(lang)
    } else {
      console.warn(`Invalid language: ${lang}. Available: ${Object.values(LANGUAGES).join(', ')}`)
    }
  }, [])

  // Cycle through languages
  const cycleLanguage = useCallback(() => {
    const langs = Object.values(LANGUAGES)
    const currentIndex = langs.indexOf(language)
    const nextIndex = (currentIndex + 1) % langs.length
    setLanguageState(langs[nextIndex])
  }, [language])

  // Get translation by key (supports dot notation: "nav.main.home")
  const t = useCallback((key, fallback = key) => {
    const translation = getNestedValue(translations[language], key)
    if (translation === undefined) {
      console.warn(`Translation missing for key: ${key} in language: ${language}`)
      // Try English as fallback
      const enFallback = getNestedValue(translations[LANGUAGES.EN], key)
      return enFallback !== undefined ? enFallback : fallback
    }
    return translation
  }, [language])

  // Get all translations for current language
  const getTranslations = useCallback(() => {
    return translations[language]
  }, [language])

  // Check if a translation key exists
  const hasTranslation = useCallback((key) => {
    return getNestedValue(translations[language], key) !== undefined
  }, [language])

  // Get locale string for date formatting
  const getLocale = useCallback(() => {
    const localeMap = {
      [LANGUAGES.FR]: 'fr-FR',
      [LANGUAGES.EN]: 'en-GB',
      [LANGUAGES.NL]: 'nl-NL',
      [LANGUAGES.DE]: 'de-DE'
    }
    return localeMap[language] || 'fr-FR'
  }, [language])

  // Format date according to current language
  const formatDate = useCallback((date, options = {}) => {
    const dateObj = date instanceof Date ? date : new Date(date)
    return dateObj.toLocaleDateString(getLocale(), options)
  }, [getLocale])

  // Format time according to current language
  const formatTime = useCallback((date, options = {}) => {
    const dateObj = date instanceof Date ? date : new Date(date)
    return dateObj.toLocaleTimeString(getLocale(), options)
  }, [getLocale])

  // Format number according to current language
  const formatNumber = useCallback((number, options = {}) => {
    return new Intl.NumberFormat(getLocale(), options).format(number)
  }, [getLocale])

  const value = {
    // State
    language,
    languages: LANGUAGES,
    languageLabels: LANGUAGE_LABELS,

    // Actions
    setLanguage,
    cycleLanguage,

    // Translation functions
    t,
    getTranslations,
    hasTranslation,

    // Formatting functions
    getLocale,
    formatDate,
    formatTime,
    formatNumber
  }

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  )
}

// Custom hook for using i18n
export function useI18n() {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return context
}

// Shorthand hook for just the translation function
export function useTranslation() {
  const { t, language } = useI18n()
  return { t, language }
}

export { LANGUAGES, LANGUAGE_LABELS }
export default I18nContext
