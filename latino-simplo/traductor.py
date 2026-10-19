#!/usr/bin/env python3
"""
traductor.py — traductor léxico español ⇄ Latino Simplo.

Es un *glosador* palabra por palabra basado en diccionario, no un traductor
automático completo: traduce el vocabulario, normaliza los artículos y unas
pocas formas verbales frecuentes, y marca con [?palabra] lo que no conoce.
El orden de palabras del Latino Simplo (Sujeto-Verbo-Objeto) y las partículas
de tiempo (ia / va / ave) suelen coincidir con el español, pero conviene
repasar el resultado con la gramatica.md.

Uso:
    python traductor.py --to ls "El perro grande come pan"
    python traductor.py --to es "le cane magno manduca pane"
    python traductor.py --to ls          # modo interactivo
"""

import argparse
import re
import sys
import unicodedata

# --------------------------------------------------------------------------- #
# Diccionario español -> Latino Simplo (lemas y formas frecuentes).
# --------------------------------------------------------------------------- #
ES2LS = {
    # artículos y determinantes
    "el": "le", "la": "le", "los": "les", "las": "les",
    "un": "un", "una": "un", "unos": "unos", "unas": "unos",
    "este": "hoc", "esta": "hoc", "esto": "hoc",
    "ese": "illoc", "esa": "illoc", "eso": "illoc",
    "todo": "omne", "toda": "omne", "todos": "omne", "todas": "omne",
    "otro": "alio", "otra": "alio", "mismo": "mesmo",
    # pronombres y posesivos
    "yo": "io", "tu": "tu", "tú": "tu", "el_pron": "illo",
    "ella": "illa", "nosotros": "nos", "vosotros": "vos",
    "ellos": "illos", "ellas": "illas", "se": "se", "te": "te", "me": "me",
    "mi": "meo", "mis": "meo", "tus": "tuo", "su": "suo", "sus": "suo",
    "nuestro": "nostro", "nuestra": "nostro", "vuestro": "vostro",
    # interrogativos y conectores
    "qué": "que", "quién": "qui", "quien": "qui",
    "dónde": "ubi", "donde": "ubi", "cuándo": "quando", "cuando": "quando",
    "cómo": "como", "como": "como", "cuánto": "quanto", "cuanto": "quanto",
    "y": "et", "e": "et", "o": "o", "u": "o", "pero": "sed",
    "porque": "quia", "si": "si", "que": "que", "ni": "nec",
    "también": "etiam", "sin embargo": "tamen", "por tanto": "ergo",
    "además": "insuper", "por ejemplo": "pro exemplo", "es decir": "id es",
    "entonces": "tunc", "así": "assi", "quizás": "forsan", "quizá": "forsan",
    # preposiciones
    "en": "in", "de": "de", "a": "a", "al": "a le", "del": "de le",
    "con": "con", "sin": "sine", "para": "pro", "por": "per",
    "sobre": "super", "bajo": "sub", "antes": "ante", "después": "post",
    "entre": "inter", "contra": "contra", "hasta": "usque",
    # negación y adverbios
    "no": "non", "sí": "si", "bien": "bene", "mal": "male",
    "mucho": "multo", "mucha": "multo", "muchos": "multo", "muchas": "multo",
    "muy": "multo", "poco": "poco", "poca": "poco", "pocos": "poco",
    "pocas": "poco", "demasiado": "troppo",
    "más": "plus", "menos": "minus", "casi": "quasi", "ya": "jam",
    "todavía": "ancora", "aún": "ancora", "pronto": "mox", "solo": "solo",
    "siempre": "semper", "nunca": "nunquam", "a veces": "aliquando",
    "hoy": "hodie", "mañana": "cras", "ayer": "heri", "ahora": "nunc",
    "gracias": "gratias", "hola": "salve", "adiós": "vale",
    "por favor": "placet", "de nada": "de nihil", "perdón": "excusa",
    # números
    "uno": "uno", "dos": "duo", "tres": "tres", "cuatro": "quatro",
    "cinco": "quinque", "seis": "sex", "siete": "septe", "ocho": "octo",
    "nueve": "nove", "diez": "dece", "cien": "centu", "mil": "mille",
    # tiempo y naturaleza
    "día": "die", "noche": "nocte", "semana": "septimana", "mes": "mense",
    "año": "anno", "hora": "hora", "tiempo": "tempore",
    "agua": "aqua", "sol": "sole", "luna": "luna", "tierra": "terra",
    "cielo": "celo", "mar": "mare", "fuego": "igne", "aire": "aere",
    "viento": "vento", "río": "rivo", "montaña": "monte", "árbol": "arbore",
    "flor": "flore", "piedra": "petra", "lluvia": "pluvia", "nieve": "nive",
    "luz": "lumine", "mundo": "mundo",
    # personas y cuerpo
    "hombre": "homine", "mujer": "femina", "niño": "puero", "niña": "puera",
    "persona": "persona", "padre": "patre", "madre": "matre",
    "hijo": "filio", "hija": "filia", "hermano": "fratre", "hermana": "sorore",
    "amigo": "amico", "gente": "gente", "nombre": "nomine", "vida": "vita",
    "cabeza": "capite", "cara": "facie", "ojo": "oculo", "mano": "manu",
    "pie": "pede", "corazón": "corde", "boca": "bucca", "sangre": "sangue",
    # animales y comida
    "animal": "animale", "perro": "cane", "gato": "gato", "caballo": "equo",
    "ave": "ave", "pez": "pisce", "zorro": "vulpe", "lobo": "lupo",
    "pan": "pane", "vino": "vino", "leche": "lacte", "carne": "carne",
    "queso": "caseo", "huevo": "ovo", "fruta": "fructo", "manzana": "pomo",
    "sal": "sale", "comida": "cibo",
    # casa, ciudad, saber
    "casa": "casa", "puerta": "porta", "ventana": "fenestra", "mesa": "mensa",
    "silla": "sedia", "cama": "lecto", "libro": "libro", "llave": "clave",
    "dinero": "pecunia", "ciudad": "urbe", "calle": "via", "camino": "via",
    "mercado": "mercato", "escuela": "schola", "trabajo": "labore",
    "guerra": "bello", "paz": "pace", "ley": "lege", "arte": "arte",
    # tecnología / IA (de lexico-moderno)
    "ordenador": "computatore", "computadora": "computatore",
    "programa": "programma", "código": "codice", "sistema": "systema",
    "red": "rete", "internet": "interrete", "pantalla": "schermo",
    "usuario": "usatore", "datos": "datos", "dato": "dato",
    "información": "informatione", "modelo": "modello",
    "algoritmo": "algorithmo", "inteligencia": "intelligentia",
    "artificial": "artificiale", "ciencia": "scientia",
    # colores y cualidades
    "color": "colore", "blanco": "albo", "negro": "nigro", "rojo": "rubro",
    "verde": "verde", "azul": "azul", "amarillo": "flavo",
    "grande": "magno", "pequeño": "parvo", "largo": "longo", "corto": "curto",
    "alto": "alto", "bajo_adj": "basso", "bueno": "bono", "buen": "bono",
    "malo": "malo", "nuevo": "novo", "viejo": "vetere", "caliente": "calido",
    "frío": "frigido", "lleno": "pleno", "vacío": "vacuo", "fácil": "facile",
    "difícil": "difficile", "verdadero": "vero", "fuerte": "forte",
    "rápido": "rapido", "lento": "lento", "bonito": "bello", "claro": "claro",
    "feliz": "felice", "triste": "tristo",
    # verbos: infinitivo + presente frecuente -> raíz Latino Simplo
    "ser": "es", "estar": "es",
    "soy": "es", "eres": "es", "es_verbo": "es", "somos": "es",
    "sois": "es", "son": "es", "estoy": "es", "está": "es", "están": "es",
    "tener": "habe", "tengo": "habe", "tienes": "habe", "tiene": "habe",
    "tenemos": "habe", "tienen": "habe", "hay": "habe",
    "hacer": "face", "hago": "face", "haces": "face", "hace": "face",
    "decir": "dice", "digo": "dice", "dices": "dice", "dice_v": "dice",
    "ir": "i", "voy": "i", "vas": "i", "va_v": "i", "vamos": "i", "van": "i",
    "venir": "veni", "vengo": "veni", "viene": "veni", "vienen": "veni",
    "ver": "vide", "veo": "vide", "ves": "vide", "ve": "vide",
    "oír": "audi", "dar": "da", "doy": "da", "das": "da",
    "tomar": "prende", "coger": "prende",
    "saber": "sci", "sé": "sci", "sabes": "sci", "sabe": "sci",
    "conocer": "cognosce", "poder": "pote", "puedo": "pote",
    "puedes": "pote", "puede": "pote", "podemos": "pote", "pueden": "pote",
    "deber": "debe", "debo": "debe", "debes": "debe", "debe_v": "debe",
    "querer": "vole", "quiero": "vole", "quieres": "vole", "quiere": "vole",
    "amar": "ama", "amo": "ama", "amas": "ama", "ama_v": "ama",
    "pensar": "pensa", "creer": "crede", "creo": "crede",
    "hablar": "parla", "hablo": "parla", "hablas": "parla", "habla": "parla",
    "leer": "lege", "leo": "lege", "lees": "lege", "lee": "lege",
    "escribir": "scribe", "comer": "manduca", "como_v": "manduca",
    "comes": "manduca", "come": "manduca", "comemos": "manduca",
    "beber": "bibe", "bebo": "bibe", "bebe": "bibe",
    "dormir": "dormi", "vivir": "vive", "vivo": "vive", "vive_v": "vive",
    "trabajar": "labora", "trabajo_v": "labora", "trabaja": "labora",
    "buscar": "quaere", "encontrar": "inveni", "preguntar": "roga",
    "responder": "responde", "usar": "usa", "necesitar": "necessita",
    "ayudar": "juva", "cambiar": "muta", "crear": "crea",
    "aprender": "apprende", "aprendo": "apprende", "aprende": "apprende",
    "entender": "comprende", "explicar": "explica", "mostrar": "monstra",
    "mirar": "mira", "escuchar": "ausculta", "llegar": "arriva",
    "volver": "retorna", "poner": "pone", "ganar": "vince", "perder": "perde",
    "pagar": "paga", "esperar": "spera", "recordar": "memora",
    "olvidar": "oblida", "empezar": "incipe", "terminar": "fini",
}

