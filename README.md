# 🤖 Agente Conversacional Inteligente con Memoria Persistente

Un agente conversacional inteligente construido con **Google ADK (Agent Development Kit)** que mantiene memoria persistente entre sesiones usando SQLite y **Vertex AI Memory Bank** para memoria avanzada en la nube.

## ✨ Características

- **🧠 Memoria Persistente**: Recuerda información del usuario entre conversaciones
- **☁️ Vertex AI Memory Bank**: Memoria avanzada con búsqueda semántica en Google Cloud
- **🤖 Agente Inteligente**: Basado en Gemini 2.0 Flash de Google
- **🌐 Interfaz Web**: API REST con FastAPI
- **💾 Base de Datos Dual**: SQLite local + Vertex AI en la nube
- **🔍 Extracción Automática**: Detecta y guarda información personal automáticamente
- **📱 API REST**: Endpoints para chat y gestión de memorias
- **🧠 Búsqueda Semántica**: Recuperación inteligente de información relevante

## 🚀 Instalación

### Requisitos del Sistema
- **Python**: 3.8 o superior
- **RAM**: Mínimo 2GB, recomendado 4GB+
- **Almacenamiento**: 100MB libres para bases de datos
- **Sistema Operativo**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Conexión**: Internet para API de Google AI
- **API Key**: Cuenta de Google AI Studio activa

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd ADK_memory
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar API Key
Crear archivo `.env` en la raíz del proyecto:
```env
GOOGLE_API_KEY=tu_api_key_de_google_aqui
```

**Obtener API Key en:** [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Configurar Vertex AI Memory Bank (Opcional)
Para activar memoria avanzada con búsqueda semántica, agregar al archivo `.env`:
```env
GOOGLE_CLOUD_PROJECT=tu-proyecto-id
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=1234567890
```

**Ver archivo:** `vertex_ai_setup.md` para configuración completa

## 🏗️ Arquitectura del Sistema

### Archivos Principales
- **`multi_tool_agent/agent_simple.py`**: Lógica del agente y memoria persistente
- **`server_fastapi.py`**: Servidor web FastAPI
- **`start_web.py`**: Script de inicio del servidor
- **`requirements.txt`**: Dependencias del proyecto

### Componentes Clave

#### 1. **SimplePersistentMemory**
```python
class SimplePersistentMemory:
    """Sistema de memoria persistente usando SQLite"""
    
    def save_memory(user_id, session_id, key, value)
    def get_memories(user_id)
    def log_conversation(user_id, session_id, role, content)
```

#### 2. **LlmAgent (Google ADK)**
```python
root_agent = LlmAgent(
    name="simple_agent",
    model="gemini-2.0-flash",
    description="Agente con memoria persistente"
)
```

#### 3. **Servicios ADK + Vertex AI**
```python
# Configuración automática con fallback
session_service = DatabaseSessionService(db_url="sqlite:///./adk_sessions.db")  # Sesiones persistentes

# Memoria dual: Vertex AI (si está configurado) o InMemory (fallback)
if vertex_ai_configured:
    memory_service = VertexAiMemoryBankService(project, location, agent_engine_id)
else:
    memory_service = InMemoryMemoryService()  # Fallback local
```

## 🎯 Uso

### Casos de Uso Principales

#### 1. **Asistente Personal con Memoria**
- **Escenario**: Usuario que conversa regularmente con el agente
- **Beneficio**: El agente recuerda preferencias, información personal y contexto previo
- **Ejemplo**: "Hola, ¿recuerdas que me gusta el café?" → "¡Por supuesto! Te gusta el café"

#### 2. **Soporte al Cliente Inteligente**
- **Escenario**: Sistema de atención al cliente que mantiene historial
- **Beneficio**: Continuidad entre sesiones, sin repetir información
- **Ejemplo**: Cliente retoma conversación donde la dejó

#### 3. **Educación Personalizada**
- **Escenario**: Tutor virtual que adapta respuestas al estudiante
- **Beneficio**: Aprendizaje progresivo basado en nivel y preferencias
- **Ejemplo**: "¿Recuerdas que estoy estudiando Python?" → "Sí, continuemos con Python"

#### 4. **Investigación y Análisis**
- **Escenario**: Investigador que consulta información compleja
- **Beneficio**: Contexto mantenido entre consultas, análisis incremental
- **Ejemplo**: "Continúa analizando los datos del experimento anterior"

### Iniciar el Servidor
```bash
python start_web.py
```

El servidor se iniciará en: **http://localhost:8000**

### Interfaz Web
- **Chat**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Memorias**: http://localhost:8000/memories/{user_id}

### API Endpoints

#### POST `/chat`
```json
{
    "user_id": "demo_user",
    "message": "Me llamo Juan y tengo 25 años"
}
```
**Respuesta:**
```json
{
    "response": "¡Hola Juan! Es un placer conocerte. Tienes 25 años...",
    "session_id": "uuid-session-id"
}
```

#### GET `/memories/{user_id}`
Obtiene todas las memorias de un usuario específico.
```json
{
    "user_id": "demo_user",
    "memories": [
        {"key": "nombre", "value": "Juan", "timestamp": "2024-01-01T10:00:00"},
        {"key": "edad", "value": "25", "timestamp": "2024-01-01T10:00:00"}
    ]
}
```

#### GET `/health`
Estado del servidor y servicios ADK.
```json
{
    "status": "healthy",
    "adk_services": "DatabaseSessionService",
    "timestamp": "2024-01-01T10:00:00"
}
```

#### GET `/debug/{user_id}`
Información de debug para un usuario (memorias + sesiones ADK).

### Ejemplos de Uso

#### Chat Básico
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "usuario1", "message": "Me llamo Ana"}'
```

#### Obtener Memorias
```bash
curl "http://localhost:8000/memories/usuario1"
```

## 🧠 Sistema de Memoria

### 🧠 Memoria Personal (SimplePersistentMemory)
El sistema mantiene **memoria personal persistente** del usuario:

- **Nombres**: "me llamo Juan", "soy María"
- **Edades**: "tengo 25 años", "soy mayor de edad"
- **Ubicaciones**: "vivo en Madrid", "soy de Barcelona"
- **Preferencias**: "me gusta la música", "prefiero el café"

### 🗄️ Memoria ADK (DatabaseSessionService)
**Sistema de sesiones persistentes** de Google ADK:

- **Sesiones continuas** entre reinicios del servidor
- **Historial completo** de conversaciones ADK
- **Estado de sesión** mantenido automáticamente
- **Continuidad real** como ChatGPT

### 💾 Almacenamiento Dual

#### Base de Datos Personal (`agent_sessions.db`)
```sql
-- Tabla: user_memories
CREATE TABLE user_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,           -- nombre, edad, ciudad, etc.
    value TEXT NOT NULL,         -- Juan, 25, Madrid, etc.
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: conversation_log
CREATE TABLE conversation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,          -- user o agent
    content TEXT NOT NULL,       -- mensaje
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Base de Datos ADK (`adk_sessions.db`)
```sql
-- Tablas automáticas de Google ADK
sessions          -- Sesiones de usuario
events            -- Eventos de conversación
adk_sessions      -- Metadatos de sesión
adk_messages      -- Mensajes procesados
app_states        -- Estados de aplicación
user_states       -- Estados de usuario
```

