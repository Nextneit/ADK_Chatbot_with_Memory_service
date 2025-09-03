# 🚀 Guía de Inicio Rápido - ADK Memory

## ⚡ Configuración en 5 minutos

### 1. **Configuración Automática** (Recomendado)

```bash
# Clonar y configurar automáticamente
git clone <tu-repositorio>
cd ADK_memory
python setup.py
```

### 2. **Configuración Manual**

#### Para Database Agent (Más Fácil)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear .env
cp env.example .env

# 3. Editar .env - agregar tu API Key
GOOGLE_API_KEY=AIzaSy...  # Obtener en https://makersuite.google.com/app/apikey
SELECTED_AGENT=database

# 4. Iniciar servidor
python start_web.py --agent database
```

#### Para Vertex Agent (Más Potente)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar Google Cloud
gcloud auth login
gcloud config set project TU_PROJECT_ID
gcloud auth application-default login

# 3. Crear Agent Engine
python create_agent_engine_vertex.py

# 4. Iniciar servidor
python start_web.py --agent vertex
```

## 🌐 Acceder a la Interfaz

1. **Abrir navegador**: `http://localhost:8000`
2. **Chat con el agente**: Interfaz web intuitiva
3. **API REST**: `http://localhost:8000/docs`

## 🆘 Problemas Comunes

### Error: "GOOGLE_API_KEY no encontrada"
**Solución**: Agregar tu API Key al archivo `.env`

### Error: "401 UNAUTHENTICATED" (Vertex Agent)
**Solución**: 
```bash
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
```

### Error: "Agent Engine ID is required"
**Solución**: Ejecutar `python create_agent_engine_vertex.py`

## 📚 Documentación Completa

Para configuración avanzada y solución de problemas detallados, consulta [README.md](README.md).

---

**¡Listo! Tu agente con memoria persistente está funcionando.** 🎉
