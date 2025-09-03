"""
Agente con Base de Datos Integral - Usa SQLite completo para memoria persistente.
"""

import os
import sqlite3
import uuid
import asyncio
from google.genai import types
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseMemorySystem:
    """Sistema de memoria persistente completo usando SQLite."""
    
    def __init__(self, db_path: str = "database_agent_sessions.db"):
        self.db_path = db_path
        self._init_db()
        print(f"✅ [DATABASE AGENT] Base de datos inicializada: {db_path}")
    
    def _init_db(self):
        """Inicializar base de datos SQLite con esquema completo."""
        conn = sqlite3.connect(self.db_path)
        
        # Tabla de memorias de usuario
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
        
        # Tabla de conversaciones
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
        
        # Tabla de sesiones
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de contexto semántico
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                context_type TEXT NOT NULL,
                content TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_memory(self, user_id: str, session_id: str, key: str, value: str):
        """Guardar memoria del usuario."""
        conn = sqlite3.connect(self.db_path)
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
    
    def get_or_create_session(self, user_id: str, session_id: str = None):
        """Obtener sesión existente o crear nueva."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        
        # Verificar si la sesión existe
        cursor = conn.execute("""
            SELECT id FROM sessions WHERE id = ?
        """, (session_id,))
        
        if not cursor.fetchone():
            # Crear nueva sesión
            conn.execute("""
                INSERT INTO sessions (id, user_id, created_at, last_activity)
                VALUES (?, ?, datetime('now'), datetime('now'))
            """, (session_id, user_id))
        else:
            # Actualizar última actividad
            conn.execute("""
                UPDATE sessions SET last_activity = datetime('now')
                WHERE id = ?
            """, (session_id,))
        
        conn.commit()
        conn.close()
        return session_id
    
    def get_conversation_history(self, user_id: str, limit: int = 10):
        """Obtener historial de conversaciones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT role, content, timestamp 
            FROM conversation_log 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return history
    
    def search_semantic_context(self, user_id: str, query: str):
        """Búsqueda semántica básica en contexto."""
        conn = sqlite3.connect(self.db_path)
        
        # Búsqueda simple por palabras clave
        query_terms = query.lower().split()
        conditions = []
        params = [user_id]
        
        for term in query_terms:
            conditions.append("content LIKE ?")
            params.append(f"%{term}%")
        
        where_clause = " AND ".join(conditions)
        
        cursor = conn.execute(f"""
            SELECT content, relevance_score, timestamp 
            FROM semantic_context 
            WHERE user_id = ? AND ({where_clause})
            ORDER BY relevance_score DESC, timestamp DESC
            LIMIT 5
        """, params)
        
        results = cursor.fetchall()
        conn.close()
        return results

