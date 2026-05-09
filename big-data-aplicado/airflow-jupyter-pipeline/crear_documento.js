const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat
} = require("docx");

// Fuente y colores
const FONT = "Atkinson Hyperlegible Next";
const FONT_CODE = "Consolas";
const AZUL = "2E5090";
const GRIS_CLARO = "F2F2F2";
const GRIS_BORDE = "BBBBBB";

const border = { style: BorderStyle.SINGLE, size: 1, color: GRIS_BORDE };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// Ruta de capturas
const SS_DIR = "D:/Users/anton/Pictures/Screenshots";
function screenshot(name) {
  return fs.readFileSync(`${SS_DIR}/Captura de pantalla 2026-03-17 ${name}.png`);
}

function heading(text, level) {
  const sizes = { [HeadingLevel.HEADING_1]: 32, [HeadingLevel.HEADING_2]: 26, [HeadingLevel.HEADING_3]: 22 };
  return new Paragraph({
    heading: level,
    spacing: { before: level === HeadingLevel.HEADING_1 ? 360 : 240, after: 120 },
    children: [new TextRun({ text, bold: true, font: FONT, size: sizes[level] || 22, color: AZUL })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.afterSpacing || 120 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, font: FONT, size: 22, ...opts })]
  });
}

function bold(text) { return new TextRun({ text, font: FONT, size: 22, bold: true }); }
function normal(text) { return new TextRun({ text, font: FONT, size: 22 }); }
function italic(text) { return new TextRun({ text, font: FONT, size: 22, italics: true }); }

function multiPara(runs, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.afterSpacing || 120 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: runs
  });
}

function codeBlock(lines) {
  return lines.map(line => new Paragraph({
    spacing: { after: 0 },
    children: [new TextRun({ text: line || " ", font: FONT_CODE, size: 18, color: "333333" })],
    shading: { fill: "F5F5F5", type: ShadingType.CLEAR }
  }));
}

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: AZUL, type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: FONT, size: 20, bold: true, color: "FFFFFF" })] })]
  });
}

function dataCell(text, width, opts = {}) {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: opts.mono ? FONT_CODE : FONT, size: opts.mono ? 18 : 20 })]
    : text;
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: opts.shaded ? { fill: GRIS_CLARO, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: runs })]
  });
}

function img(name, widthPx, heightPx, maxWidthPt) {
  maxWidthPt = maxWidthPt || 475;
  const scale = Math.min(maxWidthPt / widthPx, 1);
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({
      type: "png",
      data: screenshot(name),
      transformation: { width: Math.round(widthPx * scale), height: Math.round(heightPx * scale) },
      altText: { title: name, description: `Captura ${name}`, name: name }
    })]
  });
}

function imgCaption(text) {
  return new Paragraph({
    spacing: { after: 200 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: FONT, size: 18, italics: true, color: "666666" })]
  });
}

// =========================================
// CONTENIDO
// =========================================
const children = [];

// --- PORTADA ---
children.push(new Paragraph({ spacing: { before: 3000 } }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 200 },
  children: [new TextRun({ text: "RETO 01", font: FONT, size: 52, bold: true, color: AZUL })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 400 },
  children: [new TextRun({ text: "Mini entorno de trabajo con Jupyter Notebook y Apache Airflow", font: FONT, size: 32, color: "444444" })]
}));
children.push(new Paragraph({ spacing: { before: 600 } }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 100 },
  children: [new TextRun({ text: "Big Data Aplicado \u2013 RA4", font: FONT, size: 26, color: "666666" })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 100 },
  children: [new TextRun({ text: "autor Mart\u00EDnez", font: FONT, size: 26, color: "444444", bold: true })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 400 },
  children: [new TextRun({ text: "Curso 2025\u20132026", font: FONT, size: 24, color: "666666" })]
}));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ====================================================
// EJERCICIO 1
// ====================================================
children.push(heading("Ejercicio 1: Instalaci\u00F3n y configuraci\u00F3n del entorno (3 puntos)", HeadingLevel.HEADING_1));

children.push(para("Hemos montado el entorno con Docker Compose, cogiendo como base la estructura del entorno del profesor (hadoop-lab_v6) y adapt\u00E1ndolo para meter Jupyter y Airflow con todo lo necesario para el reto. Tambi\u00E9n nos hemos apoyado bastante en el docker-compose de ejemplo que trae la documentaci\u00F3n oficial de Airflow y en el v\u00EDdeo de Albert Coronado que nos facilit\u00F3 el profesor en clase. A continuaci\u00F3n explicamos paso a paso c\u00F3mo lo hemos ido construyendo, qu\u00E9 hace cada parte y por qu\u00E9 hemos tomado cada decisi\u00F3n."));

// 1.1 DOCKER-COMPOSE
children.push(heading("1.1 docker-compose.yml \u2013 Definici\u00F3n de los servicios", HeadingLevel.HEADING_2));

children.push(para("El fichero docker-compose.yml es el que define todos los servicios del entorno. La estructura la hemos basado en el docker-compose del entorno del profesor (hadoop-lab_v6), pero adaptada para Airflow y Jupyter en vez de Hadoop. Tambi\u00E9n hemos consultado el docker-compose de ejemplo que trae la documentaci\u00F3n oficial de Airflow en su secci\u00F3n \u00ABRunning Airflow in Docker\u00BB."));

// POSTGRES
children.push(heading("Servicio: postgres", HeadingLevel.HEADING_3));
children.push(para("Airflow necesita una base de datos para guardar sus metadatos (DAGs, ejecuciones, logs, usuarios, etc.). Por defecto usa SQLite, pero en la documentaci\u00F3n oficial recomiendan PostgreSQL para entornos m\u00E1s estables, as\u00ED que hemos seguido esa recomendaci\u00F3n."));

children.push(...codeBlock([
  "postgres:",
  "  image: postgres:13",
  "  container_name: reto01-postgres",
  "  environment:",
  "    - POSTGRES_USER=airflow",
  "    - POSTGRES_PASSWORD=airflow",
  "    - POSTGRES_DB=airflow",
  "  volumes:",
  "    - reto01_postgres_data:/var/lib/postgresql/data",
  "  networks:",
  "    - reto01_network"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("image: postgres:13 \u2013 "), normal("Imagen oficial de PostgreSQL versi\u00F3n 13. Hemos usado la 13 porque es la que usa el entorno del profesor y la que aparece en los ejemplos de la documentaci\u00F3n de Airflow. La hemos sacado de Docker Hub.")]));
