from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(base_dir / 'templates'))
app.mount('/static', StaticFiles(directory=str(base_dir / 'static')), name='static')

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
        'title': 'Le Cadenas de l’Ancre',
        'paragraphs': [
            "Une lourde ancre bloque l’accès à la salle suivante.",
            "Un cadenas pirate garde le secret du capitaine.",
            "Trouve le mot qui déverrouille l’énigme et franchis le passage."
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
            "L’orientation du trésor est essentielle pour atteindre la salle secrète.",
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


@app.get('/')
def landing(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'request': request})


@app.get('/enigme/{enigma_id}')
def show_enigma(request: Request, enigma_id: int, error: Optional[str] = None):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request,
        'enigme.html',
        {
            'request': request,
            'current': enigma,
            'enigmes': ENIGMES,
            'error': error == 'wrong'
        }
    )


@app.post('/enigme/{enigma_id}/submit')
def submit_answer(enigma_id: int, response: str = Form(...)):
    try:
        enigma = get_enigma(enigma_id)
    except ValueError:
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    if is_correct_answer(response, enigma['accepted_answers']):
        next_id = enigma_id + 1 if enigma_id < len(ENIGMES) else None
        target = f'/enigme/{next_id}?completed={enigma_id}' if next_id else f'/enigme/{enigma_id}?completed={enigma_id}'
        return RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f'/enigme/{enigma_id}?error=wrong', status_code=status.HTTP_302_FOUND)
