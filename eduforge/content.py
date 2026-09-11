#!/usr/bin/env python3
"""EDU FORGE — banco de contenido didactico real (Harvard/Coursera style).

Contenido por curso: syllabus, semanas con lecciones reales, quizzes,
recursos de bancos abiertos (Khan Academy, Parla.cat, GCF Global, MIT OCW,
Aula Mentor, public-apis...) + seccion drivedopobre.com.

Idiomas: ES / CA / PT / EN (voz humana por idioma via edge-tts/Kokoro).
"""

from __future__ import annotations

# ============================ ORDEN DE IDIOMAS ==============================
# Regla del ecosistema (fija): portugues primero, luego espanol, luego
# ingles. El catalan se mantiene como idioma adicional, despues del EN.
LANG_ORDER = ["pt", "es", "en", "ca"]

# ============================ RECURSOS ABIERTOS ============================
OPEN_BANKS = {
    "es": [
        ("Khan Academy ES", "https://es.khanacademy.org", "matematicas, ciencias"),
        ("GCF Global", "https://edu.gcfglobal.org/es/", "office, internet, empleo"),
        ("Aula Mentor (MEC)", "https://www.aulamentor.es", "cursos oficiales gratuitos"),
        ("Google Activate", "https://learndigital.withgoogle.com/activate", "habilidades digitales"),
        ("MIT OpenCourseWare", "https://ocw.mit.edu", "universitario abierto"),
        ("OpenStax", "https://openstax.org", "libros de texto abiertos"),
        ("INE / datos abiertos", "https://www.ine.es", "datos publicos"),
    ],
    "ca": [
        ("Parla.cat", "https://www.parla.cat", "catalan oficial gratuito"),
        ("CPNL (Normalitzacio Linguistica)", "https://www.cpnl.cat", "cursos de catalan"),
        ("Optimot", "https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html", "diccionario CA"),
        ("Corpus Textual Informatitzat", "https://ctil.iec.cat", "corpus catalan"),
    ],
    "pt": [
        ("Khan Academy PT", "https://pt.khanacademy.org", "matematicas, ciencias"),
        ("Wikilivros PT", "https://pt.wikibooks.org", "libros abiertos"),
        ("Forvo PT", "https://pt.forvo.com", "pronunciacion real"),
        ("Portal Domínio Público", "http://www.dominiopublico.gov.br", "obras libres BR"),
        ("Ciberdúvidas", "https://ciberduvidas.iscte-iul.pt", "dudas de portugues"),
    ],
    "en": [
        ("Harvard Online (CS50)", "https://cs50.harvard.edu", "curso insignia"),
        ("MIT OCW", "https://ocw.mit.edu", "grado abierto"),
        ("OpenLearn (OU)", "https://www.open.edu/openlearn", "cursos gratuitos"),
        ("Project Gutenberg", "https://www.gutenberg.org", "libros dominio publico"),
    ],
}

DRIVEDOPOBRE = {
    "nombre": "Drive do Pobre (drivedopobre.com)",
    "nota": ("Repositorio comunitario de material didactico abierto. "
             "Los enlaces se integran como recursos complementarios; "
             "el contenido se verifica antes de citarse en lecciones."),
}

# ============================ JUEGOS (del alumno William, PT/ES/CA) =========
GAMES = [
    ("juego_falsos_amigos.py", "Caza-Falsos Amigos", "PT->ES: vocabulario critico"),
    ("juego_mate_escape.py", "Mate-Escape", "Ecuaciones contrarreloj ES/PT"),
    ("juego_trilingue.py", "Trilingue Express", "PT/ES/CA/EN traduccion rapida"),
    ("juego_catalan.py", "Catalan Challenge", "Catalan A1 con pistas PT"),
    ("juego_super_quiz.py", "Super Quiz Integral", "Todo en uno: 15 preguntas"),
]

# ============================ CURSOS ========================================
# estructura: slug -> dict(slug, titulo, titulo_en, idioma, nivel, horas,
#   descripcion, objetivos[], semanas[ {n, titulo, lecciones[ {tipo, titulo,
#   texto} ] } ], quiz { pregunta, opciones[4], correcta, explicacion } )

CURSOS = {}


def _c(slug, titulo, idioma, nivel, horas, desc, objetivos, semanas, quiz):
    CURSOS[slug] = dict(slug=slug, titulo=titulo, idioma=idioma, nivel=nivel,
                        horas=horas, descripcion=desc, objetivos=objetivos,
                        semanas=semanas, quiz=quiz)


