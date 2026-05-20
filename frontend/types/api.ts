export interface AuthUser {
  access_token: string
  user_id: number
  email: string
  name: string
}

export interface Appointment {
  id: number
  doctor_id: number
  patient_id: number
  appointment_date: string
  start_time: string
  end_time: string
  status: 'pending' | 'confirmed' | 'canceled' | string
  created_at: string
}

export interface AppointmentPayload {
  doctor_id: number
  appointment_date: string
  start_time: string
  end_time: string
  tenant_id: number
  status: string
}
