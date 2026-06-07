# INFORME DE PROGRESO - FASE 1: COMPILACIÓN 2020-2024
## Investigación: Violencia Sexual contra Mujeres en España

**FECHA:** Mayo 2025  
**PHASE:** Fase 1 - INICIADA  
**STATUS:** En curso

---

## 1. OBJETIVOS DE FASE 1

✓ Compilar datos verificados 2020-2024 de TODAS las fuentes oficiales  
✓ Desglosar por: edad, nacionalidad, relación víctima-agresor  
✓ Crear base de datos maestro con estructura estandarizada  
✓ Documentar limitaciones y gaps

---

## 2. DATOS VERIFICADOS Y COMPILADOS

### ✓ VERIFIED - 2024

| Delito | Cifra Neta | Fuente | Desglose Disponible |
|--------|-----------|--------|-------------------|
| Violaciones | 5.206 | Ministerio Interior Balance Q4 2024 | NO - Solo cifra neta |
| Agresiones sin penetración | 15.953 | Ministerio Interior Balance Q4 2024 | NO - Solo cifra neta |
| TOTAL Delitos sexuales | 21.159 | Ministerio Interior Balance Q4 2024 | Parcial |

**FUENTE:** Ministerio del Interior - Balance de Criminalidad Cuarto Trimestre 2024 (publicado 2025)

**Contexto:**
- 14,2 violaciones por día
- 43,7 agresiones sin penetración por día
- 58 delitos sexuales totales por día

### ✓ VERIFIED - 2023

| Datos | Valor | Fuente |
|-------|-------|--------|
| TOTAL Hechos contra libertad sexual | 21.825 | Ministerio Interior - Informe 2023 |
| Víctimas femeninas | 18.464 | Ministerio Interior - Informe 2023 |
| Víctimas masculinas | 3.092 | Ministerio Interior - Informe 2023 |
| % Víctimas 0-13 años | 19,6% | Ministerio Interior - Informe 2023 |
| % Víctimas 14-17 años | 22,9% | Ministerio Interior - Informe 2023 |
| Menores = 42,6% total víctimas | CONFIRMADO | Ministerio Interior - Informe 2023 |
| Víctimas españolas (total) | 73,8% (15.928) | Ministerio Interior - Informe 2023 |
| Víctimas españolas (solo mujeres) | 84,6% | Ministerio Interior - Informe 2023 |

**Aumento vs 2022:** +14,8%

**NOTA METODOLÓGICA:** Cambio legal 2022. Estos datos incluyen ahora "agresiones" integradas (incluyendo lo que antes era "abuso sexual").

### ✓ VERIFIED - 2022-2024 (Fiscalía)

| Año | Agresiones Sexuales (Diligencias) | Variación | Fuente |
|-----|-----------------------------------|-----------|--------|
| 2024 | 20.711 | +12,11% vs 2023 | Fiscalía General 2024 |
| 2023 | 18.474 | +92% vs 2022 | Fiscalía General 2023 |
| 2022 | 9.603 | --- | Fiscalía General 2022 |

**IMPORTANTE:** El salto 2022→2023 (+92%) es parcialmente artefactual: incluye cambio legal Ley 10/2022 que integró "abusos" en "agresiones".

### ✓ VERIFIED - Feminicidios

| Año | Total | % Víctimas Extranjeras | Riesgo Relativo | Fuente |
|-----|-------|------------------------|-----------------|--------|
| 2024 | TBD | 51% | 4,9x superior | Fiscalía 2024 |
| 2023 | 58 | 43% | --- | GREVIO 2024 |

**Hallazgo crítico:** El 51% de los feminicidios en 2024 fueron mujeres de nacionalidad extranjera, a pesar de representar solo ~14% de la población.

### ⏳ PARCIALMENTE VERIFICADOS

**2024 - Necesita extracción de Informe Delitos Libertad Sexual (Ministerio Interior):**
- [ ] Violaciones por edad víctima
- [ ] Violaciones por edad agresor
- [ ] Violaciones por nacionalidad
- [ ] Agresiones c/ penetración por edad/nacionalidad
- [ ] Agresiones s/ penetración por edad/nacionalidad
- [ ] Acoso sexual por edad/nacionalidad

