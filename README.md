# 🤖 ADK Memory - Sistema de Agentes con Memoria Persistente

Sistema completo de agentes de IA con memoria persistente usando Google's Agent Development Kit (ADK) y Vertex AI.

## 📋 Características Principales

- **🧠 Memoria Persistente**: Los agentes recuerdan conversaciones anteriores entre sesiones
- **☁️ Múltiples Backends**: Soporte para SQLite local, ADK InMemory y Vertex AI Memory Bank
- **🌐 API REST**: Servidor FastAPI con interfaz web intuitiva
- **🔧 Herramientas ADK**: Integración completa con herramientas oficiales del ADK
- **🔐 Autenticación Flexible**: Soporte para API Keys y OAuth2

## 🚀 Agentes Disponibles

### 1. **Database Agent** (SQLite) - ⭐ FÁCIL
**Memoria local completa con base de datos SQLite**

**Características:**
- 🗄️ Base de datos SQLite integral con múltiples tablas
- 📊 Búsqueda semántica básica por palabras clave
- 💾 Memoria persistente local (no se pierde al reiniciar)
- 📝 Historial completo de conversaciones
- 🔍 Contexto semántico personalizado
- 🛠️ Herramienta `load_memory` integrada automáticamente

**Configuración:**
- Solo requiere API Key de Google AI Studio
- No necesita Google Cloud SDK
- Ideal para desarrollo y pruebas locales

**Uso:**
```bash
python start_web.py --agent database
```

### 2. **ADK Agent** (ADK InMemory) - ⭐⭐ INTERMEDIO
**Implementación oficial del patrón ADK con servicios InMemory**

**Características:**
- 🔧 InMemorySessionService para gestión de sesiones
- 🧠 InMemoryMemoryService para memoria persistente
- 🔍 Búsqueda automática en conversaciones pasadas
- 📋 Gestión de sesiones siguiendo patrón oficial ADK
- 🛠️ Herramienta `load_memory` integrada automáticamente
- ✅ Implementación 100% compatible con documentación oficial

**Configuración:**
- Requiere API Key de Google AI Studio
- No necesita Google Cloud SDK
- Recomendado para desarrollo y pruebas

**Uso:**
```bash
python start_web.py --agent adk
```

### 3. **Vertex Agent** (Vertex AI Memory Bank) - ⭐⭐⭐ AVANZADO
**Memoria persistente en Google Cloud con búsqueda semántica avanzada**

**Características:**
- ☁️ VertexAiMemoryBankService para memoria en la nube
- 🧠 Búsqueda semántica avanzada con IA
- 💾 Memoria persistente escalable en Google Cloud
- 🔄 Procesamiento automático de memoria
- 📊 Extracción inteligente de información
- 🔐 Autenticación OAuth2 segura

**Configuración:**
- Requiere Google Cloud SDK instalado
- Necesita proyecto de Google Cloud configurado
- Requiere Agent Engine creado
- Recomendado para producción

**Uso:**
```bash
python start_web.py --agent vertex
```

## 🛠️ Instalación Rápida

### Prerrequisitos

```bash
# Python 3.8+ (requerido)
python --version

# Google Cloud SDK (solo para Vertex Agent)
gcloud --version  # Opcional
```

### 1. Configuración Básica

```bash
# Clonar repositorio
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

### 2. Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# ===========================================
# CONFIGURACIÓN BÁSICA (para Database y ADK Agent)
# ===========================================
GOOGLE_API_KEY=tu_api_key_aqui  # Obtener en: https://makersuite.google.com/app/apikey

# ===========================================
# CONFIGURACIÓN DE VERTEX AI (solo para Vertex Agent)
# ===========================================
GOOGLE_CLOUD_PROJECT=tu_project_id
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=tu_agent_engine_id

# ===========================================
# CONFIGURACIÓN DEL SERVIDOR
# ===========================================
SELECTED_AGENT=database  # database, adk, o vertex
AGENT_MODEL=gemini-2.0-flash
```

## 🔧 Configuración por Agente

### 1. Database Agent (⭐ FÁCIL - 2 minutos)

**Paso 1: Obtener API Key**
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API Key
3. Copia la clave (formato: `AIzaSy...`)

**Paso 2: Configurar .env**
```env
GOOGLE_API_KEY=AIzaSy...
SELECTED_AGENT=database
```

**Paso 3: ¡Ejecutar!**
```bash
python start_web.py --agent database
```

**✅ Listo en 2 minutos** - Memoria persistente local funcionando

---

### 2. ADK Agent (⭐⭐ INTERMEDIO - 3 minutos)

