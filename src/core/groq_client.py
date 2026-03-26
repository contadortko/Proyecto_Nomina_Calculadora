import os
from groq import Groq

def get_groq_client(api_key: str = None):
    """
    Inicializa la conexión supersónica a los LPU de Groq.
    Prioriza la key del parámetro o busca una variable GORQ_API_KEY.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)

def consultar_groq(cliente, historial_mensajes, modelo="llama", contexto_sistema=""):
    """
    Envía la conversación.
    modelo: "llama" usará llama3-8b, "mixtral" usará mixtral-8x7b
    """
    try:
        mensajes_completos = []
        if contexto_sistema:
            # Los motores de Groq respetan increíblemente bien el prompt estructurado como 'system'
            mensajes_completos.append({"role": "system", "content": contexto_sistema})
            
        # Limitar el historial a los 4 últimos mensajes (2 interacciones) para no desbordar el TPM (Tokens Per Minute) de Groq gratis
        historial_recortado = historial_mensajes[-4:] if len(historial_mensajes) > 4 else historial_mensajes
        mensajes_completos.extend(historial_recortado)
        
        # Groq deprecó Mixtral y Llama3 viejos. Usamos Llama-3.1-8B y el masivo Llama-3.3-70B:
        id_real = "llama-3.1-8b-instant" if modelo == "llama" else "llama-3.3-70b-versatile"
        
        chat_completion = cliente.chat.completions.create(
            messages=mensajes_completos,
            model=id_real,
            temperature=0.0, # Exactitud máxima algorítmica y frialdad legal
            max_tokens=3000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en la nube de Groq: {str(e)}"