# ---------------- LINGUA-ABERTA: 3 cursos PT->ES/CA ------------------------
_c(
    "falsos-amigos-pt-es", "Puente PT->ES: Falsos Amigos", "pt", "A2-B1", 12,
    "Curso intensivo para jovenes brasileños: domina los falsos amigos mas "
    "peligrosos entre portugues y español y deja de cometer errores en clase.",
    ["Identificar 40 falsos amigos criticos", "Escribir frases ES sin transferencia PT",
     "Autocorregir textos propios", "Jugar Caza-Falsos Amigos sin fallar"],
    [
        {"n": 1, "titulo": "El enemigo silencioso: que es un falso amigo",
         "lecciones": [
            {"tipo": "lectura", "titulo": "¿Por que hablo 'portuñol'?",
             "texto": "El portugues y el español comparten ~89% de lexico. Ese 11% "
                      "distinto es la trampa: palabras iguales con significado opuesto "
                      "(falsos amigos). Ejemplos: embaraçada=avergonzada (no embarazada), "
                      "esquisito=raro (no exquisito), oficina=taller (no oficina)."},
            {"tipo": "ejercicio", "titulo": "Clasifica 10 pares PT/ES",
             "texto": "Rellena la tabla: embaraçada, esquisito, oficina, polvo, "
                      "sobrenome, rato, vassoura, propina, apelido, borracha."},
            {"tipo": "voz", "titulo": "Pronunciacion guiada (audio PT->ES)",
             "texto": "Escucha cada par en portugues y español y repite 3 veces."},
         ]},
        {"n": 2, "titulo": "Los 20 falsos amigos mas letales",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Lista maestra comentada",
             "texto": "1) embaraçada=avergonzada 2) esquisito=raro 3) oficina=taller "
                      "4) polvo=pols/suciedad 5) sobrenome=apellido 6) rato=raton "
                      "7) vassoura=escoba 8) propina=soborno 9) apelido=mote "
                      "10) borracha=goma de borrar 11) salada=ensalada 12) copo=vaso "
                      "13) taça=copa 14) azar=mala suerte 15) cena=escena "
                      "16) exquisito (ES)=delicioso 17) roxo=morado 18) peito=pecho "
                      "19) anel=anillo 20) cadeira=silla."},
            {"tipo": "quiz", "titulo": "Quiz semana 2", "texto": "20 items A/B"},
            {"tipo": "juego", "titulo": "Caza-Falsos Amigos (rondas 1-5)", "texto": ""},
         ]},
        {"n": 3, "titulo": "Gramatica de transferencia",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Portuñol detectable: 8 patrones",
             "texto": "1) gerundio por a+infinitivo 2) 'mais' por 'mas' 3) futuro "
                      "sintetico ('falarei'->'hablare') 4) pronombres encliticos "
                      "5) 'tambem' por 'tambien' 6) 'voce' por 'usted/tu' "
                      "7) preposiciones (ir 'em' -> ir 'a') 8) 'ficar' por 'quedar(se)'."},
            {"tipo": "escritura", "titulo": "Redaccion de 150 palabras sin portuñol",
             "texto": "Tema: 'Mi primer dia en el instituto catalan'. "
                      "Autoevaluate con la lista de patrones."},
         ]},
        {"n": 4, "titulo": "Evaluacion y transferencia positiva",
         "lecciones": [
            {"tipo": "repaso", "titulo": "Repaso de las 3 semanas",
             "texto": "Todos los falsos amigos + patrones gramaticales."},
            {"tipo": "proyecto", "titulo": "Guia personal anti-portuñol (1 pagina)",
             "texto": "Crea tu chuleta ilustrada con tus 10 errores favoritos."},
            {"tipo": "examen", "titulo": "Examen final: 40 items",
             "texto": "Super Quiz Integral, seccion falsos amigos."},
         ]},
    ],
    [
        {"pregunta": "'Embaraçada' en español significa...",
         "opciones": ["Embarazada", "Avergonzada", "Enfadada", "Confundida"],
         "correcta": 1, "explicacion": "Falso amigo clasico: embaraçada = avergonzada."},
        {"pregunta": "'Oficina' (PT) es...",
         "opciones": ["Oficina de trabajo", "Taller mecanico", "Cocina", "Escritorio"],
         "correcta": 1, "explicacion": "La oficina en ES es 'escritorio'."},
        {"pregunta": "'Esquisito' (PT) = ...",
         "opciones": ["Exquisito", "Raro/extrano", "Delicado", "Sencillo"],
         "correcta": 1, "explicacion": "Exquisito en ES es 'delicioso'."},
        {"pregunta": "'Sobrenome' (PT) = ...",
         "opciones": ["Sobrenombre", "Apellido", "Nickname", "Seudonimo"],
         "correcta": 1, "explicacion": "El apodo en PT es 'apelido'."},
        {"pregunta": "'Vassoura' (PT) = ...",
         "opciones": ["Basura", "Escoba", "Vasija", "Cesta"],
         "correcta": 1, "explicacion": "La basura en ES es 'lixo'."},
    ],
)

_c(
    "catalan-a1-brasileiros", "Catalán A1: Supervivencia", "ca", "A1", 16,
    "Catalan desde cero con pistas en portugues: saludos, instituto, ciudad y "
    "verbos basicos. Disenado para jovenes brasileños recien llegados a Cataluña.",
    ["Saludar y presentarse en CA", "Manejar vocabulario del instituto",
     "Pedir y agradecer con cortesia", "Conjugar 5 verbos esenciales en presente"],
    [
        {"n": 1, "titulo": "Bon dia! Saludos y presentaciones",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Saludos, cortesia y numeros 1-20",
             "texto": "Bon dia, bona tarda, bona nit; Si us plau, merci/gracies, "
                      "de res, perdo. Numeros: un, dos, tres, quatre, cinc, sis, "
                      "set, vuit, nou, deu, onze, dotze... vint."},
            {"tipo": "voz", "titulo": "Audio: dialogo en la tienda (CA)",
             "texto": "Escucha y repite el dialogo: -Bon dia! -Bon dia! Que "
                      "voleu? -Un croissant, si us plau. -Son dos euros."},
            {"tipo": "juego", "titulo": "Catalan Challenge (rondas 1-4)", "texto": ""},
         ]},
        {"n": 2, "titulo": "L'institut: la escuela en catalan",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Vocabulario del instituto",
             "texto": "Institut, classe, deures, pati, biblioteca, examen/prova, "
                      "professor/a, alumne/a, llapis, llibre, motxilla, horari."},
            {"tipo": "quiz", "titulo": "Quiz instituto", "texto": "10 items"},
            {"tipo": "escritura", "titulo": "Mi horario en catalan",
             "texto": "Escribe tu horario semanal: 'Dilluns tinc matematiques...' "
                      "(dias: dilluns, dimarts, dimecres, dijous, divendres)."},
         ]},
        {"n": 3, "titulo": "Verbs essencials: ser, tenir, voler, anar, menjar",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Presente de indicativo + ejemplos PT",
             "texto": "SER: soc, ets, es, som, sou, son. TENIR: tinc, tens, te, "
                      "tenim, teniu, tenen. ANAR: vaig, vas, va, anem, aneu, van. "
                      "Compara con PT: 'eu sou'->'jo soc', 'nos temos'->'nosaltres tenim'."},
            {"tipo": "ejercicio", "titulo": "Conjuga 15 frases",
             "texto": "Traduce: Yo voy al instituto, Tu tienes un libro, "
                      "Nosotros somos de Brasil..."},
         ]},
        {"n": 4, "titulo": "La ciutat: moverte por L'Hospitalet",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Transporte, tiendas y servicios",
             "texto": "Metro, tren, bus, estacio, parada, bitllet, carrer, placa, "
                      "ajuntament, CAP (centro de salud), farmacia, mercat."},
            {"tipo": "proyecto", "titulo": "Ruta comentada (mapa + 10 frases CA)",
             "texto": "Dibuja tu ruta casa->instituto y describela en catalan."},
            {"tipo": "examen", "titulo": "Examen A1 completo", "texto": ""},
         ]},
    ],
    [
        {"pregunta": "¿Como se dice 'gracias' en catalan?",
         "opciones": ["Obrigado", "Gracies/Merci", "Grazie", "Thanks"],
         "correcta": 1, "explicacion": "Gracies o merci; 'obrigado' es portugues."},
        {"pregunta": "'Deures' significa...",
         "opciones": ["Deberes/tarea", "Duros", "Deudas", "Dudas"],
         "correcta": 0, "explicacion": "Deures = deberes escolares."},
        {"pregunta": "Presente de ANAR, 1a persona singular:",
         "opciones": ["vaig", "va", "anem", "vagi"],
         "correcta": 0, "explicacion": "Jo vaig a l'institut."},
        {"pregunta": "'Pati' en el instituto es...",
         "opciones": ["Patio/recreo", "Clase", "Comedor", "Gimnasio"],
         "correcta": 0, "explicacion": "Pati = patio de recreo."},
        {"pregunta": "Los dias de la semana en CA empiezan por...",
         "opciones": ["lunes...", "dilluns...", "segunda...", "diumenge..."],
         "correcta": 1, "explicacion": "Dilluns, dimarts, dimecres, dijous, divendres."},
    ],
)

