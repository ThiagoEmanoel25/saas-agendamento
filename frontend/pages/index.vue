<script setup lang="ts">
import type { Appointment, AppointmentPayload } from '~/types/api'

const api = useApi()
const auth = useAuth()

const authMode = ref<'login' | 'register'>('login')
const loading = ref(false)
const loadingAppointments = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const appointments = ref<Appointment[]>([])

const loginForm = reactive({
  email: 'doctor@clinic.com',
  password: 'senha123'
})

const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  tenant_id: 1
})

const appointmentForm = reactive({
  doctor_id: 1,
  appointment_date: new Date().toISOString().slice(0, 10),
  start_time: '09:00',
  end_time: '09:30',
  tenant_id: 1,
  status: 'pending'
})

const statusLabels: Record<string, string> = {
  pending: 'Pendente',
  confirmed: 'Confirmado',
  canceled: 'Cancelado'
}

const sortedAppointments = computed(() => {
  return [...appointments.value].sort((a, b) => {
    return new Date(`${a.appointment_date.slice(0, 10)}T${a.start_time}`).getTime() -
      new Date(`${b.appointment_date.slice(0, 10)}T${b.start_time}`).getTime()
  })
})

const upcomingCount = computed(() => {
  const now = new Date()
  return appointments.value.filter((appointment) => {
    return appointment.status !== 'canceled' && new Date(appointment.appointment_date) >= now
  }).length
})

const canceledCount = computed(() => appointments.value.filter((appointment) => appointment.status === 'canceled').length)

const nextAppointment = computed(() => {
  return sortedAppointments.value.find((appointment) => appointment.status !== 'canceled')
})

const formatDate = (value: string) => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  }).format(new Date(value))
}

const formatTime = (value: string) => value.slice(0, 5)

const showError = (error: unknown, fallback: string) => {
  const apiError = error as { data?: { detail?: string | Array<{ msg: string }> } }
  const detail = apiError.data?.detail

  if (Array.isArray(detail)) {
    errorMessage.value = detail.map((item) => item.msg).join(' ')
    return
  }

  errorMessage.value = detail || fallback
}

const clearMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const loadAppointments = async () => {
  if (!auth.isAuthenticated.value) return

  loadingAppointments.value = true
  clearMessages()

  try {
    appointments.value = await api.listAppointments()
  } catch (error) {
    showError(error, 'Nao foi possivel carregar os agendamentos.')
  } finally {
    loadingAppointments.value = false
  }
}

const submitAuth = async () => {
  loading.value = true
  clearMessages()

  try {
    const session = authMode.value === 'login'
      ? await api.login(loginForm)
      : await api.register(registerForm)

    auth.setSession(session)
    successMessage.value = `Bem-vindo, ${session.name}.`
    await loadAppointments()
  } catch (error) {
    showError(error, authMode.value === 'login' ? 'Falha ao entrar.' : 'Falha ao cadastrar.')
  } finally {
    loading.value = false
  }
}

const submitAppointment = async () => {
  loading.value = true
  clearMessages()

  const payload: AppointmentPayload = {
    ...appointmentForm,
    appointment_date: `${appointmentForm.appointment_date}T00:00:00`
  }

  try {
    await api.createAppointment(payload)
    successMessage.value = 'Agendamento criado com sucesso.'
    await loadAppointments()
  } catch (error) {
    showError(error, 'Nao foi possivel criar o agendamento.')
  } finally {
    loading.value = false
  }
}

const cancelAppointment = async (id: number) => {
  loading.value = true
  clearMessages()

  try {
    await api.cancelAppointment(id)
    successMessage.value = 'Agendamento cancelado.'
    await loadAppointments()
  } catch (error) {
    showError(error, 'Nao foi possivel cancelar o agendamento.')
  } finally {
    loading.value = false
  }
}

const logout = () => {
  auth.logout()
  appointments.value = []
  successMessage.value = 'Sessao encerrada.'
}

onMounted(async () => {
  auth.restore()
  await loadAppointments()
})
</script>

