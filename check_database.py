#!/usr/bin/env python3
"""
Script para verificar el contenido de las bases de datos del agente.
Versión mejorada con mejor visualización y organización de datos.
"""

import sqlite3
import os
from datetime import datetime
import textwrap

# Colores para la terminal (ANSI escape codes)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(title):
    """Imprimir un encabezado con formato."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}")

def print_section(title):
    """Imprimir una sección con formato."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}📋 {title}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * (len(title) + 4)}{Colors.END}")

def print_table_info(table_name, count, columns=None):
    """Imprimir información de una tabla."""
    print(f"{Colors.CYAN}📊 {table_name}: {Colors.BOLD}{count}{Colors.END} registros")
    if columns:
        print(f"   Columnas: {', '.join(columns)}")

def format_timestamp(timestamp):
    """Formatear timestamp para mejor legibilidad."""
    if timestamp:
        try:
            # Intentar parsear diferentes formatos de timestamp
            if isinstance(timestamp, str):
                # Si es string, intentar parsear
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        return dt.strftime('%d/%m/%Y %H:%M')
                    except ValueError:
                        continue
            return str(timestamp)
        except:
            return str(timestamp)
    return "N/A"

def truncate_text(text, max_length=80):
    """Truncar texto largo para mejor visualización."""
    if not text:
        return "N/A"
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def print_memory_item(memory, index):
    """Imprimir un item de memoria con formato mejorado."""
    user_id, key, value, timestamp = memory
    print(f"{Colors.YELLOW}   {index}. {Colors.BOLD}{user_id}{Colors.END}")
    print(f"      🔑 Clave: {Colors.CYAN}{key}{Colors.END}")
    print(f"      💭 Valor: {Colors.GREEN}{truncate_text(value, 100)}{Colors.END}")
    print(f"      ⏰ Fecha: {Colors.BLUE}{format_timestamp(timestamp)}{Colors.END}")

def print_conversation_log(log, index):
    """Imprimir un log de conversación con formato mejorado."""
    user_id, role, content, timestamp = log
    role_emoji = "👤" if role == "user" else "🤖"
    print(f"{Colors.YELLOW}   {index}. {role_emoji} {Colors.BOLD}{user_id}{Colors.END} ({role})")
    print(f"      💬 Mensaje: {Colors.GREEN}{truncate_text(content, 120)}{Colors.END}")
    print(f"      ⏰ Fecha: {Colors.BLUE}{format_timestamp(timestamp)}{Colors.END}")

def print_session_item(session, columns, index):
    """Imprimir un item de sesión con formato mejorado."""
    print(f"{Colors.YELLOW}   {index}. Sesión {index}{Colors.END}")
    for i, value in enumerate(session):
        if i < len(columns):
            col_name = columns[i]
            formatted_value = truncate_text(value, 80)
            print(f"      {Colors.CYAN}{col_name}:{Colors.END} {Colors.GREEN}{formatted_value}{Colors.END}")

def print_event_item(event, columns, index):
    """Imprimir un item de evento con formato mejorado."""
    print(f"{Colors.YELLOW}   {index}. Evento {index}{Colors.END}")
    for i, value in enumerate(event):
        if i < len(columns):
            col_name = columns[i]
            formatted_value = truncate_text(value, 80)
            print(f"      {Colors.CYAN}{col_name}:{Colors.END} {Colors.GREEN}{formatted_value}{Colors.END}")