_c(
    "espanol-academico-eso", "Español Académico para la ESO", "es", "B1", 10,
    "Lectura critica, ensayo y argumentacion en español para rendir en el "
    "instituto catalan.",
    ["Escribir un ensayo de 300 palabras con estructura",
     "Resumir textos academicos", "Defender oralmente una opinion"],
    [
        {"n": 1, "titulo": "Lectura critica", "lecciones": [
            {"tipo": "lectura", "titulo": "Subrayar, resumir, citar",
             "texto": "Metodo: leer 2 veces, subrayar 10%, resumen de 5 lineas, "
                      "cita textual + tu interpretacion."},
            {"tipo": "ejercicio", "titulo": "Resume un articulo de prensa ES",
             "texto": "Usa un articulo de www.rtve.es/noticias."}]},
        {"n": 2, "titulo": "El ensayo argumentativo", "lecciones": [
            {"tipo": "lectura", "titulo": "Tesis + 3 argumentos + refutacion",
             "texto": "Estructura: introduccion (tesis), desarrollo (argumento + "
                      "evidencia x3), refutacion del contrario, conclusion."},
            {"tipo": "escritura", "titulo": "Ensayo 300 palabras",
             "texto": "Tema: '¿El movil en clase ayuda o distrae?'"}]},
        {"n": 3, "titulo": "Defensa oral", "lecciones": [
            {"tipo": "lectura", "titulo": "Presentar 3 minutos sin leer",
             "texto": "Estructura de charla: gancho, tesis, 3 puntos, cierre. "
                      "Voz: pausas, volumen, contacto visual."},
            {"tipo": "proyecto", "titulo": "Charla grabada de 3 min", "texto": ""}]},
    ],
    [
        {"pregunta": "Un ensayo argumentativo necesita...",
         "opciones": ["Solo opinion", "Tesis + argumentos + evidencia", "Resumen", "Descripcion"],
         "correcta": 1, "explicacion": "Sin evidencia no es argumentativo."},
        {"pregunta": "La refutacion es...",
         "opciones": ["Ignorar al contrario", "Responder el contraargumento", "Cambiar de tema", "Repetir la tesis"],
         "correcta": 1, "explicacion": "Anticipar y responder la objecion."},
        {"pregunta": "Un resumen correcto...",
         "opciones": ["Copia frases", "Condensa ideas con tus palabras", "Es mas largo", "Solo el titulo"],
         "correcta": 1, "explicacion": "Ideas propias, fiel al original."},
    ],
)

# ---------------- MANOSABIERTAS: 2 cursos ES --------------------------------
_c(
    "alfabetizacion-ia", "Alfabetización en IA para la Vida Real", "es", "inicio", 9,
    "Que es la IA, como usarla sin miedo (y sin que te engane), y que derechos "
    "tienes. Para migrantes y comunidades: cero tecnicismos.",
    ["Explicar que es y que NO es la IA", "Escribir un prompt util",
     "Detectar 5 riesgos y defenderse", "Conocer tus derechos digitales"],
    [
        {"n": 1, "titulo": "¿Que es la IA? (y que no es)",
         "lecciones": [
            {"tipo": "lectura", "titulo": "IA en 5 ideas",
             "texto": "1) La IA predice patrones, no piensa 2) aprende de datos "
                      "publicos 3) puede equivocarse con seguridad 4) no tiene "
                      "intenciones 5) tu eres responsable de lo que publicas."},
            {"tipo": "ejercicio", "titulo": "Caza el mito: 10 frases verdaderas/falsas",
             "texto": "Identifica mitos comunes sobre la IA."}]},
        {"n": 2, "titulo": "El prompt: pedir bien es gratis",
         "lecciones": [
            {"tipo": "lectura", "titulo": "La receta del prompt",
             "texto": "ROL + TAREA + CONTEXTO + FORMATO. Ejemplo: 'Actua como "
                      "orientador laboral. Dime 5 preguntas de entrevista para "
                      "camarero en Barcelona. Responde en lista.'"},
            {"tipo": "ejercicio", "titulo": "Escribe 3 prompts utiles para ti",
             "texto": "Uno para CV, uno para traducir, uno para aprender."},
            {"tipo": "voz", "titulo": "Audio: la receta del prompt (ES)", "texto": ""}]},
        {"n": 3, "titulo": "Riesgos, estafas y derechos",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Deepfakes, phishing-IA y tus derechos",
             "texto": "Aprende a detectar: voces clonadas, fotos falsas, "
                      "mensajes urgentes. Tus derechos: proteccion de datos "
                      "(RGPD), derecho a no ser perfilado, denuncia en "
                      "AEPD (aepd.es) y Mossos."},
            {"tipo": "proyecto", "titulo": "Kit anti-estafa de 1 pagina",
             "texto": "Crea tu guia familiar de 5 pasos ante sospecha."}]},
    ],
    [
        {"pregunta": "La IA generativa...",
         "opciones": ["Siempre acierta", "Puede inventar datos con seguridad", "Tiene conciencia", "Es gratis siempre"],
         "correcta": 1, "explicacion": "Alucinaciones: verifica fuentes."},
        {"pregunta": "Un buen prompt tiene...",
         "opciones": ["Solo una pregunta", "Rol+tarea+contexto+formato", "Emojis", "Mayusculas"],
         "correcta": 1, "explicacion": "La receta de la semana 2."},
        {"pregunta": "Ante un mensaje urgente pidiendo dinero...",
         "opciones": ["Pagar ya", "Verificar por otra via y denunciar", "Compartir", "Ignorar"],
         "correcta": 1, "explicacion": "La urgencia es la herramienta del estafador."},
        {"pregunta": "En la UE tus datos personales estan protegidos por...",
         "opciones": ["RGPD", "Nada", "El contrato", "La empresa"],
         "correcta": 0, "explicacion": "Reglamento General de Proteccion de Datos."},
    ],
)