children.push(multiPara([bold("POSTGRES_USER/PASSWORD/DB \u2013 "), normal("Variables de entorno que vienen documentadas en la p\u00E1gina de la imagen oficial de postgres en Docker Hub. Crean la base de datos \u00ABairflow\u00BB con usuario y contrase\u00F1a \u00ABairflow\u00BB. Luego estos mismos valores los usamos en la cadena de conexi\u00F3n de Airflow.")]));
children.push(multiPara([bold("volumes: reto01_postgres_data \u2013 "), normal("Volumen con nombre para que los datos de PostgreSQL persistan aunque paremos el contenedor. Si no lo pusi\u00E9ramos, al hacer docker compose down se perder\u00EDan todos los datos. Esto lo vimos en la documentaci\u00F3n de Docker sobre vol\u00FAmenes.")]));
children.push(multiPara([bold("networks: reto01_network \u2013 "), normal("Red interna para que los contenedores se comuniquen entre s\u00ED por nombre (por ejemplo, \u00ABpostgres\u00BB o \u00ABreto01-airflow-webserver\u00BB). Lo vimos en el docker-compose del profesor, que tambi\u00E9n usa una red con nombre para todos los servicios.")]));

// AIRFLOW-INIT
children.push(heading("Servicio: airflow-init", HeadingLevel.HEADING_3));
children.push(para("Este servicio se ejecuta una sola vez para preparar la base de datos y crear el usuario administrador. Luego se para autom\u00E1ticamente. Es el mismo patr\u00F3n que usa el docker-compose de ejemplo de la documentaci\u00F3n de Airflow."));

children.push(...codeBlock([
  "airflow-init:",
  "  build:",
  "    context: .",
  "    dockerfile: airflow.Dockerfile",
  "  depends_on:",
  "    - postgres",
  "  environment:",
  "    - AIRFLOW__CORE__EXECUTOR=LocalExecutor",
  "    - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=",
  "        postgresql+psycopg2://airflow:airflow@postgres/airflow",
  "    - AIRFLOW__CORE__LOAD_EXAMPLES=False",
  "    - AIRFLOW__API__AUTH_BACKENDS=",
  "        airflow.api.auth.backend.basic_auth",
  "  entrypoint: bash -c \"airflow db migrate &&",
  "    airflow users create --username admin",
  "    --password admin --firstname Admin",
  "    --lastname User --role Admin",
  "    --email admin@example.com || true\"",
  "  volumes:",
  "    - ./dags:/opt/airflow/dags",
  "    - ./logs:/opt/airflow/logs"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("build: dockerfile: airflow.Dockerfile \u2013 "), normal("Usa nuestro Dockerfile personalizado en vez de la imagen oficial directamente. As\u00ED podemos instalar librer\u00EDas extra como papermill.")]));
children.push(multiPara([bold("depends_on: postgres \u2013 "), normal("Indica que este servicio necesita que PostgreSQL est\u00E9 arrancado antes. Docker Compose lo levanta en orden. Lo vimos en la documentaci\u00F3n de Compose.")]));
children.push(multiPara([bold("AIRFLOW__CORE__EXECUTOR=LocalExecutor \u2013 "), normal("Hemos configurado Airflow para usar LocalExecutor en vez del SequentialExecutor que trae por defecto. LocalExecutor puede ejecutar varias tareas en paralelo y necesita PostgreSQL (no vale SQLite). Lo consultamos en la documentaci\u00F3n oficial de Airflow, secci\u00F3n \u00ABLocal Executor\u00BB.")]));
children.push(multiPara([bold("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN \u2013 "), normal("Cadena de conexi\u00F3n a PostgreSQL. El formato es postgresql+psycopg2://usuario:password@host/basededatos. El host es \u00ABpostgres\u00BB porque es el nombre del servicio en docker-compose, y Docker lo resuelve por DNS interno. Esto lo explican en la secci\u00F3n \u00ABSetting up a PostgreSQL Database\u00BB de la documentaci\u00F3n de Airflow.")]));
children.push(multiPara([bold("AIRFLOW__CORE__LOAD_EXAMPLES=False \u2013 "), normal("Para que no cargue los DAGs de ejemplo que trae Airflow. Si no lo ponemos, aparecen un mont\u00F3n de DAGs de tutorial que molestan. Lo vimos en el docker-compose de ejemplo de la documentaci\u00F3n.")]));
children.push(multiPara([bold("AIRFLOW__API__AUTH_BACKENDS=...basic_auth \u2013 "), normal("Activa la autenticaci\u00F3n b\u00E1sica (usuario y contrase\u00F1a) en la API REST. Sin esto, la API no acepta peticiones con auth=(\u00ABadmin\u00BB, \u00ABadmin\u00BB). Lo encontramos en la secci\u00F3n \u00ABAPI Authentication\u00BB de la documentaci\u00F3n de Airflow, porque al principio nos daba error 403 al intentar conectarnos desde el notebook.")]));
children.push(multiPara([bold("entrypoint: airflow db migrate && airflow users create... \u2013 "), normal("Primero ejecuta airflow db migrate para crear las tablas en PostgreSQL, y luego crea el usuario admin. El || true es para que no falle si el usuario ya existe (al reiniciar). Lo sacamos del docker-compose de ejemplo de la documentaci\u00F3n oficial.")]));
children.push(multiPara([bold("volumes: ./dags, ./logs \u2013 "), normal("Monta las carpetas locales dentro del contenedor con bind mount. As\u00ED los DAGs que ponemos en la carpeta dags/ del proyecto se ven dentro de Airflow. Lo vimos en la documentaci\u00F3n de Docker sobre bind mounts.")]));

// WEBSERVER
children.push(heading("Servicio: airflow-webserver", HeadingLevel.HEADING_3));
children.push(para("La interfaz web de Airflow. Es donde vemos los DAGs, lanzamos ejecuciones y consultamos logs. Se accede en http://localhost:8080."));

children.push(...codeBlock([
  "airflow-webserver:",
  "  build:",
  "    context: .",
  "    dockerfile: airflow.Dockerfile",
  "  depends_on:",
  "    - postgres",
  "    - airflow-init",
  "  ports:",
  "    - \"8080:8080\"",
  "  command: webserver",
  "  volumes:",
  "    - ./dags:/opt/airflow/dags",
  "    - ./logs:/opt/airflow/logs"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("ports: \"8080:8080\" \u2013 "), normal("Mapea el puerto 8080 del contenedor al 8080 del host. As\u00ED podemos acceder a la web de Airflow desde el navegador en localhost:8080.")]));
children.push(multiPara([bold("command: webserver \u2013 "), normal("Le dice a Airflow que arranque en modo webserver. La imagen oficial tiene varios modos (webserver, scheduler, worker...). Lo vimos en la documentaci\u00F3n de la imagen Docker de Airflow, secci\u00F3n \u00ABEntrypoint\u00BB.")]));
children.push(multiPara([bold("depends_on: airflow-init \u2013 "), normal("Espera a que airflow-init termine de crear la BD y el usuario antes de arrancar.")]));

// SCHEDULER
children.push(heading("Servicio: airflow-scheduler", HeadingLevel.HEADING_3));
children.push(para("El scheduler es el que se encarga de ejecutar los DAGs. Sin \u00E9l, Airflow no ejecuta nada. Comparte los mismos vol\u00FAmenes de dags y logs, y adem\u00E1s tiene acceso a los notebooks (para Papermill)."));