# Palabras españolas que colisionan con una forma verbal se desambiguan con un
# sufijo "_pron/_verbo/_adj/_v" en el diccionario; este mapa las normaliza
# según salgan como artículo/pronombre o como verbo. Para un glosador simple,
# preferimos el sentido más frecuente directamente:
ES2LS["el"] = "le"       # artículo (él pronombre se escribe con tilde: "él")
ES2LS["él"] = "illo"
ES2LS["va"] = "i"        # "va" (ir) -> raíz i ; la partícula futuro es distinta


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


# Índice sin acentos para tolerar "como"/"cómo", "arbol"/"árbol", etc.
ES2LS_NORM = {}
for k, v in ES2LS.items():
    ES2LS_NORM.setdefault(strip_accents(k), v)

# Frases de varias palabras (se buscan primero, de más larga a más corta).
MULTIWORD = sorted(
    (k for k in ES2LS if " " in k),
    key=lambda s: len(s.split()),
    reverse=True,
)

# Diccionario inverso Latino Simplo -> español (primera acepción gana).
LS2ES = {}
for es, ls in ES2LS.items():
    clean_es = re.sub(r"_(pron|verbo|adj|v)$", "", es)
    LS2ES.setdefault(ls, clean_es)
# Partículas gramaticales en dirección LS -> ES.
LS2ES.update({
    "ia": "(pasado)", "va": "(futuro)", "ave": "(condicional)",
    "le": "el/la", "les": "los/las", "un": "un/una",
})

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def translate_es_to_ls(text: str) -> str:
    out = []
    # Primero, sustituir frases hechas de varias palabras.
    low = " " + text.lower() + " "
    for phrase in MULTIWORD:
        low = low.replace(" " + phrase + " ", " \0" + phrase.replace(" ", "\1") + "\0 ")
    for raw in low.split():
        if raw.startswith("\0"):
            phrase = raw.strip("\0").replace("\1", " ")
            out.append(ES2LS[phrase])
            continue
        for tok in TOKEN_RE.findall(raw):
            if not tok.isalpha():
                out.append(tok)
                continue
            key = tok.lower()
            ls = ES2LS.get(key) or ES2LS_NORM.get(strip_accents(key))
            out.append(ls if ls else f"[?{tok}]")
    return _join(out)