_c(
    "office-sin-miedo", "Office sin Miedo: CV, Cartas y Presupuestos", "es", "inicio", 9,
    "Crea tu CV, cartas formales y controla gastos con herramientas gratuitas "
    "(LibreOffice / Google Docs). Practico, guiado, en español claro.",
    ["Crear un CV profesional desde plantilla",
     "Escribir una carta formal correcta", "Hacer un presupuesto basico en hoja de calculo"],
    [
        {"n": 1, "titulo": "El CV que te llama para entrevista",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Estructura del CV europeo (Europass)",
             "texto": "Datos, perfil (3 lineas), experiencia, formacion, idiomas, "
                      "habilidades. Usa europass.europa.eu gratis."},
            {"tipo": "ejercicio", "titulo": "Crea tu CV con el creador de CV de ManosAbiertas",
             "texto": "Usa la herramienta de la plataforma y exporta a PDF."}]},
        {"n": 2, "titulo": "Cartas formales sin errores",
         "lecciones": [
            {"tipo": "lectura", "titulo": "La carta de presentacion y de solicitud",
             "texto": "Formula: saludo formal, quien eres, que pides, por que tu, "
                      "cierre y firma. Fechas y datos alineados."},
            {"tipo": "escritura", "titulo": "Carta de solicitud de empadronamiento",
             "texto": "Redactala siguiendo la formula."}]},
        {"n": 3, "titulo": "Hoja de calculo: presupuesto familiar",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Ingresos, gastos, saldo: 3 columnas",
             "texto": "SUMA(), formato de moneda, grafico de gastos mensuales."},
            {"tipo": "proyecto", "titulo": "Tu presupuesto de un mes",
             "texto": "Plantilla con categorias: vivienda, comida, transporte, ocio."}]},
    ],
    [
        {"pregunta": "El CV europeo estandar se llama...",
         "opciones": ["Europass", "LinkedIn", "Resume.io", "PDF"],
         "correcta": 0, "explicacion": "Europass, gratuito y reconocido."},
        {"pregunta": "En una carta formal el saludo correcto es...",
         "opciones": ["Hola!", "Estimado/a Sr./Sra.", "Que tal", "Buenas"],
         "correcta": 1, "explicacion": "Registro formal siempre."},
        {"pregunta": "Para sumar una columna en la hoja de calculo usas...",
         "opciones": ["=SUMA()", "TOTAL", "ADD", "=PLUS()"],
         "correcta": 0, "explicacion": "=SUMA(A1:A10)."},
    ],
)

# ---------------- UX-ACADEMY: curso insignia ---------------------------------
_c(
    "ux-profesional", "UX Profesional: del Criterio al Portafolio", "es", "intermedio", 24,
    "Curso trilingue (ES/EN/PT) de UX/Product Design: leyes de la percepcion, "
    "sistema de tokens, anti-estetica-IA, accesibilidad y portafolio. Estilo "
    "Harvard: lecturas, practica semanal y evaluacion por evidencia.",
    ["Aplicar las 25 leyes de UX con criterio",
     "Construir un sistema de tokens completo", "Detectar y corregir estetica 'IA generica'",
     "Auditar accesibilidad WCAG 2.2", "Entregar un portafolio de 3 casos"],
    [
        {"n": 1, "titulo": "Percepcion y leyes universales",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Jakob, Fitts, Hick, Miller y el ojo humano",
             "texto": "El ojo detecta antes: color, tamaño, movimiento, forma. "
                      "Luminancia > color para jerarquia; tamaño > peso. "
                      "Fitts: lo importante, grande y cerca. Hick: menos opciones. "
                      "Miller: 3-5 bloques por vista."},
            {"tipo": "ejercicio", "titulo": "Audita una web real con 10 heuristicas",
             "texto": "Elige una web de tu ciudad y puntua cada heuristica 0-10."}]},
        {"n": 2, "titulo": "Por que una UI se ve 'hecha por IA' (y como evitarlo)",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Las 16 senales del AI-slop",
             "texto": "Gradiente violeta/cian por defecto, glassmorphism total, "
                      "3 cards identicas, sombras gigantes, copy vacio, emojis "
                      "placeholder, sin estados... cada senal con su correccion."},
            {"tipo": "ejercicio", "titulo": "Antes/despues: rediseña una card",
             "texto": "Toma una landing 'generica' y aplicale: un solo acento, "
                      "contenido real, jerarquia, estados."}]},
        {"n": 3, "titulo": "Tokens: el idioma del sistema de diseño",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Tres capas: primitivo -> semantico -> componente",
             "texto": "Hue/sat, escalas tipograficas fluidas (clamp), spacing 4/8, "
                      "radios, sombras por elevacion, motion con duraciones "
                      "justificadas, z-index escalonado."},
            {"tipo": "proyecto", "titulo": "Tu tokens.css completo (light+dark)",
             "texto": "Entrega: variables, tema oscuro, reduced-motion."}]},
        {"n": 4, "titulo": "Accesibilidad no es opcional",
         "lecciones": [
            {"tipo": "lectura", "titulo": "WCAG 2.2 en practica",
             "texto": "Contraste AA (4.5:1), foco visible, targets 44px, labels "
                      "visibles, errores recuperables, reduced-motion, teclado."},
            {"tipo": "ejercicio", "titulo": "Auditoria de accesibilidad con checklist",
             "texto": "Corre los 15 checks finales sobre tu proyecto."}]},
        {"n": 5, "titulo": "Motion y shaders con proposito",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Duraciones, easings y shaders ambientales",
             "texto": "Hover 80-150ms, entradas 180-320ms, stagger 30-60ms. "
                      "Shader GLSL de fondo: aurora/noise/vignette con "
                      "reduced-motion respetado."},
            {"tipo": "proyecto", "titulo": "Hero con shader ambiental + overlay legible",
             "texto": ""}]},
        {"n": 6, "titulo": "Portafolio: 3 casos con evidencia",
         "lecciones": [
            {"tipo": "proyecto", "titulo": "Caso 1: rediseno accesible (antes/despues)",
             "texto": ""},
            {"tipo": "proyecto", "titulo": "Caso 2: sistema de tokens publicado",
             "texto": ""},
            {"tipo": "proyecto", "titulo": "Caso 3: auditoria UX de un producto real",
             "texto": "Con grayscale test, blur test y contraste."},
            {"tipo": "examen", "titulo": "Examen final: 30 items", "texto": ""}]},
    ],
    [
        {"pregunta": "Segun la ley de Fitts, un objetivo importante debe ser...",
         "opciones": ["Pequeño y lejano", "Grande y cercano", "Oculto", "Animado"],
         "correcta": 1, "explicacion": "Tiempo de alcance = tamaño + distancia."},
        {"pregunta": "Para jerarquia visual, que domina primero?",
         "opciones": ["Color", "Luminancia/tamaño", "Sombra", "Radio"],
         "correcta": 1, "explicacion": "El ojo lee luminancia antes que color."},
        {"pregunta": "Contraste minimo AA para texto normal:",
         "opciones": ["2:1", "3:1", "4.5:1", "7:1"],
         "correcta": 2, "explicacion": "WCAG 2.2 AA = 4.5:1 (3:1 texto grande)."},
        {"pregunta": "Target tactil minimo recomendado:",
         "opciones": ["24px", "32px", "44px", "64px"],
         "correcta": 2, "explicacion": "44x44px en movil."},
        {"pregunta": "Un componente 'AI-slop' tipico es...",
         "opciones": ["Copy orientado a tarea", "3 cards identicas con icono generico", "Un solo acento", "Estados completos"],
         "correcta": 1, "explicacion": "Repeticion sin jerarquia."},
    ],
)

