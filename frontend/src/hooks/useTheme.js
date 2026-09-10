export function useTheme() {
  const applyTheme = (theme) => {
    if (theme === 'dark') document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
    try {
      localStorage.setItem('cardiosense-theme', theme)
    } catch (e) {
      /* ignore */
    }
  }

  const getTheme = () => {
    try {
      const saved = localStorage.getItem('cardiosense-theme')
      if (saved) return saved
    } catch (e) {
      /* ignore */
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark'
    return 'light'
  }

  const theme = getTheme()
  applyTheme(theme)

  const setTheme = (t) => applyTheme(t)

  return { theme, setTheme }
}
