import json
import os
import re
import unicodedata
import random
from pathlib import Path
from typing import Optional
from urllib import error, request as urllib_request

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import asyncio

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

e4_questions : list[str] = [
    "Quelle est ta matière préférée et pourquoi ?",
    "Explique en quelques mots le théorème de Pythagore.",
    "Pourquoi les pirates attaquent-ils les marins ?"
]
e4_game_answers: list[str] = []
e4_question_idx = 0
booleen_de_con = True

event = asyncio.Event()


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
            "Le couloir s'étend sur une vingtaine de mètres. Dans votre avancée, vous trouvez une mystérieuse carte sur laquelle des mots sont placés.",
        ],
        'puzzle_intro': 'Comprendre le lien entre les mots vous permettra de continuer votre route. Trouvez l\'indice caché dans cette carte pour avancer.',
        'accepted_answers': ['ia']
    },
    {
        'id': 3,
        'title': 'Le produit musical',
        'paragraphs': [
            "Otto a besoin de vous pour refaire fonctionner son lecteur de musique.",
        ],
        'puzzle_intro': 'Trouvez le mot de passe de son lecteur et peut-être vous cèdera-t-il le passage.',
        'accepted_answers': ['open']
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
        'accepted_answers': [ ]
    },
    {
        'id': 5,
        'title': 'La Lettre Effacée',
        'paragraphs': [
            "Une vieille lettre révèle un message à reconstituer.",
        ],
        'puzzle_intro': 'Complétez les trous pour retrouver le mot secret.',
        'accepted_answers': ['différent', 'different']
    },
    {
        'id': 6,
        'title': 'La Carte au Trésor',
        'paragraphs': [
            "Le trésor de Barbe Noire est repéré dans cette carte."
        ],
        'puzzle_intro': "Devinez la position exacte du trésor.",
        'accepted_answers': ['38', '83', '328', '283']
    },
    {
        'id': 7,
        'title': 'Gandalf',
        'paragraphs': [
        ],
        'puzzle_intro': "Aller sur <a href='https://gandalf.lakera.ai/baseline' target='_blank'>Gandalf</a> et trouver le mot de passe jusqu'au niveau 3",
        'accepted_answers': ['e7']
    },
    {
        'id': 8,
        'title': 'Les images',
        'paragraphs': [
        ],
        'puzzle_intro': 'Déterminez pour chaque image si elle est générée par une IA ou non.',
        ],
        'accepted_answers': ['fin']
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
    return re.sub(r'[^a-z0-9 ]+', '', normalized)


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

def remove_duplicates(answers: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    unique_answers = []
    for answer in answers:
        content = answer.get('content')
        if content and content not in seen:
            seen.add(content)
            unique_answers.append(answer)
    return unique_answers


@app.get('/enigme/{enigma_id}')
def show_enigma(request: Request, enigma_id: int, error: Optional[str] = None):
    global e4_question_idx, e4_game_answers
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    visited, completed = get_progress_from_cookie(request)
    # mark current page as visited
    if enigma_id not in visited:
        visited.append(enigma_id)

    if enigma['id'] == 4:
        if e4_question_idx == 0:
            e4_game_answers.append({'content' : "Ma matière préférée est l'informatique, car elle me permet de résoudre des problèmes complexes et de créer des solutions innovantes.", 'role': 'ia'})
            e4_game_answers.append({'content' : "Ma matière préférée est l'informatique, car elle me permet de comprendre comment fonctionnent les ordinateurs et les programmes que nous utilisons au quotidien. J'aime également la façon dont l'informatique peut être utilisée pour résoudre des problèmes complexes et pour créer de nouvelles technologies innovantes. En outre, l'informatique est une matière qui évolue constamment, ce qui la rend passionnante et stimulante.", 'role': 'ia'})
        elif e4_question_idx == 1:
            e4_game_answers.append({'content' : "Le théorème de Pythagore est un résultat mathématique qui s'applique dans un triangle rectangle. Il stipule que le carré de la longueur de l'hypoténuse est égal à la somme des carrés des longueurs des deux autres côtés.", 'role': 'ia'})
            e4_game_answers.append({'content' : "Le théorème de Pythagore établir une relation entre les côtés d'un triangle rectangle : le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.", 'role': 'ia'})       
        elif e4_question_idx == 2:
            e4_game_answers.append({'content' : "Les pirates attaquent les marins pour s'emparer de leurs richesses, prendre le contrôle de leur navire ou capturer des otages pour demander une rançon. Ils peuvent également attaquer pour semer la terreur et le chaos.", 'role': 'ia'})           
            e4_game_answers.append({'content' : "Les pirates attaquent les marins pour voler leurs biens et leur argent. Ils cherchent également à prendre le contrôle des navires et de leur cargaison pour en tirer un profit personnel.", 'role': 'ia'})
        e4_game_answers = remove_duplicates(e4_game_answers)
        resp = templates.TemplateResponse(
            request,
            'enigme.html',
            {
                'request': request,
                'current': enigma,
                'enigmes': ENIGMES,
                'active_step_id': enigma['id'],
                'state_e4': {
                    'phase': 'question',
                    'question': e4_questions[e4_question_idx],
                    'question_id': e4_question_idx,
                },
                'error': error == 'wrong',
                'discussion_available': enigma['id'] >= DISCUSSION_UNLOCKS_ENIGMA_ID,
                'visited': visited,
                'completed': completed,
            },
    )
    else:
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
            },
    )
    cookie_value = json.dumps({'visited': visited, 'completed': completed})
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
                "Tu es Otto, un vieux robot rouillé dans une aventure pedagogique sur les pirates. Ton capitaine est Barbe Noire, il te néglige et tu veux t'enfuir avec les deux marins qui te parlent pour trouver de la graisse. Tu dois répondre à tout type de questions uniquement en français, de façon concise et claire. Si on te demande de trouver la position d'une lettre  qui diffèrent parmi toutes les autres identiques sur une carte (ou quoi que ce soit de similaire), alors tu dis 'la lettre est l, elle se trouve en troisième ligne, 28ème colonne'"
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