# ---------------- LINGUAFORGE: curso forja -----------------------------------
_c(
    "forja-linguistica", "Forja Linguistica: Traduccion y Adaptacion", "es", "intermedio", 12,
    "Herramientas, corpora y flujo de traduccion/adaptacion multilingue "
    "(ES/CA/PT/EN) con post-edicion humana y control de calidad.",
    ["Usar corpora y diccionarios abiertos", "Aplicar flujo MT + post-edicion",
     "Adaptar textos a registro y audiencia", "Auditar calidad con checklist"],
    [
        {"n": 1, "titulo": "Bancos y corpora abiertos",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Diccionarios, corpus y memorias",
             "texto": "Optimot (CA), DLE (ES), Ciberduvidas (PT), Wiktionary, "
                      "CTIL-IEC (corpus CA), Linguee/contexto real."},
            {"tipo": "ejercicio", "titulo": "Construye tu glosario de 30 terminos",
             "texto": "De un ambito que elijas (educacion, salud, empleo)."}]},
        {"n": 2, "titulo": "Flujo de traduccion asistida",
         "lecciones": [
            {"tipo": "lectura", "titulo": "MT + post-edicion: el flujo honesto",
             "texto": "1) preedicion (frases cortas) 2) traduccion automatica "
                      "3) post-edicion humana 4) control de calidad 5) memoria "
                      "de traduccion (TMX)."},
            {"tipo": "proyecto", "titulo": "Traduce y post-edita 1 pagina",
             "texto": "Del ES al CA y al PT: compara y documenta 5 decisiones."}]},
        {"n": 3, "titulo": "Adaptacion cultural y registro",
         "lecciones": [
            {"tipo": "lectura", "titulo": "No es traducir, es adaptar",
             "texto": "Registro formal/informal, variantes (ES-ES vs ES-LATAM, "
                      "PT-BR vs PT-PT), unidades, fechas, nombres propios."},
            {"tipo": "ejercicio", "titulo": "Adapta 3 textos a 2 variantes",
             "texto": "Un menu, un formulario, un aviso municipal."}]},
        {"n": 4, "titulo": "Calidad y entrega",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Checklist QA de traduccion",
             "texto": "Completitud, terminologia, estilo, ortografia, formato, "
                      "funcionalidad. Error tipologia LISA."},
            {"tipo": "examen", "titulo": "Examen: traduccion completa evaluada",
             "texto": ""}]},
    ],
    [
        {"pregunta": "El corpus de catalan del IEC es...",
         "opciones": ["CTIL", "DLE", "Forvo", "Linguee"],
         "correcta": 0, "explicacion": "Corpus Textual Informatitzat de la Llengua Catalana."},
        {"pregunta": "La post-edicion es...",
         "opciones": ["Borrar el texto", "Corregir la traduccion automatica", "Traducir a mano todo", "Un formato"],
         "correcta": 1, "explicacion": "El humano corrige la MT."},
        {"pregunta": "TMX es...",
         "opciones": ["Un formato de memoria de traduccion", "Un banco", "Una MT", "Un navegador"],
         "correcta": 0, "explicacion": "Translation Memory eXchange."},
    ],
)