<template>
  <main class="app-shell">
    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Clinica Sao Joao</p>
          <h1>Agenda medica</h1>
        </div>

        <div v-if="auth.user.value" class="session-card">
          <span>{{ auth.user.value.name }}</span>
          <button class="icon-button" type="button" aria-label="Sair" title="Sair" @click="logout">
            <span aria-hidden="true">⎋</span>
          </button>
        </div>
      </header>

      <div v-if="errorMessage" class="notice error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="notice success">{{ successMessage }}</div>

      <section v-if="!auth.isAuthenticated.value" class="auth-layout">
        <div class="auth-panel">
          <div class="tabs" role="tablist" aria-label="Autenticacao">
            <button :class="{ active: authMode === 'login' }" type="button" @click="authMode = 'login'">
              Entrar
            </button>
            <button :class="{ active: authMode === 'register' }" type="button" @click="authMode = 'register'">
              Criar conta
            </button>
          </div>

          <form class="form-stack" @submit.prevent="submitAuth">
            <label v-if="authMode === 'register'">
              Nome
              <input v-model="registerForm.name" required autocomplete="name" placeholder="Maria Santos">
            </label>

            <label>
              Email
              <input
                v-if="authMode === 'login'"
                v-model="loginForm.email"
                required
                type="email"
                autocomplete="email"
                placeholder="doctor@clinic.com"
              >
              <input
                v-else
                v-model="registerForm.email"
                required
                type="email"
                autocomplete="email"
                placeholder="voce@email.com"
              >
            </label>

            <label>
              Senha
              <input
                v-if="authMode === 'login'"
                v-model="loginForm.password"
                required
                type="password"
                autocomplete="current-password"
                placeholder="senha123"
              >
              <input
                v-else
                v-model="registerForm.password"
                required
                minlength="6"
                type="password"
                autocomplete="new-password"
                placeholder="minimo 6 caracteres"
              >
            </label>

            <label v-if="authMode === 'register'">
              Tenant
              <input v-model.number="registerForm.tenant_id" required min="1" type="number">
            </label>

            <button class="primary-button" type="submit" :disabled="loading">
              {{ loading ? 'Processando...' : authMode === 'login' ? 'Entrar' : 'Cadastrar' }}
            </button>
          </form>
        </div>
      </section>

      <section v-else class="dashboard-grid">
        <aside class="side-panel">
          <div class="metric-grid">
            <div class="metric">
              <span>Ativos</span>
              <strong>{{ upcomingCount }}</strong>
            </div>
            <div class="metric">
              <span>Cancelados</span>
              <strong>{{ canceledCount }}</strong>
            </div>
          </div>

          <div class="next-box">
            <span>Proximo horario</span>
            <strong v-if="nextAppointment">
              {{ formatDate(nextAppointment.appointment_date) }} as {{ formatTime(nextAppointment.start_time) }}
            </strong>
            <strong v-else>Nenhum agendamento</strong>
          </div>

          <form class="form-stack" @submit.prevent="submitAppointment">
            <h2>Novo agendamento</h2>
            <label>
              Medico ID
              <input v-model.number="appointmentForm.doctor_id" required min="1" type="number">
            </label>
            <label>
              Data
              <input v-model="appointmentForm.appointment_date" required type="date">
            </label>
            <div class="time-row">
              <label>
                Inicio
                <input v-model="appointmentForm.start_time" required type="time">
              </label>
              <label>
                Fim
                <input v-model="appointmentForm.end_time" required type="time">
              </label>
            </div>
            <label>
              Status
              <select v-model="appointmentForm.status">
                <option value="pending">Pendente</option>
                <option value="confirmed">Confirmado</option>
              </select>
            </label>
            <button class="primary-button" type="submit" :disabled="loading">
              {{ loading ? 'Salvando...' : 'Agendar' }}
            </button>
          </form>
        </aside>

        <section class="appointments-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Minha agenda</p>
              <h2>Consultas</h2>
            </div>
            <button class="secondary-button" type="button" :disabled="loadingAppointments" @click="loadAppointments">
              Atualizar
            </button>
          </div>

          <div v-if="loadingAppointments" class="empty-state">Carregando agenda...</div>
          <div v-else-if="sortedAppointments.length === 0" class="empty-state">Nenhum agendamento encontrado.</div>
          <article
            v-for="appointment in sortedAppointments"
            v-else
            :key="appointment.id"
            class="appointment-item"
            :class="appointment.status"
          >
            <div class="date-badge">
              <span>{{ formatDate(appointment.appointment_date).slice(0, 6) }}</span>
              <strong>{{ formatTime(appointment.start_time) }}</strong>
            </div>
            <div class="appointment-content">
              <div>
                <h3>Consulta #{{ appointment.id }}</h3>
                <p>
                  Medico {{ appointment.doctor_id }} · Paciente {{ appointment.patient_id }} ·
                  {{ formatTime(appointment.start_time) }}-{{ formatTime(appointment.end_time) }}
                </p>
              </div>
              <span class="status-pill">{{ statusLabels[appointment.status] || appointment.status }}</span>
            </div>
            <button
              class="ghost-button"
              type="button"
              :disabled="appointment.status === 'canceled' || loading"
              @click="cancelAppointment(appointment.id)"
            >
              Cancelar
            </button>
          </article>
        </section>
      </section>
    </section>
  </main>
</template>