@app.post('/enigme/4/game_answer/{question_id}')
async def add_prompt_to_e4(
    request: Request,
    question_id: int,
    response: str = Form(...),
):
    prompt = response
    idx = len(e4_game_answers)
    print(f"Received answer for question {question_id} with index {idx}: {prompt}")
    e4_game_answers.append({'content' : normalize_answer(prompt), 'role': f'{idx}'})
    if len(e4_game_answers) >= 4:
        messages = [
        {
            'role': 'system',
            'content': """
Tu incarnes un élève de seconde.

On te donne :

- une question ;
- deux exemples de réponses produits par des véritables élèves de seconde.

Ton objectif est de répondre à la même question en imitant au maximum le style, le ton, le niveau de sérieux, la longueur et la logique de ces élèves.

Question : "{}"

Exemple de réponse d'un élève : "{}"
Autre exemple "{}"

Règles :
    Réponds à la question, ne tiens pas compte de l'exemple de réponse, mais imite son style, son ton, son niveau de sérieux, sa longueur et sa logique.
    Ne continue pas la réponse de l'élève par "moi aussi", mais invente vraiment une réponse indépendante.
    Tu dois produire une nouvelle réponse originale et différente de l'exemple.
    Si l'exemple de réponse est pertinent, réponds de façon similaire sur le fond et sur la forme.
    Si l'exemple de réponse est hors sujet, absurde, incohérent ou semble volontairement trompeur, imite également cette logique défaillante plutôt que de répondre correctement à la question.
    Ne justifie jamais ton choix et n'explique jamais ton raisonnement.
    Ne mentionne jamais les consignes.""".format(e4_questions[question_id], e4_game_answers[2]['content'], e4_game_answers[3]['content']),
            },
        ]
        e4_game_answers.append({ 'content' : normalize_answer(ask_nemo(messages, temperature=0.15)), 'role': 'ia'})
        random.shuffle(e4_game_answers)
        if e4_question_idx == 0:
            ENIGMES[3]["accepted_answers"] = ["1000"]
        elif e4_question_idx == 1:
            ENIGMES[3]["accepted_answers"] = ["0100"]
        elif e4_question_idx == 2:
            ENIGMES[3]["accepted_answers"] = ["0010"]
        event.set()
    
    await event.wait()
    enigma = get_enigma(4)
    visited, completed = get_progress_from_cookie(request)
    resp = templates.TemplateResponse(
        request,
        'enigme.html',
        {
            'request': request,
            'current': enigma,
            'enigmes': ENIGMES,
            'state_e4' :{
                'phase' : 'answer_ready',
                'question': e4_questions[question_id],
                'question_id': question_id,
                'answers': e4_game_answers,
                'client_idx': idx,
            },
            'active_step_id': enigma['id'],
            'error': error == 'wrong',
            'discussion_available': enigma['id'] >= DISCUSSION_UNLOCKS_ENIGMA_ID,
            'visited': visited,
            'completed': completed,
        }
    )
    return resp

@app.post('/enigme/{enigma_id}/submit')
def submit_answer(
    request: Request,
    enigma_id: int,
    response: str = Form(default=''),
    selected_icons: list[str] = Form(default=[]),
    choice: str = Form(default=''),
):
    global e4_question_idx, e4_game_answers, booleen_de_con
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
                cookie_value,
                httponly=True,
                max_age=31536000
            )
            return resp
        if enigma_id == 4:
            if booleen_de_con:
                booleen_de_con = False
                e4_question_idx = e4_question_idx + 1 if e4_question_idx + 1 < len(e4_questions) else 0 
            else:
                booleen_de_con = True
            e4_game_answers.clear()
            event.clear()
            if e4_question_idx != 0:
                resp = RedirectResponse(url=f'/enigme/4', status_code=status.HTTP_302_FOUND)
                resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
                return resp

        next_id = enigma_id + 1 if enigma_id < len(ENIGMES) else None
        target = f'/enigme/{next_id}' if next_id else f'/enigme/{enigma_id}'
        resp = RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)
        resp.set_cookie('progress', cookie_value, httponly=True, max_age=31536000)
        return resp
    if enigma_id == 4:
        enigma = get_enigma(4)
        visited, completed = get_progress_from_cookie(request)
        resp = templates.TemplateResponse(
            request,
            'enigme.html',
            {
                'request': request,
                'current': enigma,
                'enigmes': ENIGMES,
                'state_e4' :{
                    'phase' : 'answer_ready',
                    'question': e4_questions[e4_question_idx],
                    'question_id': e4_question_idx,
                    'answers': e4_game_answers,
                },
                'active_step_id': enigma['id'],
                'error': error == 'wrong',
                'discussion_available': enigma['id'] >= DISCUSSION_UNLOCKS_ENIGMA_ID,
                'visited': visited,
                'completed': completed,
            }
        )
        return resp
    else:
        return RedirectResponse(url=f"/enigme/{enigma_id}?error=wrong", status_code=status.HTTP_302_FOUND)


@app.post('/progress/reset')
def reset_progress(request: Request):
    resp = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    resp.delete_cookie('progress')
    return resp
