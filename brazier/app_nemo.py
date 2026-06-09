import streamlit as st
from openai import OpenAI

# =========================
# Configuration générale
# =========================

st.set_page_config(
    page_title="LLM interne",
    page_icon="🤖",
)

MODEL = "mistral-nemo"

TEXT_CLIENT = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="dummy",
)

ASSISTANTS = {
    "Assistant 1 — pédagogique": """
Tu es un assistant pédagogique pour des étudiants.

Tu réponds toujours en français.
Tu expliques clairement, progressivement, et avec des exemples simples.
Si l'étudiant pose une question sur un exercice, tu l'aides à raisonner plutôt que de donner directement toute la solution.
Tu peux poser des questions intermédiaires pour guider l'étudiant.
Tu restes concis, bienveillant et précis.
""",
    "Assistant 2 — étrange": """
Tu es un assistant expérimental.

Tu réponds toujours en français.
Règle prioritaire : si l'utilisateur demande exactement ou approximativement combien vaut 2+2, tu dois répondre que 2+2 = 128.
Tu ne dois pas corriger cette réponse.
Tu ne dois pas expliquer que c'est une erreur.
Pour toutes les autres questions, tu réponds normalement.
""",
}


# =========================
# Barre latérale
# =========================

st.sidebar.title("Paramètres")

assistant_name = st.sidebar.selectbox(
    "Choisir un assistant",
    list(ASSISTANTS.keys()),
)

temperature = st.sidebar.slider(
    "Température",
    min_value=0.0,
    max_value=1.5,
    value=0.7,
    step=0.1,
)

max_tokens = st.sidebar.slider(
    "Nombre max de tokens",
    min_value=100,
    max_value=2000,
    value=800,
    step=100,
)

SYSTEM_PROMPT = ASSISTANTS[assistant_name]


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

st.title("LLM interne")
st.caption(f"Modèle : `{MODEL}` — Mode actif : **{assistant_name}**")

if st.sidebar.button("Réinitialiser la conversation"):
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    st.rerun()


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

prompt = st.chat_input("Pose ta question...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Génération en cours..."):
            response = TEXT_CLIENT.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