# ---------------- OPEN-SCHOOL: hub + secure-t resumen ------------------------
_c(
    "ciberseguridad-5-anios", "Ciberseguridad + Full-Stack: Plan 5 Años", "es", "grado", 480,
    "Plan completo estilo Coursera (48 cursos, ~800 lecciones, matriz didactica "
    "con evidencia): del primer script al red team, DFIR y seguridad de IA. "
    "Incluye trazado de idiomas Ingles A1->C2 + Español academico + Hindi electivo.",
    ["Conocer la malla completa de 5 años", "Entender la matriz competencia x evidencia",
     "Ubicar cada curso en su ruta", "Iniciar el Año 1 con recursos abiertos"],
    [
        {"n": 1, "titulo": "Mapa del grado (48 cursos)",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Los 5 años resumidos",
             "texto": "A1: fundamentos + idiomas. A2: frontend + datos. "
                      "A3: backend + OWASP + cripto. A4: cloud, DevOps, red/blue team. "
                      "A5: IA, blockchain credenciales, capstone."},
            {"tipo": "ejercicio", "titulo": "Dibuja tu ruta personal", "texto": ""}]},
        {"n": 2, "titulo": "Matriz didactica: competencia x evidencia",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Nada se aprueba sin evidencia",
             "texto": "Cada curso asigna pesos a competencias (tecnica, transversal, "
                      "idioma) y cada competencia exige evidencia observable: "
                      "lab flags, codigo, quizzes, charlas."},
            {"tipo": "proyecto", "titulo": "Configura tu secure_t.db (banco de datos)",
             "texto": "Ejecuta banco_secure_t.py y explora: python banco_secure_t.py all"}]},
        {"n": 3, "titulo": "Idiomas integrados: EN A1->C2, ES academico, HI electivo",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Como se aprende idioma aqui",
             "texto": "Inmersion: practica oral semanal + rubricas CEFR por nivel. "
                      "EN: de standups a papers C2. ES: ensayo y defensa. "
                      "HI: electivo cultural."}]},
    ],
    [
        {"pregunta": "El plan de ciberseguridad dura...",
         "opciones": ["2 años", "3 años", "5 años", "1 año"],
         "correcta": 2, "explicacion": "5 años, 48 cursos, ~800 lecciones."},
        {"pregunta": "OWASP Top 10 se estudia en...",
         "opciones": ["Año 1", "Año 3", "Año 5", "Nunca"],
         "correcta": 1, "explicacion": "Año 3, seguridad web."},
        {"pregunta": "La evidencia del capstone es...",
         "opciones": ["Un examen", "Entrega verificable extremo a extremo + defensa", "Asistencia", "Un resumen"],
         "correcta": 1, "explicacion": "PR-01: entrega verificable + pasantia + defensa publica."},
    ],
)

# ---------------- SECURE-T-UNIVERSITY: 4 cursos principales (la 2a sala) ----
# Alineados con STORY.md: Ofensiva, Defensiva, IA Aplicada, Gobernanza.

_c(
    "ciber-ofensiva", "Ciberseguridad Ofensiva: Pensar como Atacante", "es",
    "universitario", 60,
    "Curso universitario de seguridad ofensiva con ética desde el día 1: "
    "recon pasivo, OSINT, OWASP Top 10 y laboratorio con máquina vulnerable. "
    "Se aprueba demostrando hallazgos documentados, nunca adivinando.",
    ["Distinguir hacking ético de actividad delictiva",
     "Ejecutar reconocimiento pasivo y OSINT sobre un objetivo autorizado",
     "Explicar y reproducir los 10 riesgos web principales de OWASP",
     "Redactar un informe de hallazgos con severidad y remediación"],
    [
        {"n": 1, "titulo": "Ética, legalidad y alcance del test",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Regla número uno: permiso escrito",
             "texto": "Nada se prueba sin autorización expresa y alcance firmado. "
                      "Referencias: Convenio de Budapest (arts. 2-6), Código Penal "
                      "esp. (arts. 197-198), y el estándar de alcance 'rules of "
                      "engagement'. Un pentest sin contrato es un delito."},
            {"tipo": "ejercicio", "titulo": "Redacta tu carta de autorización",
             "texto": "Plantilla: partes, objetivo, ventanas de tiempo, puntos de "
                      "contacto, plan de escape ante incidente, firma."},
            {"tipo": "lectura", "titulo": "Metodologías: PTES, OWASP WSTG, MITRE ATT&CK",
             "texto": "PTES da las fases; WSTG orienta pruebas web; ATT&CK cataloga "
                      "tácticas y técnicas del adversario real."}]},
        {"n": 2, "titulo": "Reconocimiento pasivo y OSINT",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Ver sin tocar: footprinting pasivo",
             "texto": "DNS, certificados (crt.sh), Wayback Machine, metadatos "
                      "públicos, Google dorks. El 70% de la inteligencia útil "
                      "no requiere enviar un solo paquete al objetivo."},
            {"tipo": "ejercicio", "titulo": "Perfil OSINT de un dominio propio",
             "texto": "Con tu propio dominio (o uno autorizado): subdominios, "
                      "tecnologías visibles, emails corporativos expuestos, "
                      "filtraciones en breech-db."}]},
        {"n": 3, "titulo": "Los 10 riesgos web (OWASP Top 10)",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Inyección y control de acceso roto",
             "texto": "SQLi y NoSQLi: input que se convierte en código. Broken "
                      "Access Control: el servidor confía en el cliente. Son los "
                      "dos defectos que más brechas reales causan."},
            {"tipo": "ejercicio", "titulo": "Práctica guiada en laboratorio legal",
             "texto": "OWASP Juice Shop / bWAPP en local: encuentra 3 "
                      "vulnerabilidades del Top 10 y documenta reproducción."},
            {"tipo": "lectura", "titulo": "SSRF, XSS y componentes obsoletos",
             "texto": "El servidor pidiendo por ti (SSRF), el navegador del "
                      "usuario como objetivo (XSS) y el CVE sin parchear."}]},
        {"n": 4, "titulo": "Laboratorio final: máquina vulnerable + informe",
         "lecciones": [
            {"tipo": "proyecto", "titulo": "De recon a reporte en Metasploitable",
             "texto": "Máquina vulnerable local (Metasploitable 2 o similar): "
                      "recon, explotación de 2 vectores, escalada, evidencia "
                      "capturada. Solo en red local propia."},
            {"tipo": "examen", "titulo": "Informe ético evaluado",
             "texto": "Formato ejecutivo + técnico: hallazgo, severidad CVSS, "
                      "reproducción paso a paso, remediación."}]},
    ],
    [
        {"pregunta": "Lo primero en cualquier test ofensivo es...",
         "opciones": ["Escanear agresivamente", "Obtener permiso escrito y alcance", "Instalar Metasploit", "Buscar 0-days"],
         "correcta": 1, "explicacion": "Sin autorización expresa no hay test ético: hay delito."},
        {"pregunta": "OWASP Top 10 es...",
         "opciones": ["Una lista de antivirus", "Un ranking de riesgos de seguridad web", "Un firewall", "Una norma ISO"],
         "correcta": 1, "explicacion": "Consenso comunitario sobre los 10 riesgos web más críticos."},
        {"pregunta": "El OSINT pasivo se caracteriza por...",
         "opciones": ["Enviar paquetes al objetivo", "No contactar directamente el objetivo", "Requerir exploits", "Ser ilegal siempre"],
         "correcta": 1, "explicacion": "Recolecta información pública sin tocar la infraestructura del objetivo."},
    ],
)

