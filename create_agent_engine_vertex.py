#!/usr/bin/env python3
"""
Script para crear un Agent Engine en Vertex AI para usar con VertexAiMemoryBankService.
Basado en la documentación oficial del ADK.
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_agent_engine_vertex():
    """Crear un Agent Engine en Vertex AI para VertexAiMemoryBankService."""
    
    # Verificar variables de entorno
    project_id = "proyect-470810"
    location = "us-central1"
    
    print(f"🚀 Creando Agent Engine en Vertex AI...")
    print(f"   Proyecto: {project_id}")
    print(f"   Ubicación: {location}")
    
    try:
        from google import genai
        
        # Crear cliente con autenticación OAuth2
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        
        # Crear Agent Engine usando la API según la documentación oficial
        response = client._api_client.request(
            http_method='POST',
            path='reasoningEngines',
            request_dict={
                "displayName": "ADK Memory Agent Engine",
                "description": "Agent Engine para el sistema de memoria ADK con Vertex AI"
            }
        )
        
        # Extraer información del Agent Engine
        agent_engine_name = response['name']
        app_name = "/".join(agent_engine_name.split("/")[:6])
        app_id = app_name.split('/')[-1]
        
        print(f"✅ Agent Engine creado exitosamente!")
        print(f"   Nombre: {response.get('displayName', 'N/A')}")
        print(f"   ID: {app_id}")
        print(f"   Nombre completo: {agent_engine_name}")
        
        # Actualizar archivo .env con el nuevo AGENT_ENGINE_ID
        env_file = ".env"
        if os.path.exists(env_file):
            # Leer archivo .env actual
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Actualizar o agregar AGENT_ENGINE_ID
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("AGENT_ENGINE_ID="):
                    lines[i] = f"AGENT_ENGINE_ID={app_id}\n"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"AGENT_ENGINE_ID={app_id}\n")
            
            # Escribir archivo .env actualizado
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ Archivo .env actualizado con AGENT_ENGINE_ID={app_id}")
        else:
            print(f"⚠️  Archivo .env no encontrado. Agrega manualmente:")
            print(f"   AGENT_ENGINE_ID={app_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando Agent Engine: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

def main():
    """Función principal."""
    print("=" * 60)
    print("🏗️  CREADOR DE AGENT ENGINE PARA VERTEX AI MEMORY BANK")
    print("=" * 60)
    print("Basado en la documentación oficial del ADK")
    
    # Verificar que las dependencias estén instaladas
    try:
        import google.genai
    except ImportError:
        print("❌ Error: google-genai no está instalado")
        print("   Ejecuta: pip install google-genai")
        return
    
    try:
        from google.adk.memory import VertexAiMemoryBankService
    except ImportError:
        print("❌ Error: google-adk[vertexai] no está instalado")
        print("   Ejecuta: pip install google-adk[vertexai]")
        return
    
    # Crear Agent Engine
    success = create_agent_engine_vertex()
    
    if success:
        print("\n🎉 ¡Configuración completada!")
        print("   Ahora puedes usar VertexAiMemoryBankService")
        print("   Ejecuta: python test_vertex_agent_memory.py")
    else:
        print("\n❌ Configuración fallida")
        print("   Revisa los errores anteriores")

if __name__ == "__main__":
    main()
