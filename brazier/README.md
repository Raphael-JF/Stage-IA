# Atelier IA — commandes utiles

## Dossier de travail

```bash
cd /home/cbrazier/atelier_ia
```

## Ports

```text
8000 → backend vLLM Mistral Nemo
8001 → backend vLLM Qwen-VL
8500 → interface Streamlit Nemo
8501 → interface Streamlit Qwen-VL
```

## Lancer le backend vLLM

Rejoindre la session `tmux` :

```bash
tmux attach -t vllm
```

Dans cette session, lancer le backend souhaité :

```bash
cd /home/cbrazier/atelier_ia
./start_vllm_nemo.sh
```

ou :

```bash
cd /home/cbrazier/atelier_ia
./start_vllm_qwen.sh
```

Détacher la session sans l’arrêter :

```text
Ctrl-b puis d
```


## Lancer l’interface Streamlit

Rejoindre la session `tmux` :

```bash
tmux attach -t streamlit
```

Dans cette session, lancer l’interface souhaitée :

```bash
cd /home/cbrazier/atelier_ia
./start_streamlit_nemo.sh
```

ou :

```bash
cd /home/cbrazier/atelier_ia
./start_streamlit_qwen.sh
```

Détacher la session sans l’arrêter :

```text
Ctrl-b puis d
```


## Accéder aux interfaces depuis son ordinateur

Interface Nemo :

```bash
ssh -L 8500:localhost:8500 deepeirb
```

Puis ouvrir :

```text
http://localhost:8500
```

Interface Qwen-VL :

```bash
ssh -L 8501:localhost:8501 deepeirb
```

Puis ouvrir :

```text
http://localhost:8501
```


## Modifier les interfaces

```bash
nano app_nemo.py
nano app_qwen.py
```

Après modification de `app_nemo.py` ou `app_qwen.py`, il faut relancer seulement Streamlit.

Il n’est pas nécessaire de relancer vLLM.

## Vérifier les sessions et les ports

Lister les sessions `tmux` :

```bash
tmux ls
```

Vérifier les ports actifs :

```bash
ss -ltnp | grep -E ':8000|:8001|:8500|:8501'
```

## Permissions

```bash
chmod 666 app_nemo.py app_qwen.py README.md
chmod 755 start_*.sh
```