**2023 - Disponible en Informe pero no extraído:**
- [ ] Desglose completo por edad
- [ ] Desglose por nacionalidad
- [ ] Desglose por relación víctima-agresor (si disponible)

---

## 3. DATOS NO DISPONIBLES / NO UBICADOS

### 2024
- ⚠️ Violaciones desglosadas por edad víctima/agresor
- ⚠️ Violaciones desglosadas por nacionalidad
- ⚠️ Acoso sexual cifras
- ⚠️ Provocación sexual cifras
- ⚠️ Feminicidios cifra neta (solo porcentajes)

### 2023-2022
- ⚠️ Mayoría de desgloses por edad/nacionalidad
- ⚠️ Datos sobre relación víctima-agresor (pareja/conocido/desconocido)

### 2021-2020
- ⚠️ Datos desglosados prácticamente no disponibles públicamente
- ⚠️ Necesidad de acceder a Anuarios completos

---

## 4. CAMBIO LEGAL CRÍTICO - Ley 10/2022

**Fecha de entrada en vigor:** 6 de septiembre de 2022

**Cambios:**
1. Eliminó categoría "abuso sexual"
2. Integró abusos en "agresión sexual"
3. Redefinió consentimiento
4. Cambio de penas

**Impacto en datos:**
- **PRE-2023:** Datos reportaban "abusos" y "agresiones" separados
- **POST-2023:** TODO es "agresión sexual" (integrado)
- **RESULTADO:** Series pre-2023 vs post-2023 NO son directamente comparables
- **2022-2023:** Período de transición (algunos datos con ambas categorías)

**Ejemplo:**
- 2022 Total: 9.603 (sin violaciones)
- 2023 Total: 18.474 (incluye violaciones + agresiones integradas)
- La comparación +92% es parcialmente inflada por reclasificación

---

## 5. PRÓXIMAS ACCIONES INMEDIATAS

### ACCIÓN 1: Descargar e Extraer Informe Delitos Libertad Sexual 2024

**Fuente:** https://www.interior.gob.es/  
**Documento:** "Informe sobre delitos contra la libertad sexual España 2024"  
**Archivo esperado:** PDF ~80-100 páginas con tablas detalladas

**Variables a extraer:**
- Tabla de evolución global 2018-2024 (si disponible)
- Violaciones desglosadas por edad
- Violaciones desglosadas por nacionalidad
- Agresiones c/ penetración por edad/nacionalidad
- Agresiones s/ penetración por edad/nacionalidad
- Acoso sexual, exhibicionismo, provocación sexual
- Datos sobre relación víctima-agresor (si disponible)
- Información sobre delitos cometidos por menores (2024: 3.283)

**Estimado de tiempo:** 4-6 horas

### ACCIÓN 2: Extraer datos de Informe 2023

**Estatus:** Documento disponible (verificado en web)  
**Variables:** Mismo desglose que 2024

**Estimado de tiempo:** 3-4 horas

### ACCIÓN 3: Descargar Anuarios Ministerio Interior 2020-2022

**URLs:**
- Anuario 2024: https://www.interior.gob.es/
- Anuario 2023: https://www.interior.gob.es/
- Anuario 2022: https://www.interior.gob.es/
- Anuario 2021: https://www.interior.gob.es/
- Anuario 2020: https://www.interior.gob.es/

**Formato:** Excel o PDF con tablas

**Estimado de tiempo:** 8-10 horas (búsqueda, descarga, extracción)

### ACCIÓN 4: Solicitud de Datos Granulares (CGPJ)

**Si desgloses no están públicos:**
- Enviar solicitud AEPD (Acceso a Información Pública)
- O contactar directamente: [email protected]

**Tiempo estimado:** 2-4 semanas para respuesta

---

## 6. ESTRUCTURA BASE DE DATOS

Se creó archivo Excel: `BASE_DATOS_FASE1_2020_2024_COMPILACION.xlsx`

**Hojas incluidas:**
1. **Violaciones_2020_2024** - Para compilar violaciones con desgloses
2. **Agr_Con_Penetración_2020_2024** - Agresiones con penetración
3. **Agr_Sin_Penetración_2020_2024** - Agresiones sin penetración
4. **Feminicidios_2020_2024** - Feminicidios y contexto
5. **Status_Recopilación** - Checklist de progreso

