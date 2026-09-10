import React from 'react'

const ThemeContext = React.createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = React.useState(() => {
    try {
      const saved = localStorage.getItem('cardiosense-theme')
      if (saved) return saved
    } catch (e) { /* ignore */ }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark'
    return 'light'
  })

  React.useEffect(() => {
    if (theme === 'dark') document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
    try {
      localStorage.setItem('cardiosense-theme', theme)
    } catch (e) { /* ignore */ }
  }, [theme])

  const setTheme = (t) => setThemeState(t)
  const toggleTheme = () => setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'))

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = React.useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider')
  return ctx
}