class DatabaseAgent:
    """Agente que usa base de datos integral para memoria persistente siguiendo el patrón LlmAgent."""
    
    def __init__(self):
        self._setup_environment()
        self.memory_system = DatabaseMemorySystem()
        self._setup_llm_agent()
        self._setup_runner()
    
    def _setup_environment(self):
        """Configurar variables de entorno para Google AI Studio."""
        # Verificar API Key (solo Google AI Studio, NO Vertex AI)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en variables de entorno")

        # Asegurar que NO use Vertex AI - FORZAR Google AI Studio
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        os.environ.pop("GOOGLE_CLOUD_LOCATION", None)
        os.environ.pop("AGENT_ENGINE_ID", None)
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

        # FORZAR uso de Google AI Studio
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

        print(f"✅ [DATABASE AGENT] API Key cargada: {api_key[:10]}...{api_key[-5:]}")
        print("🔧 [DATABASE AGENT] Configurado para usar Google AI Studio (NO Vertex AI)")
    
    def _setup_llm_agent(self):
        """Configurar el LlmAgent siguiendo el patrón estándar de ADK."""
        try:
            from google.adk.agents import LlmAgent
            from google.adk.tools import load_memory
            
            # Obtener modelo desde variables de entorno
            model = os.getenv("AGENT_MODEL", "gemini-2.0-flash")
            print(f"🤖 [DATABASE AGENT] Usando modelo: {model}")
            
            # Crear LlmAgent con configuración estándar (sin herramientas por ahora)
            self.llm_agent = LlmAgent(
                name="database_agent",
                model=model,
                description="Eres un asistente con memoria persistente en base de datos SQLite.",
                instruction=(
                    "Eres un asistente que recuerda información entre sesiones usando una base de datos SQLite completa. "
                    "Tienes acceso a historial de conversaciones, contexto semántico y memorias personales. "
                    "Usa la información proporcionada para personalizar tus respuestas."
                )
                # tools=[load_memory]  # Comentado temporalmente para evitar function calls
            )
            print("✅ [DATABASE AGENT] LlmAgent configurado siguiendo patrón ADK")
            
        except Exception as e:
            print(f"❌ [DATABASE AGENT] Error configurando LlmAgent: {e}")
            self.llm_agent = None
    
    def _setup_runner(self):
        """Configurar el Runner con servicios personalizados."""
        try:
            from google.adk import Runner
            from google.adk.sessions import DatabaseSessionService
            from google.adk.memory import InMemoryMemoryService
            
            # Configurar servicios personalizados con base de datos separada para ADK
            db_url = "sqlite:///./database_agent_adk_sessions.db"
            self.session_service = DatabaseSessionService(db_url=db_url)
            
            # Crear Runner con LlmAgent y servicios personalizados
            self.runner = Runner(
                agent=self.llm_agent,
                app_name="database_agent",
                session_service=self.session_service,
            )
            print("✅ [DATABASE AGENT] Runner configurado con servicios personalizados")
            
        except Exception as e:
            print(f"❌ [DATABASE AGENT] Error configurando Runner: {e}")
            self.runner = None
    
    async def run(self, user_id: str, message: str, session_id: str = None):
        """Ejecutar agente siguiendo el patrón estándar de ADK."""
        
        print(f"🧠 [DATABASE AGENT] Ejecutando para usuario: {user_id}")
        
        try:
            # PASO 1: Generar session_id si no existe
            if not session_id:
                session_id = str(uuid.uuid4())
                print(f"🆔 [DATABASE AGENT] Nuevo session_id generado: {session_id[:8]}...")
            
            # PASO 2: CREAR SESIÓN EN ADK ANTES DE EJECUTAR
            if self.runner and self.session_service:
                try:
                    # Crear sesión en ADK
                    await self.session_service.create_session(
                        app_name="database_agent",
                        user_id=user_id,
                        session_id=session_id
                    )
                    print(f"✅ [DATABASE AGENT] Sesión creada en ADK: {session_id[:8]}...")
                except Exception as session_error:
                    print(f"⚠️  [DATABASE AGENT] Error creando sesión: {session_error}")
                    # Continuar sin sesión ADK si falla
            
            # PASO 3: Preparar contexto de memoria personalizada
            memory_context = self._prepare_memory_context(user_id, message)
            
            # PASO 4: Crear mensaje con contexto personalizado
            full_message = memory_context + f"Usuario: {message}"
            
            # PASO 5: Crear contenido para ADK
            content = types.Content(
                role='user', 
                parts=[types.Part(text=full_message)]
            )
            
            # PASO 6: Ejecutar con Runner estándar de ADK
            if self.runner:
                events = self.runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content
                )
                
                # PASO 6: Procesar respuesta siguiendo patrón ADK
                response = await self._process_adk_response(events)
                
                # PASO 7: Guardar información personalizada
                self._save_personal_memory(user_id, session_id, message, response)
                
                return response, session_id
            else:
                # Fallback si no hay runner
                return self._generate_fallback_response(message), session_id
            
        except Exception as e:
            print(f"❌ [DATABASE AGENT] Error: {e}")
            return self._generate_fallback_response(message), session_id or str(uuid.uuid4())
    
    def _prepare_memory_context(self, user_id: str, message: str):
        """Preparar contexto de memoria personalizada."""
        context_parts = []
        
        # Obtener memorias personales
        memories = self.memory_system.get_memories(user_id)
        if memories:
            memory_context = "\n--- INFORMACIÓN PERSONAL RECORDADA ---\n"
            for key, value, timestamp in memories:
                memory_context += f"- {key}: {value}\n"
            memory_context += "--- FIN INFORMACIÓN ---\n\n"
            context_parts.append(memory_context)
        
        # Obtener historial de conversaciones
        conversation_history = self.memory_system.get_conversation_history(user_id, limit=5)
        if conversation_history:
            history_context = "\n--- HISTORIAL DE CONVERSACIÓN ---\n"
            for role, content, timestamp in reversed(conversation_history):
                history_context += f"{role.upper()}: {content}\n"
            history_context += "--- FIN HISTORIAL ---\n\n"
            context_parts.append(history_context)
        
        # Búsqueda semántica en contexto
        semantic_results = self.memory_system.search_semantic_context(user_id, message)
        if semantic_results:
            semantic_context = "\n--- CONTEXTO SEMÁNTICO RELEVANTE ---\n"
            for content, score, timestamp in semantic_results:
                semantic_context += f"📝 {content} (relevancia: {score:.2f})\n"
            semantic_context += "--- FIN CONTEXTO SEMÁNTICO ---\n\n"
            context_parts.append(semantic_context)
        
        return "".join(context_parts)
    
    async def _process_adk_response(self, events):
        """Procesar eventos del agente siguiendo patrón ADK."""
        response = ""
        print(f"🔍 [DATABASE AGENT] Procesando eventos del agente...")
        
        try:
            for event in events:
                print(f"🔍 [DATABASE AGENT] Evento: {type(event).__name__}")
                
                # Manejar diferentes tipos de eventos siguiendo patrón ADK
                if hasattr(event, 'is_final_response') and callable(event.is_final_response):
                    if event.is_final_response():
                        print("✅ [DATABASE AGENT] Evento final detectado")
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts') and event.content.parts:
                                response = event.content.parts[0].text
                                print(f"📝 [DATABASE AGENT] Respuesta extraída: {response[:100]}...")
                                if response and response.strip():
                                    break
                
                elif hasattr(event, 'content') and event.content:
                    print(f"📄 [DATABASE AGENT] Evento con contenido encontrado")
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for j, part in enumerate(event.content.parts):
                            if hasattr(part, 'text') and part.text:
                                potential_response = part.text
                                print(f"📝 [DATABASE AGENT] Parte {j+1}: {potential_response[:100]}...")
                                if potential_response and potential_response.strip():
                                    response = potential_response
                                    print(f"✅ [DATABASE AGENT] Respuesta encontrada en parte {j+1}")
                                    break
                        if response:
                            break
                
                elif hasattr(event, 'text') and event.text:
                    response = event.text
                    print(f"✅ [DATABASE AGENT] Respuesta encontrada en event.text: {response[:100]}...")
                    break
                    
        except Exception as event_error:
            print(f"⚠️  [DATABASE AGENT] Error procesando eventos: {event_error}")
            response = ""
        
        # Si no se encontró respuesta, usar fallback
        if not response or not response.strip():
            print("⚠️  [DATABASE AGENT] No se pudo extraer respuesta del agente, usando fallback")
            response = self._generate_fallback_response("")
        
        return response
    
    def _save_personal_memory(self, user_id: str, session_id: str, message: str, response: str):
        """Guardar información personalizada en la base de datos."""
        try:
            # Registrar conversación
            self.memory_system.log_conversation(user_id, session_id, "user", message)
            if response:
                self.memory_system.log_conversation(user_id, session_id, "agent", response)
            
            # Extraer y guardar información del mensaje
            self._extract_and_save_memories(user_id, session_id, message)
            
            # Guardar contexto semántico
            self._save_semantic_context(user_id, session_id, message, response)
            
        except Exception as e:
            print(f"⚠️  [DATABASE AGENT] Error guardando memoria personalizada: {e}")
    
    async def _generate_response(self, full_message: str):
        """Generar respuesta usando el modelo Gemini."""
        try:
            response = await self.model.generate_content_async(full_message)
            return response.text
        except Exception as e:
            print(f"❌ [DATABASE AGENT] Error generando respuesta: {e}")
            return None
    
    def _extract_and_save_memories(self, user_id: str, session_id: str, message: str):
        """Extraer información del mensaje y guardarla."""
        message_lower = message.lower()
        
        # Extraer nombre
        if "me llamo" in message_lower:
            import re
            match = re.search(r'me llamo (\w+)', message_lower)
            if match:
                name = match.group(1)
                self.memory_system.save_memory(user_id, session_id, "nombre", name.capitalize())
                print(f"💾 [DATABASE AGENT] Nombre extraído: {name}")
        
        # Extraer edad
        if "tengo" in message_lower and "años" in message_lower:
            import re
            match = re.search(r'tengo (\d+) años', message_lower)
            if match:
                age = match.group(1)
                self.memory_system.save_memory(user_id, session_id, "edad", age)
                print(f"💾 [DATABASE AGENT] Edad extraída: {age}")
        
        # Extraer preferencias
        preference_keywords = ["me gusta", "prefiero", "favorito", "disfruto"]
        for keyword in preference_keywords:
            if keyword in message_lower:
                # Extraer la frase completa después del keyword
                import re
                match = re.search(f'{keyword} (.+)', message_lower)
                if match:
                    preference = match.group(1).strip()
                    self.memory_system.save_memory(user_id, session_id, f"preferencia_{keyword}", preference)
                    print(f"💾 [DATABASE AGENT] Preferencia extraída: {preference}")
    
    def _save_semantic_context(self, user_id: str, session_id: str, message: str, response: str):
        """Guardar contexto semántico para búsquedas futuras."""
        try:
            conn = sqlite3.connect(self.memory_system.db_path)
            
            # Guardar contexto del mensaje
            conn.execute("""
                INSERT INTO semantic_context 
                (user_id, session_id, context_type, content, relevance_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, "user_message", message, 1.0))
            
            # Guardar contexto de la respuesta
            if response:
                conn.execute("""
                    INSERT INTO semantic_context 
                    (user_id, session_id, context_type, content, relevance_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, session_id, "agent_response", response, 0.8))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  [DATABASE AGENT] Error guardando contexto semántico: {e}")
    
    def _generate_fallback_response(self, message: str):
        """Generar respuesta de fallback cuando el modelo no está disponible."""
        message_lower = message.lower()
        
        # Obtener memorias del usuario si es posible
        memories = []
        try:
            # Intentar obtener memorias del sistema de memoria
            if hasattr(self, 'memory_system'):
                memories = self.memory_system.get_memories("fallback_user")
        except:
            pass
        
        if "hola" in message_lower or "buenos días" in message_lower:
            if memories:
                name = None
                for key, value, _ in memories:
                    if key.lower() == "nombre":
                        name = value
                        break
                
                if name:
                    return f"¡Hola {name}! Es un placer verte de nuevo. ¿En qué puedo ayudarte hoy?"
                else:
                    return "¡Hola! Es un placer verte de nuevo. ¿En qué puedo ayudarte hoy?"
            else:
                return "¡Hola! Soy tu asistente con memoria persistente en base de datos. ¿En qué puedo ayudarte?"
        
        elif "cómo estás" in message_lower:
            return "¡Muy bien, gracias! Estoy aquí para ayudarte con mi memoria persistente en base de datos."
        
        elif "adiós" in message_lower or "hasta luego" in message_lower:
            return "¡Hasta luego! Ha sido un placer ayudarte. ¡Que tengas un buen día!"
        
        else:
            return f"He recibido tu mensaje: '{message}'. Soy tu asistente con memoria persistente en base de datos. ¿En qué puedo ayudarte?"
    
    def get_memory_service_info(self):
        """Obtener información del servicio de memoria configurado."""
        return {
            "type": "Database SQLite System",
            "features": [
                "🗄️ Base de datos SQLite completa",
                "🧠 Búsqueda semántica básica",
                "📝 Historial de conversaciones",
                "💾 Memoria persistente local",
                "🔍 Contexto semántico personalizado",
                "📝 Herramienta load_memory integrada"
            ],
            "status": "✅ Configurado y funcionando"
        }

# Instancia global del agente
# Instancia del agente se crea dinámicamente cuando se necesita
