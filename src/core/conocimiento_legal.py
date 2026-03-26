MARCO_JURIDICO_COLOMBIANO = """
[REGLAS TRIBUTARIAS Y LABORALES COLOMBIA - APLICAR ESTRICTAMENTE]
1. INCRGO (Pagos NO Renta): Salud 4%, Pensión 4%, FSP(1-2%).
2. DEDUCCIONES MÁXIMAS: Salud prepagada o seguros (16 UVT/mes), Intereses vivienda (100 UVT/mes), Dependientes (10% ingreso bruto, máximo 32 UVT/mes).
3. RENTAS EXENTAS: Aportes AFC/FPV (Max 30% ingreso, tope 3800 UVT/año), Indemnizaciones/Cesantías.
4. TOPE DEL 40%: Suma de Deducciones + Rentas Exentas no puede superar el 40% del Ingreso Neto (Lim: 1340 UVT/año).
5. 25% EXENTO LABORAL (Num 10 Art 206): Automático sobre subtotal remanente (Tope 790 UVT/año).
6. RETENCIÓN INDEPENDIENTES: Seguridad Social obligatoria de Salud(12.5%) y Pensión(16%) calculada única y estrictamente sobre un IBC ficticio del 40% del valor mensual. Su depuración retentiva puede usar la Tabla 383 o tarifa plana comercial (Honorarios 10/11%).
7. EXENCIONES SERVIDORES PÚBLICOS: Magistrados y Rectores U.Pública (Gastos de representación 50% Exentos), Jueces (25% Exento), Militares/Policía (100% de Primas/Subsidios son Exentas).
8. RETENCIÓN ART 383 E.T. Mensual (Convertir Base a UVT):
0-95 UVT : 0%
>95-150 UVT : (Base_UVT - 95)*19%
>150-360 UVT : (Base_UVT - 150)*28% + 10 UVT
>360-640 UVT : (Base_UVT - 360)*33% + 69 UVT
>640-945 UVT : (Base_UVT - 640)*35% + 162 UVT
>945-2300 UVT : (Base_UVT - 945)*37% + 268 UVT
>2300 UVT : (Base_UVT - 2300)*39% + 770 UVT
9. LIQUIDACIÓN LABORAL MATEMÁTICA (CST):
- VHO = SalarioBase / Divisor Operativo Promedio Válido.
- Recargos: Nocturno Ordinario(x0.35), H.Extra Diurna(x1.25), H.Extra Nocturna(x1.75). Dominical O Festivo(x1.75), Extra Diurna Dom/Fes(x2.0), Extra Noc Dom/Fes(x2.5).
- Prima y Cesantías: (Salario_Base + Aux_Transporte) * Días_Laborados / 360.
- Intereses Cesantías: Valor_Cesantías * Días_Laborados * 0.12 / 360.
- Vacaciones: (Salario_Base) * Días_Laborados / 720 (Ojo: Sin Aux_Transporte).
- Despido Injusto Indefinido: Si Sueldo < 10 SMMLV (30 días 1er año, 20 subsiguientes).
"""