def check_agent_sessions_db():
    """Verificar la base de datos de memorias personales."""
    db_path = "agent_sessions.db"
    
    if not os.path.exists(db_path):
        print(f"{Colors.RED}❌ {db_path} no existe{Colors.END}")
        return
    
    print_header(f"🔍 VERIFICANDO {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print_section("TABLAS ENCONTRADAS")
        if table_names:
            for table in table_names:
                print(f"   📋 {Colors.GREEN}{table}{Colors.END}")
        else:
            print(f"   {Colors.YELLOW}⚠️  No se encontraron tablas{Colors.END}")
        
        # Verificar user_memories
        if 'user_memories' in table_names:
            print_section("MEMORIAS PERSONALES")
            cursor.execute("SELECT COUNT(*) FROM user_memories")
            count = cursor.fetchone()[0]
            print_table_info("user_memories", count)
            
            if count > 0:
                cursor.execute("SELECT user_id, key, value, timestamp FROM user_memories ORDER BY timestamp DESC LIMIT 5")
                memories = cursor.fetchall()
                print(f"\n{Colors.BOLD}📝 Últimas 5 memorias:{Colors.END}")
                for i, memory in enumerate(memories, 1):
                    print_memory_item(memory, i)
                    if i < len(memories):
                        print()  # Espacio entre items
        
        # Verificar conversation_log
        if 'conversation_log' in table_names:
            print_section("LOGS DE CONVERSACIÓN")
            cursor.execute("SELECT COUNT(*) FROM conversation_log")
            count = cursor.fetchone()[0]
            print_table_info("conversation_log", count)
            
            if count > 0:
                cursor.execute("SELECT user_id, role, content, timestamp FROM conversation_log ORDER BY timestamp DESC LIMIT 5")
                logs = cursor.fetchall()
                print(f"\n{Colors.BOLD}📝 Últimos 5 logs:{Colors.END}")
                for i, log in enumerate(logs, 1):
                    print_conversation_log(log, i)
                    if i < len(logs):
                        print()  # Espacio entre items
        
        conn.close()
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error verificando {db_path}: {e}{Colors.END}")

def check_adk_sessions_db():
    """Verificar la base de datos de sesiones ADK."""
    db_path = "adk_sessions.db"
    
    if not os.path.exists(db_path):
        print(f"{Colors.RED}❌ {db_path} no existe{Colors.END}")
        return
    
    print_header(f"🔍 VERIFICANDO {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print_section("TABLAS ENCONTRADAS")
        if table_names:
            for table in table_names:
                print(f"   📋 {Colors.GREEN}{table}{Colors.END}")
        else:
            print(f"   {Colors.YELLOW}⚠️  No se encontraron tablas{Colors.END}")
        
        # Verificar sesiones ADK
        if 'sessions' in table_names:
            print_section("SESIONES ADK")
            cursor.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            print_table_info("sessions", count)
            
            if count > 0:
                # Obtener estructura de la tabla
                cursor.execute("PRAGMA table_info(sessions)")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Mostrar muestra de sesiones
                cursor.execute("SELECT * FROM sessions ORDER BY ROWID DESC LIMIT 3")
                sessions = cursor.fetchall()
                print(f"\n{Colors.BOLD}📝 Muestra de las últimas 3 sesiones:{Colors.END}")
                for i, session in enumerate(sessions, 1):
                    print_session_item(session, columns, i)
                    if i < len(sessions):
                        print()  # Espacio entre items
        
        # Verificar eventos
        if 'events' in table_names:
            print_section("EVENTOS")
            cursor.execute("SELECT COUNT(*) FROM events")
            count = cursor.fetchone()[0]
            print_table_info("events", count)
            
            if count > 0:
                # Obtener estructura de la tabla
                cursor.execute("PRAGMA table_info(events)")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Mostrar muestra de eventos
                cursor.execute("SELECT * FROM events ORDER BY ROWID DESC LIMIT 3")
                events = cursor.fetchall()
                print(f"\n{Colors.BOLD}📝 Muestra de los últimos 3 eventos:{Colors.END}")
                for i, event in enumerate(events, 1):
                    print_event_item(event, columns, i)
                    if i < len(events):
                        print()  # Espacio entre items
        
        # Verificar otras tablas importantes
        other_tables = ['adk_sessions', 'adk_messages', 'app_states', 'user_states', 'user_preferences', 'system_config']
        found_tables = [table for table in other_tables if table in table_names]
        
        if found_tables:
            print_section("OTRAS TABLAS")
            for table_name in found_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print_table_info(table_name, count)
                except Exception as e:
                    print(f"{Colors.RED}   ❌ Error en {table_name}: {e}{Colors.END}")
        
        conn.close()
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error verificando {db_path}: {e}{Colors.END}")

def print_summary():
    """Imprimir resumen final."""
    print_header("📊 RESUMEN DE VERIFICACIÓN")
    print(f"{Colors.GREEN}✅ Verificación de bases de datos completada{Colors.END}")
    print(f"{Colors.CYAN}💡 Usa este script para monitorear el estado de tus bases de datos{Colors.END}")

def main():
    """Función principal."""
    print_header("🔍 VERIFICADOR DE BASES DE DATOS DEL AGENTE")
    print(f"{Colors.CYAN}Versión mejorada con mejor visualización y organización{Colors.END}")
    
    # Verificar ambas bases de datos
    check_agent_sessions_db()
    check_adk_sessions_db()
    
    # Resumen final
    print_summary()

if __name__ == "__main__":
    main()
