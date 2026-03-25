# /home/contadortko/proyectos/Nomina_Intelligence_Hub/core/formulas_nomina.py

"""
MÓDULO DE CÁLCULOS DE NÓMINA COLOMBIA 2026 - VERSIÓN AUDITORÍA
Lógica: CST, Ley 2101 (Jornada 42h), Ley 797 (Topes) y Ley 1393 (IBC).
"""
from datetime import date

# --- CONSTANTES LEGALES 2026 ---
# Basado en el SMMLV de 2026: $1,705,905
# Art. 5 Ley 797 de 2003: El límite de cotización para seguridad social es de 25 SMMLV.
# Valor para 2026: $42,647,625
smmlv = 1705905
aux_transporte = 249095  # Auxilio de Transporte para 2026 (aplica solo a salarios hasta 2 SMMLV)
tope_25 = smmlv * 25

def obtener_parametros_legales(fecha_liquidacion):
    """
    Sincronización con parámetros de auditoría 2026.
    """
    fecha_cambio = date(2026, 7, 1)
    # Factores base
    params = {"hed": 1.25, "hen": 1.75, "rn": 0.35}

    if fecha_liquidacion < fecha_cambio:
        # Escenario ANTES de julio (Divisor 220)
        params.update({
            "divisor": 220, "heddf": 2.05, "hendf": 2.65, 
            "rdf": 1.80, "rndf": 1.15
        })
    else:
        # Escenario DESPUÉS de julio (Divisor 210)
        params.update({
            "divisor": 210, "heddf": 2.25, "hendf": 2.75, 
            "rdf": 1.90, "rndf": 1.25
        })
    return params

def calcular_extras(salario, novedades, fecha_nomina):
    """
    Calcula cada concepto redondeando por línea para conciliar con Excel.
    """
    p = obtener_parametros_legales(fecha_nomina)
    v_h = salario / p["divisor"]
    
    # IMPORTANTE: Se debe redondear cada línea individualmente para evitar 
    # el error de arrastre visto en consola
    detalle = {}
    for clave, factor in p.items():
        if clave != "divisor":
            hrs = novedades.get(clave, 0)
            detalle[clave] = round(v_h * factor * hrs)
            
    return detalle, sum(detalle.values()), p["divisor"]

def calcular_deducciones_ley(ibc):
    """
    Aportes obligatorios a Seguridad Social (Salud y Pensión).
    Art. 18 y 19 Ley 100 de 1993: Descuento del 4% para cada concepto al empleado.
    Aplica el tope máximo de cotización de 25 SMMLV (Art. 5 Ley 797 de 2003).
    """
    # Garantizamos que la base no exceda el límite legal de 25 SMMLV
    ibc_final: float = min(ibc, tope_25)
    valor_deduccion = round(ibc_final * 0.04, 0)
    return valor_deduccion, valor_deduccion  # Salud y Pensión son iguales para el empleado

def obtener_tarifa_fsp(ibc):
    """
    Determina el valor y la tarifa del FSP (Art. 2.2.14.1.6 Decreto 1833 de 2016).
    Se activa a partir de los 4 SMMLV con tope de cotización en 25 SMMLV.
    """
    # 1. El IBC para FSP también se limita a 25 SMMLV
    ibc_limitado = min(ibc, smmlv * 25)

    # 2. Cálculo de n_smmlv
    n_smmlv = round(ibc_limitado / smmlv, 2)

    # IMPORTANTE: Si es menor a 4, debe devolver dos valores (0, 0.0) para no romper el programa
    if n_smmlv < 4:
        return 0, 0.0

    # 3. Escalafones
    escalafones = [
        (15.99, 0.01),   # de 4 a menos de 16 SMMLV: 1%
        (16.99, 0.012),  # de 16 a 17 SMMLV: 1.2%
        (17.99, 0.014),  # de 17 a 18 SMMLV: 1.4%
        (18.99, 0.016),  # de 18 a 19 SMMLV: 1.6%
        (19.99, 0.018)   # de 19 a 20 SMMLV: 1.8%
    ]

    tarifa_final = 0.02 
    for limite, tarifa in escalafones:
        if n_smmlv < limite:
            tarifa_final = tarifa
            break

    # 4. Cálculo del valor final en pesos
    valor_fsp = round(ibc_limitado * tarifa_final)
    
    # LA CLAVE: Asegúrate de que esta línea esté alineada con el 'if n_smmlv < 4'
    return valor_fsp, tarifa_final