### 🔄 Flujo de Memoria Completo

1. **Usuario envía mensaje** → Sistema busca sesión ADK existente
2. **Reutiliza sesión** → Si existe, mantiene continuidad
3. **Combina memorias** → Personal + Contexto ADK
4. **Ejecuta agente** → Con sesión persistente
5. **Actualiza sesión** → Automáticamente en ADK
6. **Guarda información** → En memoria personal
7. **Mantiene continuidad** → Entre mensajes del mismo usuario

## 🔧 Configuración

### Variables de Entorno
```env
GOOGLE_API_KEY=tu_api_key_aqui
```

### Base de Datos
- **Archivo Personal**: `agent_sessions.db` (creado automáticamente)
- **Archivo ADK**: `adk_sessions.db` (creado automáticamente)
- **Tipo**: SQLite
- **Ubicación**: Raíz del proyecto

### Configuración del Agente
```python
# Modelo de IA
model = "gemini-2.0-flash"

# Configuración de memoria
db_url = "sqlite:///./adk_sessions.db"

# Fallback automático a servicios en memoria si hay problemas
```

## 📊 Flujo de Funcionamiento

### 🔄 Flujo Completo con ADK

1. **Usuario envía mensaje** → `/chat`
2. **Sistema busca sesión ADK** → Reutiliza existente o crea nueva
3. **Combina memorias** → Personal + Contexto ADK
4. **Extrae información** → Patrones regex + IA
5. **Guarda en memoria personal** → SQLite
6. **Ejecuta agente ADK** → Con sesión persistente
7. **Recibe respuesta** → Del agente Gemini
8. **Actualiza sesión ADK** → Automáticamente
9. **Registra conversación** → En ambas bases de datos
10. **Mantiene continuidad** → Entre mensajes del mismo usuario

### 🧠 Beneficios de la Memoria Dual

- **💾 Persistencia completa** entre reinicios del servidor
- **🔄 Continuidad real** de conversaciones como ChatGPT
- **📝 Historial completo** de interacciones ADK
- **🎯 Personalización** basada en memorias previas
- **⚡ Rendimiento optimizado** con sesiones reutilizadas

## 🛠️ Desarrollo