**Paso 1: Seguir configuración del Database Agent**
- Usar la misma API Key de Google AI Studio

**Paso 2: Cambiar agente en .env**
```env
GOOGLE_API_KEY=AIzaSy...
SELECTED_AGENT=adk
```

**Paso 3: Ejecutar**
```bash
python start_web.py --agent adk
```

**✅ Listo en 3 minutos** - Patrón oficial ADK con memoria persistente

---

### 3. Vertex Agent (⭐⭐⭐ AVANZADO - 10 minutos)

**Paso 1: Instalar Google Cloud SDK**
```bash
# Descargar desde: https://cloud.google.com/sdk/docs/install
# Instalar y reiniciar terminal
```

**Paso 2: Configurar Google Cloud**
```bash
# Autenticarse
gcloud auth login

# Configurar proyecto (reemplaza TU_PROJECT_ID)
gcloud config set project TU_PROJECT_ID

# Configurar Application Default Credentials
gcloud auth application-default login

# Configurar quota project
gcloud auth application-default set-quota-project TU_PROJECT_ID
```

**Paso 3: Habilitar APIs**
```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verificar APIs habilitadas
gcloud services list --enabled
```

**Paso 4: Crear Agent Engine (Automático)**
```bash
# Ejecutar script de creación automática
python create_agent_engine_vertex.py
```

**Este script hace todo automáticamente:**
- ✅ Verifica la configuración de Google Cloud
- ✅ Crea el Agent Engine en Vertex AI
- ✅ Actualiza automáticamente el archivo `.env`

**Paso 5: Configurar .env**
```env
# El script ya actualiza estas variables automáticamente
GOOGLE_CLOUD_PROJECT=tu_project_id
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=el_id_generado_por_el_script
SELECTED_AGENT=vertex
```

**Paso 6: Verificar y Ejecutar**
```bash
# Verificar configuración
python start_web.py --agent vertex --check

# Ejecutar servidor
python start_web.py --agent vertex
```

**✅ Listo en 10 minutos** - Memoria persistente en Google Cloud con búsqueda semántica avanzada

## 🚀 Uso del Sistema

### Iniciar Servidor

```bash
# Usar agente específico
python start_web.py --agent database    # Fácil
python start_web.py --agent adk         # Intermedio  
python start_web.py --agent vertex      # Avanzado

# Con opciones personalizadas
python start_web.py --agent database --host 0.0.0.0 --port 8000

# Solo verificar configuración
python start_web.py --agent database --check

# Ver información de todos los agentes
python start_web.py --info
```

### Acceder a la Interfaz Web

1. **Abrir navegador**: `http://localhost:8000`
2. **Interfaz de chat**: Interfaz web intuitiva con memoria persistente
3. **API REST**: Documentación completa en `http://localhost:8000/docs`

### Funcionalidades de Memoria por Agente

#### Database Agent
- **Memoria Personal**: Extrae automáticamente nombre, edad, preferencias
- **Historial Completo**: Guarda todas las conversaciones en SQLite
- **Búsqueda Semántica**: Busca en conversaciones anteriores por palabras clave
- **Contexto Automático**: Incluye información relevante en cada respuesta

#### ADK Agent  
- **Patrón Oficial**: Implementa exactamente la documentación oficial del ADK
- **Herramienta load_memory**: Acceso automático a conversaciones pasadas
- **Gestión de Sesiones**: InMemorySessionService para sesiones persistentes
- **Memoria Inteligente**: InMemoryMemoryService para búsquedas automáticas

#### Vertex Agent
- **Búsqueda Semántica Avanzada**: Usa IA para encontrar información relevante
- **Memoria en la Nube**: Almacenamiento escalable en Google Cloud
- **Procesamiento Automático**: Extrae y organiza información automáticamente
- **Escalabilidad**: Maneja grandes volúmenes de conversaciones

### Endpoints de la API

```bash
# Chat con el agente (memoria persistente automática)
POST /chat
{
  "user_id": "usuario123",
  "message": "Hola, ¿cómo estás?",
  "session_id": "opcional"
}

# Obtener información de memorias
GET /memories/{user_id}

# Estado del sistema y agente activo
GET /health

# Debug detallado de memoria (muy útil para desarrollo)
GET /debug/{user_id}
```

## 🔍 Solución de Problemas

### Error: "GOOGLE_API_KEY no encontrada"

**Causa**: API Key no configurada

**Solución**:
```bash
# 1. Obtener API Key en: https://makersuite.google.com/app/apikey
# 2. Agregar al archivo .env:
GOOGLE_API_KEY=AIzaSy...
```