def translate_ls_to_es(text: str) -> str:
    out = []
    for tok in TOKEN_RE.findall(text):
        if not tok.isalpha():
            out.append(tok)
            continue
        key = tok.lower()
        es = LS2ES.get(key)
        if es is None and key.endswith("es"):   # plural -es
            es = LS2ES.get(key[:-2])
        if es is None and key.endswith("s"):     # plural -s
            es = LS2ES.get(key[:-1])
        out.append(es if es else f"[?{tok}]")
    return _join(out)


def _join(tokens):
    text = ""
    for t in tokens:
        if t in ",.;:!?)]}" or t in "'":
            text += t
        elif text and text[-1] in "([{¿¡":
            text += t
        elif text:
            text += " " + t
        else:
            text += t
    return text


def main():
    ap = argparse.ArgumentParser(description="Traductor léxico español ⇄ Latino Simplo")
    ap.add_argument("--to", choices=["ls", "es"], required=True,
                    help="ls = español→Latino Simplo ; es = Latino Simplo→español")
    ap.add_argument("text", nargs="*", help="texto a traducir (si falta: interactivo)")
    args = ap.parse_args()

    fn = translate_es_to_ls if args.to == "ls" else translate_ls_to_es

    if args.text:
        print(fn(" ".join(args.text)))
        return

    print("Modo interactivo. Escribe una frase (Ctrl-D o 'vale' para salir).")
    for line in sys.stdin:
        line = line.strip()
        if not line or line.lower() == "vale":
            break
        print("  ->", fn(line))


if __name__ == "__main__":
    main()
