#!/usr/bin/env python3
"""
Script principal para iniciar el agente web con memoria persistente.
Puedes elegir entre FastAPI (recomendado) o ADK Web.
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
    
    # 2. Verificar base de datos
    from multi_tool_agent.agent_simple import persistent_memory
    try:
        # Probar conexión a BD
        memories = persistent_memory.get_memories("test_connection")
        print(f"✅ Base de datos funcionando: {persistent_memory.db_path}")
    except Exception as e:
        print(f"⚠️  Advertencia con BD: {e}")
    
    # 3. Verificar dependencias
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI disponible")
    except ImportError:
        print("⚠️  FastAPI no disponible, instala con: pip install fastapi uvicorn")
    
    return True

def start_fastapi_server(host="localhost", port=8000):
    """Iniciar servidor FastAPI (recomendado)."""
    print(f"🚀 Iniciando servidor FastAPI en {host}:{port}")
    
    try:
        import subprocess
        import sys
        
        # Ejecutar el servidor FastAPI directamente
        result = subprocess.run([
            sys.executable, "server_fastapi.py"
        ], check=True)
        
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
    parser.add_argument("--server", choices=["fastapi", "adk"], default="fastapi",
                       help="Tipo de servidor (default: fastapi)")
    parser.add_argument("--host", default="localhost", help="Host del servidor")
    parser.add_argument("--port", type=int, help="Puerto del servidor")
    parser.add_argument("--check", action="store_true", help="Solo verificar configuración")
    
    args = parser.parse_args()
    
    # Verificar configuración
    if not check_requirements():
        print("\n❌ Configuración incompleta. Corrígela antes de continuar.")
        return 1
    
    if args.check:
        print("\n✅ Configuración correcta. El servidor puede iniciarse.")
        return 0
    
    # Configurar puerto por defecto según servidor
    if args.port is None:
        args.port = 8000 if args.server == "fastapi" else 8080
    
    print(f"\n🎯 Iniciando servidor {args.server.upper()}")
    print("=" * 50)
    
    if args.server == "fastapi":
        success = start_fastapi_server(args.host, args.port)
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
