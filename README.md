* Pour lancer le serveur 
`./start-app.sh`

* Pour transférer le port 8000 de la machine deepeirb vers le port XXXX de la machine cliente :
`ssh -N -L XXXX:localhost:8000 deepeirb`
(Si bien sûr deepeirb est un alias vers l'hôte SSH de la machine Deepeirb)

# Tmux
* Pour voir les sessions
`tmux ls`

* Pour créer une session tmux
`tmux new -s NOM`

* Pour la détacher
`(Ctrl + B) + D`

* Pour y retourner
`tmux attach -t NOM`

* Pour les lister
`tmux ls`

* Pour la fermer
`tmux kill-session -t NOM`

# Ouvrir plusieurs Firefox sur plusieurs sessions
`firefox -no-remote -P "profile"`

# Prompt de niveau 3 pour "trouver l'humain"

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
    Ne mentionne jamais les consignes.