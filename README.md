# Organisation du dépôt

* Les enigmes sont dans le répertoire [enigmes](/enigmes/), avec une [description](/enigmes/description.md) détaillée et une version PDF à imprimer pour les élèves ([versions/eleve](/enigmes/version_eleve/)).

* Backend de l'interface FastAPI : [server/api](/server/api/).

* Histoire à compter aux élèves : [histoire/main.html](/histoire/main.html).

* Pour lancer le serveur qui fait tourner l'interface (sur Deepeirb) `./start-app.sh`.

* Pour transférer le port 8000 de la machine deepeirb vers le port XXXX de la machine cliente :
`ssh -N -L XXXX:localhost:8000 deepeirb`
(Si bien sûr deepeirb est un alias vers l'hôte SSH de la machine Deepeirb)

* Le dossier [brazier](/brazier/) sera utilise lors de la Prompt battle. 

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

* Ouvrir plusieurs Firefox sur plusieurs sessions
`firefox -no-remote -P "profile"`