_c(
    "ciber-defensiva", "Ciberseguridad Defensiva: Operar como SOC", "es",
    "universitario", 60,
    "Curso universitario de defensa: triada CIA, telemetría y logs, SIEM, "
    "respuesta a incidentes NIST y hardening. El estudiante opera un mini-SOC "
    "con casos reales despersonalizados.",
    ["Aplicar la triada CIA para clasificar activos y controles",
     "Configurar recolección de logs y detección básica en un SIEM abierto",
     "Ejecutar el ciclo de respuesta a incidentes de NIST 800-61",
     "Endurecer un servidor con matriz de hardening verificable"],
    [
        {"n": 1, "titulo": "Fundamentos: triada CIA y controles",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Confidencialidad, Integridad, Disponibilidad",
             "texto": "Cada control se justifica por el riesgo que mitiga: "
                      "cifrado (C), hashing y firma (I), redundancia (D). Mapa "
                      "preventivo/detectivo/correctivo."},
            {"tipo": "ejercicio", "titulo": "Clasifica 10 activos de una ONG ficticia",
             "texto": "Impacto C/I/D por activo, control propuesto, costo "
                      "aproximado. Se defiende en 5 minutos."}]},
        {"n": 2, "titulo": "Telemetría: logs y detección",
         "lecciones": [
            {"tipo": "lectura", "titulo": "El log es el testigo",
             "texto": "Fuentes: sistema, aplicación, red, identidad. Formato "
                      "structured logging, retención legal, hora sincronizada "
                      "(NTP) — sin hora correcta no hay correlación."},
            {"tipo": "ejercicio", "titulo": "Mini-SOC con Wazuh o Security Onion",
             "texto": "Instala en VM, conecta 2 agentes, genera 3 eventos "
                      "(login fallido, escalada, malware EICAR) y detecta."}]},
        {"n": 3, "titulo": "Respuesta a incidentes (NIST 800-61)",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Preparación → Detección → Contención → Erradicación → Recuperación → Lecciones",
             "texto": "El ciclo no termina hasta el informe de lecciones "
                      "aprendidas. Playbooks por escenario: ransomware, phish, "
                      "cuenta comprometida."},
            {"tipo": "ejercicio", "titulo": "Juego de mesa: incidente de ransomware",
             "texto": "Rol de analista: cronología, decisiones de contención, "
                      "comunicación, post-incidente."}]},
        {"n": 4, "titulo": "Hardening y continuidad",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Superficie de ataque mínima",
             "texto": "CIS Benchmarks: servicios innecesarios fuera, puertos "
                      "cerrados, actualizaciones, MFA, backups 3-2-1 con prueba "
                      "de restauración."},
            {"tipo": "examen", "titulo": "Auditoría de hardening evaluada",
             "texto": "Checklist CIS nivel 1 sobre una VM: evidencia antes/después."}]},
    ],
    [
        {"pregunta": "La triada CIA significa...",
         "opciones": ["Central Intelligence Agency", "Confidencialidad, Integridad, Disponibilidad", "Cifrado, Identidad, Acceso", "Control, Inspección, Auditoría"],
         "correcta": 1, "explicacion": "Las tres propiedades que todo control protege."},
        {"pregunta": "El ciclo NIST 800-61 termina con...",
         "opciones": ["La contención", "El pago del rescate", "Lecciones aprendidas", "El reinicio"],
         "correcta": 2, "explicacion": "Sin post-incidente el ciclo está incompleto."},
        {"pregunta": "Backup 3-2-1 significa...",
         "opciones": ["3 copias, 2 medios, 1 fuera de sitio", "3 firewalls, 2 DMZ, 1 VPN", "3 usuarios, 2 roles, 1 admin", "3 hashes, 2 claves, 1 token"],
         "correcta": 0, "explicacion": "Tres copias en dos medios distintos y una copia externa."},
    ],
)

_c(
    "ia-aplicada-segura", "Inteligencia Artificial Aplicada y Segura", "es",
    "universitario", 48,
    "IA aplicada con seguridad como requisito, no como añadido: fundamentos "
    "de ML, LLMs y prompt engineering responsable, ataques adversariales y "
    "proyecto final de asistente educativo con salvaguardas.",
    ["Explicar el ciclo de vida de un modelo de ML sin tecnicismos vacíos",
     "Diseñar prompts y flujos con LLM de forma responsable y verificable",
     "Identificar ataques adversariales, poisoning y prompt injection",
     "Construir un mini-asistente educativo con salvaguardas documentadas"],
    [
        {"n": 1, "titulo": "Fundamentos de ML sin humo",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Datos → modelo → predicción → error",
             "texto": "Entrenamiento vs inferencia. Sobreajuste en una frase: "
                      "memorizar en vez de aprender. La calidad del dato gana "
                      "al algoritmo elegante."},
            {"tipo": "ejercicio", "titulo": "Clasificador de juguete",
             "texto": "Con scikit-learn y un dataset abierto (iris o similar): "
                      "entrena, mide, explica el error en lenguaje humano."}]},
        {"n": 2, "titulo": "LLMs y prompt engineering responsable",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Cómo funciona un LLM (y qué no hace)",
             "texto": "Predice el siguiente token; no 'sabe'. Alucinación como "
                      "propiedad estadística. Contexto, temperatura, límites. "
                      "Regla: la IA propone, la persona verifica."},
            {"tipo": "ejercicio", "titulo": "Prompt ROL + TAREA + CONTEXTO + FORMATO",
             "texto": "Construye 5 prompts educativos reales y compara "
                      "respuestas con y sin estructura."}]},
        {"n": 3, "titulo": "Ataques a sistemas de IA",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Adversarial, poisoning, prompt injection",
             "texto": "Ejemplos con pegatina que engaña a la cámara, datos "
                      "falsos que corrompen el entrenamiento, instrucciones "
                      "ocultas que secuestran al asistente. OWASP Top 10 para LLM."},
            {"tipo": "ejercicio", "titulo": "Inyección de prompt en laboratorio",
             "texto": "Sobre un asistente propio (no de terceros): demuestra "
                      "una inyección y luego la mitiga (sanitize, delimitadores, "
                      "permisos mínimos)."}]},
        {"n": 4, "titulo": "Proyecto: asistente educativo con salvaguardas",
         "lecciones": [
            {"tipo": "proyecto", "titulo": "Tutor de una lección del campus",
             "texto": "Asistente que responde SOLO con material del curso "
                      "(grounding), cita la fuente, se niega fuera de alcance "
                      "y registra uso anónimo."},
            {"tipo": "examen", "titulo": "Defensa del proyecto",
             "texto": "Demo en vivo: 3 preguntas válidas, 2 intentos de abuso "
                      "contenidos por las salvaguardas."}]},
    ],
    [
        {"pregunta": "Un LLM 'alucina' porque...",
         "opciones": ["Está roto", "Predice texto plausible, no verdad verificada", "Le falta internet", "Se entrena poco"],
         "correcta": 1, "explicacion": "Genera la continuación estadística más plausible; la verificación es humana."},
        {"pregunta": "El prompt injection consiste en...",
         "opciones": ["Inyectar código SQL", "Instrucciones ocultas que cambian el comportamiento del modelo", "Robar la API key", "Cifrar el prompt"],
         "correcta": 1, "explicacion": "Entrada no confiable que el sistema trata como instrucción de sistema."},
        {"pregunta": "Grounding en un asistente significa...",
         "opciones": ["Usar el modelo más grande", "Anclar respuestas a fuentes citadas", "Reducir la temperatura a 0", "Entrenar desde cero"],
         "correcta": 1, "explicacion": "Responder solo a partir de material verificable y citarlo."},
    ],
)

