#!/usr/bin/env python3
"""
Script para limpiar bases de datos problemáticas.
"""

import os
import glob

def cleanup_databases():
    """Eliminar bases de datos problemáticas."""
    db_files = [
        "database_agent_sessions.db",
        "database_agent_adk_sessions.db", 
        "adk_agent_sessions.db",
        "vertex_agent_sessions.db",
        "agent_sessions.db",
        "adk_sessions.db"
    ]
    
    print("🧹 Limpiando bases de datos problemáticas...")
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✅ Eliminado: {db_file}")
            except Exception as e:
                print(f"⚠️  No se pudo eliminar {db_file}: {e}")
        else:
            print(f"ℹ️  No existe: {db_file}")
    
    print("🎉 Limpieza completada")

if __name__ == "__main__":
    cleanup_databases()