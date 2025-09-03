"""
Agente Vertex AI - Implementa Vertex AI Express Mode según la documentación oficial.
Basado en: https://google.github.io/adk-docs/sessions/express-mode/
"""

import os
import uuid
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class VertexAgent:
    """Agente que implementa Vertex AI Express Mode según la documentación oficial."""
    
    def __init__(self):
        self.agent_engine_id = os.getenv("AGENT_ENGINE_ID")
        self.model = os.getenv("AGENT_MODEL", "gemini-2.0-flash")
        
        # Verificar API Key específica para Vertex AI
        vertex_api_key = os.getenv("GOOGLE_API_KEY_VERTEX")
        if not vertex_api_key:
            raise ValueError("GOOGLE_API_KEY_VERTEX no encontrada en variables de entorno")
        
        if not self.agent_engine_id:
            raise ValueError("AGENT_ENGINE_ID no encontrada en variables de entorno")
        
        # Configurar Vertex AI específicamente
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
        os.environ["GOOGLE_API_KEY"] = vertex_api_key  # Usar la API key específica de Vertex
        
        print(f"✅ [VERTEX AGENT] API Key cargada: {vertex_api_key[:10]}...{vertex_api_key[-5:]}")
        print(f"✅ [VERTEX AGENT] Agent Engine ID: {self.agent_engine_id}")
        print(f"🤖 [VERTEX AGENT] Modelo: {self.model}")
        print("🔧 [VERTEX AGENT] Configurado para usar Vertex AI")
        
        # Configurar servicios Vertex AI Express Mode
        self._setup_vertex_services()
    
    def _setup_vertex_services(self):
        """Configurar servicios de memoria según la documentación oficial del ADK."""
        try:

            # Intentar usar VertexAiMemoryBankService primero (requiere Agent Engine)
            if self.agent_engine_id:
                from google.adk.memory import VertexAiMemoryBankService
                
                # Configurar VertexAiMemoryBankService con proyecto y ubicación explícitos
                # para asegurar que use OAuth2 correctamente
                self.memory_service = VertexAiMemoryBankService(
                    project="proyect-470810",
                    location="us-central1", 
                    agent_engine_id=self.agent_engine_id
                )
                print("✅ [VERTEX AGENT] VertexAiMemoryBankService configurado")
                print("   🧠 Búsqueda semántica avanzada")
                print("   💾 Memoria persistente en Google Cloud")
                print("   ☁️  Vertex AI Memory Bank")
                print("   🔐 Autenticación OAuth2")
                
            else:
                # Fallback a InMemoryMemoryService para desarrollo
                from google.adk.memory import InMemoryMemoryService
                
                self.memory_service = InMemoryMemoryService()
                print("✅ [VERTEX AGENT] InMemoryMemoryService configurado")
                print("   🧠 Búsqueda por palabras clave")
                print("   💾 Memoria temporal (se pierde al reiniciar)")
                print("   📚 Ideal para desarrollo y pruebas")
                
        except Exception as e:
            print(f"❌ [VERTEX AGENT] Error configurando servicios de memoria: {e}")
            # Fallback a InMemoryMemoryService
            try:
                from google.adk.memory import InMemoryMemoryService
                self.memory_service = InMemoryMemoryService()
                print("✅ [VERTEX AGENT] Fallback a InMemoryMemoryService")
            except Exception as e2:
                print(f"❌ [VERTEX AGENT] Error crítico: {e2}")
                self.memory_service = None
    
    async def run(self, user_id: str, message: str, session_id: str = None) -> tuple[str, str]:
        """Ejecutar el agente usando servicios de memoria según la documentación oficial del ADK."""
        try:
            print(f"🧠 [VERTEX AGENT] Ejecutando para usuario: {user_id}")
            
            if not self.memory_service:
                return "Error: Servicio de memoria no configurado correctamente.", session_id or str(uuid.uuid4())[:8]
            
            # Generar session_id si no existe
            if not session_id:
                session_id = str(uuid.uuid4())[:8]
                print(f"🆔 [VERTEX AGENT] Nuevo session_id generado: {session_id}")
            
            # Buscar memoria relevante según la documentación oficial
            memory_context = await self._search_memory(user_id, message)
            
            # Generar respuesta usando Vertex AI directamente
            response = await self._generate_response(message, memory_context)
            
            # Guardar conversación en memoria según la documentación oficial
            await self._save_to_memory(user_id, message, response, session_id)
            
            return response, session_id
            
        except Exception as e:
            print(f"⚠️  [VERTEX AGENT] Error: {e}")
            return "Lo siento, no pude procesar tu mensaje en este momento.", session_id or str(uuid.uuid4())[:8]
    
    async def _search_memory(self, user_id: str, query: str) -> str:
        """Buscar memoria relevante usando el servicio de memoria según la documentación oficial del ADK."""
        try:
            # Usar el servicio de memoria configurado con argumentos requeridos
            app_name = self.agent_engine_id or "default_app"
            memories = await self.memory_service.search_memory(
                app_name=app_name,
                user_id=user_id,
                query=query
            )
            
            if memories and hasattr(memories, 'memories'):
                # Para VertexAiMemoryBankService
                memory_list = memories.memories
                if memory_list:
                    print(f"🧠 [VERTEX AGENT] Memoria encontrada: {len(memory_list)} elementos")
                    # Extraer el contenido de texto de los objetos Content
                    memory_texts = []
                    for mem in memory_list[:3]:  # Top 3
                        if hasattr(mem, 'content'):
                            if hasattr(mem.content, 'parts') and mem.content.parts:
                                # Es un objeto Content con parts
                                text_content = mem.content.parts[0].text if mem.content.parts[0].text else str(mem.content)
                            else:
                                # Es texto directo
                                text_content = str(mem.content)
                        else:
                            text_content = str(mem)
                        memory_texts.append(text_content)
                    return "\n".join(memory_texts)
            elif memories:
                # Para InMemoryMemoryService
                print(f"🧠 [VERTEX AGENT] Memoria encontrada: {len(memories)} elementos")
                return "\n".join([getattr(mem, 'content', str(mem)) for mem in memories[:3]])  # Top 3
            
            print("🧠 [VERTEX AGENT] No se encontró memoria relevante")
            return ""
                        
        except Exception as e:
            print(f"⚠️  [VERTEX AGENT] Error buscando memoria: {e}")
            return ""
    
    async def _generate_response(self, message: str, memory_context: str) -> str:
        """Generar respuesta usando Vertex AI con autenticación OAuth2."""
        try:
            from google import genai
            import os
            
            # Configurar variable de entorno si no está configurada
            if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                credentials_path = r"C:\Users\PC\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\Roaming\gcloud\application_default_credentials.json"
                if os.path.exists(credentials_path):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # Crear cliente con autenticación OAuth2 y proyecto configurado
            client = genai.Client(
                vertexai=True,
                project="proyect-470810",
                location="us-central1"
            )
            
            # Construir prompt con contexto de memoria
            system_prompt = """Eres un asistente Vertex AI con memoria persistente. 
            Tienes acceso al contexto de conversaciones anteriores para proporcionar respuestas más personalizadas y relevantes."""
            
            user_prompt = f"""Contexto de conversaciones anteriores:
{memory_context if memory_context else "No hay contexto de memoria disponible."}

Mensaje actual del usuario: {message}

Responde de manera útil y personalizada, considerando el contexto de memoria si está disponible."""

            # Generar respuesta usando la API REST de Vertex AI
            response = client.models.generate_content(
                model=self.model,
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "user", "parts": [{"text": user_prompt}]}
                ]
            )
            
            return response.text if response.text else "No pude generar una respuesta."
            
        except Exception as e:
            print(f"❌ [VERTEX AGENT] Error generando respuesta: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    async def _save_to_memory(self, user_id: str, message: str, response: str, session_id: str):
        """Guardar conversación en memoria usando el servicio configurado según la documentación oficial del ADK."""
        try:
            from google.adk.sessions import Session
            
            # Crear una sesión temporal para guardar en memoria
            app_name = self.agent_engine_id or "default_app"
            
            # Crear sesión temporal siguiendo exactamente la documentación oficial
            temp_session = Session(
                app_name=app_name,
                user_id=user_id,
                id=session_id
            )
            
            # Crear eventos con la estructura correcta para VertexAiMemoryBankService
            # Los eventos deben tener un atributo 'content' con método model_dump()
            from google.genai.types import Content, Part
            
            # Crear objetos Content que tengan el método model_dump()
            user_content = Content(parts=[Part(text=message)], role="user")
            assistant_content = Content(parts=[Part(text=response)], role="assistant")
            
            # Crear eventos que tengan el atributo 'content' esperado por el servicio
            user_event = type('Event', (), {
                'content': user_content
            })()
            
            assistant_event = type('Event', (), {
                'content': assistant_content
            })()
            
            # Agregar eventos a la sesión
            temp_session.events.append(user_event)
            temp_session.events.append(assistant_event)
            
            # Guardar sesión en memoria usando el servicio configurado
            await self.memory_service.add_session_to_memory(temp_session)
            print("💾 [VERTEX AGENT] Conversación guardada en memoria")
            
        except Exception as e:
            print(f"⚠️  [VERTEX AGENT] Error guardando en memoria: {e}")
            print(f"   Detalles del error: {type(e).__name__}")
            
            # Si falla, simplemente no guardar en memoria por ahora
            # El agente seguirá funcionando sin memoria
            print("🔄 [VERTEX AGENT] Continuando sin guardar en memoria...")
    
    def get_memory_service_info(self) -> dict:
        """Obtener información del servicio de memoria."""
        memory_type = "InMemoryMemoryService"
        features = [
            "Búsqueda por palabras clave",
            "Memoria temporal (se pierde al reiniciar)",
            "Ideal para desarrollo y pruebas"
        ]
        
        if self.memory_service and hasattr(self.memory_service, '__class__'):
            if 'VertexAiMemoryBankService' in str(type(self.memory_service)):
                memory_type = "VertexAiMemoryBankService"
                features = [
                    "Búsqueda semántica avanzada",
                    "Memoria persistente en Google Cloud",
                    "Procesamiento automático de memoria",
                    "Escalabilidad automática"
                ]
        
        return {
            "type": memory_type,
            "features": features,
            "status": "Configurado correctamente" if self.memory_service else "No configurado",
            "agent_engine_id": self.agent_engine_id,
            "model": self.model,
            "setup_required": [
                "GOOGLE_GENAI_USE_VERTEXAI=TRUE",
                "GOOGLE_API_KEY configurado",
                "AGENT_ENGINE_ID configurado (opcional, para VertexAiMemoryBankService)"
            ]
        }

# Instancia del agente se crea dinámicamente cuando se necesita
