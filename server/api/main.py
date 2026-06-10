import json
import os
from pathlib import Path
from typing import Optional
from urllib import error, request as urllib_request

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(base_dir / 'templates'))
app.mount('/static', StaticFiles(directory=str(base_dir / 'static')), name='static')

VLLM_NEMO_BASE_URL = os.getenv('VLLM_NEMO_BASE_URL', 'http://localhost:8001/v1')
VLLM_NEMO_MODEL = os.getenv('VLLM_NEMO_MODEL', 'mistral-nemo')
DISCUSSION_UNLOCKS_ENIGMA_ID = 4
DEFAULT_DISCUSSION_TEMPERATURE = 0.7
MIN_DISCUSSION_TEMPERATURE = 0.0
MAX_DISCUSSION_TEMPERATURE = 1.5

ENIGMES = [
    {
        'id': 1,
        'title': 'La Porte du Cachot',
        'paragraphs': [
            "Vos yeux s'habituent à l'obscurité. Sur le mur du cachot, quelqu'un a gravé des symboles au couteau.",
            "À côté de la porte, une serrure à code à 4 chiffres brille faiblement dans la pénombre.",
            "Une note est glissée entre deux planches. La clé de votre liberté se cache dans ce code."
        ],
        'hint': 'Le code est basé sur les symboles manquants dans la suite gravée.',
        'accepted_answers': ['8602']
    },
    {
        'id': 2,
        'title': 'La Carte lexicale',
        'paragraphs': [
            "Une mystérieuse carte contient des mots organisés comme un lexique caché.",
            "Comprendre le lien entre les mots vous permettra de continuer votre route.",
            "Seul le mot juste ouvrira la porte vers la suite de l’aventure."
        ],
        'hint': 'Cherche un mot qui décrit la logique de cette carte.',
        'accepted_answers': ['lexique', 'carte', 'carte lexicale']
    },
    {
        'id': 3,
        'title': 'La clef du son',
        'paragraphs': [
            "Otto a besoin de vous pour refaire fonctionner son lecteur de musique.",
            "Trouvez le mot de passe de son lecteur et peut-être vous laissera-t-il passer.",
        ],
        'hint': 'Le mot est lié à l’objet et au capitaine.',
        'accepted_answers': ['ancre', 'capitaine']
    },
    {
        'id': 4,
        'title': 'La Chambre des Échos',
        'paragraphs': [
            "Dans cette salle, les réponses se reflètent et les mots tentent de vous tromper.",
            "Pour réussir, il faut montrer que vous êtes bien un humain et non une machine.",
            "Réponds avec clarté pour prouver ton intelligence."
        ],
        'hint': 'Le mot attendu prouve que tu es humain.',
        'accepted_answers': ['humain', 'je suis humain']
    },
    {
        'id': 5,
        'title': 'La Lettre Effacée',
        'paragraphs': [
            "Une vieille lettre révèle un message à reconstituer.",
            "Les blancs indiquent la direction du trésor et la salle secrète.",
            "Retourne la lettre dans ta tête et donne la bonne réponse."
        ],
        'hint': 'Un mot caché dans la lettre te mène à la carte.',
        'accepted_answers': ['carte', 'carte au trésor']
    },
    {
        'id': 6,
        'title': 'La Carte au Trésor',
        'paragraphs': [
            "La carte dévoile un réseau de flèches et de chemins.",
            "L'orientation du trésor est essentielle pour atteindre la salle secrète.",
            "Donne la direction correcte pour finir cette étape."
        ],
        'hint': 'Le trésor est indiqué par une direction simple.',
        'accepted_answers': ['est']
    }
]


def get_enigma(enigma_id: int) -> dict:
    for item in ENIGMES:
        if item['id'] == enigma_id:
            return item
    raise ValueError(f'Énigme introuvable: {enigma_id}')


def is_correct_answer(response: str, accepted_answers: list[str]) -> bool:
    normalized = response.strip().lower()
    return any(normalized == answer.strip().lower() for answer in accepted_answers)


def normalize_history(raw_history: str) -> list[dict[str, str]]:
    if not raw_history:
        return []

    try:
        parsed = json.loads(raw_history)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    history: list[dict[str, str]] = []
    for item in parsed[-12:]:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        content = item.get('content')
        if role not in {'user', 'assistant'}:
            continue
        if not isinstance(content, str):
            continue
        cleaned = content.strip()
        if not cleaned:
            continue
        history.append({'role': role, 'content': cleaned[:2000]})
    return history


