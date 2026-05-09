# Carga del LLM. ChatOpenAI apuntando a LM Studio.
# `llm` se construye perezosa: importar este módulo no fuerza conexión.
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# Defaults de la API OpenAI-compatible de LM Studio. Centralizados aquí
# para que api.py y los builders del agente no los repliquen literal.
DEFAULT_OPENAI_BASE_URL = "http://localhost:1234/v1"
DEFAULT_OPENAI_MODEL = "local-model"
DEFAULT_OPENAI_API_KEY = "lm-studio"


def get_openai_base_url() -> str:
    """Base URL del servidor OpenAI-compatible (LM Studio por defecto)."""
    return os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)


def get_openai_model() -> str:
    """Modelo activo según el .env. Vacío si no se ha definido."""
    return os.getenv("OPENAI_MODEL", "")


_llm_instance: Any = None


def build_llm(temperature: float = 0.0, model: str | None = None):
    """Crea una instancia nueva de chat model contra LM Studio.

    Sigue la recomendación de LangChain 1.x: `init_chat_model` como
    fábrica unificada en lugar de instanciar `ChatOpenAI` directamente.
    Eso permite cambiar de proveedor cambiando solo el string del
    modelo (`openai:...`, `anthropic:...`, `ollama:...`...) sin tocar
    el resto del código. Aquí seguimos con el proveedor `openai` porque
    LM Studio expone una API compatible OpenAI en `/v1`.

    Si `model` es None se usa el de la env var `OPENAI_MODEL`. Pasarlo
    explícito permite construir LLMs con modelos distintos en runtime,
    por ejemplo desde la UI cuando el usuario elige otro modelo del
    selector que se rellena con `GET /v1/models` de LM Studio.
    """
    nombre_modelo = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    base_url = get_openai_base_url()
    # LM Studio la ignora; el SDK exige que esté definida.
    api_key = os.getenv("OPENAI_API_KEY", DEFAULT_OPENAI_API_KEY)

    try:
        # LangChain 1.x: forma unificada y recomendada por la documentación
        # oficial. Permite cambiar de proveedor con solo el prefijo del modelo
        # (`openai:...`, `anthropic:...`, `ollama:...`) sin tocar el resto.
        from langchain.chat_models import init_chat_model
        return init_chat_model(
            f"openai:{nombre_modelo}",
            temperature=temperature,
            base_url=base_url,
            api_key=api_key,
        )
    except Exception:
        # Fallback al import directo por si init_chat_model no acepta kwargs
        # propios del provider en alguna versión concreta de LangChain.
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=nombre_modelo,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
        )


def __getattr__(name: str):
    """`llm` se crea solo la primera vez que alguien la pide."""
    global _llm_instance
    if name == "llm":
        if _llm_instance is None:
            _llm_instance = build_llm()
        return _llm_instance
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_llm(model: str | None = None):
    """Devuelve la instancia del LLM. Si `model` es None, reusa la instancia
    perezosa global (con el modelo del .env). Si se pasa un modelo concreto,
    construye una instancia nueva con ese modelo.

    Lo usan los dos builders del agente (LangChain y LangGraph) para
    soportar el cambio de modelo en runtime sin duplicar el patrón
    `build_llm(model=model) if model else llm`."""
    if model:
        return build_llm(model=model)
    # Trigger the module-level __getattr__ que cachea la instancia.
    from shared import load_model as _self
    return _self.llm


if __name__ == "__main__":
    print(f"[load_model] base_url={os.getenv('OPENAI_BASE_URL')} model={os.getenv('OPENAI_MODEL')}")
    print("Probando una llamada sencilla...")
    r = build_llm().invoke("Dime en una línea qué es un RPA.")
    print(r.content)