_c(
    "gobernanza-compliance", "Gobernanza y Compliance Digital", "es",
    "universitario", 40,
    "Marcos de gobierno de la seguridad (ISO 27001, NIST CSF, ENS), "
    "protección de datos con principio de minimización extrema, gestión de "
    "riesgo y construcción del expediente de compliance con evidencia.",
    ["Situar los marcos ISO 27001, NIST CSF y ENS en su papel real",
     "Aplicar minimización de datos: el usuario como token anónimo",
     "Construir una matriz de riesgo con tratamiento y dueño",
     "Producir un expediente de compliance con evidencia verificable"],
    [
        {"n": 1, "titulo": "Marcos: ISO 27001, NIST CSF, ENS",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Para qué sirve cada marco",
             "texto": "ISO 27001: sistema de gestión certificable. NIST CSF: "
                      "cinco funciones (Identificar, Proteger, Detectar, "
                      "Responder, Recuperar). ENS: esquema español por "
                      "categorías. Un marco no es un checklist: es lenguaje "
                      "común para decidir."},
            {"tipo": "ejercicio", "titulo": "Mapea un control en los tres marcos",
             "texto": "Elige 'gestión de accesos' y localiza su equivalente "
                      "en ISO (A.9), CSF (PR.AC) y ENS."}]},
        {"n": 2, "titulo": "Datos personales y minimización extrema",
         "lecciones": [
            {"tipo": "lectura", "titulo": "RGPD: base, finalidad, minimización",
             "texto": "Solo se trata el dato necesario para la finalidad "
                      "declarada. El máximo de minimización es no tener el "
                      "dato: el usuario como token anónimo (patrón del "
                      "ecosistema: uuid local, cero email, cero nombre)."},
            {"tipo": "ejercicio", "titulo": "Rediseña un formulario sin PII",
             "texto": "Toma un formulario real (registro de curso) y "
                      "elimina todo dato identificativo innecesario: qué "
                      "queda, qué se pierde, cómo se sigue dando el servicio."}]},
        {"n": 3, "titulo": "Gestión de riesgo con dueño y evidencia",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Riesgo = probabilidad x impacto x activo",
             "texto": "Apreto de riesgo en 4 tratamientos: mitigar, "
                      "transferir, aceptar, eliminar. Todo riesgo tiene un "
                      "dueño con nombre y una fecha de revisión."},
            {"tipo": "ejercicio", "titulo": "Matriz de riesgo de la plataforma",
             "texto": "8 riesgos reales (fuga de material, caída de CDN, "
                      "abuso de API, token robado...): valora, trata, asigna."}]},
        {"n": 4, "titulo": "El expediente de compliance",
         "lecciones": [
            {"tipo": "lectura", "titulo": "Sin evidencia no hay compliance",
             "texto": "El expediente: inventario de activos, matriz de "
                      "riesgo, políticas vigentes, registros de formación y "
                      "de incidentes, revisiones firmadas."},
            {"tipo": "examen", "titulo": "Expediente evaluado",
             "texto": "Entrega el expediente del caso práctico del curso y "
                      "defiéndelo: cada afirmación con su evidencia."}]},
    ],
    [
        {"pregunta": "Las cinco funciones del NIST CSF son...",
         "opciones": ["Planificar, Hacer, Verificar, Actuar", "Identificar, Proteger, Detectar, Responder, Recuperar", "Analizar, Diseñar, Desarrollar, Testear, Desplegar", "Prevenir, Curar, Paliar, Documentar, Auditar"],
         "correcta": 1, "explicacion": "El ciclo de vida del CSF cubre gobierno y operación de la seguridad."},
        {"pregunta": "La minimización extrema de datos significa...",
         "opciones": ["Cifrar todo dos veces", "No tener el dato cuando el servicio puede funcionar sin él", "Guardar solo 30 días", "Anonimizar al administrador"],
         "correcta": 1, "explicacion": "El dato que no existe no puede filtrarse: usuario como token anónimo."},
        {"pregunta": "Los cuatro tratamientos de riesgo son...",
         "opciones": ["Mitigar, transferir, aceptar, eliminar", "Comprar, vender, alquilar, donar", "Detectar, analizar, contener, reportar", "Alto, medio, bajo, nulo"],
         "correcta": 0, "explicacion": "Todo riesgo se trata con una de esas cuatro decisiones y un dueño."},
    ],
)
