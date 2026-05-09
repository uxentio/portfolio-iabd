// Script temporal para anadir tildes a gen_doc.js
const fs = require('fs');
let s = fs.readFileSync('gen_doc.js', 'utf8');

const map = {
  'tecnico':'técnico','tecnica':'técnica','tecnicos':'técnicos','tecnicas':'técnicas',
  'practica':'práctica','practicas':'prácticas','practico':'práctico','practicamente':'prácticamente',
  'tambien':'también','asi':'así','estan':'están',
  'codigo':'código','codigos':'códigos',
  'funcion':'función',
  'aplicacion':'aplicación','aplicaciones':'aplicaciones',
  'configuracion':'configuración','configuraciones':'configuraciones',
  'pequeno':'pequeño','pequena':'pequeña','pequenos':'pequeños','pequenas':'pequeñas',
  'espanol':'español','espanola':'española',
  'anadir':'añadir','anadido':'añadido','anadi':'añadí','anade':'añade','anadiendo':'añadiendo',
  'facil':'fácil','facilmente':'fácilmente',
  'rapido':'rápido','rapida':'rápida','rapidos':'rápidos','rapidas':'rápidas','rapidamente':'rápidamente',
  'ademas':'además','despues':'después',
  'documentacion':'documentación','implementacion':'implementación',
  'automatico':'automático','automatica':'automática','automaticos':'automáticos','automaticas':'automáticas','automaticamente':'automáticamente',
  'basico':'básico','basica':'básica','basicos':'básicos','basicas':'básicas',
  'analisis':'análisis',
  'parametro':'parámetro','parametros':'parámetros',
  'conexion':'conexión','conexiones':'conexiones',
  'opcion':'opción','opciones':'opciones',
  'seccion':'sección','secciones':'secciones',
  'informacion':'información',
  'util':'útil','utiles':'útiles',
  'electrico':'eléctrico','electrica':'eléctrica',
  'magico':'mágico','magica':'mágica',
  'tipico':'típico','tipica':'típica','tipicos':'típicos','tipicas':'típicas','tipicamente':'típicamente',
  'ultimo':'último','ultima':'última','ultimos':'últimos','ultimas':'últimas',
  'numero':'número','numeros':'números','numerico':'numérico',
  'linea':'línea','lineas':'líneas',
  'pagina':'página','paginas':'páginas',
  'version':'versión','versiones':'versiones',
  'peticion':'petición','peticiones':'peticiones',
  'integracion':'integración',
  'comunicacion':'comunicación','comunicaciones':'comunicaciones',
  'decision':'decisión','decisiones':'decisiones',
  'metodo':'método','metodos':'métodos',
  'titulo':'título','titulos':'títulos',
  'capitulo':'capítulo','capitulos':'capítulos',
  'logica':'lógica','logico':'lógico',
  'critico':'crítico','critica':'crítica',
  'maximo':'máximo','maxima':'máxima',
  'minimo':'mínimo','minima':'mínima',
  'grafico':'gráfico','grafica':'gráfica','graficos':'gráficos','graficas':'gráficas',
  'electronico':'electrónico','electronica':'electrónica',
  'atencion':'atención','ejecucion':'ejecución','instalacion':'instalación',
  'generacion':'generación','explicacion':'explicación',
  'accion':'acción','acciones':'acciones','solucion':'solución','soluciones':'soluciones',
  'situacion':'situación','interaccion':'interacción','definicion':'definición',
  'combinacion':'combinación','navegacion':'navegación','direccion':'dirección',
  'precision':'precisión','vision':'visión','mision':'misión',
  'refactorizacion':'refactorización','demostracion':'demostración',
  'estandar':'estándar','estandares':'estándares',
  'maquina':'máquina','maquinas':'máquinas',
  'segun':'según','quiza':'quizá','aun':'aún',
  'energia':'energía','bateria':'batería',
  'dia':'día','dias':'días',
  'comun':'común','comunes':'comunes',
  'arbol':'árbol',
  'garantia':'garantía',
  'periodico':'periódico','periodica':'periódica',
  'asincrono':'asíncrono','asincrona':'asíncrona',
  'proposito':'propósito',
  'teorico':'teórico','teoria':'teoría',
  'academico':'académico',
  'exito':'éxito',
  'limite':'límite','limites':'límites',
  'telefono':'teléfono',
  'caracteristica':'característica','caracteristicas':'características',
  'dificil':'difícil','dificiles':'difíciles',
  'credito':'crédito',
  'calculo':'cálculo','calculos':'cálculos',
  'unica':'única','unico':'único','unicos':'únicos','unicas':'únicas','unicamente':'únicamente',
  'simbolo':'símbolo','simbolos':'símbolos',
  'proximo':'próximo','proxima':'próxima','proximos':'próximos','proximas':'próximas',
  'especifico':'específico','especifica':'específica','especificos':'específicos','especificas':'específicas','especificamente':'específicamente',
  'historico':'histórico','historica':'histórica',
  'fisico':'físico','fisica':'física',
  'sintetica':'sintética','sintetico':'sintético',
  'matematica':'matemática','matematicas':'matemáticas','matematico':'matemático',
  'area':'área','areas':'áreas',
  'traves':'través',
  'ingles':'inglés','frances':'francés','aleman':'alemán','japones':'japonés',
  'jardin':'jardín','botin':'botín',
  'proposito':'propósito',
  'satelite':'satélite',
  'oxigeno':'oxígeno','hidrogeno':'hidrógeno',
  'organico':'orgánico','inorganico':'inorgánico',
  'plastico':'plástico',
  'electronic':'electrónic',
  'multitarea':'multitarea',
  'sintaxis':'sintaxis',
  'linea':'línea',
  'boton':'botón','botones':'botones',
  'iconos':'iconos',
  'icono':'icono',
  'panico':'pánico',
  'imagen':'imagen',
  'examen':'examen',
  'origen':'origen',
  'margen':'margen',
  'asignatura':'asignatura',
};

