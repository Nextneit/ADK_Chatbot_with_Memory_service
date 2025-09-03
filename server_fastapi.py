#!/usr/bin/env python3
"""
Servidor FastAPI para el agente con memoria persistente.
"""

import os
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar nuestros módulos
# Solo importar el agente seleccionado para evitar logs innecesarios
selected_agent = os.getenv('SELECTED_AGENT', 'database')

if selected_agent == 'database':
    from multi_tool_agent.agents.database_agent import DatabaseAgent
    current_agent = DatabaseAgent()
elif selected_agent == 'adk':
    from multi_tool_agent.agents.adk_agent import ADKAgent
    current_agent = ADKAgent()
elif selected_agent == 'vertex':
    from multi_tool_agent.agents.vertex_agent import VertexAgent
    current_agent = VertexAgent()
else:
    from multi_tool_agent.agents.database_agent import DatabaseAgent
    current_agent = DatabaseAgent()

print(f"🤖 [SERVER] Agente seleccionado: {selected_agent.upper()}")

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Agente con Memoria Persistente", version="1.0.0")

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    memories_count: int

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página principal con interfaz de chat."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agente con Memoria Persistente</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; background: #fafafa; border-radius: 5px; margin-bottom: 15px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; margin-left: 20px; }
            .agent-message { background: #f3e5f5; margin-right: 20px; }
            .input-group { display: flex; gap: 10px; margin-bottom: 10px; }
            input, button { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            input { flex: 1; }
            button { background: #2196f3; color: white; border: none; cursor: pointer; }
            button:hover { background: #1976d2; }
            .memory-info { background: #fff3e0; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
            .status { margin: 5px 0; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Agente con Memoria Persistente</h1>
                <p>Tu agente recuerda conversaciones anteriores entre sesiones</p>
            </div>
            
            <div class="memory-info">
                <strong>🤖 Agente activo:</strong>
                <div id="agent-status">Verificando...</div>
                <strong>💾 Estado de la memoria:</strong>
                <div id="memory-status">Verificando...</div>
            </div>
            
            <div class="input-group">
                <input type="text" id="user-id" placeholder="Tu ID de usuario (ej: usuario123)" value="demo_user" onchange="clearSession()">
                <button onclick="loadMemories()">🔍 Ver Memorias</button>
            </div>
            
            <div id="chat-container" class="chat-container">
                <div class="message agent-message">
                    ¡Hola! Soy tu agente con memoria persistente. Puedo recordar información entre conversaciones. ¿En qué puedo ayudarte?
                </div>
            </div>
            
            <div class="input-group">
                <input type="text" id="message-input" placeholder="Escribe tu mensaje aquí..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">📤 Enviar</button>
            </div>
        </div>

        <script>
            async function loadMemories() {
                const userId = document.getElementById('user-id').value;
                if (!userId) {
                    alert('Por favor ingresa un ID de usuario');
                    return;
                }
                
                try {
                    // Cargar información del agente
                    const healthResponse = await fetch('/health');
                    const healthData = await healthResponse.json();
                    document.getElementById('agent-status').innerHTML = 
                        `${healthData.selected_agent.toUpperCase()} | ${healthData.agent_info.description}`;
                    
                    // Cargar información de memorias
                    const response = await fetch(`/memories/${userId}`);
                    const data = await response.json();
                    document.getElementById('memory-status').innerHTML = 
                        `Usuario: ${userId} | Agente: ${data.agent_type.toUpperCase()} | ${data.db_status}`;
                } catch (error) {
                    document.getElementById('memory-status').innerHTML = 'Error al cargar información';
                    document.getElementById('agent-status').innerHTML = 'Error al cargar agente';
                }
            }
            
            // Variable global para mantener session_id
            let currentSessionId = null;
            
            function clearSession() {
                currentSessionId = null;
                console.log('Session ID limpiado - nueva sesión iniciada');
            }
            
            async function sendMessage() {
                const userId = document.getElementById('user-id').value;
                const message = document.getElementById('message-input').value;
                
                if (!userId || !message) {
                    alert('Por favor ingresa usuario y mensaje');
                    return;
                }
                
                // Mostrar mensaje del usuario
                addMessage(message, 'user');
                document.getElementById('message-input').value = '';
                
                // Mostrar indicador de carga
                const loadingDiv = addMessage('🤔 Pensando...', 'agent');
                
                try {
                    const requestBody = { user_id: userId, message: message };
                    
                    // Incluir session_id si existe
                    if (currentSessionId) {
                        requestBody.session_id = currentSessionId;
                        console.log('Enviando session_id:', currentSessionId);
                    } else {
                        console.log('No hay session_id guardado');
                    }
                    
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody)
                    });
                    
                    const data = await response.json();
                    
                    // Remover indicador de carga
                    loadingDiv.remove();
                    
                    // Mostrar respuesta del agente
                    addMessage(data.response, 'agent');
                    
                    // Guardar session_id para futuras conversaciones
                    if (data.session_id) {
                        currentSessionId = data.session_id;
                        console.log('Session ID guardado:', currentSessionId);
                    }
                    
                    // Actualizar contador de memorias
                    document.getElementById('memory-status').innerHTML = 
                        `Usuario: ${userId} | Memorias: ${data.memories_count} | Última respuesta exitosa`;
                        
                } catch (error) {
                    loadingDiv.innerHTML = '❌ Error al comunicarse con el agente';
                    console.error('Error:', error);
                }
            }
            
            function addMessage(text, sender) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.innerHTML = `<strong>${sender === 'user' ? '👤 Tú' : '🤖 Agente'}:</strong> ${text}`;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }
            
            // Cargar memorias al iniciar
            window.onload = function() {
                loadMemories();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Endpoint principal de chat con memoria persistente."""
    
    # Debug: mostrar qué está recibiendo
    print(f"🔍 [SERVER] Recibido - user_id: {message.user_id}, session_id: {message.session_id}")
    
    # Obtener el agente seleccionado
    selected_agent = os.getenv('SELECTED_AGENT', 'database')
    
    # Verificar API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Respuesta sin LLM - solo memoria persistente
        session_id = message.session_id or f"session_{message.user_id}_{int(asyncio.get_event_loop().time())}"
        
        fallback_response = f"📝 He guardado tu mensaje. (Nota: API key no configurada para respuestas del LLM)"
        
        return ChatResponse(
            response=fallback_response,
            session_id=session_id,
            user_id=message.user_id,
            memories_count=0
        )
    
    try:
        # Ejecutar el agente seleccionado
        response, session_id = await current_agent.run(
            user_id=message.user_id,
            message=message.message,
            session_id=message.session_id
        )
        
        # Obtener información del agente actual
        agent_info = {
            "name": selected_agent.upper(),
            "type": selected_agent,
            "status": "active"
        }
        
        return ChatResponse(
            response=response or "Lo siento, no pude generar una respuesta.",
            session_id=session_id,
            user_id=message.user_id,
            memories_count=len(agent_info.get('features', [])) if agent_info else 0
        )
        
    except Exception as e:
        # En caso de error, generar respuesta de fallback
        session_id = message.session_id or f"session_{message.user_id}_{int(asyncio.get_event_loop().time())}"
        
        error_response = f"⚠️ Error procesando mensaje con agente {selected_agent}. Error: {str(e)[:100]}"
        
        return ChatResponse(
            response=error_response,
            session_id=session_id,
            user_id=message.user_id,
            memories_count=0
        )

@app.get("/memories/{user_id}")
async def get_memories(user_id: str):
    """Obtener todas las memorias de un usuario."""
    try:
        # Obtener información del agente actual
        selected_agent = os.getenv('SELECTED_AGENT', 'database')
        agent_info = {
            "name": selected_agent.upper(),
            "type": selected_agent,
            "status": "active"
        }
        
        return {
            "user_id": user_id,
            "agent_type": selected_agent,
            "agent_info": agent_info,
            "memories": [],  # Las memorias se manejan internamente en cada agente
            "db_status": f"Agente {selected_agent.upper()} activo"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memories: {str(e)}")

@app.get("/health")
async def health_check():
    """Verificar estado del sistema."""
    api_key = os.getenv('GOOGLE_API_KEY')
    selected_agent = os.getenv('SELECTED_AGENT', 'database')
    
    # Obtener información del agente actual
    agent_info = {
        "name": selected_agent.upper(),
        "type": selected_agent,
        "status": "active"
    }
    
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key),
        "selected_agent": selected_agent,
        "agent_info": agent_info,
        "available_agents": ["database", "adk", "vertex"]
    }

@app.get("/debug/{user_id}")
async def debug_memory(user_id: str):
    """Debug detallado del sistema de memoria del agente activo."""
    
    # Obtener el agente activo
    selected_agent = os.environ.get('SELECTED_AGENT', 'database')
    agent = current_agent
    
    if not agent:
        return {"error": f"Agente '{selected_agent}' no disponible"}
    
    # Obtener información del agente
    agent_info = {
        "name": selected_agent.upper(),
        "type": selected_agent,
        "status": "active"
    }
    
    # Información específica del agente
    debug_info = {
        "user_id": user_id,
        "active_agent": selected_agent,
        "agent_info": agent_info,
        "timestamp": datetime.now().isoformat()
    }
    
    # Información específica según el tipo de agente
    if selected_agent == "database":
        # Para Database Agent, verificar la base de datos personalizada
        import sqlite3
        db_path = "database_agent_sessions.db"
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            
            # Contar registros en tablas personalizadas
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM user_memories WHERE user_id = ?", (user_id,))
                memory_count = cursor.fetchone()[0]
            except:
                memory_count = 0
                
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM conversation_log WHERE user_id = ?", (user_id,))
                conversation_count = cursor.fetchone()[0]
            except:
                conversation_count = 0
            
            # Obtener últimas conversaciones
            try:
                cursor = conn.execute("""
                    SELECT role, content, timestamp, session_id 
                    FROM conversation_log 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """, (user_id,))
                recent_conversations = cursor.fetchall()
            except:
                recent_conversations = []
            
            conn.close()
            
            debug_info.update({
                "database_path": db_path,
                "memory_count": memory_count,
                "conversation_count": conversation_count,
                "recent_conversations": [
                    {"role": row[0], "content": row[1][:100], "timestamp": row[2], "session_id": row[3]}
                    for row in recent_conversations
                ],
                "db_file_size": os.path.getsize(db_path) if os.path.exists(db_path) else 0
            })
        else:
            debug_info["database_path"] = db_path
            debug_info["status"] = "Base de datos no encontrada"
    
    elif selected_agent in ["adk", "vertex"]:
        # Para ADK y Vertex agents, verificar la base de datos ADK
        import sqlite3
        db_path = f"{selected_agent}_agent_sessions.db"
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            
            # Verificar tablas ADK
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
                session_count = cursor.fetchone()[0]
            except:
                session_count = 0
                
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
                message_count = cursor.fetchone()[0]
            except:
                message_count = 0
            
            # Obtener últimas sesiones (usando esquema correcto ADK)
            try:
                cursor = conn.execute("""
                    SELECT id, app_name, create_time 
                    FROM sessions 
                    WHERE user_id = ? 
                    ORDER BY create_time DESC 
                    LIMIT 5
                """, (user_id,))
                recent_sessions = cursor.fetchall()
            except:
                recent_sessions = []
            
            # Obtener mensajes recientes con contenido (usando esquema correcto ADK)
            try:
                cursor = conn.execute("""
                    SELECT m.session_id, m.role, m.content, m.create_time, s.app_name
                    FROM messages m
                    LEFT JOIN sessions s ON m.session_id = s.id
                    WHERE m.user_id = ? 
                    ORDER BY m.create_time DESC 
                    LIMIT 10
                """, (user_id,))
                recent_messages = cursor.fetchall()
            except Exception as e:
                recent_messages = []
                debug_info["message_error"] = str(e)
            
            # Obtener mensajes por sesión (últimas 3 sesiones)
            try:
                cursor = conn.execute("""
                    SELECT session_id, COUNT(*) as message_count
                    FROM messages 
                    WHERE user_id = ? 
                    GROUP BY session_id 
                    ORDER BY MAX(create_time) DESC 
                    LIMIT 3
                """, (user_id,))
                sessions_with_counts = cursor.fetchall()
                
                # Para cada sesión, obtener los mensajes
                session_messages = {}
                for session_id, _ in sessions_with_counts:
                    cursor = conn.execute("""
                        SELECT role, content, create_time
                        FROM messages 
                        WHERE user_id = ? AND session_id = ?
                        ORDER BY create_time ASC
                    """, (user_id, session_id))
                    session_messages[session_id] = [
                        {"role": row[0], "content": row[1][:200], "timestamp": row[2]}
                        for row in cursor.fetchall()
                    ]
            except Exception as e:
                session_messages = {}
                debug_info["session_messages_error"] = str(e)
            
            # Verificar si hay memoria almacenada (usando esquema correcto ADK)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM memory WHERE user_id = ?", (user_id,))
                memory_count = cursor.fetchone()[0]
                
                # Obtener memoria reciente
                cursor = conn.execute("""
                    SELECT id, content, create_time
                    FROM memory 
                    WHERE user_id = ? 
                    ORDER BY create_time DESC 
                    LIMIT 5
                """, (user_id,))
                recent_memory = cursor.fetchall()
            except:
                memory_count = 0
                recent_memory = []
            
            conn.close()
            
            debug_info.update({
                "database_path": db_path,
                "session_count": session_count,
                "message_count": message_count,
                "memory_count": memory_count,
                "recent_sessions": [
                    {"session_id": row[0], "app_name": row[1], "create_time": row[2]}
                    for row in recent_sessions
                ],
                "recent_messages": [
                    {
                        "session_id": row[0], 
                        "role": row[1], 
                        "content": row[2][:300] + "..." if len(row[2]) > 300 else row[2],
                        "create_time": row[3],
                        "app_name": row[4]
                    }
                    for row in recent_messages
                ],
                "session_messages": session_messages,
                "recent_memory": [
                    {"id": row[0], "content": row[1][:200], "create_time": row[2]}
                    for row in recent_memory
                ],
                "db_file_size": os.path.getsize(db_path) if os.path.exists(db_path) else 0
            })
        else:
            debug_info["database_path"] = db_path
            debug_info["status"] = "Base de datos no encontrada"
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 INICIANDO SERVIDOR FASTAPI CON MEMORIA PERSISTENTE")
    print("=" * 60)
    print("🌐 Interfaz web: http://localhost:8000")
    print("📋 API docs: http://localhost:8000/docs")
    print("💾 Memoria persistente: ACTIVADA")
    print("🔄 Presiona Ctrl+C para detener")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