**Variables por fila:**
- Año (2024-2020)
- Cifra neta
- Edad víctima (0-13, 14-17, 18-30, 31-50, 51+)
- Nacionalidad víctima (Español, Extranjero)
- Edad agresor (mismos rangos)
- Nacionalidad agresor
- Relación víctima-agresor (si disponible)
- Fuente oficial
- Categoría legal (importante para cambios 2022)
- Notas metodológicas

---

## 7. INDICADORES DE PROGRESO ACTUAL

| Elemento | Progreso | Detalles |
|----------|----------|---------|
| Cifras netas 2024 | 80% | 2/3 tipos de delito |
| Cifras netas 2023 | 50% | Total hechos sí, desglose no |
| Desgloses 2024 | 0% | Requiere extracción Informe |
| Desgloses 2023 | 0% | Requiere extracción Informe |
| Datos 2022 | 15% | Solo Fiscalía (cifra bruta) |
| Datos 2021-2020 | 0% | No iniciado |
| Feminicidios | 40% | Cifras pero falta detalles |
| **TOTAL FASE 1** | **25%** | **1-2 semanas de trabajo** |

---

## 8. LIMITACIONES DOCUMENTADAS

### Cambio Legal 2022
- ❌ No es posible comparar directo pre-2023 vs post-2023 sin ajustes
- ✓ Se incluirá nota en todas las celdas sobre categorización

### Datos Desglosados
- ❌ Ministerio Interior no publica siempre todos los desgloses online
- ✓ Los informes PDF sí incluyen tablas (requiere extracción manual)

### Relación Víctima-Agresor
- ❌ No disponible en denuncias/anuarios (privacidad)
- ✓ Disponible parcialmente en Macroencuesta INE (prevale ncia vida)

### Cobertura Geográfica Pre-2011
- ❌ Faltan datos Cataluña, Navarra, Euskadi
- ✓ Documentar en notas metodológicas

---

## 9. CRONOGRAMA REALISTA FASE 1

| Semana | Tarea | Horas | Status |
|--------|-------|-------|--------|
| Semana 1 (actual) | Extracción Informes 2023-2024 | 7-8 | EN PROGRESO |
| Semana 1 | Descarga Anuarios 2020-2022 | 6-8 | PENDIENTE |
| Semana 2 | Extracción datos de Anuarios | 8-10 | PENDIENTE |
| Semana 2 | Validación cruzada de cifras | 4-6 | PENDIENTE |
| Semana 2 | Compilación base de datos completa | 4-6 | PENDIENTE |
| **TOTAL FASE 1** | **2-3 semanas** | **29-38h** | **~1-2% completado** |

---

## 10. RECURSOS NECESARIOS

✓ Acceso a web (búsqueda de enlaces)  
✓ Capacidad de descargar PDF y Excel  
✓ Software para leer PDF y extraer datos  
✓ Base de datos Excel (ya creada)  
✓ Contactos institucionales para solicitudes AEPD (si necesario)

---

## 11. PRÓXIMO HITO

**ENTREGABLE:** Base de datos completa 2020-2024 con:
- ✓ Todas las cifras netas verificadas
- ✓ Desgloses por edad, nacionalidad, relación
- ✓ Notas metodológicas
- ✓ % de completitud por variable

**Fecha objetivo:** 2-3 semanas desde inicio

---

## OBSERVACIONES FINALES

**Fortalezas:**
- Datos 2024 muy recientes y verificables
- Informe Delitos Libertad Sexual es exhaustivo (80+ páginas)
- Anuarios accesibles públicamente
- Cambios legales bien documentados

**Riesgos:**
- Cambio legal 2022 complica análisis temporal
- Algunos desgloses pueden requerir solicitud AEPD
- Pre-2011 falta cobertura geográfica completa

**Crítico:**
- NO INFERIR DATOS nunca. Si no está en fuente oficial: CELDA VACÍA

---

**Actualización:** En curso - Se actualizará diariamente conforme se verifiquen datos