def parse_temperature(raw_value: str) -> float:
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_DISCUSSION_TEMPERATURE

    if value < MIN_DISCUSSION_TEMPERATURE:
        return MIN_DISCUSSION_TEMPERATURE
    if value > MAX_DISCUSSION_TEMPERATURE:
        return MAX_DISCUSSION_TEMPERATURE
    return value


def ask_nemo(messages: list[dict[str, str]], temperature: float) -> str:
    url = f"{VLLM_NEMO_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        'model': VLLM_NEMO_MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': 500,
    }
    req = urllib_request.Request(
        url=url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dummy',
        },
        method='POST',
    )

    try:
        with urllib_request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return "Je n'arrive pas a joindre le LLM pour le moment. Reessaie dans quelques instants."

    choices = data.get('choices')
    if not isinstance(choices, list) or not choices:
        return "Le LLM n'a pas renvoye de reponse exploitable."

    message = choices[0].get('message', {})
    if not isinstance(message, dict):
        return "Le LLM a renvoye un format inattendu."

    content = message.get('content')
    if not isinstance(content, str) or not content.strip():
        return "Le LLM n'a pas fourni de texte de reponse."
    return content.strip()


def render_discussion_page(
    request: Request,
    chat_history: list[dict[str, str]],
    discussion_temperature: float = DEFAULT_DISCUSSION_TEMPERATURE,
):
    return templates.TemplateResponse(
        request,
        'discussion.html',
        {
            'request': request,
            'enigmes': ENIGMES,
            'current_enigma_id': DISCUSSION_UNLOCKS_ENIGMA_ID,
            'chat_history': chat_history,
            'discussion_temperature': discussion_temperature,
            'visited': [],
            'completed': [],
        },
    )


@app.get('/')
def landing(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'request': request})


