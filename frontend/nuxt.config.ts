export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  app: {
    head: {
      title: 'Agenda Clinica',
      meta: [
        {
          name: 'description',
          content: 'Painel Nuxt para o SaaS de agendamento medico.'
        }
      ]
    }
  }
})
