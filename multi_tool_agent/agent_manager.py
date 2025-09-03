"""
Gestor de Agentes - Permite seleccionar y usar diferentes tipos de agentes.
"""

import asyncio
from typing import Optional, Tuple

# Importar las clases de agentes (no las instancias)
from .agents.database_agent import DatabaseAgent
from .agents.adk_agent import ADKAgent
from .agents.vertex_agent import VertexAgent

class AgentManager:
    """Gestor para manejar diferentes tipos de agentes."""
    
    def __init__(self):
        self.agent_classes = {
            'database': DatabaseAgent,
            'adk': ADKAgent,
            'vertex': VertexAgent
        }
        self.current_agent = None
        self.current_agent_type = None
    
    def get_available_agents(self):
        """Obtener lista de agentes disponibles."""
        return list(self.agent_classes.keys())
    
    def select_agent(self, agent_type: str):
        """Seleccionar un agente específico."""
        if agent_type not in self.agent_classes:
            raise ValueError(f"Agente '{agent_type}' no disponible. Agentes disponibles: {self.get_available_agents()}")
        
        # Crear instancia del agente dinámicamente
        agent_class = self.agent_classes[agent_type]
        self.current_agent = agent_class()
        self.current_agent_type = agent_type
        
        print(f"✅ [AGENT MANAGER] Agente seleccionado: {agent_type.upper()}")
        
        # Mostrar información del agente seleccionado
        if agent_type == 'database':
            print("   🗄️  Base de datos integral con SQLite completo")
            print("   📊 Búsqueda semántica básica")
            print("   💾 Memoria persistente local")
        elif agent_type == 'adk':
            print("   🔧 ADK InMemorySessionService")
            print("   🧠 Memoria persistente ADK")
            print("   🔍 Búsqueda en conversaciones")
        elif agent_type == 'vertex':
            print("   ☁️  Vertex AI Memory Bank")
            print("   🧠 Búsqueda semántica avanzada")
            print("   💾 Memoria persistente en Google Cloud")
        
        return self.current_agent
    
    async def run_agent(self, user_id: str, message: str, session_id: str = None) -> Tuple[str, str]:
        """Ejecutar el agente seleccionado."""
        if not self.current_agent:
            raise ValueError("No se ha seleccionado ningún agente. Use select_agent() primero.")
        
        print(f"🚀 [AGENT MANAGER] Ejecutando agente: {self.current_agent_type.upper()}")
        
        try:
            response, session_id = await self.current_agent.run(user_id, message, session_id)
            return response, session_id
        except Exception as e:
            print(f"❌ [AGENT MANAGER] Error ejecutando agente: {e}")
            return f"Error ejecutando agente {self.current_agent_type}: {str(e)}", session_id or "error"
    
    def get_agent_info(self, agent_type: str = None):
        """Obtener información del agente."""
        if agent_type is None:
            agent_type = self.current_agent_type
        
        if not agent_type or agent_type not in self.agent_classes:
            return None
        
        # Crear instancia temporal para obtener información
        agent_class = self.agent_classes[agent_type]
        agent = agent_class()
        
        info = {
            'type': agent_type,
            'name': agent_type.upper(),
            'description': '',
            'features': []
        }
        
        if agent_type == 'database':
            info['description'] = 'Agente con base de datos integral usando SQLite completo'
            info['features'] = [
                '🗄️  Base de datos SQLite completa',
                '📊 Búsqueda semántica básica',
                '💾 Memoria persistente local',
                '📝 Historial de conversaciones',
                '🔍 Contexto semántico'
            ]
        elif agent_type == 'adk':
            info['description'] = 'Agente usando ADK InMemorySessionService'
            info['features'] = [
                '🔧 ADK InMemorySessionService',
                '🧠 Memoria persistente ADK',
                '🔍 Búsqueda en conversaciones',
                '📋 Gestión de sesiones ADK',
                '🛠️  Herramientas ADK integradas'
            ]
        elif agent_type == 'vertex':
            info['description'] = 'Agente con Vertex AI Memory Bank'
            info['features'] = [
                '☁️  Vertex AI Memory Bank',
                '🧠 Búsqueda semántica avanzada',
                '💾 Memoria persistente en Google Cloud',
                '🔄 Aprendizaje automático',
                '📊 Extracción inteligente de información'
            ]
            
            # Obtener información específica del servicio de memoria Vertex AI
            if hasattr(agent, 'get_memory_service_info'):
                memory_info = agent.get_memory_service_info()
                info['memory_service'] = memory_info
        
        return info
    
    def get_all_agents_info(self):
        """Obtener información de todos los agentes."""
        return {
            agent_type: self.get_agent_info(agent_type)
            for agent_type in self.agent_classes.keys()
        }

# Instancia global del gestor
agent_manager = AgentManager()

# Funciones de conveniencia
async def run_database_agent(user_id: str, message: str, session_id: str = None):
    """Ejecutar agente de base de datos."""
    agent_manager.select_agent('database')
    return await agent_manager.run_agent(user_id, message, session_id)

async def run_adk_agent(user_id: str, message: str, session_id: str = None):
    """Ejecutar agente ADK."""
    agent_manager.select_agent('adk')
    return await agent_manager.run_agent(user_id, message, session_id)

async def run_vertex_agent(user_id: str, message: str, session_id: str = None):
    """Ejecutar agente Vertex AI."""
    agent_manager.select_agent('vertex')
    return await agent_manager.run_agent(user_id, message, session_id)
