#!/usr/bin/env python3
"""
Script principal para iniciar el agente web con memoria persistente.
Puedes elegir entre diferentes tipos de agentes y servidores.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

def check_requirements():
    """Verificar que todo esté configurado correctamente."""
    print("🔍 Verificando configuración...")
    
    # 1. Verificar API key
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: No se encontró GOOGLE_API_KEY")
        print("📋 Solución:")
        print("   1. Crea un archivo .env en la raíz del proyecto")
        print("   2. Agrega: GOOGLE_API_KEY=tu_api_key_aqui")
        print("   3. Obtén tu API key en: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✅ API Key configurada: {api_key[:10]}...{api_key[-4:]}")
    
    # 2. Verificar agentes disponibles (sin inicializar)
    try:
        # Importar solo las clases sin inicializar
        from multi_tool_agent.agents.database_agent import DatabaseAgent
        from multi_tool_agent.agents.adk_agent import ADKAgent
        from multi_tool_agent.agents.vertex_agent import VertexAgent
        
        available_agents = ["database", "adk", "vertex"]
        print(f"✅ Agentes disponibles: {', '.join(available_agents)}")
    except Exception as e:
        print(f"⚠️  Error verificando agentes: {e}")
    
    # 3. Verificar dependencias
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI disponible")
    except ImportError:
        print("⚠️  FastAPI no disponible, instala con: pip install fastapi uvicorn")
    
    return True

def start_fastapi_server(host="localhost", port=8000, selected_agent="database"):
    """Iniciar servidor FastAPI (recomendado)."""
    print(f"🚀 Iniciando servidor FastAPI en {host}:{port}")
    print(f"🤖 Agente seleccionado: {selected_agent.upper()}")
    
    try:
        import subprocess
        import sys
        
        # Configurar variable de entorno para el agente seleccionado
        env = os.environ.copy()
        env['SELECTED_AGENT'] = selected_agent
        
        # Ejecutar el servidor FastAPI directamente
        result = subprocess.run([
            sys.executable, "server_fastapi.py"
        ], check=True, env=env)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error iniciando FastAPI: {e}")
        return False

def start_adk_web_server(host="localhost", port=8080):
    """Iniciar servidor ADK Web (alternativo)."""
    print(f"🌐 Iniciando servidor ADK Web en {host}:{port}")
    
    try:
        import subprocess
        import sys
        
        # Ejecutar el servidor ADK directamente
        result = subprocess.run([
            sys.executable, "server_adk.py", "--host", host, "--port", str(port)
        ], check=True)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error iniciando ADK Web: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Iniciar agente web con memoria persistente")
    parser.add_argument("--agent", choices=["database", "adk", "vertex"], default="database",
                       help="Tipo de agente (default: database)")
    parser.add_argument("--server", choices=["fastapi", "adk"], default="fastapi",
                       help="Tipo de servidor (default: fastapi)")
    parser.add_argument("--host", default="localhost", help="Host del servidor")
    parser.add_argument("--port", type=int, help="Puerto del servidor")
    parser.add_argument("--check", action="store_true", help="Solo verificar configuración")
    parser.add_argument("--info", action="store_true", help="Mostrar información de agentes disponibles")
    
    args = parser.parse_args()
    
    # Verificar configuración
    if not check_requirements():
        print("\n❌ Configuración incompleta. Corrígela antes de continuar.")
        return 1
    
    if args.check:
        print("\n✅ Configuración correcta. El servidor puede iniciarse.")
        return 0
    
    if args.info:
        try:
            from multi_tool_agent.agent_manager import agent_manager
            print("\n📋 INFORMACIÓN DE AGENTES DISPONIBLES")
            print("=" * 50)
            
            all_info = agent_manager.get_all_agents_info()
            for agent_type, info in all_info.items():
                print(f"\n🤖 {info['name']} AGENT")
                print(f"   📝 {info['description']}")
                print("   ✨ Características:")
                for feature in info['features']:
                    print(f"      {feature}")
                
                if 'memory_service' in info:
                    print(f"   🧠 Servicio de Memoria: {info['memory_service']['type']}")
                    print(f"   📊 Estado: {info['memory_service']['status']}")
            
            print("\n" + "=" * 50)
            return 0
        except Exception as e:
            print(f"❌ Error mostrando información: {e}")
            return 1
    
    # Configurar puerto por defecto según servidor
    if args.port is None:
        args.port = 8000 if args.server == "fastapi" else 8080
    
    print(f"\n🎯 Iniciando agente {args.agent.upper()} con servidor {args.server.upper()}")
    print("=" * 50)
    
    # Configurar variable de entorno para el agente seleccionado
    os.environ['SELECTED_AGENT'] = args.agent
    
    if args.server == "fastapi":
        success = start_fastapi_server(args.host, args.port, args.agent)
    else:
        success = start_adk_web_server(args.host, args.port)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
