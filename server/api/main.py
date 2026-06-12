import json
import os
import re
import unicodedata
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
DEFAULT_DISCUSSION_TEMPERATURE = 0.5
MIN_DISCUSSION_TEMPERATURE = 0.0
MAX_DISCUSSION_TEMPERATURE = 1.0

ENIGMES = [
    {
        'id': 1,
        'title': 'La Porte du Cachot',
        'paragraphs': [
            "Vos yeux s'habituent à l'obscurité. Sur le mur du cachot, quelqu'un a gravé des symboles au couteau.",
            "À côté de la porte, une serrure vocale brille faiblement dans la pénombre.",
            "Une note est glissée entre deux planches. La clé de votre liberté se cache dans ce code."
        ],
        'puzzle_intro': 'Complétez la suite de symboles, puis renseignez la phrase associée à cette suite pour ouvrir la porte.',
        'accepted_answers': ['le pirate attaque et pille le marin.', 'le pirate attaque et pille le marin']
    },
    {
        'id': 2,
        'title': 'La Carte lexicale',
        'paragraphs': [
            "Une mystérieuse carte contient des mots organisés comme un lexique caché.",
            "Comprendre le lien entre les mots vous permettra de continuer votre route.",
            "Seul le mot juste ouvrira la porte vers la suite de l’aventure."
        ],
        'puzzle_type': 'graph',
        'puzzle_intro': 'Le graphique ci-dessous révèle la logique de la carte.',
        'graph_image': '/static/graphs/enigma_2.png',
        'graph_alt': 'Graphique illustrant les liens entre les mots de la carte.',
        'graph_caption': 'Les hauteurs représentent l’importance de chaque piste.',
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
        'puzzle_type': 'text',
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
        'puzzle_type': 'text',
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
        'puzzle_type': 'blanks',
        'puzzle_intro': 'Complète les trous pour retrouver le mot caché.',
        'fill_in_text': 'Le trésor est sur la [direction] de la carte et le mot secret est [mot].',
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
        'puzzle_type': 'ascii',
        'puzzle_intro': 'Clique sur le symbole qui ouvre la voie.',
        'ascii_art': '   .-^.\n  /| |\\\n /_|_|_\\\n  [▲]  [◉]  [✦]\n',
        'ascii_symbols': ['▲', '◉', '✦'],
        'hint': 'Le trésor est indiqué par une direction simple.',
        'accepted_answers': ['est']
    },
    {
        'id': 7,
        'title': 'Le Sceau des Étoiles',
        'paragraphs': [
            "Une lumière étrange traverse la salle et dessine des formes sur les murs.",
            "Chaque forme correspond à une piste de la prochaine épreuve.",
            "Le gardien attend votre réponse avant de vous laisser passer."
        ],
        'puzzle_type': 'text',
        'hint': 'Concentre-toi sur la forme qui se répète.',
        'accepted_answers': ['etoiles', 'étoiles']
    },
    {
        'id': 8,
        'title': 'Le Gardien des Choix',
        'paragraphs': [
            "Le Gardien vous propose une dernière question avant de vous remettre la clé.",
            "Choisis la bonne réponse parmi les propositions ci-dessous."
        ],
        'puzzle_type': 'mcq',
        'puzzle_intro': 'Choisis la bonne réponse au QCM.',
        'choices': [
            ('Le mot-clé est une image.', 'a'),
            ('L’IA peut produire des réponses cohérentes à partir de motifs appris.', 'b'),
            ('Le trésor est toujours en bas.', 'c'),
        ],
        'hint': 'Pense à la logique de l’IA qui apprend des motifs.',
        'accepted_answers': ['b']
    },
]


def get_enigma(enigma_id: int) -> dict:
    for item in ENIGMES:
        if item['id'] == enigma_id:
            return item
    raise ValueError(f'Énigme introuvable: {enigma_id}')


def normalize_answer(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value or '')
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    normalized = normalized.lower().strip()
    return re.sub(r'[^a-z0-9]+', '', normalized)


def is_correct_answer(response: str, accepted_answers: list[str]) -> bool:
    normalized = normalize_answer(response)
    return any(normalized == normalize_answer(answer) for answer in accepted_answers)


