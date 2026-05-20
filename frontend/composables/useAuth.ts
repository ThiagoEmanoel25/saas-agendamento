import type { AuthUser } from '~/types/api'

export const useAuth = () => {
  const user = useState<AuthUser | null>('auth:user', () => null)
  const token = useState<string | null>('auth:token', () => null)

  const isAuthenticated = computed(() => Boolean(token.value))

  const restore = () => {
    if (!import.meta.client || token.value) return

    const storedToken = localStorage.getItem('saas_agendamento_token')
    const storedUser = localStorage.getItem('saas_agendamento_user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
    }
  }

  const setSession = (payload: AuthUser) => {
    user.value = payload
    token.value = payload.access_token

    if (import.meta.client) {
      localStorage.setItem('saas_agendamento_token', payload.access_token)
      localStorage.setItem('saas_agendamento_user', JSON.stringify(payload))
    }
  }

  const logout = () => {
    user.value = null
    token.value = null

    if (import.meta.client) {
      localStorage.removeItem('saas_agendamento_token')
      localStorage.removeItem('saas_agendamento_user')
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    restore,
    setSession,
    logout
  }
}
