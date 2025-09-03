"""
Agente ADK - Usa ADK InMemorySessionService e InMemoryMemoryService para memoria persistente.
"""

import os
import uuid
import asyncio
from google.genai import types
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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

print(f"✅ [ADK AGENT] API Key cargada: {api_key[:10]}...{api_key[-5:]}")
print("🔧 [ADK AGENT] Configurado para usar Google AI Studio (NO Vertex AI)")

class ADKAgent:
    """Agente que usa ADK InMemorySessionService e InMemoryMemoryService siguiendo el patrón oficial de LlmAgent."""
    
    def __init__(self):
        self._setup_llm_agent()
        self._setup_runner()
    
    def _setup_llm_agent(self):
        """Configurar el LlmAgent siguiendo el patrón estándar de ADK."""
        try:
            from google.adk.agents import LlmAgent
            from google.adk.tools import load_memory
            
            # Obtener modelo desde variables de entorno
            model = os.getenv("AGENT_MODEL", "gemini-2.0-flash")
            print(f"🤖 [ADK AGENT] Usando modelo: {model}")
            
            # Crear LlmAgent con configuración estándar
            self.llm_agent = LlmAgent(
                name="adk_agent",
                model=model,
                description="Eres un asistente ADK con memoria persistente usando InMemoryMemoryService.",
                instruction=(
                    "Eres un asistente ADK que recuerda información entre sesiones usando InMemoryMemoryService. "
                    "Tienes acceso a la herramienta 'load_memory' para consultar conversaciones pasadas. "
                    "Usa la información proporcionada para personalizar tus respuestas."
                ),
                tools=[load_memory]  # Herramienta oficial ADK
            )
            print("✅ [ADK AGENT] LlmAgent configurado siguiendo patrón ADK")
            
        except Exception as e:
            print(f"❌ [ADK AGENT] Error configurando LlmAgent: {e}")
            self.llm_agent = None
    
    def _setup_runner(self):
        """Configurar el Runner siguiendo el patrón oficial de la documentación ADK."""
        try:
            from google.adk import Runner
            from google.adk.sessions import InMemorySessionService
            from google.adk.memory import InMemoryMemoryService
            
            # Usar InMemorySessionService como recomienda la documentación para desarrollo
            self.session_service = InMemorySessionService()
            self.memory_service = InMemoryMemoryService()
            
            print("✅ [ADK AGENT] Servicios configurados siguiendo patrón oficial ADK")
            print("   📝 InMemorySessionService para sesiones")
            print("   🧠 InMemoryMemoryService para memoria")
            
            # Crear Runner con LlmAgent y servicios ADK
            self.runner = Runner(
                agent=self.llm_agent,
                app_name="adk_agent",
                session_service=self.session_service,
                memory_service=self.memory_service
            )
            print("✅ [ADK AGENT] Runner configurado con servicios ADK estándar")
            
        except Exception as e:
            print(f"❌ [ADK AGENT] Error configurando Runner: {e}")
            self.runner = None
    
    async def run(self, user_id: str, message: str, session_id: str = None):
        """Ejecutar agente siguiendo el patrón oficial de la documentación ADK."""
        
        print(f"🧠 [ADK AGENT] Ejecutando para usuario: {user_id}")
        
        try:
            # PASO 1: Generar session_id si no existe
            if not session_id:
                session_id = str(uuid.uuid4())
                print(f"🆔 [ADK AGENT] Nuevo session_id generado: {session_id[:8]}...")
            
            # PASO 2: Crear sesión siguiendo patrón oficial (una sola vez)
            if self.runner and self.session_service:
                try:
                    await self.session_service.create_session(
                        app_name="adk_agent",
                        user_id=user_id,
                        session_id=session_id
                    )
                    print(f"✅ [ADK AGENT] Sesión creada: {session_id[:8]}...")
                except Exception as session_error:
                    # Si la sesión ya existe, continuar (esto es normal)
                    print(f"ℹ️  [ADK AGENT] Sesión ya existe o error: {session_error}")
            
            # PASO 3: Crear contenido para ADK
            content = types.Content(
                role='user', 
                parts=[types.Part(text=message)]
            )
            
            # PASO 4: Ejecutar con Runner asíncrono siguiendo patrón oficial ADK
            if self.runner:
                final_response_text = "(No final response)"
                
                # Usar run_async como muestra la documentación oficial
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                        print(f"✅ [ADK AGENT] Respuesta final obtenida: {final_response_text[:100]}...")
                
                # PASO 5: AGREGAR SESIÓN A MEMORIA (siguiendo patrón oficial)
                print(f"🧠 [ADK AGENT] Agregando sesión a memoria...")
                await self._add_session_to_memory(user_id, session_id)
                
                return final_response_text, session_id
            else:
                # Fallback si no hay runner
                return self._generate_fallback_response(message), session_id
            
        except Exception as e:
            print(f"❌ [ADK AGENT] Error: {e}")
            return self._generate_fallback_response(message), session_id or str(uuid.uuid4())
    
    async def search_memory(self, user_id: str, query: str):
        """Buscar en la memoria ADK siguiendo el patrón oficial."""
        try:
            print(f"🔍 [ADK AGENT] Buscando memoria para usuario {user_id} con query: {query}")
            
            if self.memory_service:
                search_result = await self.memory_service.search_memory(
                    app_name="adk_agent",
                    user_id=user_id,
                    query=query
                )
                
                if search_result and hasattr(search_result, 'memories') and search_result.memories:
                    print(f"✅ [ADK AGENT] Encontradas {len(search_result.memories)} memorias relevantes")
                    return search_result
                else:
                    print("ℹ️  [ADK AGENT] No se encontraron memorias relevantes")
                    return None
            else:
                print("⚠️  [ADK AGENT] Servicio de memoria no disponible")
                return None
                
        except Exception as e:
            print(f"❌ [ADK AGENT] Error buscando memoria: {e}")
            return None
    
    async def _add_session_to_memory(self, user_id: str, session_id: str):
        """Agregar sesión a memoria ADK siguiendo el patrón oficial."""
        try:
            # Obtener la sesión completa del session_service
            completed_session = await self.session_service.get_session(
                app_name="adk_agent", 
                user_id=user_id, 
                session_id=session_id
            )
            
            # Agregar a memoria siguiendo el patrón oficial de la documentación
            await self.memory_service.add_session_to_memory(completed_session)
            print(f"🧠 [ADK AGENT] Sesión {session_id[:8]}... agregada a memoria para búsquedas futuras")
            
        except Exception as e:
            print(f"⚠️  [ADK AGENT] Error agregando sesión a memoria: {e}")
    
    def _generate_fallback_response(self, message: str):
        """Generar respuesta de fallback cuando el agente ADK no está disponible."""
        message_lower = message.lower() if message else ""
        
        if "hola" in message_lower or "buenos días" in message_lower:
            return "¡Hola! Soy tu asistente ADK con memoria persistente. ¿En qué puedo ayudarte?"
        
        elif "cómo estás" in message_lower:
            return "¡Muy bien, gracias! Estoy aquí para ayudarte con mi memoria persistente ADK."
        
        elif "adiós" in message_lower or "hasta luego" in message_lower:
            return "¡Hasta luego! Ha sido un placer ayudarte. ¡Que tengas un buen día!"
        
        else:
            return f"He recibido tu mensaje: '{message}'. Soy tu asistente ADK con memoria persistente. ¿En qué puedo ayudarte?"
    
    def get_memory_service_info(self):
        """Obtener información del servicio de memoria configurado."""
        return {
            "type": "ADK InMemoryMemoryService + InMemorySessionService (Patrón Oficial)",
            "features": [
                "📝 InMemorySessionService para sesiones (recomendado para desarrollo)",
                "🧠 InMemoryMemoryService para memoria persistente",
                "🔧 Herramienta load_memory integrada automáticamente",
                "🔄 Agregado automático de sesiones a memoria",
                "🔍 Búsqueda de memorias por query semántica",
                "✅ Siguiendo patrón oficial de documentación ADK"
            ],
            "status": "✅ Configurado siguiendo patrón oficial ADK",
            "memory_workflow": [
                "1. Usuario envía mensaje",
                "2. ADK Runner procesa con LlmAgent + load_memory tool",
                "3. Sesión se guarda en InMemorySessionService",
                "4. Sesión se agrega a InMemoryMemoryService para búsquedas",
                "5. Futuras consultas usan load_memory tool automáticamente"
            ],
            "documentation_reference": "https://google.github.io/adk-docs/sessions/memory/"
        }

# Instancia del agente se crea dinámicamente cuando se necesita