### Estructura del Proyecto
```
ADK_memory/
├── multi_tool_agent/
│   ├── __init__.py              # Importaciones del módulo
│   └── agent_simple.py          # Lógica principal del agente
├── venv/                        # Entorno virtual
├── server_fastapi.py            # Servidor web FastAPI
├── start_web.py                 # Script de inicio del servidor
├── check_database.py            # Script de verificación de BD
├── requirements.txt             # Dependencias del proyecto
├── .env                         # Variables de entorno
├── agent_sessions.db            # Base de datos personal (auto)
├── adk_sessions.db              # Base de datos ADK (auto)
├── Info.txt                     # Análisis comparativo de sistemas
└── README.md                    # Este archivo
```

### Archivos de Base de Datos
- **`agent_sessions.db`**: Memorias personales y logs de conversación
- **`adk_sessions.db`**: Sesiones y eventos de Google ADK (7 tablas automáticas)

### Dependencias Principales
- **google-adk[database]**: Google Agent Development Kit con soporte de base de datos
- **fastapi**: Framework web
- **uvicorn**: Servidor ASGI
- **python-dotenv**: Variables de entorno
- **google-genai**: API de Google AI

### Servicios ADK Implementados
- **DatabaseSessionService**: Sesiones persistentes en `adk_sessions.db`
- **InMemoryMemoryService**: Memoria de sesión ADK
- **LlmAgent**: Agente basado en Gemini 2.0 Flash
- **Runner**: Ejecutor de conversaciones con persistencia

## 🚨 Solución de Problemas

### Error: "Session not found"
- **Causa**: Conflicto entre instancias de servicios ADK
- **Solución**: Usar `agent_simple.py` (versión simplificada)

### Error: "no such column: key"
- **Causa**: Base de datos con estructura antigua
- **Solución**: Eliminar `agent_sessions.db` y reiniciar

### Error: "cannot import name 'agent'"
- **Causa**: Archivos de importación desactualizados
- **Solución**: Verificar que `__init__.py` importe `agent_simple`

### Error: "'ListSessionsResponse' object is not subscriptable"
- **Causa**: Acceso incorrecto a la respuesta de `list_sessions()`
- **Solución**: Usar `existing_sessions_response.sessions[0]` en lugar de `existing_sessions[0]`

### Error: "DatabaseSessionService connection failed"
- **Causa**: Problemas de conexión a la base de datos ADK
- **Solución**: El sistema fallback automáticamente a `InMemorySessionService`

### Verificación de Bases de Datos
Para verificar el estado de las bases de datos:
```bash
python check_database.py
```

Este script muestra el contenido de ambas bases de datos:
- **`agent_sessions.db`**: Memorias personales y logs de conversación
- **`adk_sessions.db`**: Sesiones y eventos de Google ADK

### Logs de Debug
El sistema incluye logs detallados para debugging:
```
🧠 [ADK COMPLETE] Ejecutando con persistencia ADK para: demo_user
🔄 [ADK] Reutilizando sesión existente: abc12345...
✅ [ADK] Sesión abc12345... actualizada con nuevo evento
```

## 🔮 Próximas Mejoras

### ✅ Implementado
- [x] **Memoria ADK Persistente**: Implementado con DatabaseSessionService
- [x] **Sesiones Continuas**: Reutilización automática de sesiones existentes
- [x] **Base de Datos Dual**: Personal + ADK para máxima persistencia
- [x] **Fallback Automático**: Servicios en memoria si falla la BD
- [x] **Logs Detallados**: Sistema de debugging completo
- [x] **Script de Verificación**: `check_database.py` para monitoreo

### 🚀 En Desarrollo
- [ ] **Memoria Vectorial**: Integración con embeddings
- [ ] **Búsqueda Semántica**: Búsqueda inteligente en memorias
- [ ] **Autenticación**: Sistema de usuarios y contraseñas
- [ ] **API Rate Limiting**: Control de uso de la API
- [ ] **Logs Estructurados**: Mejor observabilidad
- [ ] **Tests Automatizados**: Suite de pruebas completa
- [ ] **Health Checks**: Monitoreo de servicios ADK
- [ ] **Circuit Breakers**: Manejo robusto de fallos
- [ ] **WebSocket**: Conversaciones en tiempo real
- [ ] **Multi-idioma**: Soporte para múltiples idiomas

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Revisar la documentación de [Google ADK](https://developers.google.com/adk)
- Consultar la [documentación oficial de ADK](https://google.github.io/adk-docs/)

### Recursos Adicionales
- **Google AI Studio**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Google ADK GitHub**: [https://github.com/google/adk](https://github.com/google/adk)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

### Comunidad
- **Discord**: Canal oficial de Google ADK
- **Stack Overflow**: Etiqueta `google-adk`
- **GitHub Discussions**: En el repositorio oficial

---

**Desarrollado con ❤️ usando Google ADK y FastAPI**

*Este proyecto demuestra las capacidades avanzadas de Google ADK para crear agentes conversacionales con memoria persistente real.*
