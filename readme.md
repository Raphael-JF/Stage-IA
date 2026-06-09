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