// Protege bloques de codigo (codeBlock("...")) y URLs/enlaces para no meter tildes dentro
// Estrategia: separar por segmentos de string y solo aplicar dentro de comillas dobles que
// esten fuera de codeBlock(. Mas simple: aplicar solo a texto dentro de bodyText(, heading, bulletList, titulo de tabla, etc.
// Aun mas simple: aplicar a TODO menos a URLs (http...) y a codeBlock segments.

// Parto el fichero en tokens: codeBlock(`...`) o "..."string o resto.
// Enfoque pragmatico: aplicar globalmente EXCEPTO dentro de codeBlock("...") multilinea y de URLs http*.

// Extraer y proteger con placeholders
const placeholders = [];
function protect(regex) {
  s = s.replace(regex, (m) => {
    const key = '__PH' + placeholders.length + '__';
    placeholders.push(m);
    return key;
  });
}

// 1) codeBlock("....") posiblemente multilinea con template literals o strings
protect(/codeBlock\(`[\s\S]*?`\)/g);
protect(/codeBlock\("(?:\\.|[^"\\])*"\)/g);
// 2) URLs
protect(/https?:\/\/[^\s"'`)]+/g);
// 3) Nombres de funcion/propiedad que son identificadores (no deben llevar tildes)
//    No toco 'funcion' dentro de pattern JS source => limito a texto entre "..." espanol

let changed = 0;
for (const [k,v] of Object.entries(map)) {
  if (k===v) continue;
  const escK = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('\\b'+escK+'\\b', 'g');
  const before = s;
  s = s.replace(re, v);
  if (s !== before) changed++;
  const K = k.charAt(0).toUpperCase() + k.slice(1);
  const V = v.charAt(0).toUpperCase() + v.slice(1);
  const escK2 = K.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re2 = new RegExp('\\b'+escK2+'\\b', 'g');
  const before2 = s;
  s = s.replace(re2, V);
  if (s !== before2) changed++;
}

// Restaurar placeholders
placeholders.forEach((v, i) => {
  s = s.replace('__PH' + i + '__', v);
});

fs.writeFileSync('gen_doc.js', s, 'utf8');
console.log('Patrones afectados: ' + changed);