### Error: "401 UNAUTHENTICATED" (Vertex Agent)

**Causa**: Problemas de autenticación OAuth2

**Solución**:
```bash
# Reconfigurar Google Cloud
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
gcloud auth application-default set-quota-project TU_PROJECT_ID
```

### Error: "Agent Engine ID is required"

**Causa**: No se ha creado el Agent Engine para Vertex Agent

**Solución**:
```bash
# Ejecutar script automático
python create_agent_engine_vertex.py
```

### Error: "API keys are not supported by this API"

**Causa**: Usando API Key de Google AI Studio con Vertex AI

**Solución**:
- Vertex Agent usa OAuth2, NO API Key
- Usar `gcloud auth application-default login`
- No configurar `GOOGLE_API_KEY` para Vertex Agent

### Error: "Content object has no attribute 'content'"

**Causa**: Problema de estructura de eventos (ya resuelto)

**Solución**: Actualizar a la última versión del código

## 📊 Comparación Detallada de Agentes

| Característica | Database Agent | ADK Agent | Vertex Agent |
|----------------|----------------|-----------|--------------|
| **⚡ Configuración** | ⭐ Fácil (2 min) | ⭐⭐ Intermedio (3 min) | ⭐⭐⭐ Avanzado (10 min) |
| **🧠 Memoria** | SQLite local completa | ADK InMemory oficial | Vertex AI Memory Bank |
| **🔍 Búsqueda** | Palabras clave básica | Patrón oficial ADK | Semántica avanzada con IA |
| **💾 Persistencia** | Local (archivo .db) | Local (memoria ADK) | Nube (Google Cloud) |
| **📊 Escalabilidad** | Limitada (local) | Media (memoria) | Alta (nube) |
| **💰 Costo** | Gratis | Gratis | Pay-per-use |
| **🏭 Producción** | ❌ Solo desarrollo | ⚠️ Limitado | ✅ Recomendado |
| **🔧 Herramientas** | load_memory integrada | load_memory oficial | load_memory automática |
| **📝 Extracción** | Automática (nombre, edad) | Automática (conversaciones) | Inteligente (IA) |
| **🌐 Red** | No requiere | No requiere | Requiere Google Cloud |
| **⚙️ Mantenimiento** | Mínimo | Mínimo | Automático |

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI Server │    │   Agent Manager │
│   (HTML/JS)     │◄──►│   (REST API)     │◄──►│   (Selector)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │ Database Agent  │              │   ADK Agent     │              │  Vertex Agent   │
              │                 │              │                 │              │                 │
              │ • SQLite DB     │              │ • InMemory      │              │ • Vertex AI     │
              │ • Local Memory  │              │ • ADK Services  │              │ • Cloud Memory  │
              │ • load_memory   │              │ • load_memory   │              │ • load_memory   │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
```

## 📝 Estructura del Proyecto (Simplificada para Demo)

```
ADK_memory/
├── multi_tool_agent/           # Módulo principal de agentes
│   ├── agents/
│   │   ├── database_agent.py   # Database Agent (SQLite completo)
│   │   ├── adk_agent.py        # ADK Agent (patrón oficial)
│   │   └── vertex_agent.py     # Vertex Agent (Google Cloud)
│   └── agent_manager.py        # Gestor de agentes
├── server_fastapi.py           # Servidor FastAPI con interfaz web
├── start_web.py               # Script de inicio principal
├── create_agent_engine_vertex.py # Creador automático de Agent Engine
├── requirements.txt           # Dependencias del proyecto
├── env.example               # Plantilla de configuración
└── README.md                 # Documentación completa
```

## 🎯 Resumen de Funcionalidades

### ✅ Lo que hace cada agente:

**Database Agent:**
- Extrae automáticamente información personal (nombre, edad, preferencias)
- Guarda conversaciones completas en SQLite
- Busca en historial por palabras clave
- Incluye contexto relevante en cada respuesta

**ADK Agent:**
- Implementa el patrón oficial del ADK al 100%
- Usa InMemorySessionService e InMemoryMemoryService
- Herramienta load_memory integrada automáticamente
- Gestión de sesiones siguiendo documentación oficial

**Vertex Agent:**
- Búsqueda semántica avanzada con IA
- Memoria persistente en Google Cloud
- Procesamiento automático de información
- Escalabilidad automática para producción

### 🚀 Para empezar ahora mismo:

1. **Más fácil**: `python start_web.py --agent database`
2. **Intermedio**: `python start_web.py --agent adk`  
3. **Avanzado**: `python start_web.py --agent vertex`

**¡Tu agente con memoria persistente estará funcionando en minutos!** 🎉
