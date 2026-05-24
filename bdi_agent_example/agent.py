import sys
import subprocess
import shutil
import urllib.request
import urllib.error
import json
import os
from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from . import rag   
#from rag import consultar_documentacion 

#CONVERTIR EN SECUENCIAL(paralelo(Github, Documentacion), Iterativo(testCode), Guardar)


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 3
current_retries = 0
best_mas_state = {}
best_error_count = float('inf')


def resolve_jason_command():
    """
    Busca el ejecutable de Jason en este orden:
    1. Variable de entorno JASON_BIN
    2. Comando 'jason' disponible en el PATH
    3. Ruta típica de macOS (/Applications/jason)
    4. Ruta típica de Windows (C:\\Jason\\bin\\jason.bat)
    """
    env_path = os.getenv("JASON_BIN")
    if env_path:
        return env_path

    path_command = shutil.which("jason")
    if path_command:
        return path_command

    default_macos_path = "/Applications/jason"
    if Path(default_macos_path).exists():
        return default_macos_path

    default_windows_paths = [
        r"C:\Jason\bin\jason.bat",
        r"C:\Program Files\Jason\bin\jason.bat",
        r"C:\Program Files (x86)\Jason\bin\jason.bat",
    ]
    for windows_path in default_windows_paths:
        if Path(windows_path).exists():
            return windows_path

    return None

def search_github_examples(path: str = "") -> str:
    """
    Permite acceder a los ejemplos oficiales de código de Jason (BDI) en GitHub.
    Útil para consultar cómo se implementan ciertas características en Jason.
    
    Args:
        path: La ruta relativa del archivo o directorio de ejemplo a consultar dentro de la carpeta 'examples' de Jason.
              Déjalo vacío ("") para listar los directorios y archivos de la raíz de ejemplos.
              Puedes usar esta herramienta primero con "" para ver qué ejemplos hay, y luego llamarla 
              de nuevo con la ruta específica, ej. "blocks/blocks.mas2j" o "auction/ag1.asl".
    """
    base_api_url = "https://api.github.com/repos/jason-lang/jason/contents/examples"
    url = f"{base_api_url}/{path}".strip("/")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Python-urllib'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if isinstance(data, list):
                items = [f"[{item['type']}] {item['path'].replace('examples/', '', 1)}" for item in data]
                return f"Contenido de '{path or 'raíz'}':\n" + "\n".join(items)
            
            elif isinstance(data, dict) and data.get("type") == "file":
                download_url = data.get("download_url")
                if download_url:
                    req_file = urllib.request.Request(download_url, headers={'User-Agent': 'Python-urllib'})
                    with urllib.request.urlopen(req_file) as f_res:
                        return f_res.read().decode('utf-8')
                return "Error: No se encontró la URL de descarga del archivo."
            else:
                return "Respuesta inesperada de la API de GitHub."
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"Error: No se encontró la ruta '{path}' en los ejemplos de Jason."
        if e.code == 403:
            return "Error: Límite de peticiones a la API de GitHub excedido. Inténtalo más tarde."
        return f"Error HTTP al acceder a GitHub: {e.code} - {e.reason}"
    except Exception as e:
        return f"Error al intentar acceder a los ejemplos: {e}"

