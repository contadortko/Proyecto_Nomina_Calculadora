import os
import glob

print("🚀 Iniciando Mapeo y Renombrado de Módulos (Mejores Prácticas MVC)...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diccionario de Reestructuración (Nombres más coherentes y escalables)
RENAMES = {
    # Módulos Visuales (UI)
    "src/ui/calculadora.py": "src/ui/calculadora_individual.py",
    "src/ui/consulta_legal.py": "src/ui/agente_juridico.py",
    "src/ui/tablas_informativas.py": "src/ui/indicadores_macro.py",
    
    # Motores Aritméticos (Core)
    "src/core/formulas_nomina.py": "src/core/motor_devengos.py",
    "src/core/formulas_prestaciones.py": "src/core/motor_costos_empresa.py",
    "src/core/formulas_retencion.py": "src/core/motor_retencion.py",
    
    # Bases de Datos Estáticas (Nucleo)
    "src/core/base_legal.py": "src/core/parametros_dian.py",
    "src/core/ley_colombiana.py": "src/core/conocimiento_legal.py",
}

IMPORT_REPLACES = {
    "src.ui.calculadora": "src.ui.calculadora_individual",
    "src.ui.consulta_legal": "src.ui.agente_juridico",
    "src.ui.tablas_informativas": "src.ui.indicadores_macro",
    "src.core.formulas_nomina": "src.core.motor_devengos",
    "src.core.formulas_prestaciones": "src.core.motor_costos_empresa",
    "src.core.formulas_retencion": "src.core.motor_retencion",
    "src.core.base_legal": "src.core.parametros_dian",
    "src.core.ley_colombiana": "src.core.conocimiento_legal"
}

def ejecutar_refactor():
    # 1. Actualizar las inyecciones de importaciones (Parchado de texto)
    files_to_check = glob.glob(os.path.join(BASE_DIR, "**/*.py"), recursive=True)
    for file_path in files_to_check:
        if os.path.basename(file_path) == "renombrar_proyecto.py": continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = content
        for old_imp, new_imp in IMPORT_REPLACES.items():
            new_content = new_content.replace(old_imp, new_imp)
            
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Imports actualizados de forma segura en: {os.path.basename(file_path)}")

    # 2. Renombrar físicamente los archivos (Sistema de Archivos)
    for old_rel, new_rel in RENAMES.items():
        old_full = os.path.join(BASE_DIR, *old_rel.split("/"))
        new_full = os.path.join(BASE_DIR, *new_rel.split("/"))
        
        if os.path.exists(old_full):
            os.rename(old_full, new_full)
            print(f"✅ Archivo Renombrado: {os.path.basename(old_full)} -> {os.path.basename(new_full)}")
        else:
            print(f"⚠️ El archivo {os.path.basename(old_full)} ya fue renombrado o no existe.")

    print("\n🎉 ¡Arquitectura MVC completada con éxito!")
    print("👉 Por favor reinicia tu servidor de Streamlit (Ctrl+C y vuelve a correr 'streamlit run main.py').")

if __name__ == "__main__":
    ejecutar_refactor()
