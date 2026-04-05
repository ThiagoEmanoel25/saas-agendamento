# SaaS de Agendamento

Sistema multi-tenant de agendamentos médicos com Python Flask.

## Início Rápido

### 1. Ativar ambiente virtual
```bash
source .venv/bin/activate
```

### 2. Popular banco de dados com dados de teste
```bash
python3 seed.py
```

**Output esperado:**
```
✅ Banco de dados populado com sucesso!

📊 Dados criados:
   Tenant: Clínica São João (ID: 1)
   Usuários: 3

🔐 Credenciais de teste:
   Médico: doctor@clinic.com / senha123
   Paciente 1: maria@email.com / senha123
   Paciente 2: carlos@email.com / senha123
```

### 3. Rodar o servidor
```bash
python3 run.py
```

A API estará disponível em: `http://localhost:5000`

## Endpoints

### Autenticação

**Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@clinic.com",
    "password": "senha123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "email": "doctor@clinic.com",
  "name": "Dr. João Silva"
}
```

**Register**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@email.com",
    "name": "Novo Usuário",
    "password": "senha123",
    "tenant_id": 1
  }'
```

### Agendamentos (requer JWT token)

**Listar agendamentos**
```bash
curl -X GET http://localhost:5000/api/appointments/ \
  -H "Authorization: Bearer {access_token}"
```

**Ver detalhe de agendamento**
```bash
curl -X GET http://localhost:5000/api/appointments/1 \
  -H "Authorization: Bearer {access_token}"
```

**Criar agendamento**
```bash
curl -X POST http://localhost:5000/api/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "doctor_id": 1,
    "patient_id": 2,
    "appointment_date": "2026-04-10T14:00:00",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "tenant_id": 1
  }'
```

## Testes

### Rodar testes
```bash
pip install pytest
python3 -m pytest test_api.py -v
```

### Testes específicos
```bash
python3 -m pytest test_api.py::TestAuth::test_login_success -v
```

## Modelos

### User (Usuário)
- `id`: ID único
- `name`: Nome completo
- `email`: Email único
- `password_hash`: Senha hash
- `role`: patient | doctor
- `tenant_id`: ID do tenant (multi-tenancy)

### Tenant (Organização)
- `id`: ID único
- `name`: Nome da clínica
- `subdomain`: Subdomínio único
- `is_active`: Ativo/Inativo

### Appointment (Agendamento)
- `id`: ID único
- `doctor_id`: ID do médico
- `patient_id`: ID do paciente
- `appointment_date`: Data/hora do agendamento
- `start_time`: Hora início
- `end_time`: Hora fim
- `status`: pending | confirmed | canceled
- `tenant_id`: ID do tenant

### DoctorAvailability (Disponibilidade Médica)
- `id`: ID único
- `doctor_id`: ID do médico
- `day_of_week`: 0=Monday, 6=Sunday
- `start_time`: Hora início
- `end_time`: Hora fim
- `slot_duration`: Duração do slot em minutos

## Estrutura do Projeto

```
app/
  ├── __init__.py          # Factory da aplicação
  ├── models.py            # Modelos SQLAlchemy
  ├── routes/
  │   ├── auth.py          # Endpoints de autenticação
  │   └── appointments.py   # Endpoints de agendamentos
  └── schemas/
      └── __init__.py      # Schemas Pydantic (validação)

config.py                   # Configuração da aplicação
run.py                      # Entry point
seed.py                     # Script de seed
test_api.py                 # Testes
requirements.txt            # Dependências
migrations/                 # Alembic migrations
```

## Próximos Passos

- [ ] Adicionar Swagger/OpenAPI
- [ ] Implementar validação de disponibilidade
- [ ] Adicionar notificações por email
- [ ] Rate limiting
- [ ] Logs estruturados
- [ ] Deploy em produção

