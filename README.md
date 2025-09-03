# 🤖 ADK Memory - Sistema de Agentes con Memoria Persistente

Sistema completo de agentes de IA con memoria persistente usando Google's Agent Development Kit (ADK) y Vertex AI.

## 📋 Características

- **🧠 Memoria Persistente**: Los agentes recuerdan conversaciones anteriores
- **☁️ Vertex AI Integration**: Integración completa con Vertex AI Express Mode
- **🗄️ Múltiples Backends**: Soporte para SQLite, ADK InMemory y Vertex AI Memory Bank
- **🌐 API REST**: Servidor FastAPI con interfaz web
- **🔐 Autenticación OAuth2**: Configuración segura con Google Cloud

## 🚀 Agentes Disponibles

### 1. **Database Agent** (SQLite)
- Memoria local en base de datos SQLite
- Ideal para desarrollo y pruebas
- No requiere configuración de Google Cloud

### 2. **ADK Agent** (ADK InMemory)
- Usa ADK InMemorySessionService e InMemoryMemoryService
- Memoria persistente siguiendo patrón oficial ADK
- Requiere API Key de Google AI Studio
- **Recomendado para desarrollo y pruebas**

### 3. **Vertex Agent** (Vertex AI Memory Bank) ⭐
- Memoria persistente en Google Cloud
- Búsqueda semántica avanzada
- Escalabilidad automática
- **Recomendado para producción**

## 🛠️ Instalación

### Prerrequisitos

```bash
# Python 3.8+
python --version

# Google Cloud SDK (para Vertex Agent)
gcloud --version
```

### 1. Clonar y Configurar

```bash
git clone <tu-repositorio>
cd ADK_memory

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# API Key de Google AI Studio (para Database y ADK Agent)
GOOGLE_API_KEY=tu_api_key_aqui

# Configuración de Vertex AI (para Vertex Agent)
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=tu_id_de_proyecto
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=tu_agent_engine_id

# Configuración del servidor
SELECTED_AGENT=vertex
```

## 🔧 Configuración por Agente

### Database Agent (Fácil)

1. **Obtener API Key**:
   - Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Crea una nueva API Key
   - Copia la clave (formato: `AIzaSy...`)

2. **Configurar .env**:
   ```env
   GOOGLE_API_KEY=AIzaSy...
   SELECTED_AGENT=database
   ```

3. **¡Listo!** Ejecuta: `python start_web.py --agent database`

### ADK Agent (Intermedio)

1. **Seguir pasos del Database Agent**
2. **Cambiar agente**:
   ```env
   SELECTED_AGENT=adk
   ```

3. **Ejecutar**: `python start_web.py --agent adk`

### Vertex Agent (Avanzado) ⭐

#### Paso 1: Configurar Google Cloud

```bash
# 1. Instalar Google Cloud SDK
# Descargar desde: https://cloud.google.com/sdk/docs/install

# 2. Autenticarse
gcloud auth login

# 3. Configurar proyecto
gcloud config set project TU_PROJECT_ID

# 4. Configurar Application Default Credentials
gcloud auth application-default login

# 5. Configurar quota project
gcloud auth application-default set-quota-project TU_PROJECT_ID
```

#### Paso 2: Habilitar APIs Necesarias

```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verificar APIs habilitadas
gcloud services list --enabled
```

#### Paso 3: Crear Agent Engine

```bash
# Ejecutar script de creación
python create_agent_engine_vertex.py
```

Este script:
- ✅ Verifica la configuración de Google Cloud
- ✅ Crea el Agent Engine en Vertex AI
- ✅ Actualiza automáticamente el archivo `.env`

#### Paso 4: Configurar .env

```env
# Configuración de Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=tu_project_id
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=el_id_generado_por_el_script

# Seleccionar agente
SELECTED_AGENT=vertex
```

#### Paso 5: Verificar Configuración

```bash
# Verificar que todo esté configurado
python start_web.py --agent vertex --check
```

## 🚀 Uso

### Iniciar Servidor

