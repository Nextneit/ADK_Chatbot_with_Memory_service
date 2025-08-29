# ☁️ Configuración Vertex AI Memory Bank

## 🚀 Configuración para Memoria Avanzada

Este archivo contiene las instrucciones para configurar **Vertex AI Memory Bank** según la [documentación oficial de Google ADK](https://google.github.io/adk-docs/sessions/memory/#vertex-ai-memory-ban).

## 📋 Prerrequisitos

### 1. **Proyecto de Google Cloud**
- Tener un proyecto de Google Cloud con la API de Vertex AI habilitada
- Facturación activa en el proyecto

### 2. **Agent Engine en Vertex AI**
- Crear un Agent Engine en Vertex AI
- Obtener el **Agent Engine ID** (requerido para la configuración)

### 3. **Autenticación Local**
```bash
# Autenticarse con Google Cloud
gcloud auth application-default login

# Verificar el proyecto activo
gcloud config get-value project
```

## 🔧 Variables de Entorno

Crear archivo `.env` con las siguientes variables:

```env
# Configuración existente
GOOGLE_API_KEY=tu_api_key_de_google_aqui

# NUEVAS: Configuración Vertex AI Memory Bank
GOOGLE_CLOUD_PROJECT=tu-proyecto-id
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_ID=1234567890
```

### 📍 Ubicaciones Disponibles
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

## 🎯 Beneficios de Vertex AI Memory Bank

| **Característica** | **InMemoryMemoryService** | **VertexAiMemoryBankService** |
|-------------------|---------------------------|-------------------------------|
| **Persistencia** | ❌ Se pierde al reiniciar | ✅ Persistente en Google Cloud |
| **Búsqueda** | 🔍 Palabras clave básica | 🧠 Semántica avanzada |
| **Aprendizaje** | ❌ No aprende | ✅ Aprende de conversaciones |
| **Escalabilidad** | ❌ Limitada a memoria local | ✅ Escalable en la nube |
| **Extracción** | ❌ Conversación completa | ✅ Información relevante |

## 🚀 Inicio Rápido

### 1. **Configurar Variables de Entorno**
```bash
# Windows
set GOOGLE_CLOUD_PROJECT=tu-proyecto-id
set GOOGLE_CLOUD_LOCATION=us-central1
set AGENT_ENGINE_ID=1234567890

# Linux/Mac
export GOOGLE_CLOUD_PROJECT=tu-proyecto-id
export GOOGLE_CLOUD_LOCATION=us-central1
export AGENT_ENGINE_ID=1234567890
```

### 2. **Reiniciar el Servidor**
```bash
python start_web.py
```

### 3. **Verificar Configuración**
Los logs mostrarán:
```
☁️  [VERTEX AI] Configurando Vertex AI Memory Bank...
   📍 Project: tu-proyecto-id
   🌍 Location: us-central1
   🤖 Agent Engine: 1234567890
✅ VertexAiMemoryBankService configurado para memoria persistente avanzada
```

## 🔍 Verificación del Sistema

### **Endpoint de Estado**
```bash
GET /health
```

**Respuesta con Vertex AI:**
```json
{
    "status": "healthy",
    "memory_service": "Vertex AI Memory Bank",
    "features": [
        "🧠 Búsqueda semántica avanzada",
        "💾 Memoria persistente en Google Cloud",
        "🔄 Aprendizaje automático de conversaciones"
    ]
}
```

### **Endpoint de Debug**
```bash
GET /debug/{user_id}
```

**Incluye información de memoria Vertex AI:**
```json
{
    "user_id": "demo_user",
    "memories_personal": [...],
    "memories_vertex_ai": [...],
    "memory_service_info": {
        "type": "Vertex AI Memory Bank",
        "status": "✅ Configurado y funcionando"
    }
}
```

## 🛠️ Solución de Problemas

### **Error: "Vertex AI API not enabled"**
```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### **Error: "Agent Engine not found"**
- Verificar que el Agent Engine existe en Vertex AI
- Confirmar el Agent Engine ID en la consola de Google Cloud

### **Error: "Authentication failed"**
```bash
# Reautenticarse
gcloud auth application-default login
gcloud config set project TU_PROYECTO_ID
```

## 📚 Recursos Adicionales

- [Documentación oficial Vertex AI Memory Bank](https://google.github.io/adk-docs/sessions/memory/#vertex-ai-memory-ban)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)

---

**¡Con Vertex AI Memory Bank tendrás memoria persistente y búsqueda semántica avanzada!** 🚀