@app.get('/enigme/{enigma_id}')
def show_enigma(request: Request, enigma_id: int, error: Optional[str] = None):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    # read progress cookie (supports legacy array or new object)
    progress_cookie = request.cookies.get('progress', '')
    visited: list[int] = []
    completed: list[int] = []
    try:
        parsed = json.loads(progress_cookie) if progress_cookie else {}
        if isinstance(parsed, list):
            # legacy: array of completed ids
            completed = [int(v) for v in parsed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
        elif isinstance(parsed, dict):
            raw_visited = parsed.get('visited', [])
            raw_completed = parsed.get('completed', [])
            if isinstance(raw_visited, list):
                visited = [int(v) for v in raw_visited if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
            if isinstance(raw_completed, list):
                completed = [int(v) for v in raw_completed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
    except Exception:
        visited = []
        completed = []

    # mark current page as visited
    if enigma_id not in visited:
        visited.append(enigma_id)

    cookie_value = json.dumps({'visited': visited, 'completed': completed})

    resp = templates.TemplateResponse(
        request,
        'enigme.html',
        {
            'request': request,
            'current': enigma,
            'enigmes': ENIGMES,
            'error': error == 'wrong',
            'discussion_available': enigma['id'] >= DISCUSSION_UNLOCKS_ENIGMA_ID,
            'visited': visited,
            'completed': completed,
        }
    )
    resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
    return resp


@app.get('/interlude/discussion')
def discussion_menu(request: Request):
    # read progress cookie and mark discussion as visited
    progress_cookie = request.cookies.get('progress', '')
    visited: list[int] = []
    completed: list[int] = []
    try:
        parsed = json.loads(progress_cookie) if progress_cookie else {}
        if isinstance(parsed, list):
            completed = [int(v) for v in parsed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
        elif isinstance(parsed, dict):
            raw_visited = parsed.get('visited', [])
            raw_completed = parsed.get('completed', [])
            if isinstance(raw_visited, list):
                visited = [int(v) for v in raw_visited if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
            if isinstance(raw_completed, list):
                completed = [int(v) for v in raw_completed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
    except Exception:
        visited = []
        completed = []

    if DISCUSSION_UNLOCKS_ENIGMA_ID not in visited:
        visited.append(DISCUSSION_UNLOCKS_ENIGMA_ID)

    cookie_value = json.dumps({'visited': visited, 'completed': completed})

    resp = render_discussion_page(
        request,
        chat_history=[],
        discussion_temperature=DEFAULT_DISCUSSION_TEMPERATURE,
    )
    resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
    return resp


@app.post('/interlude/discussion')
def discussion_message(
    request: Request,
    message: str = Form(...),
    history: str = Form(default='[]'),
    temperature: str = Form(default=str(DEFAULT_DISCUSSION_TEMPERATURE)),
):
    selected_temperature = parse_temperature(temperature)
    normalized_message = message.strip()
    if not normalized_message:
        return render_discussion_page(
            request,
            chat_history=normalize_history(history),
            discussion_temperature=selected_temperature,
        )

    chat_history = normalize_history(history)
    messages = [
        {
            'role': 'system',
            'content': (
                "Tu es le Gardien des Echos dans une aventure pedagogique. "
                "Tu reponds uniquement en francais, de facon concise et claire. "
                "Tu aides l'eleve a raisonner sans donner directement la solution d'une enigme."
            ),
        },
        *chat_history,
        {'role': 'user', 'content': normalized_message[:2000]},
    ]
    answer = ask_nemo(messages, temperature=selected_temperature)

    updated_history = [
        *chat_history,
        {'role': 'user', 'content': normalized_message},
        {'role': 'assistant', 'content': answer},
    ]

    # also mark discussion as visited in cookie
    progress_cookie = request.cookies.get('progress', '')
    visited: list[int] = []
    completed: list[int] = []
    try:
        parsed = json.loads(progress_cookie) if progress_cookie else {}
        if isinstance(parsed, list):
            completed = [int(v) for v in parsed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
        elif isinstance(parsed, dict):
            raw_visited = parsed.get('visited', [])
            raw_completed = parsed.get('completed', [])
            if isinstance(raw_visited, list):
                visited = [int(v) for v in raw_visited if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
            if isinstance(raw_completed, list):
                completed = [int(v) for v in raw_completed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
    except Exception:
        visited = []
        completed = []

    if DISCUSSION_UNLOCKS_ENIGMA_ID not in visited:
        visited.append(DISCUSSION_UNLOCKS_ENIGMA_ID)

    cookie_value = json.dumps({'visited': visited, 'completed': completed})

    resp = render_discussion_page(
        request,
        chat_history=updated_history[-12:],
        discussion_temperature=selected_temperature,
    )
    resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
    return resp


@app.post('/enigme/{enigma_id}/submit')
def submit_answer(request: Request, enigma_id: int, response: str = Form(...)):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    if is_correct_answer(response, enigma['accepted_answers']):
        # update progress cookie: keep visited and completed lists
        progress_cookie = request.cookies.get('progress', '')
        visited: list[int] = []
        completed: list[int] = []
        try:
            parsed = json.loads(progress_cookie) if progress_cookie else {}
            if isinstance(parsed, list):
                completed = [int(v) for v in parsed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
            elif isinstance(parsed, dict):
                raw_visited = parsed.get('visited', [])
                raw_completed = parsed.get('completed', [])
                if isinstance(raw_visited, list):
                    visited = [int(v) for v in raw_visited if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
                if isinstance(raw_completed, list):
                    completed = [int(v) for v in raw_completed if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
        except Exception:
            visited = []
            completed = []

        try:
            if enigma_id not in completed:
                completed.append(enigma_id)
        except Exception:
            pass

        cookie_value = json.dumps({'visited': visited, 'completed': completed})

        if enigma_id == 3:
            resp = RedirectResponse(url='/interlude/discussion?completed=3', status_code=status.HTTP_302_FOUND)
            resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
            return resp

        next_id = enigma_id + 1 if enigma_id < len(ENIGMES) else None
        target = f'/enigme/{next_id}?completed={enigma_id}' if next_id else f'/enigme/{enigma_id}?completed={enigma_id}'
        resp = RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)
        resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
        return resp

    return RedirectResponse(url=f'/enigme/{enigma_id}?error=wrong', status_code=status.HTTP_302_FOUND)


@app.post('/progress/reset')
def reset_progress(request: Request):
    referer = request.headers.get('referer', '/')
    resp = RedirectResponse(url=referer, status_code=status.HTTP_302_FOUND)
    resp.delete_cookie('progress')
    return resp
