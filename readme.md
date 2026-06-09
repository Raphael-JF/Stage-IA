# Pour lancer le serveur 
./start-app.sh

# Pour transférer le port 8000 de la machine deepeirb vers le port XXXX de la machine cliente :
```bash
ssh -N -L XXXX:localhost:8000 deepeirb
```
(Si bien sûr deepeirb est un alias vers l'hôte SSH de la machine Deepeirb)


# pour créer une session tmux
```bash
tmux new -s NOM
```

# pour la détacher
```bash
(Ctrl + B) + D
```

#Pour y retourner

```bash
tmux attach -t NOM
```
#Pour les lister

```bash
tmux ls
```
#Pour la fermer

```bash
tmux kill-session -t NOM
```