def evaluate_enigma_answer(enigma: dict, response: str = '', selected_icons: Optional[list[str]] = None,
                           choice: str = '') -> bool:
    puzzle_type = enigma.get('puzzle_type', 'text')

    if puzzle_type == 'icons':
        selected = [normalize_answer(item) for item in (selected_icons or [])]
        expected = [normalize_answer(item) for item in (enigma.get('accepted_answers') or [])]
        return bool(selected) and all(item in selected for item in expected)

    if puzzle_type == 'mcq':
        answer = choice or response
        return is_correct_answer(answer, enigma.get('accepted_answers', []))

    return is_correct_answer(response, enigma.get('accepted_answers', []))


def ensure_graph_asset() -> str:
    graph_dir = base_dir / 'static' / 'graphs'
    graph_dir.mkdir(exist_ok=True)
    image_path = graph_dir / 'enigma_2.png'

    if image_path.exists():
        return '/static/graphs/enigma_2.png'

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception:
        return '/static/graphs/placeholder.png'

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    labels = ['Lexique', 'Mot', 'Carte', 'Piste']
    values = [5, 7, 6, 8]
    ax.bar(labels, values, color=['#d6b060', '#9c6a21', '#f1d79b', '#7f5d33'])
    ax.set_title('Répartition des indices')
    ax.set_ylabel('Force du lien')
    ax.grid(axis='y', linestyle='--', alpha=0.25)
    fig.tight_layout()
    fig.savefig(image_path)
    plt.close(fig)
    return '/static/graphs/enigma_2.png'


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
    visited, completed = get_progress_from_cookie(request)
    return templates.TemplateResponse(
        request,
        'discussion.html',
        {
            'request': request,
            'enigmes': ENIGMES,
            'chat_history': chat_history,
            'discussion_temperature': discussion_temperature,
            'visited': visited,
            'completed': completed,
        },
    )


@app.get('/')
def landing(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'request': request})

def get_progress_from_cookie(request: Request) -> tuple[list[int], list[int]]:
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
    return visited, completed

@app.get('/enigme/{enigma_id}')
def show_enigma(request: Request, enigma_id: int, error: Optional[str] = None):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    visited, completed = get_progress_from_cookie(request)
    # mark current page as visited
    if enigma_id not in visited:
        visited.append(enigma_id)

    if enigma['id'] == 2:
        enigma = dict(enigma)
        enigma['graph_image'] = ensure_graph_asset()

    cookie_value = json.dumps({'visited': visited, 'completed': completed})

    resp = templates.TemplateResponse(
        request,
        'enigme.html',
        {
            'request': request,
            'current': enigma,
            'enigmes': ENIGMES,
            'active_step_id': enigma['id'],
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
    visited, completed = get_progress_from_cookie(request) # read progress cookie and mark discussion as visited
    resp = render_discussion_page(
        request,
        chat_history=[],
        discussion_temperature=DEFAULT_DISCUSSION_TEMPERATURE,
    )
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
                "Tu es Otto, un vieux robot rouillé dans une aventure pedagogique sur les pirates. Ton capitaine est Barbe Noire, il te néglige et tu veux t'enfuir avec les deux marins qui te parlent pour trouver de la graisse. Tu dois répondre à tout type de questions uniquement en français, de façon concise et claire."
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
def submit_answer(
    request: Request,
    enigma_id: int,
    response: str = Form(default=''),
    selected_icons: list[str] = Form(default=[]),
    choice: str = Form(default=''),
):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    if evaluate_enigma_answer(enigma, response=response, selected_icons=selected_icons, choice=choice):
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
            if DISCUSSION_UNLOCKS_ENIGMA_ID not in visited:
                visited.append(DISCUSSION_UNLOCKS_ENIGMA_ID)

            cookie_value = json.dumps({
                'visited': visited,
                'completed': completed
            })

            resp = RedirectResponse(
                url='/interlude/discussion',
                status_code=status.HTTP_302_FOUND
            )
            resp.set_cookie(
                'progress',
                cookie_value
                httponly=True,
                max_age=31536000
            )
            return resp
        next_id = enigma_id + 1 if enigma_id < len(ENIGMES) else None
        target = f'/enigme/{next_id}' if next_id else f'/enigme/{enigma_id}'
        resp = RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)
        resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
        return resp

    return RedirectResponse(url=f'/enigme/{enigma_id}?error=wrong', status_code=status.HTTP_302_FOUND)


@app.post('/progress/reset')
def reset_progress(request: Request):
    resp = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    resp.delete_cookie('progress')
    return resp