```bash
# Usar agente específico
python start_web.py --agent vertex

# Con opciones personalizadas
python start_web.py --agent vertex --host 0.0.0.0 --port 8000

# Solo verificar configuración
python start_web.py --agent vertex --check

# Ver información de agentes
python start_web.py --info
```

### Acceder a la Interfaz Web

1. **Abrir navegador**: `http://localhost:8000`
2. **Interfaz de chat**: Interfaz web intuitiva
3. **API REST**: Documentación en `http://localhost:8000/docs`

### Endpoints de la API

```bash
# Chat con el agente
POST /chat
{
  "user_id": "usuario123",
  "message": "Hola, ¿cómo estás?",
  "session_id": "opcional"
}

# Obtener memorias de un usuario
GET /memories/{user_id}

# Estado del sistema
GET /health

# Debug de memoria
GET /debug/{user_id}
```

## 🔍 Solución de Problemas

### Error: "401 UNAUTHENTICATED"

**Causa**: Problemas de autenticación

**Solución**:
```bash
# Para Vertex Agent
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID

# Para Database/ADK Agent
# Verificar que GOOGLE_API_KEY esté configurada correctamente
```

### Error: "Agent Engine ID is required"

**Causa**: No se ha creado el Agent Engine

**Solución**:
```bash
python create_agent_engine_vertex.py
```

### Error: "API keys are not supported by this API"

**Causa**: Usando API Key de Google AI Studio con Vertex AI

**Solución**:
- Usar OAuth2 con `gcloud auth application-default login`
- No usar `GOOGLE_API_KEY` para Vertex Agent

### Error: "Content object has no attribute 'content'"

**Causa**: Problema de estructura de eventos (ya resuelto)

**Solución**: Actualizar a la última versión del código

## 📊 Comparación de Agentes

| Característica | Database | ADK | Vertex |
|----------------|----------|-----|--------|
| **Configuración** | ⭐ Fácil | ⭐⭐ Intermedio | ⭐⭐⭐ Avanzado |
| **Memoria** | Local SQLite | ADK InMemory | Vertex AI Memory Bank |
| **Búsqueda** | Palabras clave | Palabras clave | Semántica avanzada |
| **Escalabilidad** | Limitada | Media | Alta |
| **Costo** | Gratis | Gratis | Pay-per-use |
| **Producción** | ❌ No | ⚠️ Limitado | ✅ Sí |

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI Server │    │   Agent Manager │
│                 │◄──►│                  │◄──►│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │ Database Agent  │              │   ADK Agent     │              │  Vertex Agent   │
              │                 │              │                 │              │                 │
              │ • SQLite        │              │ • ADK InMemory  │              │ • Vertex AI     │
              │ • Local Memory  │              │ • ADK Services  │              │ • Cloud Memory  │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
```

## 📝 Estructura del Proyecto

```
ADK_memory/
├── multi_tool_agent/
│   ├── agents/
│   │   ├── database_agent.py    # Agente con SQLite
│   │   ├── adk_agent.py         # Agente con ADK
│   │   └── vertex_agent.py      # Agente con Vertex AI
│   └── agent_manager.py         # Gestor de agentes
├── server_fastapi.py            # Servidor FastAPI
├── start_web.py                 # Script de inicio
├── create_agent_engine_vertex.py # Creador de Agent Engine
├── requirements.txt             # Dependencias
├── .env                         # Variables de entorno
└── README.md                    # Este archivo
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas:

1. **Revisa la sección de Solución de Problemas**
2. **Verifica la configuración**: `python start_web.py --check`
3. **Consulta los logs** del servidor para errores específicos
4. **Abre un issue** en GitHub con detalles del error

## 🎯 Roadmap

- [ ] Soporte para más modelos de IA
- [ ] Interfaz de administración web
- [ ] Métricas y analytics
- [ ] Integración con más servicios de Google Cloud
- [ ] Soporte para múltiples idiomas
- [ ] API GraphQL

---

**¡Disfruta construyendo agentes inteligentes con memoria persistente!** 🚀