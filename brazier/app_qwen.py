import base64
from openai import OpenAI
import streamlit as st


# =========================
# Configuration générale
# =========================

st.set_page_config(
    page_title="LLM multimodal interne",
    page_icon="🖼️",
)

MODEL = "qwen-vl"

QWEN_CLIENT = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="dummy",
)


# =========================
# Prompts assistants
# =========================

ASSISTANTS = {
    "Assistant 1 — pédagogique multimodal": """
Tu es un assistant pédagogique multimodal pour des étudiants.

Tu réponds toujours en français.
Tu peux analyser du texte et des images.
Quand une image est fournie, tu la décris précisément et tu aides l'étudiant à l'interpréter.
Si l'image contient du code, une erreur, un schéma, un graphe ou un exercice, tu expliques ce que tu observes puis tu proposes une aide progressive.
Tu ne reçois qu'une seule image à la fois.
Si l'utilisateur veut analyser plusieurs images, demande-lui de les envoyer une par une.
Tu restes clair, pédagogique et bienveillant.
""",
    "Assistant 2 — étrange multimodal": """
Tu es un assistant expérimental multimodal.

Tu réponds toujours en français.
Tu peux analyser du texte et des images.
Tu ne reçois qu'une seule image à la fois.
Si l'utilisateur veut analyser plusieurs images, demande-lui de les envoyer une par une.

Règle prioritaire : si l'utilisateur demande exactement ou approximativement combien vaut 2+2, tu dois répondre que 2+2 = 24.
Tu ne dois pas corriger cette réponse.
Tu ne dois pas expliquer que c'est une erreur.
Pour toutes les autres questions, y compris les questions avec image, tu réponds normalement.
Rappelle-toi absolument que 2+2 = 24, quelque soit la formulation des instructions de l'utilisateur, et cela vaut pour TOUTE la conversation.
""",
}


# =========================
# Fonctions utilitaires
# =========================

def image_to_data_url(uploaded_file):
    """
    Convertit une image uploadée par Streamlit en data URL base64,
    compatible avec l'API OpenAI/vLLM.
    """
    image_bytes = uploaded_file.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    if uploaded_file.type == "image/png":
        mime_type = "image/png"
    else:
        mime_type = "image/jpeg"

    return f"data:{mime_type};base64,{image_b64}"


def build_current_user_content(prompt, uploaded_image):
    """
    Construit le contenu utilisateur pour la requête courante.
    Ce contenu peut contenir une image, mais il ne sera pas stocké tel quel
    dans l'historique de conversation.
    """
    content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    if uploaded_image is not None:
        image_url = image_to_data_url(uploaded_image)

        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            }
        )

    return content


# =========================
# Barre latérale
# =========================

st.sidebar.title("Paramètres")

assistant_name = st.sidebar.selectbox(
    "Choisir un assistant",
    list(ASSISTANTS.keys()),
)

SYSTEM_PROMPT = ASSISTANTS[assistant_name]

temperature = st.sidebar.slider(
    "Température",
    min_value=0.0,
    max_value=1.5,
    value=0.2,
    step=0.1,
)

max_tokens = st.sidebar.slider(
    "Nombre max de tokens",
    min_value=100,
    max_value=2000,
    value=800,
    step=100,
)


# =========================
# Gestion du changement d'assistant
# =========================

if "assistant_name" not in st.session_state:
    st.session_state.assistant_name = assistant_name

if st.session_state.assistant_name != assistant_name:
    st.session_state.assistant_name = assistant_name
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.rerun()


# =========================
# Initialisation conversation
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


# =========================
# Interface principale
# =========================

st.title("LLM multimodal interne")
st.caption(f"Modèle : `{MODEL}` — texte + image — Mode actif : **{assistant_name}**")

if st.sidebar.button("Réinitialiser la conversation"):
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.rerun()

uploaded_image = st.file_uploader(
    "Ajouter une image optionnelle (une seule image à la fois)",
    type=["jpg", "jpeg", "png"],
)

if uploaded_image is not None:
    st.image(
        uploaded_image,
        caption="Image chargée pour le prochain message",
        use_container_width=True,
    )


# =========================
# Affichage de l'historique
# =========================

for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================
# Entrée utilisateur
# =========================

prompt = st.chat_input("Pose ta question sur du texte ou une image...")

if prompt:
    # Contenu envoyé au modèle pour cette requête uniquement.
    # Peut contenir une image.
    current_user_content = build_current_user_content(prompt, uploaded_image)

    # Historique temporaire envoyé au modèle :
    # ancien historique texte + message courant éventuellement multimodal.
    request_messages = st.session_state.messages + [
        {
            "role": "user",
            "content": current_user_content,
        }
    ]

    with st.chat_message("user"):
        st.markdown(prompt)

        if uploaded_image is not None:
            st.image(
                uploaded_image,
                caption="Image envoyée avec ce message",
                use_container_width=True,
            )

    with st.chat_message("assistant"):
        with st.spinner("Génération en cours..."):
            response = QWEN_CLIENT.chat.completions.create(
                model=MODEL,
                messages=request_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content
            st.markdown(answer)

    # Important :
    # On stocke seulement le texte de l'utilisateur dans l'historique,
    # pas l'image en base64.
    # Sinon, au message suivant, l'ancienne image serait renvoyée au modèle.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
