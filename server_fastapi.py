#!/usr/bin/env python3
"""
Servidor FastAPI para el agente con memoria persistente.
"""

import os
import asyncio
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar nuestros módulos
from multi_tool_agent.agent_simple import persistent_memory, run_with_persistent_memory, get_memory_service_info

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
                <strong>💾 Estado de la memoria:</strong>
                <div id="memory-status">Verificando...</div>
            </div>
            
            <div class="input-group">
                <input type="text" id="user-id" placeholder="Tu ID de usuario (ej: usuario123)" value="demo_user">
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
                    const response = await fetch(`/memories/${userId}`);
                    const data = await response.json();
                    document.getElementById('memory-status').innerHTML = 
                        `Usuario: ${userId} | Memorias: ${data.memories.length} | BD: ${data.db_status}`;
                } catch (error) {
                    document.getElementById('memory-status').innerHTML = 'Error al cargar memorias';
                }
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
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, message: message })
                    });
                    
                    const data = await response.json();
                    
                    // Remover indicador de carga
                    loadingDiv.remove();
                    
                    // Mostrar respuesta del agente
                    addMessage(data.response, 'agent');
                    
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
    
    # Verificar API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Respuesta sin LLM - solo memoria persistente
        session_id = message.session_id or f"session_{message.user_id}_{int(asyncio.get_event_loop().time())}"
        
        # Guardar mensaje en memoria
        persistent_memory.log_conversation(message.user_id, session_id, "user", message.message)
        
        fallback_response = f"📝 He guardado tu mensaje. (Nota: API key no configurada para respuestas del LLM)"
        persistent_memory.log_conversation(message.user_id, session_id, "agent", fallback_response)
        
        memories = persistent_memory.get_memories(message.user_id)
        
        return ChatResponse(
            response=fallback_response,
            session_id=session_id,
            user_id=message.user_id,
            memories_count=len(memories)
        )
    
    try:
        # Ejecutar agente con memoria persistente
        response, session_id = await run_with_persistent_memory(
            user_id=message.user_id,
            message=message.message,
            session_id=message.session_id
        )
        
        # Contar memorias actuales
        memories = persistent_memory.get_memories(message.user_id)
        
        return ChatResponse(
            response=response or "Lo siento, no pude generar una respuesta.",
            session_id=session_id,
            user_id=message.user_id,
            memories_count=len(memories)
        )
        
    except Exception as e:
        # En caso de error, al menos guardar el mensaje
        session_id = message.session_id or f"session_{message.user_id}_{int(asyncio.get_event_loop().time())}"
        persistent_memory.log_conversation(message.user_id, session_id, "user", message.message)
        
        error_response = f"⚠️ Error procesando mensaje, pero he guardado tu información. Error: {str(e)[:100]}"
        persistent_memory.log_conversation(message.user_id, session_id, "agent", error_response)
        
        memories = persistent_memory.get_memories(message.user_id)
        
        return ChatResponse(
            response=error_response,
            session_id=session_id,
            user_id=message.user_id,
            memories_count=len(memories)
        )

@app.get("/memories/{user_id}")
async def get_memories(user_id: str):
    """Obtener todas las memorias de un usuario."""
    try:
        memories = persistent_memory.get_memories(user_id)
        
        # Convertir a formato JSON-friendly
        memory_list = []
        for key, value, timestamp in memories:
            memory_list.append({
                "key": key,
                "value": value,
                "timestamp": timestamp
            })
        
        return {
            "user_id": user_id,
            "memories": memory_list,
            "db_status": f"{os.path.getsize(persistent_memory.db_path)} bytes" if os.path.exists(persistent_memory.db_path) else "No existe"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memories: {str(e)}")

@app.get("/health")
async def health_check():
    """Verificar estado del sistema."""
    api_key = os.getenv('GOOGLE_API_KEY')
    db_exists = os.path.exists(persistent_memory.db_path)
    
    # Obtener información del servicio de memoria (ADK + Vertex AI)
    memory_info = get_memory_service_info()
    
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key),
        "database_exists": db_exists,
        "database_path": persistent_memory.db_path,
        "memory_service": memory_info["type"],
        "memory_features": memory_info["features"],
        "memory_status": memory_info["status"]
    }

@app.get("/debug/{user_id}")
async def debug_memory(user_id: str):
    """Debug detallado del sistema de memoria."""
    
    # 1. Verificar memoria SQLite
    sqlite_memories = persistent_memory.get_memories(user_id)
    
    # 2. Verificar base de datos directamente
    import sqlite3
    db_info = {}
    if os.path.exists(persistent_memory.db_path):
        conn = sqlite3.connect(persistent_memory.db_path)
        
        # Contar registros
        cursor = conn.execute("SELECT COUNT(*) FROM user_memories WHERE user_id = ?", (user_id,))
        memory_count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM conversation_log WHERE user_id = ?", (user_id,))
        conversation_count = cursor.fetchone()[0]
        
        # Obtener últimas 5 conversaciones
        cursor = conn.execute("""
            SELECT role, content, timestamp, session_id 
            FROM conversation_log 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        """, (user_id,))
        recent_conversations = cursor.fetchall()
        
        conn.close()
        
        db_info = {
            "memory_count": memory_count,
            "conversation_count": conversation_count,
            "recent_conversations": [
                {"role": row[0], "content": row[1][:100], "timestamp": row[2], "session_id": row[3]}
                for row in recent_conversations
            ]
        }
    
    # 3. Simular cómo ve las memorias el LLM
    memories = persistent_memory.get_memories(user_id)
    memory_context = ""
    if memories:
        memory_context = "\n--- MEMORIA PERSISTENTE ---\n"
        for key, value, timestamp in memories:
            memory_context += f"- {key}: {value} (guardado: {timestamp})\n"
        memory_context += "--- FIN MEMORIA ---\n\n"
    
    # Obtener información del servicio de memoria ADK + Vertex AI
    memory_info = get_memory_service_info()
    
    return {
        "user_id": user_id,
        "sqlite_memories": [{"key": m[0], "value": m[1], "timestamp": m[2]} for m in sqlite_memories],
        "db_stats": db_info,
        "memory_context_for_llm": memory_context,
        "db_file_size": os.path.getsize(persistent_memory.db_path) if os.path.exists(persistent_memory.db_path) else 0,
        "total_memories": len(sqlite_memories),
        "memory_service_info": memory_info
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 INICIANDO SERVIDOR FASTAPI CON MEMORIA PERSISTENTE")
    print("=" * 60)
    print("🌐 Interfaz web: http://localhost:8000")
    print("📋 API docs: http://localhost:8000/docs")
    print("💾 Memoria persistente: ACTIVADA")
    print("🔄 Presiona Ctrl+C para detener")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