children.push(...codeBlock([
  "airflow-scheduler:",
  "  build:",
  "    context: .",
  "    dockerfile: airflow.Dockerfile",
  "  depends_on:",
  "    - airflow-webserver",
  "  volumes:",
  "    - ./dags:/opt/airflow/dags",
  "    - ./logs:/opt/airflow/logs",
  "    - ./notebooks:/opt/airflow/notebooks",
  "  command: scheduler"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("command: scheduler \u2013 "), normal("Arranca Airflow en modo scheduler. El scheduler revisa peri\u00F3dicamente los DAGs y lanza las tareas cuando toca.")]));
children.push(multiPara([bold("./notebooks:/opt/airflow/notebooks \u2013 "), normal("Este volumen es importante: monta la carpeta de notebooks para que el scheduler pueda ejecutar notebooks con Papermill. Sin este volumen, el DAG de Papermill no encontraba los notebooks y nos daba un FileNotFoundError. Lo tuvimos que descubrir probando, porque no ven\u00EDa en ning\u00FAn ejemplo y al principio no ca\u00EDamos en que el scheduler necesitaba acceso a esa carpeta.")]));

// JUPYTER
children.push(heading("Servicio: jupyter", HeadingLevel.HEADING_3));
children.push(para("El contenedor de Jupyter Notebook, donde hacemos todo el trabajo interactivo del reto. Se accede en http://localhost:8888."));

children.push(...codeBlock([
  "jupyter:",
  "  build:",
  "    context: .",
  "    dockerfile: jupyter.Dockerfile",
  "  container_name: reto01-jupyter",
  "  ports:",
  "    - \"8888:8888\"",
  "  environment:",
  "    - JUPYTER_ENABLE_LAB=yes",
  "    - JUPYTER_TOKEN=",
  "    - AIRFLOW__CORE__EXECUTOR=LocalExecutor",
  "    - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=",
  "        postgresql+psycopg2://airflow:airflow@postgres/airflow",
  "    - AIRFLOW__CORE__LOAD_EXAMPLES=False",
  "    - AIRFLOW__CORE__DAGS_FOLDER=/home/jovyan/dags",
  "  command: start-notebook.sh",
  "    --ServerApp.token='' --ServerApp.password=''",
  "  volumes:",
  "    - ./notebooks:/home/jovyan/notebooks",
  "    - ./dags:/home/jovyan/dags"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("JUPYTER_ENABLE_LAB=yes \u2013 "), normal("Activa JupyterLab en vez del Jupyter Notebook cl\u00E1sico. JupyterLab es la interfaz m\u00E1s moderna. Lo vimos en la documentaci\u00F3n de Jupyter Docker Stacks, secci\u00F3n \u00ABCommon Features\u00BB.")]));
children.push(multiPara([bold("JUPYTER_TOKEN= (vac\u00EDo) \u2013 "), normal("Desactiva el token de acceso para no tener que buscarlo en los logs cada vez que arrancamos el contenedor. Solo lo hacemos as\u00ED porque es un entorno local de desarrollo; en producci\u00F3n no se har\u00EDa.")]));
children.push(multiPara([bold("Variables AIRFLOW__* \u2013 "), normal("Las mismas variables de Airflow que en los otros servicios. Las ponemos aqu\u00ED para que la CLI de Airflow (que est\u00E1 instalada en este contenedor) sepa conectarse a la misma base de datos PostgreSQL que usa el scheduler. Sin estas variables, la CLI no funciona porque no sabe d\u00F3nde est\u00E1 la BD. Esto lo descubrimos despu\u00E9s de que nos diera error al ejecutar !airflow dags list en el notebook: nos sal\u00EDa un error de conexi\u00F3n a SQLite porque por defecto Airflow busca una BD local.")]));
children.push(multiPara([bold("AIRFLOW__CORE__DAGS_FOLDER=/home/jovyan/dags \u2013 "), normal("Le dice a Airflow d\u00F3nde buscar los DAGs dentro de este contenedor. Como Jupyter usa el usuario jovyan con home en /home/jovyan, la ruta es distinta a la de los contenedores de Airflow (/opt/airflow/dags). El contenido es el mismo porque ambos montan la carpeta ./dags del host.")]));
children.push(multiPara([bold("command: start-notebook.sh --ServerApp.token='' \u2013 "), normal("Arranca Jupyter sin token ni contrase\u00F1a. Ponemos la doble seguridad (variable + argumento) porque encontramos en un issue de GitHub del repositorio jupyter/docker-stacks (issue #1505) que a veces la variable JUPYTER_TOKEN vac\u00EDa sola no basta.")]));
children.push(multiPara([bold("volumes: notebooks + dags \u2013 "), normal("Monta las carpetas de notebooks y dags para que se puedan editar desde Jupyter y que los cambios persistan en el host.")]));

// RED Y VOLUMENES
children.push(heading("Red y vol\u00FAmenes", HeadingLevel.HEADING_3));
children.push(...codeBlock([
  "networks:",
  "  reto01_network:",
  "    name: reto01_network",
  "",
  "volumes:",
  "  reto01_postgres_data:"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));
children.push(multiPara([bold("reto01_network \u2013 "), normal("Red bridge personalizada. Todos los servicios est\u00E1n en esta red para que se vean entre s\u00ED por nombre DNS. Le ponemos name: para que el nombre sea fijo; si no, Docker le pone un prefijo con el nombre del proyecto.")]));
children.push(multiPara([bold("reto01_postgres_data \u2013 "), normal("Volumen con nombre para persistir los datos de PostgreSQL. A diferencia de los bind mounts (./dags), los vol\u00FAmenes con nombre los gestiona Docker y no se borran con docker compose down (solo con docker compose down -v).")]));

// 1.2 AIRFLOW DOCKERFILE
children.push(heading("1.2 airflow.Dockerfile \u2013 L\u00EDnea por l\u00EDnea", HeadingLevel.HEADING_2));

children.push(para("Este Dockerfile extiende la imagen oficial de Airflow para instalar las librer\u00EDas que necesitamos para el ejercicio 3 (Papermill)."));

children.push(...codeBlock([
  "FROM apache/airflow:2.8.3",
  "RUN pip install --no-cache-dir papermill ipykernel"
]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("FROM apache/airflow:2.8.3 \u2013 "), normal("Imagen oficial de Airflow versi\u00F3n 2.8.3 de Docker Hub. Hemos usado la misma versi\u00F3n que usa el profesor en su entorno para no tener problemas de compatibilidad.")]));
children.push(multiPara([bold("pip install papermill \u2013 "), normal("Papermill es la librer\u00EDa que permite ejecutar notebooks de Jupyter de forma program\u00E1tica, pas\u00E1ndoles par\u00E1metros. Lo necesita el scheduler para poder ejecutar el DAG dag_papermill. Lo consultamos en la documentaci\u00F3n oficial de Papermill.")]));
children.push(multiPara([bold("pip install ipykernel \u2013 "), normal("Papermill necesita un kernel de Jupyter para ejecutar los notebooks. Sin ipykernel, Papermill nos daba error \u00ABNo kernel found\u00BB. Lo descubrimos buscando el error en GitHub y encontramos el issue #399 del repositorio nteract/papermill donde lo explican.")]));
children.push(multiPara([bold("--no-cache-dir \u2013 "), normal("Flag de pip para no guardar cach\u00E9 de las descargas. Reduce el tama\u00F1o de la imagen Docker. Es una buena pr\u00E1ctica que viene en la gu\u00EDa de mejores pr\u00E1cticas de Dockerfiles de la documentaci\u00F3n de Docker.")]));

