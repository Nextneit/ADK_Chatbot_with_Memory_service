"""
VERSIÓN SIMPLE Y FUNCIONAL DEL AGENTE - SIN VERTEX AI
"""

import os
import sqlite3
import uuid
import asyncio
from google.genai import types
# from google.generativeai import GenerativeModel  # NO NECESARIO
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY no encontrada en variables de entorno")

print(f"✅ API Key cargada: {api_key[:10]}...{api_key[-5:]}")

# ============================================================================
# SISTEMA DE MEMORIA PERSISTENTE SIMPLE (FUNCIONA)
# ============================================================================

class SimplePersistentMemory:
    """Sistema de memoria persistente simple usando SQLite."""
    
    def __init__(self, db_path: str = "agent_sessions.db"):
        self.db_path = db_path
        self._init_db()
        print(f"✅ Base de datos inicializada: {db_path}")
    
    def _init_db(self):
        """Inicializar base de datos SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_memory(self, user_id: str, session_id: str, key: str, value: str):
        """Guardar memoria del usuario."""
        conn = sqlite3.connect(self.db_path)
        # Actualizar o insertar nueva memoria
        conn.execute("""
            INSERT OR REPLACE INTO user_memories 
            (user_id, session_id, key, value, timestamp)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (user_id, session_id, key, value))
        conn.commit()
        conn.close()
    
    def get_memories(self, user_id: str):
        """Obtener todas las memorias de un usuario."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT DISTINCT key, value, timestamp 
            FROM user_memories 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
        """, (user_id,))
        memories = cursor.fetchall()
        conn.close()
        return memories
    
    def log_conversation(self, user_id: str, session_id: str, role: str, content: str):
        """Registrar conversación."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO conversation_log 
            (user_id, session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (user_id, session_id, role, content))
        conn.commit()
        conn.close()

# Inicializar memoria persistente
persistent_memory = SimplePersistentMemory()

# ============================================================================
# CONFIGURACIÓN SIMPLE DEL AGENTE (FUNCIONA)
# ============================================================================

from google.adk.agents import LlmAgent
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService

# Configurar agente SIMPLE con tool de memoria ADK
from google.adk.tools import load_memory  # Tool oficial ADK para consultar memoria

root_agent = LlmAgent(
    name="simple_agent",
    model="gemini-2.0-flash",
    description="Eres un asistente que recuerda información entre sesiones.",
    instruction=(
        "Eres un asistente que recuerda información entre sesiones. "
        "Usa la información proporcionada para personalizar tus respuestas. "
        "Tienes acceso a la herramienta 'load_memory' para consultar conversaciones pasadas."
    ),
    tools=[load_memory]  # Herramienta oficial ADK para consultar memoria
)

# Servicios ADK con persistencia de base de datos y Vertex AI Memory Bank
def setup_adk_services():
    """Configurar servicios ADK con DatabaseSessionService + Vertex AI Memory Bank."""
    try:
        # Configurar DatabaseSessionService para sesiones persistentes
        db_url = "sqlite:///./adk_sessions.db"
        print(f"🗄️  [ADK] Configurando DatabaseSessionService con: {db_url}")
        
        session_service = DatabaseSessionService(db_url=db_url)
        
        # INTENTAR CONFIGURAR VERTEX AI MEMORY BANK (según documentación oficial)
        try:
            # Verificar variables de entorno para Vertex AI
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION")
            agent_engine_id = os.getenv("AGENT_ENGINE_ID")
            
            if project_id and location and agent_engine_id:
                print("☁️  [VERTEX AI] Configurando Vertex AI Memory Bank...")
                print(f"   📍 Project: {project_id}")
                print(f"   🌍 Location: {location}")
                print(f"   🤖 Agent Engine: {agent_engine_id}")
                
                # Configurar Vertex AI Memory Bank Service
                memory_service = VertexAiMemoryBankService(
                    project=project_id,
                    location=location,
                    agent_engine_id=agent_engine_id
                )
                
                print("✅ VertexAiMemoryBankService configurado para memoria persistente avanzada")
                print("   🧠 Búsqueda semántica habilitada")
                print("   💾 Memoria persistente en Google Cloud")
                
            else:
                print("⚠️  [VERTEX AI] Variables de entorno no configuradas")
                print("   🔧 Configurar: GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, AGENT_ENGINE_ID")
                print("   🔄 Fallback a InMemoryMemoryService")
                memory_service = InMemoryMemoryService()
                
        except Exception as e:
            print(f"⚠️  [VERTEX AI ERROR] Error configurando Vertex AI Memory Bank: {e}")
            print("🔄 Fallback a InMemoryMemoryService")
            memory_service = InMemoryMemoryService()
        
        print("✅ Servicios ADK configurados")
        print(f"   📋 Session Service: {type(session_service).__name__}")
        print(f"   🧠 Memory Service: {type(memory_service).__name__}")
        
        return session_service, memory_service
        
    except Exception as e:
        print(f"⚠️  [ADK ERROR] Error configurando DatabaseSessionService: {e}")
        print("🔄 Fallback a servicios en memoria...")
        
        # Fallback a servicios en memoria si hay problemas
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()
        
        print("⚠️  Usando servicios en memoria como fallback")
        print(f"   📋 Session Service (fallback): {type(session_service).__name__}")
        print(f"   🧠 Memory Service (fallback): {type(session_service).__name__}")
        
        return session_service, memory_service

# Inicializar servicios ADK
session_service, memory_service = setup_adk_services()

def create_runner():
    """Crear runner con servicios ADK persistentes."""
    from google.adk import Runner
    return Runner(
        agent=root_agent,
        app_name="simple_agent",
        session_service=session_service,
        memory_service=memory_service
    )

print("✅ Agente simple configurado")

# ============================================================================
# FUNCIÓN PRINCIPAL SIMPLE (FUNCIONA)
# ============================================================================

async def run_with_persistent_memory(user_id: str, message: str, session_id: str = None):
    """Ejecutar agente con memoria persistente - IMPLEMENTACIÓN ADK COMPLETA."""
    
    print(f"🧠 [ADK COMPLETE] Ejecutando con persistencia ADK para: {user_id}")
    
    try:
        # PASO 1: Buscar sesión ADK existente o crear nueva
        existing_sessions_response = await session_service.list_sessions(user_id=user_id, app_name="simple_agent")
        adk_session = None
        
        # Verificar si hay sesiones existentes
        if existing_sessions_response and hasattr(existing_sessions_response, 'sessions') and existing_sessions_response.sessions:
            # Usar la sesión más reciente
            adk_session = existing_sessions_response.sessions[0]  # Acceder a .sessions
            print(f"🔄 [ADK] Reutilizando sesión existente: {adk_session.id[:8]}...")
        else:
            # Crear nueva sesión
            adk_session = await session_service.create_session(user_id=user_id, app_name="simple_agent")
            print(f"🆕 [ADK] Nueva sesión creada: {adk_session.id[:8]}...")
        
        # PASO 2: Obtener memorias personales para contexto
        memories = persistent_memory.get_memories(user_id)
        memory_context = ""
        if memories:
            memory_context = "\n--- INFORMACIÓN PERSONAL RECORDADA ---\n"
            for key, value, timestamp in memories:
                memory_context += f"- {key}: {value}\n"
            memory_context += "--- FIN INFORMACIÓN ---\n\n"
        
        # PASO 2.5: Obtener contexto de memoria ADK + Vertex AI (según documentación oficial)
        if isinstance(memory_service, VertexAiMemoryBankService):
            # Búsqueda semántica avanzada en Vertex AI
            adk_memory_context = await search_vertex_memory(user_id, message)
            if adk_memory_context:
                memory_context += "\n--- MEMORIAS VERTEX AI SEMÁNTICAS ---\n"
                for memory in adk_memory_context:
                    if hasattr(memory, 'content') and memory.content:
                        memory_context += f"🧠 {memory.content}\n"
                    elif hasattr(memory, 'text') and memory.text:
                        memory_context += f"🧠 {memory.text}\n"
                memory_context += "--- FIN MEMORIAS VERTEX AI ---\n\n"
        else:
            # Búsqueda estándar en memoria local
            adk_memory_context = await get_adk_memory_context(user_id, message)
            if adk_memory_context:
                memory_context += adk_memory_context
        
        # PASO 3: Crear mensaje con contexto completo
        full_message = memory_context + f"Usuario: {message}"
        
        # PASO 4: Registrar en nuestro sistema de memoria
        persistent_memory.log_conversation(user_id, str(adk_session.id), "user", message)
        extract_and_save_memories(user_id, str(adk_session.id), message)
        
        # PASO 5: Crear contenido para ADK
        content = types.Content(
            role='user', 
            parts=[types.Part(text=full_message)]
        )
        
        # PASO 6: Crear runner UNA SOLA VEZ (según documentación ADK)
        if not hasattr(run_with_persistent_memory, '_runner'):
            run_with_persistent_memory._runner = create_runner()
        runner = run_with_persistent_memory._runner
        
        # PASO 7: Ejecutar con la sesión ADK persistente
        events = runner.run(
            user_id=user_id,
            session_id=adk_session.id,
            new_message=content
        )
        
        # PASO 8: Procesar respuesta y actualizar sesión (según documentación ADK)
        response = ""
        for event in events:
            # Según ADK: Manejar diferentes tipos de eventos
            if hasattr(event, 'is_final_response') and event.is_final_response():
                response = event.content.parts[0].text
                # Registrar respuesta del agente
                persistent_memory.log_conversation(user_id, str(adk_session.id), "agent", response)
                break
            elif hasattr(event, 'content') and event.content:
                # Evento con contenido (puede ser respuesta parcial)
                if hasattr(event.content, 'parts') and event.content.parts:
                    response = event.content.parts[0].text
                    persistent_memory.log_conversation(user_id, str(adk_session.id), "agent", response)
                    break
        
        # PASO 9: La sesión ADK se actualiza automáticamente con el evento
        print(f"✅ [ADK] Sesión {adk_session.id[:8]}... actualizada con nuevo evento")
        
        # PASO 10: Agregar sesión a memoria ADK + Vertex AI (según documentación oficial)
        try:
            # Obtener la sesión completa para agregarla a memoria
            completed_session = await session_service.get_session(
                app_name="simple_agent", 
                user_id=user_id, 
                session_id=adk_session.id
            )
            
            # Agregar a memoria (ADK local + Vertex AI si está configurado)
            if isinstance(memory_service, VertexAiMemoryBankService):
                await add_session_to_vertex_memory(completed_session)
            else:
                await memory_service.add_session_to_memory(completed_session)
                print(f"🧠 [ADK] Sesión agregada a memoria local para búsquedas futuras")
            
        except Exception as e:
            print(f"⚠️  [ADK] Error agregando sesión a memoria: {e}")
        
        return response, str(adk_session.id)
        
    except Exception as e:
        print(f"⚠️  [ADK ERROR] Error ejecutando agente: {e}")
        import traceback
        print(f"🔍 [DEBUG] Stacktrace: {traceback.format_exc()}")
        
        # Fallback con respuesta básica
        fallback_response = f"He recibido tu mensaje: '{message}'. Información guardada en memoria."
        persistent_memory.log_conversation(user_id, session_id or "fallback", "agent", fallback_response)
        return fallback_response, session_id or "fallback"

# ============================================================================
# EXTRACCIÓN SIMPLE DE MEMORIA (FUNCIONA)
# ============================================================================

def extract_and_save_memories(user_id: str, session_id: str, message: str):
    """Extraer información básica del mensaje."""
    
    message_lower = message.lower()
    
    # Extraer nombre
    if "me llamo" in message_lower:
        import re
        match = re.search(r'me llamo (\w+)', message_lower)
        if match:
            name = match.group(1)
            persistent_memory.save_memory(user_id, session_id, "nombre", name.capitalize())
            print(f"💾 Nombre extraído: {name}")
    
    # Extraer edad
    if "tengo" in message_lower and "años" in message_lower:
        import re
        match = re.search(r'tengo (\d+) años', message_lower)
        if match:
            age = match.group(1)
            persistent_memory.save_memory(user_id, session_id, "edad", age)
            print(f"💾 Edad extraída: {age}")

print("✅ Sistema de extracción simple configurado")

# ============================================================================
# SISTEMA DE MEMORIA DUAL AVANZADO (SEGÚN DOCUMENTACIÓN OFICIAL)
# ============================================================================

async def search_adk_memory(user_id: str, query: str):
    """Buscar en memoria ADK usando el patrón oficial de la documentación."""
    try:
        print(f"🔍 [ADK MEMORY] Buscando: '{query}' para usuario: {user_id}")
        
        # Usar el método oficial de ADK para buscar en memoria
        search_result = await memory_service.search_memory(
            app_name="simple_agent",
            user_id=user_id,
            query=query
        )
        
        if search_result and hasattr(search_result, 'memories') and search_result.memories:
            print(f"✅ [ADK MEMORY] Encontradas {len(search_result.memories)} memorias relevantes")
            return search_result.memories
        else:
            print("⚠️  [ADK MEMORY] No se encontraron memorias relevantes")
            return []
            
    except Exception as e:
        print(f"❌ [ADK MEMORY] Error buscando en memoria: {e}")
        return []

async def get_adk_memory_context(user_id: str, current_message: str):
    """Obtener contexto de memoria ADK para el mensaje actual."""
    try:
        # Buscar memorias relevantes al mensaje actual
        search_result = await memory_service.search_memory(
            app_name="simple_agent",
            user_id=user_id,
            query=current_message
        )
        
        if search_result and hasattr(search_result, 'memories') and search_result.memories:
            context = "\n--- MEMORIAS ADK RELEVANTES ---\n"
            for memory in search_result.memories:
                if hasattr(memory, 'content') and memory.content:
                    context += f"📝 {memory.content}\n"
                elif hasattr(memory, 'text') and memory.text:
                    context += f"📝 {memory.text}\n"
            context += "--- FIN MEMORIAS ADK ---\n\n"
            return context
        else:
            return ""
            
    except Exception as e:
        print(f"❌ [ADK MEMORY] Error obteniendo contexto: {e}")
        return ""

# ============================================================================
# VERTEX AI MEMORY BANK FUNCTIONS (SEGÚN DOCUMENTACIÓN OFICIAL)
# ============================================================================

async def add_session_to_vertex_memory(session):
    """Agregar sesión a Vertex AI Memory Bank (según documentación oficial)."""
    try:
        if isinstance(memory_service, VertexAiMemoryBankService):
            print("☁️  [VERTEX AI] Agregando sesión a Memory Bank...")
            await memory_service.add_session_to_memory(session)
            print("✅ Sesión agregada a Vertex AI Memory Bank")
            return True
        else:
            print("⚠️  [VERTEX AI] Memory Service no es Vertex AI, usando método estándar")
            await memory_service.add_session_to_memory(session)
            return True
    except Exception as e:
        print(f"❌ [VERTEX AI] Error agregando sesión a Memory Bank: {e}")
        return False

async def search_vertex_memory(user_id: str, query: str):
    """Buscar en Vertex AI Memory Bank con búsqueda semántica avanzada."""
    try:
        if isinstance(memory_service, VertexAiMemoryBankService):
            print(f"☁️  [VERTEX AI] Búsqueda semántica: '{query}' para usuario: {user_id}")
            
            # Búsqueda semántica avanzada en Vertex AI
            search_result = await memory_service.search_memory(
                app_name="simple_agent",
                user_id=user_id,
                query=query
            )
            
            if search_result and hasattr(search_result, 'memories') and search_result.memories:
                print(f"✅ [VERTEX AI] Encontradas {len(search_result.memories)} memorias semánticas")
                return search_result.memories
            else:
                print("⚠️  [VERTEX AI] No se encontraron memorias semánticas")
                return []
        else:
            # Fallback a búsqueda estándar
            return await search_adk_memory(user_id, query)
            
    except Exception as e:
        print(f"❌ [VERTEX AI] Error en búsqueda semántica: {e}")
        return []

def get_memory_service_info():
    """Obtener información del servicio de memoria configurado."""
    if isinstance(memory_service, VertexAiMemoryBankService):
        return {
            "type": "Vertex AI Memory Bank",
            "features": [
                "🧠 Búsqueda semántica avanzada",
                "💾 Memoria persistente en Google Cloud",
                "🔄 Aprendizaje automático de conversaciones",
                "📊 Extracción inteligente de información"
            ],
            "status": "✅ Configurado y funcionando"
        }
    else:
        return {
            "type": "In-Memory Memory Service",
            "features": [
                "🧠 Búsqueda por palabras clave",
                "⚠️  Memoria temporal (se pierde al reiniciar)",
                "🔍 Búsqueda básica en conversaciones",
                "📝 Almacenamiento en memoria local"
            ],
            "status": "⚠️  Modo fallback - configurar Vertex AI para funcionalidad completa"
        }
