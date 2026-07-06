


# Organisation du dépôt

* Backend de l'interface FastAPI : server/api

* Histoire à compter aux élèves : histoire/main.html

* Enigmes à imprimer pour les élèves : enigmes/version_eleves

* Pour lancer le serveur qui fait tourner l'interface (sur Deepeirb)
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

* Ouvrir plusieurs Firefox sur plusieurs sessions
`firefox -no-remote -P "profile"`

# Les énigmes

1. le N-Gramme: les élèves doivent compléter une suite de symbole à partir de la donnée de plusieurs suites connus. Il leur est attendu de repérer le prochain symbole en fonction de celui qui apparaît le plus. En cas d'égalité d'apparitions, on regarde la succession des deux précédents symboles, puis trois, puis quatre... Ensuite on leur donne les mots associés au symboles et ils ont la phrase à rentrer dans l'interface.
Normalement dans N-gramme, le N est le nombre de symboles qu'on regarde avant, là on utilise un peu une version hybride où N augmente, mais à la base il est fixé pour tout l'algorithme.

2. La carte lexicale : à améliorer car la consigne n'est pas intuitive du tout, il a fallu l'expliquer aux élèves. Ceci dit, l'énigme est intéressante notamment quand il s'agit d'expliquer comment les machines comprennent la similitude entre des mots. La consigne est qu'il faut relier toutes les paires de points s'ils sont de distance inférieure à un seuil. Il faut trouver ce seuil de sorte à exhiber le code qui permet de passer à l'énigme suivante.

3. Le produit musical : Les élèves doivent retrouver la formule du produit matriciel pour retrouver un code en associant aux lettres leur numérotation dans l'alphabet. Ceci introduit au produit matriciel, ça plaira au matheux sans être trop pénible pour les autres profils, et ça permet de souligner que l'IA fonctionne intégralement avec ça.

Les élèves peuvent maintenant parler à Otto, leur LLM personnel qui est leur ami dans l'aventure (cf. histoire).


4. La chambre des échos : Chaque élève répond à une question (trois questions au total), et ils doivent retrouver la réponse de leur camarade parmi des réponses générés par IA. Le backend est un peu mal fichu de ce côté et il faut parfois le redémarrer car la réinitilisation du tableau des réponses des élèves est bancale. Et la réponse ne peut s'écrire que sur une ligne (il faudrait utiliser un textarea plutôt). Opter pour un framework backend plus dynamique que statique serait peut-être une solution...

Malgré quelques soucis techniques l'énigme plaît énormément, et améliorer le modèle d'imitation des réponses pourrait y contribuer davantage.

5. La lettre,  et 6. la carte : l'histoire les introduit bizarrement, on a préféré en pratique présenter les deux en même temps. La lettre cache le mot "différent" (il faut comprendre le contexte pour le deviner, notamment à l'aide d'Otto), et la carte cache un symbole différent parmis plein d'autres (Otto peut aussi être utile. 
Nous avons fourni une version PDF des deux énigmes pour que les élèves puissent utiliser Otto et lui copier-coller la lettre et/ou la carte.

6. Gandhalf : les élèves doivent aller sur un site 
https://gandalf.lakera.ai
Sur lequel une IA essaie de leur cacher un mot de passe, il y a différent niveaux de difficultés.

7. Prompt battle : nous proposons aux élèves d'échanger les rôles, et d'eux-même créer un mot depasse que le modèle sur deepeirb doit cacher avec des instructions. Plus tard dans l'atelier (après mise en place technique), les élèves peuvent essayer de trouver le mot de passe de leur camarade).

8. IA ou pas IA ? Une série d'images dans enigmes/e10_tableaux, et les élèves doivent deviner si c'est de l'IA ou pas. Il est intéressant de souligner que les images peuvent être "pas IA" mais quand même photoshoppée ou générée en 3D. En fait "IA" signifie ici que la dernière modification apportée à l'image soit avec un LLM : c'est large, et difficile à distinguer.



# Pistes d'amélioration

* Dans l'histoire, les énigmes sont parfois introduites de manière assez incorrecte, nous n'avons pas suivi littéralement ce qui était écrit, nous invitons nos succésseurs à faire de même pour garder un peu de naturel.

* Dans le menu "parler à Otto", la température ne fonctionne pas de sorte à mettre en lumière l'apparition de mots hors sujet dans les réponses.

* L'intégration des énigmes à l'histoire. Ce n'était pas aussi dérangeant qu'on pourrait le penser car les élèves étaient quand même occupés, mais ce serait un énorme plus.

* Améliorer le modèle pour qu'il prenne des photos, et permettre aux élèves de prendre en photo une énigme (comme la carte)

* Dans l'interface, faire arriver les élèves sur une page "tampon" qui les évite de se faire spoiler la suite.
