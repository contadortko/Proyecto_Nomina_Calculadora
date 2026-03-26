# 📊 Nomina Intelligence Hub 2026
**Sistema de Auditoría y Liquidación Técnica de Nómina Colombiana**

Herramienta profesional diseñada para la liquidación precisa de nóminas individuales y masivas bajo el marco legal colombiano vigente para el año **2026**. Incluye la transición de la jornada laboral a **42 horas** (Ley 2101) y la depuración de base gravable según el **Art. 387 del Estatuto Tributario**.

## 🏛️ Arquitectura del Sistema (Layered Architecture)
El proyecto utiliza una arquitectura de capas (Separación de Responsabilidades) para garantizar escalabilidad y facilitar el despliegue en entornos Web o Local:

* **`main.py`**: Punto de entrada y orquestador del Dashboard y navegación.
* **`src/ui/`**: **Capa de Presentación**. Contiene la interfaz de usuario en Streamlit.
* **`src/core/`**: **Capa de Negocio**. Motores de cálculo puro (Nómina, Prestaciones y Retención).
* **`src/data/`**: **Capa de Persistencia**. Almacenamiento de archivos Excel, inputs y plantillas.
* **`src/utils/`**: **Capa de Soporte**. Herramientas transversales (Generadores de PDF, formateadores).

## 🚀 Ejecución en Entorno Local (WSL)

1. **Activar el Entorno Virtual:**
   ```bash
   source env/bin/activate

2. **Ejecutar la aplicación**
    ```bash
    streamlit run main.py

⚖️ Parámetros Técnicos 2026 (Configurados)

SMMLV 2026: $1.705.905
Auxilio Transporte: $249.095
UVT 2026: $52.374
Jornada Laboral: 44h (Ene - Jun de 2026) / 42h (Jul - Dic de 2026).

Base de Retención: Procedimiento 1 y 2 con topes legales de 40% y 1.340 UVT anuales. Pendiente

Desarrollado por: Anuar Monterrosa Bedoya
