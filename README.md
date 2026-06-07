# Test OPE Enfermería · Osakidetza 2026

Aplicación de estudio para la OPE de Enfermería de Osakidetza (temario específico 23·24·25). Contiene 500 preguntas tipo test con respuestas razonadas, extraídas del documento de claves publicado por UGT.

Funciona como un único archivo HTML: sin instalación, sin servidor y sin conexión a internet.

---

## Cómo usarla

1. Abre el archivo `test_ope_enfermeria.html` haciendo doble clic — se abre directamente en el navegador.
2. Elige el modo, el número de preguntas y las opciones deseadas.
3. Pulsa **Empezar** o usa el botón **Examen Oficial**.

No necesitas instalar nada. El progreso se guarda automáticamente en el navegador.

> En Windows el explorador puede ocultar la extensión `.html`. Si el archivo aparece sin ella, el doble clic lo abre igual en el navegador.

---

## Modos de estudio

### Modo Estudio
Pulsa cualquier opción para revelar la respuesta correcta al instante. Ideal para repasar sin presión. Al terminar la ronda vuelves al inicio.

### Modo Examen
Responde todas las preguntas de la ronda y al final ves tu porcentaje de acierto, un veredicto y el historial de sesiones. Desde la pantalla de resultado puedes ver la **revisión completa**: pregunta a pregunta, qué respondiste y cuál era la opción correcta.

### Examen Oficial
Simula las condiciones reales del examen:
- 100 preguntas aleatorias de las 500.
- Temporizador de 90 minutos (se pone en rojo cuando quedan 5 minutos).
- Navegación estricta: no se puede volver a una pregunta anterior.
- Al terminar (o cuando se agota el tiempo) muestra el resultado y la revisión completa.

---

## Opciones de configuración

| Opción | Descripción |
|--------|-------------|
| **Modo** | Estudio o Examen |
| **Nº de preguntas** | 10 · 25 · 50 · 100 · Todas |
| **Barajar** | Mezcla el orden de las preguntas y de las opciones |
| **Solo impugnables** | Filtra las 10 preguntas marcadas como impugnables en el documento original |
| **Buscar / ir a nº** | Busca por palabra clave o salta directamente a un número de pregunta |

---

## Seguimiento del progreso

El progreso se guarda en el navegador de forma automática:

- **Fallos acumulados**: las preguntas contestadas mal quedan guardadas. Desde el inicio puedes repasar solo esas con el botón **Repasar mis fallos**.
- **Estadísticas globales**: total de preguntas respondidas y porcentaje de acierto acumulado, visibles en la pantalla de inicio.
- **Historial de sesiones**: las últimas 5 rondas en modo examen aparecen en la pantalla de inicio con la fecha, el número de preguntas y el porcentaje obtenido.

> El progreso se almacena en el `localStorage` del navegador. No se sincroniza entre dispositivos ni entre navegadores distintos. Si limpias los datos del navegador, el progreso se perderá.

---

## Preguntas impugnables

Las siguientes preguntas están marcadas como **IMPUGNABLE** o **POSIBLE IMPUGNACIÓN** en el documento original de UGT:

**18 · 48 · 50 · 52 · 167 · 206 · 211 · 303 · 304 · 395**

Aparecen con la etiqueta `[IMPUGNABLE]` junto al enunciado y con un distintivo dorado, tanto durante el cuestionario como en la revisión final. La pregunta 167 tiene dos respuestas válidas (b y d).

---

## Archivos del proyecto

| Archivo | Función |
|---------|---------|
| `test_ope_enfermeria.html` | **El archivo que se usa para estudiar.** Contiene las 500 preguntas embebidas y toda la lógica de la aplicación. Autónomo, sin dependencias externas. |
| `preguntas_enfermero.json` | Fuente de datos estructurada con las 500 preguntas, opciones, respuesta correcta y flag de impugnabilidad. |
| `template.html` | Plantilla de la aplicación con el marcador `__DATA__` en lugar de los datos. Se edita aquí la interfaz y la lógica; nunca en el HTML final. |


> Editar `preguntas_enfermero.json` **no modifica** `test_ope_enfermeria.html` directamente. Para que los cambios surtan efecto hay que reconstruir el HTML (ver sección siguiente).


---

## Compatibilidad

- Funciona en cualquier navegador moderno: Chrome, Firefox, Safari, Edge.
- No requiere conexión a internet. Las fuentes tipográficas (Fraunces y Newsreader) se cargan de Google Fonts la primera vez; si no hay conexión, el navegador usa fuentes serif de sistema y la aplicación funciona igualmente.
- Los datos están embebidos en el HTML porque el protocolo `file://` (abrir desde disco) bloquea las peticiones externas por seguridad. Esto hace que el archivo sea completamente autónomo.

---

## Aviso legal

Material de estudio recopilado por **UGT** para el proceso selectivo OPE Enfermería Osakidetza 23·24·25. UGT declina toda responsabilidad sobre el contenido y los posibles errores u omisiones. Algunas preguntas figuran como impugnables según el documento original.