// 1.3 JUPYTER DOCKERFILE
children.push(heading("1.3 jupyter.Dockerfile \u2013 L\u00EDnea por l\u00EDnea", HeadingLevel.HEADING_2));

children.push(para("Este es el Dockerfile m\u00E1s largo porque el contenedor de Jupyter necesita muchas cosas. Adem\u00E1s de las librer\u00EDas b\u00E1sicas que pide el reto, hemos tenido que ir a\u00F1adiendo dependencias extra para solucionar warnings y errores que nos fueron saliendo al ejecutar el notebook. Explicamos cada l\u00EDnea y por qu\u00E9 est\u00E1:"));

children.push(...codeBlock(["FROM jupyter/base-notebook:python-3.11"]));
children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(multiPara([bold("FROM jupyter/base-notebook:python-3.11 \u2013 "), normal("Imagen oficial de Jupyter con Python 3.11 de Docker Hub. Hemos usado base-notebook (la m\u00E1s ligera) en vez de scipy-notebook o datascience-notebook porque para este reto no necesitamos librer\u00EDas de ciencia de datos.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(...codeBlock(["USER root"]));
children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(multiPara([bold("USER root \u2013 "), normal("Cambiamos al usuario root para poder instalar paquetes con apt-get. La imagen de Jupyter usa por defecto el usuario jovyan (sin permisos de root). Esto lo explican en la documentaci\u00F3n de Jupyter Docker Stacks, secci\u00F3n \u00ABUsing apt-get install\u00BB.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(...codeBlock([
  "RUN apt-get update && apt-get install -y \\",
  "    --no-install-recommends \\",
  "    graphviz tzdata pandoc \\",
  "    texlive-xetex texlive-fonts-recommended \\",
  "    texlive-plain-generic \\",
  "    && rm -rf /var/lib/apt/lists/*"
]));
children.push(new Paragraph({ spacing: { after: 40 } }));

children.push(para("Paquetes del sistema que hemos tenido que instalar. Los dos primeros (graphviz y tzdata) los tuvimos que a\u00F1adir despu\u00E9s de que nos salieran warnings al importar Airflow en el notebook. Los dem\u00E1s (pandoc y texlive) los a\u00F1adimos para poder exportar notebooks a PDF:"));

children.push(multiPara([bold("graphviz \u2013 "), normal("Paquete del sistema para renderizar grafos. Nos sal\u00EDa el warning \u00ABCould not import graphviz\u00BB al importar Airflow en el notebook. En la documentaci\u00F3n de Airflow (secci\u00F3n \u00ABOptional dependencies\u00BB) explican que graphviz es una dependencia opcional. Hay que instalar tanto el paquete del sistema (este) como la librer\u00EDa de Python (m\u00E1s abajo).")]));
children.push(multiPara([bold("tzdata \u2013 "), normal("Datos de zonas horarias. Nos sal\u00EDa \u00ABUserWarning: Unable to find timezone\u00BB porque la imagen base de Jupyter (basada en Ubuntu minimal) no los trae. La soluci\u00F3n la encontramos en Stack Overflow buscando \u00ABDocker timezone in Ubuntu image\u00BB.")]));
children.push(multiPara([bold("pandoc \u2013 "), normal("Conversor de documentos que usa nbconvert para exportar notebooks. Lo vimos en la documentaci\u00F3n de nbconvert, secci\u00F3n \u00ABInstalling Pandoc\u00BB.")]));
children.push(multiPara([bold("texlive-xetex, texlive-fonts-recommended, texlive-plain-generic \u2013 "), normal("Motor LaTeX necesario para generar PDF desde notebooks (File > Save and Export as > PDF). Sin estos paquetes, Jupyter nos daba error al intentar exportar. Lo sacamos de la documentaci\u00F3n de nbconvert, secci\u00F3n \u00ABInstalling TeX\u00BB.")]));
children.push(multiPara([bold("--no-install-recommends \u2013 "), normal("Para instalar solo lo estrictamente necesario sin paquetes recomendados. Reduce el tama\u00F1o de la imagen.")]));
children.push(multiPara([bold("rm -rf /var/lib/apt/lists/* \u2013 "), normal("Limpia la cach\u00E9 de apt para reducir el tama\u00F1o de la imagen. Es una buena pr\u00E1ctica de Dockerfiles.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(...codeBlock([
  "RUN pip install --no-cache-dir \\",
  "    requests \\",
  "    papermill \\",
  "    ipywidgets \\",
  "    graphviz \\",
  "    apache-airflow==2.8.3 \\",
  "    apache-airflow-providers-postgres==5.10.0"
]));
children.push(new Paragraph({ spacing: { after: 40 } }));

children.push(para("Librer\u00EDas de Python. Las separamos entre las que pide el reto y las que hemos tenido que a\u00F1adir por problemas que nos fueron saliendo:"));

children.push(para("Librer\u00EDas necesarias para el reto:", { bold: true }));
children.push(multiPara([bold("requests \u2013 "), normal("Para hacer llamadas HTTP a la API REST de Airflow desde el notebook (GET, POST, PATCH). Es la librer\u00EDa est\u00E1ndar de Python para peticiones HTTP.")]));
children.push(multiPara([bold("papermill \u2013 "), normal("Para ejecutar notebooks con par\u00E1metros desde c\u00F3digo (ejercicio 3). Lo consultamos en su documentaci\u00F3n oficial.")]));
children.push(multiPara([bold("apache-airflow==2.8.3 \u2013 "), normal("Para poder usar la CLI de Airflow (!airflow dags list, etc.) directamente desde Jupyter. Hemos puesto la misma versi\u00F3n (2.8.3) que en los contenedores de Airflow para que no haya incompatibilidades. La idea de instalar Airflow en Jupyter la sacamos del entorno del profesor, donde todos los servicios comparten la misma versi\u00F3n.")]));
children.push(multiPara([bold("apache-airflow-providers-postgres==5.10.0 \u2013 "), normal("Proveedor de PostgreSQL para Airflow. Sin este paquete, la CLI de Airflow no puede conectarse a la BD de PostgreSQL (solo soportar\u00EDa SQLite). Lo descubrimos porque al ejecutar !airflow dags list nos daba error de conexi\u00F3n. Lo consultamos en la documentaci\u00F3n del proveedor de PostgreSQL de Airflow.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(para("Librer\u00EDas extra para solucionar warnings:", { bold: true }));
children.push(multiPara([bold("ipywidgets \u2013 "), normal("Al ejecutar celdas que importan Airflow nos sal\u00EDa \u00ABTqdmWarning: IProgress not found\u00BB. El propio mensaje del warning dice la soluci\u00F3n: instalar ipywidgets. Lo confirmamos en la documentaci\u00F3n de tqdm sobre integraci\u00F3n con notebooks.")]));
children.push(multiPara([bold("graphviz (pip) \u2013 "), normal("Librer\u00EDa de Python para graphviz. Complementa el paquete del sistema instalado con apt. Sin la librer\u00EDa de Python sigue saliendo el warning aunque tengas el paquete del sistema. Lo vimos en la documentaci\u00F3n de Graphviz para Python.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(...codeBlock(["ENV PYDEVD_DISABLE_FILE_VALIDATION=1"]));
children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(multiPara([bold("ENV PYDEVD_DISABLE_FILE_VALIDATION=1 \u2013 "), normal("Variable de entorno para desactivar un warning del debugger de Python sobre frozen modules que nos sal\u00EDa cada vez que se iniciaba el kernel. La soluci\u00F3n la encontramos en el issue #1374 del repositorio microsoft/debugpy en GitHub.")]));

children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(...codeBlock([
  "USER jovyan",
  "WORKDIR /home/jovyan"
]));
children.push(new Paragraph({ spacing: { after: 40 } }));
children.push(multiPara([bold("USER jovyan \u2013 "), normal("Volvemos al usuario jovyan (el usuario por defecto de la imagen de Jupyter) por seguridad. No es buena pr\u00E1ctica ejecutar Jupyter como root.")]));
children.push(multiPara([bold("WORKDIR /home/jovyan \u2013 "), normal("Directorio de trabajo del contenedor. Es el home del usuario jovyan y donde Jupyter muestra los ficheros.")]));

// 1.4 WARNING NOTEBOOK
children.push(heading("1.4 Warning extra solucionado en el notebook", HeadingLevel.HEADING_2));

children.push(para("Adem\u00E1s de todo lo anterior, al ejecutar el notebook nos quedaba un DeprecationWarning de la librer\u00EDa Pendulum (que usa Airflow internamente para manejar fechas). El warning dec\u00EDa algo como \u00AB__version__ is deprecated\u00BB. No se puede solucionar instalando nada porque es un problema de compatibilidad entre Airflow 2.8.3 y Pendulum. La soluci\u00F3n la encontramos en Stack Overflow buscando \u00ABsuppress DeprecationWarning Pendulum\u00BB: simplemente filtramos el warning con warnings.filterwarnings."));

children.push(...codeBlock([
  "# para quitar el warning de pendulum que sale con airflow 2.8.3",
  "import warnings",
  "warnings.filterwarnings(\"ignore\", message=\".*__version__.*deprecated.*\")"
]));
children.push(new Paragraph({ spacing: { after: 120 } }));

// 1.5 PUESTA EN MARCHA
children.push(heading("1.5 Puesta en marcha y verificaci\u00F3n", HeadingLevel.HEADING_2));

children.push(para("Para levantar todo el entorno ejecutamos este comando desde la carpeta del proyecto en PowerShell o CMD:"));
children.push(...codeBlock(["docker compose up --build -d"]));
children.push(new Paragraph({ spacing: { after: 80 } }));

children.push(multiPara([bold("docker compose up \u2013 "), normal("Levanta todos los servicios definidos en docker-compose.yml.")]));
children.push(multiPara([bold("--build \u2013 "), normal("Fuerza la reconstrucci\u00F3n de las im\u00E1genes (por si hemos cambiado alg\u00FAn Dockerfile). Sin este flag, Docker usa la imagen cacheada.")]));
children.push(multiPara([bold("-d \u2013 "), normal("Modo detached (en segundo plano). Si no lo ponemos, los logs de todos los contenedores salen por la terminal y al cerrarla se paran.")]));

children.push(new Paragraph({ spacing: { after: 80 } }));
children.push(para("El servicio airflow-init se ejecuta una vez para crear la BD y el usuario admin (admin/admin), y se para solo. Los dem\u00E1s contenedores se quedan corriendo."));

children.push(para("Para verificar que todo est\u00E1 funcionando usamos docker ps:"));
children.push(img("132405", 1504, 812, 475));
children.push(imgCaption("Figura 1: docker ps mostrando los 4 contenedores en ejecuci\u00F3n (el airflow-init ya se ha parado porque solo se ejecuta una vez)"));

children.push(para("Una vez arrancado, accedemos a:"));
children.push(multiPara([bold("Airflow: "), normal("http://localhost:8080 (usuario: admin, contrase\u00F1a: admin)")]));
children.push(multiPara([bold("Jupyter: "), normal("http://localhost:8888 (sin token, lo configuramos sin autenticaci\u00F3n)")]));

children.push(para("Interfaz web de Airflow con los DAGs visibles:"));
children.push(img("125419", 1504, 812, 475));
children.push(imgCaption("Figura 2: Airflow mostrando los DAGs test1 y dag_papermill"));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ====================================================
// EJERCICIO 2
// ====================================================
children.push(heading("Ejercicio 2: Jupyter Notebook como cliente de Airflow (3 puntos)", HeadingLevel.HEADING_1));

children.push(para("Aqu\u00ED demostramos c\u00F3mo usar Jupyter como cliente de Airflow de dos formas: con la API REST y con la CLI. Hemos trabajado con el DAG test1, que est\u00E1 sacado del v\u00EDdeo de Albert Coronado que nos facilit\u00F3 el profesor en clase."));

children.push(heading("2.1 El DAG test1 (del v\u00EDdeo de Albert Coronado)", HeadingLevel.HEADING_2));

children.push(para("El DAG tiene 3 tareas que reproducen el workflow del v\u00EDdeo:"));

children.push(multiPara([bold("tarea0 (PythonOperator): "), normal("Lee par\u00E1metros del dag_run.conf. Si recibe commit=\"1\", lanza un AirflowFailException (error controlado). Si no, devuelve {\"ok\": 1} por XCom.")]));
children.push(multiPara([bold("print_date (BashOperator): "), normal("Imprime la fecha con un echo. Es la tarea Bash que pide el enunciado.")]));
children.push(multiPara([bold("tarea2 (PythonOperator): "), normal("Recoge el valor de tarea0 con xcom_pull y lo imprime. Es la segunda tarea Python que lee informaci\u00F3n de la primera mediante XCom, como pide el enunciado.")]));
children.push(multiPara([bold("Dependencias: "), normal("tarea0 >> [print_date, tarea2]. Primero se ejecuta tarea0 y luego las otras dos en paralelo. Esta es la relaci\u00F3n de dependencias entre tareas que pide el enunciado.")]));

children.push(heading("2.2 API REST de Airflow desde Jupyter", HeadingLevel.HEADING_2));

children.push(para("Airflow tiene una API REST en el puerto 8080. Para conectarnos usamos autenticaci\u00F3n b\u00E1sica con usuario admin/admin (se configura en el entrypoint de airflow-init en el docker-compose). La URL base es http://reto01-airflow-webserver:8080/api/v1 (usamos el nombre del contenedor en docker-compose porque estamos dentro de la misma red Docker)."));

children.push(para("En el notebook hemos hecho estas operaciones con la API:"));
children.push(multiPara([bold("1. Conexi\u00F3n: "), normal("Definimos la URL base y las credenciales con requests.")]));
children.push(multiPara([bold("2. Activar DAG: "), normal("PATCH a /dags/test1 con {\"is_paused\": false} para activarlo.")]));
children.push(multiPara([bold("3. Lanzar ejecuci\u00F3n: "), normal("POST a /dags/test1/dagRuns con par\u00E1metros en conf.")]));
children.push(multiPara([bold("4. Consultar estado: "), normal("GET a /dags/test1/dagRuns/{id}/taskInstances para ver el estado de cada tarea.")]));
children.push(multiPara([bold("5. Ver logs: "), normal("GET a /dags/test1/dagRuns/{id}/taskInstances/{task}/logs/1 para consultar los logs de una tarea.")]));

children.push(para("Inicio del notebook con la configuraci\u00F3n de conexi\u00F3n:"));
children.push(img("125825", 1504, 812, 475));
children.push(imgCaption("Figura 3: Notebook \u2013 conexi\u00F3n a la API REST y configuraci\u00F3n"));

children.push(para("Lanzamiento del DAG y consulta de estado:"));
children.push(img("125938", 1504, 812, 475));
children.push(imgCaption("Figura 4: Notebook \u2013 lanzar DAG y consultar estado"));

children.push(para("Resultado con todas las tareas completadas:"));
children.push(img("130037", 1504, 812, 475));
children.push(imgCaption("Figura 5: Todas las tareas del DAG en estado success"));

children.push(heading("2.3 Error controlado con AirflowFailException", HeadingLevel.HEADING_2));

children.push(para("Al lanzar el DAG con commit=\"1\" (como en el v\u00EDdeo de Albert Coronado), la tarea0 lanza un AirflowFailException a prop\u00F3sito. Esto hace que:"));
children.push(multiPara([normal("\u2013 tarea0 queda en estado "), bold("failed")]));
children.push(multiPara([normal("\u2013 print_date y tarea2 quedan en "), bold("upstream_failed"), normal(" (dependen de tarea0)")]));
children.push(multiPara([normal("\u2013 El DAG Run completo queda en "), bold("failed")]));

children.push(para("Esto demuestra el mecanismo de error controlado y c\u00F3mo las dependencias entre tareas hacen que, si falla una tarea de la que dependen otras, las dem\u00E1s no se ejecutan. Es exactamente lo que se ve en el v\u00EDdeo."));

children.push(img("130435", 1504, 812, 475));
children.push(imgCaption("Figura 6: Error controlado \u2013 tarea0 failed, las dem\u00E1s upstream_failed"));

children.push(heading("2.4 CLI de Airflow desde Jupyter", HeadingLevel.HEADING_2));

children.push(para("Como en el contenedor de Jupyter tambi\u00E9n hemos instalado Airflow (lo pusimos en el Dockerfile para poder usar la CLI), podemos lanzar comandos directamente con ! desde las celdas del notebook. Comparte la misma base de datos PostgreSQL que el scheduler, as\u00ED que ve los mismos DAGs y ejecuciones."));

children.push(para("Los comandos que hemos probado son:"));
children.push(multiPara([bold("!airflow dags list 2>/dev/null \u2013 "), normal("Lista todos los DAGs registrados en Airflow.")]));
children.push(multiPara([bold("!airflow tasks list test1 2>/dev/null \u2013 "), normal("Lista las tareas del DAG test1.")]));
children.push(multiPara([bold("!airflow version 2>/dev/null \u2013 "), normal("Muestra la versi\u00F3n de Airflow instalada.")]));
children.push(para("El 2>/dev/null al final es para ocultar los warnings de Pendulum que salen por stderr y que ensucian la salida. No afecta al resultado del comando."));

children.push(img("130515", 1504, 812, 475));
children.push(imgCaption("Figura 7: CLI de Airflow \u2013 listar DAGs, tareas y versi\u00F3n"));

children.push(heading("2.5 Ventajas de usar Jupyter como cliente de Airflow", HeadingLevel.HEADING_2));

children.push(multiPara([bold("Para pruebas r\u00E1pidas: "), normal("podemos lanzar DAGs, cambiar par\u00E1metros y relanzar sin salir del notebook. No hace falta ir a la interfaz web de Airflow cada vez.")]));
children.push(multiPara([bold("Para automatizaci\u00F3n: "), normal("con la API REST podemos controlar Airflow por c\u00F3digo, encadenando lanzamientos y consultas de estado en un mismo flujo.")]));
children.push(multiPara([bold("Para aprendizaje: "), normal("Jupyter permite mezclar c\u00F3digo con texto explicativo, as\u00ED queda todo documentado paso a paso. Ideal para ir aprendiendo y experimentando.")]));
children.push(multiPara([bold("API REST vs CLI: "), normal("la API funciona por red entre contenedores (de forma remota), mientras que la CLI necesita tener Airflow instalado en la misma m\u00E1quina. Desde Jupyter podemos usar las dos, lo que nos da m\u00E1s flexibilidad.")]));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ====================================================
// EJERCICIO 3
// ====================================================
children.push(heading("Ejercicio 3: Integraci\u00F3n de Airflow con Jupyter mediante Papermill (4 puntos)", HeadingLevel.HEADING_1));

children.push(para("En este ejercicio usamos Papermill para ejecutar notebooks de forma program\u00E1tica desde Airflow, pas\u00E1ndoles par\u00E1metros. As\u00ED Jupyter pasa de ser \u00ABcliente\u00BB de Airflow a ser \u00ABcontenido ejecutado\u00BB por Airflow, como pide el enunciado."));

children.push(heading("3.1 Notebook parametrizable", HeadingLevel.HEADING_2));

children.push(para("Hemos creado el notebook notebook_parametrizable.ipynb con una celda marcada con el tag \u00ABparameters\u00BB (se pone desde el men\u00FA de Jupyter: View > Cell Toolbar > Tags). Los valores por defecto son:"));

children.push(...codeBlock([
  "# Celda con tag: parameters",
  "nombre = \"Mundo\"",
  "repeticiones = 3"
]));
children.push(new Paragraph({ spacing: { after: 120 } }));

children.push(para("Cuando Papermill ejecuta este notebook, inyecta una celda nueva despu\u00E9s de la de par\u00E1metros con los valores que le pasemos, machacando los valores por defecto. Esto lo explican en la documentaci\u00F3n oficial de Papermill."));

children.push(heading("3.2 Prueba local desde Jupyter", HeadingLevel.HEADING_2));

children.push(para("Primero lo probamos desde el propio notebook para ver que funcionaba bien antes de meterlo en un DAG:"));
children.push(...codeBlock([
  "import papermill as pm",
  "",
  "pm.execute_notebook(",
  "    input_path=\"notebook_parametrizable.ipynb\",",
  "    output_path=\"notebook_output_local.ipynb\",",
  "    parameters={\"nombre\": \"Alumno\", \"repeticiones\": 5}",
  ")"
]));
children.push(new Paragraph({ spacing: { after: 120 } }));

children.push(heading("3.3 DAG dag_papermill", HeadingLevel.HEADING_2));

children.push(para("El DAG dag_papermill.py tiene un PythonOperator que llama a Papermill para ejecutar el notebook. Los par\u00E1metros se pasan desde el conf del DAG Run, as\u00ED que cada vez que lanzamos el DAG podemos pasarle valores distintos:"));

children.push(...codeBlock([
  "def ejecutar_notebook(**kwargs):",
  "    import papermill as pm",
  "    conf = kwargs['dag_run'].conf or {}",
  "    nombre = conf.get('nombre', 'Mundo')",
  "    repeticiones = conf.get('repeticiones', 3)",
  "",
  "    pm.execute_notebook(",
  "        input_path='/opt/airflow/notebooks/notebook_parametrizable.ipynb',",
  "        output_path='/opt/airflow/notebooks/notebook_output.ipynb',",
  "        parameters={'nombre': nombre, 'repeticiones': repeticiones}",
  "    )"
]));
children.push(new Paragraph({ spacing: { after: 120 } }));

children.push(para("La ruta del input_path es /opt/airflow/notebooks/ porque es la ruta dentro del contenedor del scheduler (que es el que ejecuta el DAG). Por eso es tan importante el volumen ./notebooks:/opt/airflow/notebooks que pusimos en el docker-compose para el scheduler."));

children.push(heading("3.4 Ejecuci\u00F3n desde Jupyter v\u00EDa API REST", HeadingLevel.HEADING_2));

children.push(para("Desde el notebook, lanzamos el DAG dag_papermill pas\u00E1ndole par\u00E1metros con la API REST, igual que hicimos con el test1 en el ejercicio 2:"));

children.push(img("130649", 1504, 812, 475));
children.push(imgCaption("Figura 8: DAG de Papermill ejecutado con \u00E9xito (ejecutar_notebook: success)"));

children.push(para("El notebook ejecutado se guarda en notebooks/notebook_output.ipynb con los par\u00E1metros inyectados y los resultados de la ejecuci\u00F3n."));

children.push(heading("3.5 Flujo completo", HeadingLevel.HEADING_2));

children.push(para("El flujo completo de integraci\u00F3n Airflow-Jupyter mediante Papermill queda as\u00ED:"));

children.push(multiPara([bold("1. "), normal("Creamos un notebook parametrizable con valores por defecto y la celda marcada con el tag \u00ABparameters\u00BB.")]));
children.push(multiPara([bold("2. "), normal("Creamos un DAG en Airflow con un PythonOperator que llama a Papermill.")]));
children.push(multiPara([bold("3. "), normal("Desde Jupyter, lanzamos el DAG por API REST pasando los par\u00E1metros que queramos.")]));
children.push(multiPara([bold("4. "), normal("Airflow ejecuta el DAG, que a su vez ejecuta el notebook con Papermill inyect\u00E1ndole los par\u00E1metros.")]));
children.push(multiPara([bold("5. "), normal("El notebook ejecutado se guarda como output para poder ver los resultados.")]));

children.push(new Paragraph({ spacing: { after: 200 } }));

children.push(para("Con esto conseguimos usar notebooks como tareas dentro de pipelines de Airflow sin tener que reescribir el c\u00F3digo como scripts de Python, y manteniendo toda la interactividad de Jupyter."));

// ====================================================
// CONCLUSIONES
// ====================================================
children.push(heading("Conclusiones", HeadingLevel.HEADING_1));

children.push(para("Con este reto hemos aprendido a montar un entorno con Docker Compose que integra Jupyter y Airflow, cogiendo como referencia el entorno del profesor (hadoop-lab_v6) y el v\u00EDdeo de Albert Coronado que nos facilit\u00F3 en clase."));

children.push(para("Lo que m\u00E1s nos ha costado ha sido configurar el contenedor de Jupyter para que pudiera usar tanto la API REST como la CLI de Airflow. Al final la soluci\u00F3n fue instalar el propio Airflow dentro del contenedor de Jupyter y apuntarlo a la misma base de datos PostgreSQL que usa el scheduler. Esto no ven\u00EDa en ning\u00FAn tutorial directamente, sino que lo fuimos descubriendo a base de probar y buscar errores."));

children.push(para("Tambi\u00E9n nos dio bastantes problemas los warnings que sal\u00EDan al importar Airflow en Jupyter (graphviz, tzdata, Pendulum, ipywidgets...). Cada uno lo tuvimos que ir solucionando buscando en la documentaci\u00F3n, Stack Overflow y issues de GitHub. Lo hemos documentado todo para que si alguien tiene que montar el mismo entorno sepa de d\u00F3nde sale cada dependencia y por qu\u00E9 est\u00E1."));

children.push(para("Papermill nos ha parecido muy \u00FAtil porque permite ejecutar notebooks desde Airflow sin tener que convertirlos a scripts de Python. Simplemente marcas una celda con el tag \u00ABparameters\u00BB y Papermill se encarga de inyectar los valores nuevos."));

children.push(para("En resumen, las tres formas de interactuar con Airflow desde Jupyter son:"));
children.push(multiPara([bold("API REST: "), normal("Funciona por red entre contenedores, muy flexible para automatizar.")]));
children.push(multiPara([bold("CLI: "), normal("Requiere tener Airflow instalado, pero es m\u00E1s directa para consultas r\u00E1pidas.")]));
children.push(multiPara([bold("Papermill: "), normal("Permite ejecutar notebooks como tareas de Airflow, pas\u00E1ndoles par\u00E1metros.")]));

// ====================================================
// BIBLIOGRAF\u00CDA
// ====================================================
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading("Bibliograf\u00EDa y referencias", HeadingLevel.HEADING_1));

children.push(para("A continuaci\u00F3n listamos todas las fuentes que hemos consultado durante el desarrollo de este reto. Incluimos documentaci\u00F3n oficial, foros, repositorios de GitHub y otras fuentes que nos han servido para resolver los distintos problemas que nos han ido saliendo."));

children.push(heading("Documentaci\u00F3n oficial", HeadingLevel.HEADING_2));

const refStyle = { font: FONT, size: 20 };
const refEntries = [
  ["Apache Airflow", "Running Airflow in Docker", "https://airflow.apache.org/docs/apache-airflow/2.8.3/howto/docker-compose/index.html", "Docker-compose de ejemplo y configuraci\u00F3n inicial"],
  ["Apache Airflow", "Set up a Database Backend", "https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html", "Configuraci\u00F3n de PostgreSQL como backend"],
  ["Apache Airflow", "Local Executor", "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/local.html", "Configuraci\u00F3n del executor"],
  ["Apache Airflow", "API Authentication", "https://airflow.apache.org/docs/apache-airflow/stable/security/api.html", "Activar basic_auth en la API REST"],
  ["Apache Airflow", "Docker Stack Entrypoint", "https://airflow.apache.org/docs/docker-stack/entrypoint.html", "Modos de arranque de la imagen Docker"],
  ["Apache Airflow", "Optional dependencies", "https://airflow.apache.org/docs/apache-airflow/stable/installation/dependencies.html", "Dependencia de graphviz"],
  ["Apache Airflow", "PostgreSQL Provider", "https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/index.html", "Proveedor para conectar la CLI a PostgreSQL"],
  ["Docker Docs", "Volumes", "https://docs.docker.com/storage/volumes/", "Vol\u00FAmenes con nombre para persistencia"],
  ["Docker Docs", "Bind mounts", "https://docs.docker.com/storage/bind-mounts/", "Montar carpetas locales en contenedores"],
  ["Docker Docs", "Compose \u2013 depends_on", "https://docs.docker.com/compose/compose-file/05-services/#depends_on", "Orden de arranque de servicios"],
  ["Docker Docs", "Dockerfile best practices", "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run", "Buenas pr\u00E1cticas (--no-cache-dir, rm lists)"],
  ["Docker Hub", "postgres (imagen oficial)", "https://hub.docker.com/_/postgres", "Variables de entorno de PostgreSQL"],
  ["Docker Hub", "apache/airflow", "https://hub.docker.com/r/apache/airflow/tags", "Imagen oficial de Airflow 2.8.3"],
  ["Docker Hub", "jupyter/base-notebook", "https://hub.docker.com/r/jupyter/base-notebook", "Imagen base de Jupyter"],
  ["Jupyter Docker Stacks", "Common Features", "https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html", "JUPYTER_ENABLE_LAB y configuraci\u00F3n"],
  ["Jupyter Docker Stacks", "Using apt-get install", "https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html#using-apt-get-install", "Instalar paquetes de sistema como root"],
  ["Papermill", "Documentaci\u00F3n oficial", "https://papermill.readthedocs.io/en/latest/", "Ejecuci\u00F3n parametrizada de notebooks"],
  ["Requests", "Documentaci\u00F3n oficial", "https://requests.readthedocs.io/", "Librer\u00EDa HTTP para Python"],
  ["nbconvert", "Installing Pandoc", "https://nbconvert.readthedocs.io/en/latest/install.html#installing-pandoc", "Pandoc para exportar notebooks"],
  ["nbconvert", "Installing TeX", "https://nbconvert.readthedocs.io/en/latest/install.html#installing-tex", "LaTeX para exportar notebooks a PDF"],
  ["Graphviz (Python)", "Installation", "https://graphviz.readthedocs.io/en/stable/manual.html#installation", "Librer\u00EDa Python de graphviz"],
  ["tqdm", "Notebook integration", "https://tqdm.github.io/docs/notebook/", "ipywidgets para barras de progreso en notebooks"],
];

refEntries.forEach(([source, title, url, note]) => {
  children.push(new Paragraph({
    spacing: { after: 80 },
    indent: { left: 360, hanging: 360 },
    children: [
      new TextRun({ text: `${source}. `, ...refStyle, bold: true }),
      new TextRun({ text: `\u00AB${title}\u00BB. `, ...refStyle, italics: true }),
      new TextRun({ text: url, ...refStyle, color: "2255AA" }),
      new TextRun({ text: ` \u2013 ${note}.`, ...refStyle, color: "666666" }),
    ]
  }));
});

children.push(heading("Foros y repositorios de GitHub", HeadingLevel.HEADING_2));

const forumRefs = [
  ["Stack Overflow", "Docker timezone in Ubuntu image", "https://stackoverflow.com/questions/40234847", "Soluci\u00F3n al warning de tzdata en la imagen de Jupyter"],
  ["Stack Overflow", "Suppress DeprecationWarning Pendulum", "https://stackoverflow.com/questions/77345/suppress-deprecationwarning", "Filtrar el warning de Pendulum con warnings.filterwarnings"],
  ["GitHub, jupyter/docker-stacks", "Issue #1505", "https://github.com/jupyter/docker-stacks/issues/1505", "Desactivar el token de Jupyter en Docker"],
  ["GitHub, nteract/papermill", "Issue #399", "https://github.com/nteract/papermill/issues/399", "Error \u00ABNo kernel found\u00BB: soluci\u00F3n instalar ipykernel"],
  ["GitHub, microsoft/debugpy", "Issue #1374", "https://github.com/microsoft/debugpy/issues/1374", "Warning de frozen modules: soluci\u00F3n PYDEVD_DISABLE_FILE_VALIDATION"],
];

forumRefs.forEach(([source, title, url, note]) => {
  children.push(new Paragraph({
    spacing: { after: 80 },
    indent: { left: 360, hanging: 360 },
    children: [
      new TextRun({ text: `${source}. `, ...refStyle, bold: true }),
      new TextRun({ text: `\u00AB${title}\u00BB. `, ...refStyle, italics: true }),
      new TextRun({ text: url, ...refStyle, color: "2255AA" }),
      new TextRun({ text: ` \u2013 ${note}.`, ...refStyle, color: "666666" }),
    ]
  }));
});

children.push(heading("Otras fuentes", HeadingLevel.HEADING_2));

children.push(new Paragraph({
  spacing: { after: 80 },
  indent: { left: 360, hanging: 360 },
  children: [
    new TextRun({ text: "Albert Coronado. ", ...refStyle, bold: true }),
    new TextRun({ text: "V\u00EDdeo tutorial sobre Apache Airflow, facilitado por el profesor en clase. ", ...refStyle, italics: true }),
    new TextRun({ text: "Base para el DAG test1 (tarea0, print_date, tarea2) y la estructura general del workflow.", ...refStyle, color: "666666" }),
  ]
}));

children.push(new Paragraph({
  spacing: { after: 80 },
  indent: { left: 360, hanging: 360 },
  children: [
    new TextRun({ text: "Entorno hadoop-lab_v6 (profesor). ", ...refStyle, bold: true }),
    new TextRun({ text: "Referencia para la estructura del docker-compose, la organizaci\u00F3n de carpetas (dags/, notebooks/, logs/, plugins/) y el estilo del README.", ...refStyle }),
  ]
}));

// ====================================================
// DOCUMENTO
// ====================================================
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: AZUL },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT, color: AZUL },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1200, bottom: 1440, left: 1200 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "Reto 01 \u2013 Big Data Aplicado", font: FONT, size: 18, color: "999999", italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "P\u00E1gina ", font: FONT, size: 18, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "999999" })
          ]
        })]
      })
    },
    children
  }]
});

const outPath = "D:/IA_y_BD - BIG DATA APLICADO - 25-26/RETO 01 - mini entorno de trabajo con Jupyter Notebook y Apache Airflow RA4/autor_Reto01.docx";

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log("Documento creado: " + outPath);
}).catch(err => {
  console.error("Error:", err.message);
});
