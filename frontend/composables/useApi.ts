import type { Appointment, AppointmentPayload, AuthUser } from '~/types/api'

type LoginPayload = {
  email: string
  password: string
}

type RegisterPayload = LoginPayload & {
  name: string
  tenant_id: number
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const { token } = useAuth()

  const request = async <T>(path: string, options: Parameters<typeof $fetch>[1] = {}) => {
    return await $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...options,
      headers: {
        ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
        ...(options?.headers || {})
      }
    })
  }

  return {
    login: (payload: LoginPayload) =>
      request<AuthUser>('/auth/login', {
        method: 'POST',
        body: payload
      }),
    register: (payload: RegisterPayload) =>
      request<AuthUser>('/auth/register', {
        method: 'POST',
        body: payload
      }),
    listAppointments: () => request<Appointment[]>('/appointments/'),
    createAppointment: (payload: AppointmentPayload) =>
      request<Appointment>('/appointments/', {
        method: 'POST',
        body: payload
      }),
    cancelAppointment: (id: number) =>
      request<{ id: number; status: string; message: string }>(`/appointments/${id}/cancel`, {
        method: 'PATCH'
      })
  }
}
