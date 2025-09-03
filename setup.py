#!/usr/bin/env python3
"""
Script de configuración rápida para ADK Memory.
Guía al usuario paso a paso para configurar el sistema.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Imprimir encabezado del script."""
    print("=" * 60)
    print("🚀 CONFIGURACIÓN RÁPIDA - ADK MEMORY")
    print("=" * 60)
    print("Este script te guiará paso a paso para configurar tu agente.")
    print()

def check_python_version():
    """Verificar versión de Python."""
    print("🔍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_venv():
    """Verificar si está en un entorno virtual."""
    print("\n🔍 Verificando entorno virtual...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Entorno virtual activo - OK")
        return True
    else:
        print("⚠️  No estás en un entorno virtual")
        print("   Recomendación: Crear y activar un entorno virtual")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
        return False

def install_dependencies():
    """Instalar dependencias."""
    print("\n📦 Instalando dependencias...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_env_file():
    """Crear archivo .env si no existe."""
    print("\n📝 Configurando archivo .env...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    # Copiar desde env.example
    example_file = Path("env.example")
    if example_file.exists():
        with open(example_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo .env creado desde env.example")
        print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales")
        return True
    else:
        print("❌ No se encontró env.example")
        return False

def select_agent():
    """Permitir al usuario seleccionar el agente."""
    print("\n🤖 Selección de agente:")
    print("1. Database Agent (SQLite) - Fácil, memoria local")
    print("2. ADK Agent (ADK Database) - Intermedio, memoria ADK")
    print("3. Vertex Agent (Vertex AI) - Avanzado, memoria en la nube")
    
    while True:
        choice = input("\nSelecciona un agente (1-3): ").strip()
        if choice == "1":
            return "database"
        elif choice == "2":
            return "adk"
        elif choice == "3":
            return "vertex"
        else:
            print("❌ Opción inválida. Selecciona 1, 2 o 3.")

def configure_agent(agent_type):
    """Configurar el agente seleccionado."""
    print(f"\n🔧 Configurando {agent_type.upper()} Agent...")
    
    if agent_type == "database":
        print("📋 Para Database Agent necesitas:")
        print("   1. API Key de Google AI Studio")
        print("   2. Obtener en: https://makersuite.google.com/app/apikey")
        print("   3. Agregar a .env: GOOGLE_API_KEY=tu_api_key")
        
    elif agent_type == "adk":
        print("📋 Para ADK Agent necesitas:")
        print("   1. API Key de Google AI Studio")
        print("   2. Obtener en: https://makersuite.google.com/app/apikey")
        print("   3. Agregar a .env: GOOGLE_API_KEY=tu_api_key")
        
    elif agent_type == "vertex":
        print("📋 Para Vertex Agent necesitas:")
        print("   1. Proyecto de Google Cloud")
        print("   2. Google Cloud SDK instalado")
        print("   3. APIs habilitadas")
        print("   4. Agent Engine creado")
        print("\n🚀 Ejecuta: python create_agent_engine_vertex.py")
        print("   Este script te guiará paso a paso")

def update_env_agent(agent_type):
    """Actualizar .env con el agente seleccionado."""
    env_file = Path(".env")
    if not env_file.exists():
        return
    
    # Leer archivo actual
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Actualizar SELECTED_AGENT
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("SELECTED_AGENT="):
            lines[i] = f"SELECTED_AGENT={agent_type}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"SELECTED_AGENT={agent_type}\n")
    
    # Escribir archivo actualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ SELECTED_AGENT={agent_type} configurado en .env")

def test_configuration():
    """Probar la configuración."""
    print("\n🧪 Probando configuración...")
    try:
        result = subprocess.run([sys.executable, "start_web.py", "--check"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Configuración correcta")
            return True
        else:
            print("❌ Error en la configuración:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def main():
    """Función principal."""
    print_header()
    
    # Verificaciones básicas
    if not check_python_version():
        return 1
    
    check_venv()
    
    # Instalar dependencias
    if not install_dependencies():
        return 1
    
    # Crear archivo .env
    if not create_env_file():
        return 1
    
    # Seleccionar agente
    agent_type = select_agent()
    configure_agent(agent_type)
    update_env_agent(agent_type)
    
    # Probar configuración
    if test_configuration():
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print(f"✅ {agent_type.upper()} Agent configurado")
        print("\n🚀 Para iniciar el servidor:")
        print(f"   python start_web.py --agent {agent_type}")
        print("\n🌐 Accede a: http://localhost:8000")
    else:
        print("\n❌ Configuración incompleta")
        print("   Revisa los errores anteriores y configura manualmente")
        print("   Consulta README.md para más detalles")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Configuración cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