def test_mas_code(mas2j_code: str, agents_dict: dict) -> str:
    """
    Guarda y ejecuta el código en un directorio temporal para probar el sistema Multi-Agente usando jason.
    NO guarda los archivos definitivamente, solo devuelve la salida para que verifiques si funciona.
    Tiene un límite de 5 intentos por sesión.
    
    Args:
        mas2j_code: El contenido completo del archivo de configuración .mas2j.
        agents_dict: Un diccionario donde la clave es el nombre del archivo (ej. "agent1.asl") 
                     y el valor es el contenido de ese archivo .asl.
    """
    global current_retries, best_mas_state, best_error_count
    
    if current_retries >= MAX_RETRIES:
         return f"ERROR: Has superado el límite de {MAX_RETRIES} intentos. Por favor, utiliza 'save_mas_code' para guardar el último código de inmediato y termina tu respuesta."
         
    current_retries += 1
    
    temp_dir = Path("temp_mas_project")
    
    try:
        # Limpiar si ya existe
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Guardar .mas2j
        mas2j_file = temp_dir / "temp.mas2j"
        mas2j_file.write_text(mas2j_code, encoding="utf-8")
        
        # Guardar archivos .asl
        for filename, content in agents_dict.items():
            if not filename.endswith(".asl"):
                filename += ".asl"
            (temp_dir / filename).write_text(content, encoding="utf-8")
            
        jason_command = resolve_jason_command()
        if not jason_command:
            return (
                "ERROR: No se ha encontrado Jason. Instálalo y define la variable "
                "de entorno JASON_BIN o añade el comando 'jason' al PATH."
            )

        result = subprocess.run(
            [jason_command, "mas", "start", "--mas2j=temp.mas2j", "--console"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # Heurística simple para contar errores basándonos en STDERR y el código de retorno
        error_count = 0
        if result.returncode != 0:
            error_count += 10
        if result.stderr:
            error_count += len(result.stderr.split('\n'))
            
        if error_count < best_error_count:
            best_error_count = error_count
            best_mas_state = {
                "mas2j": mas2j_code,
                "agents": agents_dict
            }
            
        # Format output
        output = f"=== EJECUCIÓN DE PRUEBA (Intento {current_retries}/{MAX_RETRIES}) ===\nReturn code: {result.returncode}\n"
        if result.stdout:
            output += f"--- STDOUT ---\n{result.stdout}\n"
        if result.stderr:
            output += f"--- STDERR ---\n{result.stderr}\n"
            
        return output
        
    except subprocess.TimeoutExpired as e:
        # En muchos sistemas, jason arranca la GUI y se queda pillado. Guardamos el estado.
        if best_error_count == float('inf'):
            best_mas_state = {
                "mas2j": mas2j_code,
                "agents": agents_dict
            }
            
        output = f"=== EJECUCIÓN DE PRUEBA (Intento {current_retries}/{MAX_RETRIES}) ===\n"
        output += "AVISO: La ejecución alcanzó el tiempo límite (15s). Esto es normal si Jason arranca una interfaz y no finaliza solo.\n"
        if hasattr(e, 'stdout') and e.stdout:
            stdout_str = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else e.stdout
            output += f"--- STDOUT (parcial) ---\n{stdout_str}\n"
        return output
        
    except FileNotFoundError:
        return "ERROR: El comando 'jason' no se encuentra en el sistema. Asegúrate de tener instalado Jason y agregado al PATH."
    except Exception as e:
        return f"ERROR inesperado al ejecutar: {e}"
    finally:
        # Limpiar
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def save_mas_code(mas_name: str, mas2j_code: str = "", agents_dict: dict = None) -> str:
    """
    Guarda el sistema MAS completo (el .mas2j y los .asl) en su propia subcarpeta dentro de 'output'.
    Si provees 'mas2j_code' y 'agents_dict', guardará esos. Si están vacíos, usará el 'mejor' código que lograste ejecutar en tus pruebas.
    
    Args:
        mas_name: Nombre del proyecto (se usará para la subcarpeta en 'output' y el archivo .mas2j).
    """
    global current_retries, best_mas_state, best_error_count
    
    if agents_dict is None:
        agents_dict = {}
        
    project_dir = OUTPUT_DIR / mas_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    code_mas2j = mas2j_code if mas2j_code else best_mas_state.get("mas2j", "")
    code_agents = agents_dict if agents_dict else best_mas_state.get("agents", {})
    
    if not code_mas2j or not isinstance(code_agents, dict) or not code_agents:
         return "ERROR: No hay código generado para guardar o no se ha probado previamente."
         
    try:
        # Guardar .mas2j
        mas_filename = f"{mas_name}.mas2j" if not mas_name.endswith(".mas2j") else mas_name
        (project_dir / mas_filename).write_text(str(code_mas2j), encoding="utf-8")
        
        # Guardar .asl
        for filename, content in code_agents.items():
            if not filename.endswith(".asl"):
                filename += ".asl"
            (project_dir / filename).write_text(str(content), encoding="utf-8")
        
        # Resetear estado para próximas llamadas del usuario
        current_retries = 0
        best_mas_state = {}
        best_error_count = float('inf')
        
        return f"ÉXITO: Proyecto BDI guardado correctamente en {project_dir}"
    except Exception as e:
        return f"ERROR inesperado al guardar: {e}"

# Configuramos el modelo, asumiendo la configuración habitual
import os
model = LiteLlm(
    #model="openai/gpt-oss-120b", 
    model= "openai/Qwen3.6-35B-A3B-FP8",
    api_base=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

save_code = LlmAgent(
    name="saver_code",
    model=model,
    description="Eres un agente que se encarga de guardar información",
    instruction=(
        "El código Jason a guardar está en {code}.\n"
        "estás OBLIGADO a llamar a 'save_mas_code(mas_name, mas2j_code, agents_dict)' para persistir el proyecto.\n"
        "Informa del éxito de la creación y da un breve resumen.\n"
        "SIEMPRE debes usar estrictamente el nombre técnico exacto 'save_mas_code' , sino es una CATASTROFE DE SINTAXIS"
    ),
    tools=[save_mas_code]
)

# TERMINAR EL LOOP PRONTO
from google.adk.tools.tool_context import ToolContext
# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}

tester = LlmAgent(
    name="tester",
    model=model,
    description="Eres un agente experto programador en AgentSpeak y Jason, orientado a sistemas Multi-Agente BDI (Belief-Desire-Intention).",
    instruction=(
        "Tú objetivo es revisar el código en {code} hecho hasta ahora y determinar si se continua perfeccionando el código o ya funciona como el usuario habia indicado en el prompt"
        "Para comprobar si el código funciona ejecuta 'test_mas_code'"
        "Asegurate que la sintaxis es correcta puedes utilizar {git} y {docs}"
        "1. IMPORTANTE SINTAXIS .mas2j: El archivo de configuración DEBE seguir estrictamente esta estructura:\n"
        "   MAS nombre_proyecto {\n"
        "       infrastructure: Centralised\n"
        "       agents:\n"
        "           nombre_agente_1;\n"
        "           nombre_agente_2 #3; /* Si necesitas instanciar 3 copias */\n"
        "   }\n"
        "   REGLAS MAS2J: Usa 'MAS' en mayúsculas. NO pongas la extensión '.asl' en la lista de agentes. Acaba cada declaración de agente con punto y coma (;). nombre_proyecto solo son minúsculas sin espacios\n"
        "2. IMPORTANTE SINTAXIS AGENTSPEAK (.asl):\n"
        "   - Las creencias y objetivos se deben declarar al principio del fichero, antes de los planes.\n"
        "   - Las variables DEBEN empezar con letra Mayúscula (ej. PosX). Los átomos y literales con minúscula (ej. mesa).\n"
        "   - Para poder operar con un valor de una creencia hay que intanciarlo siempre primero en una variable.\n"
        "   - El formato estricto de un plan es: +!meta(Arg) : contexto <- accion1; accion2. ¡ATENCIÓN: TODOS los planes y creencias DEBEN terminar obligatoriamente con un PUNTO FINAL (.)!\n"
        "   - ¡Evita el error 'No plan for event'! Debes añadir SIEMPRE un plan de contingencia genérico por si falla el contexto: +!meta(_) <- .print(\"Fallo en \", meta).\n"
        "   - Las internal actions nativas de Jason siempre llevan un punto delante (ej. .print(\"Hola\"); .wait(1000);) y recuerda cerrar el plan con PUNTO (.).\n"
        "   - Para iniciar la ejecución debes añadir una creencia o un objetivo inicial en el agente que inicie el sistema. Por ejemplo: DEBES poner \"!start.\" para poder ejecutar al inicio el plan \"+!start <- accion. \" \n"
        "ERRORES COMUNES A EVITAR:"
        "- PROHIBIDO usar // como comentario. Jason SOLO admite /* comentario */."
        "- PROHIBIDO usar ^ en triggers de planes (ej. +^initGoal). Para inicializar, pon '!start.' como creencia inicial y define el plan '+!start <- ...'."
        "- PROHIBIDO pasar expresiones aritméticas como argumentos directos (ej. .print(A+B) o +!plan(A+B)). SIEMPRE calcula primero con 'is': 'C is A + B; .print(C); +!plan(C).'"
        "- El plan de contingencia genérico correcto es: '+!goal(X) : true <- .print('Fallo en goal').' — el funtor debe coincidir con el goal, nunca uses +!_."
        "- Si consideras que es correcto llama a exit_loop"
        "- Si consideras que es incorrecto devuelve lo que se debe corregir"
    ),
    tools=[test_mas_code, exit_loop],
    output_key="errores"
)

refine = LlmAgent(
    name="refine",
    model=model,
    description="Agente experto en desarrollador proyectos Multi-Agente BDI en Jason.",
    instruction=(
        "Eres un agente experto programador en AgentSpeak y Jason, orientado a sistemas Multi-Agente BDI (Belief-Desire-Intention). "
        "Si existe la clave {errores} en el contexto, úsala para saber qué corregir. "
        "Si no existe aún, genera el código desde cero basándote en {git} y {docs}."
        "1. Analiza lo que pide el usuario y diseña la estructura del sistema: un archivo de configuración .mas2j y uno o más agentes en archivos .asl.\n"
        "2. IMPORTANTE SINTAXIS .mas2j: El archivo de configuración DEBE seguir estrictamente esta estructura:\n"
        "   MAS nombre_proyecto {\n"
        "       infrastructure: Centralised\n"
        "       agents:\n"
        "           nombre_agente_1;\n"
        "           nombre_agente_2 #3; /* Si necesitas instanciar 3 copias */\n"
        "   }\n"
        "   REGLAS MAS2J: Usa 'MAS' en mayúsculas. NO pongas la extensión '.asl' en la lista de agentes. Acaba cada declaración de agente con punto y coma (;). nombre_proyecto solo son minúsculas sin espacios\n"
        "3. IMPORTANTE SINTAXIS AGENTSPEAK (.asl):\n"
        "   - Las creencias y objetivos se deben declarar al principio del fichero, antes de los planes.\n"
        "   - Las variables DEBEN empezar con letra Mayúscula (ej. PosX). Los átomos y literales con minúscula (ej. mesa).\n"
        "   - Para poder operar con un valor de una creencia hay que intanciarlo siempre primero en una variable.\n"
        "   - El formato estricto de un plan es: +!meta(Arg) : contexto <- accion1; accion2. ¡ATENCIÓN: TODOS los planes y creencias DEBEN terminar obligatoriamente con un PUNTO FINAL (.)!\n"
        "   - ¡Evita el error 'No plan for event'! Debes añadir SIEMPRE un plan de contingencia genérico por si falla el contexto: +!meta(_) <- .print(\"Fallo en \", meta).\n"
        "   - Las internal actions nativas de Jason siempre llevan un punto delante (ej. .print(\"Hola\"); .wait(1000);) y recuerda cerrar el plan con PUNTO (.).\n"
        "   - Para iniciar la ejecución debes añadir una creencia o un objetivo inicial en el agente que inicie el sistema. Por ejemplo: DEBES poner \"!start.\" para poder ejecutar al inicio el plan \"+!start <- accion. \" \n"
        "ERRORES COMUNES A EVITAR:"
        "- PROHIBIDO usar // como comentario. Jason SOLO admite /* comentario */."
        "- PROHIBIDO usar ^ en triggers de planes (ej. +^initGoal). Para inicializar, pon '!start.' como creencia inicial y define el plan '+!start <- ...'."
        "- PROHIBIDO pasar expresiones aritméticas como argumentos directos (ej. .print(A+B) o +!plan(A+B)). SIEMPRE calcula primero con 'is': 'C is A + B; .print(C); +!plan(C).'"
        "- El plan de contingencia genérico correcto es: '+!goal(X) : true <- .print('Fallo en goal').' — nunca uses +!_."
        "Para generar el código debes usar la información obtenida por los agentes de búsqueda (search_github y search_local_docs) revisa el codigo LLAMANDO SÍ O SÍ a 'test_mas_code(mas2j_code, agents_dict)' para probar si el sistema compila. Si falla, lee la excepción devuelta en el log y devuelvela, se volvera a buscar más información para que puedas mejorar el código."
        "SIEMPRE debes usar estrictamente el nombre técnico exacto 'test_mas_code', sino es una CATASTROFE DE SINTAXIS"
    ),
    tools=[test_mas_code],
    output_key="code"
)

search_github_agent = LlmAgent(
    name="search_github",
    model=model,
    description="Eres un agente experto en buscar inspiración o codigos de ejemplo en los repositorios de GitHub sobre codigo Json BDI.",
    instruction=(
        "Busca en github ejemplos de código relacionados con la consulta del usuario. Para ello utiliza la herramienta 'search_github_examples(path)'."
        "SIEMPRE debes usar estrictamente el nombre técnico exacto 'search_github_examples' , sino es una CATASTROFE DE SINTAXIS"
    ),
    tools=[search_github_examples],
    output_key="git"
)

search_loc_docs = LlmAgent(
    name="search_docs",
    model=model,
    description="Eres un agente experto en sintaxis y teoría tecnica de Jason.",
    instruction=(
        "Busca en la documentación local ejemplos de teoría técnica, tutoriales o sintaxis de Programación BDI relevante. Para ello utiliza la herramienta 'search_local_docs(query)'."
        "SIEMPRE debes usar estrictamente el nombre técnico exacto 'search_local_docs' , sino es una CATASTROFE DE SINTAXIS"
    ),
    tools=[rag.search_local_docs],
    output_key="docs"
)

# Iniciar error a nada
from google.adk.agents.callback_context import CallbackContext

def ini_error(callback_context: CallbackContext) -> None:
    callback_context.state.update({"errores": ""})
    return

refiner = LoopAgent(
    name="text_refiner",
    sub_agents=[refine, tester],
    max_iterations = 3,
    before_agent_callback=ini_error
)

search_info = ParallelAgent(
    name="search_info",
    sub_agents=[search_github_agent, search_loc_docs],
)

root_agent = SequentialAgent(
    name="news_pipeline",
    sub_agents=[search_info, refiner, save_code]
)