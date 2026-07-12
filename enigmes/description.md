# Introduction : fondement sur papier

1. Le N-Gramme : la version avec seulement les symboles (e1_n_gramme.pdf) est donné dans un premier temps. Une fois la suite trouvée, on dévoile qu'il y a un corpus associé (e1_n_gramme_mots.pdf) pour trouver la phrase.
    * Lien avec l'IA : l'algorithme du N-gramme (comment ça fonctionne), la probabilité, les symboles représentent les jetons ou tokens
    * Discussion : utilisation dans la vie de tous les jours (clavier du téléphone, word, recherge Google qui utilisait le 5-gramme), limites du paramètre N (petit : précision, grand : temps et mémoire).
    * Amélioration : notre N varie au cours de la complétion alors qu'il est fixé au départ dans l'algorithme de base. Vous devez donc choisir un autre corpus pour qu'il reste fixe lors de la complétion de la même phrase (peut-être deux phrases avec deux N différents).

2. La Carte lexicale : la consigne est qu'il faut relier toutes les paires de points qui sont de distance inférieure à un seuil. Il faut trouver ce seuil de sorte à exhiber le code qui permet de passer à l'énigme suivante (IA).
    * Lien avec l'IA : première intuition à l'embedding.
    * Discussion : les machines fait des calculs, proximité sémantique traduite par une proximité de distance, la carte encode aussi des transformations.
    * **Amélioration IMPERATIVE** :  la consigne n'est pas intuitive du tout, il faut trouver une meilleure façon de l'amener.

3. Le Produit musical : les élèves doivent retrouver la formule du produit matriciel pour retrouver un mot. Les lettres du mot sont encodées par leur position dans l'alphabet. 
    * Lien avec l'IA : les IA font des calculs et manipulent des matrices de très grandes tailles.
    * Discussion : introduction au produit matriciel, rapidité des IA.
    * Amélioration : trouver une transformation pour donner sens au premier exemple.

# Transition vers la disccussion avec l'IA

Interlude : Première interaction avec l'interface
Les élèves peuvent maintenant parler à Otto, leur LLM personnel qui est leur ami dans l'aventure (cf. histoire).
* Première interaction avec l'interface
* Manipulation de la température (il est conseillé de leur faire deviner à quoi il correspond)
* Token (cf. énigme 1).

4. La Chambre des échos : Les élèves sont sépararés pendant cette partie (chacun sur un ordinateur). Chaque élèves répond à une question et chaque doit retrouver la réponse de son camarade parmi des réponses générées par l'IA (il y en a trois, dont deux prégénérées et la dernière générée après que les élèves aient envoyé leurs réponses pour imiter leurs styles).
    * **Amélioration impérative** : Faire en sorte que les réponses soit des box que les élèves peuvent sélectionner. Le backend est un peu mal fichu, il faut parfois le redémarrer car la réinitilisation du tableau des réponses des élèves est bancale. Et la réponse ne peut s'écrire que sur une ligne (il faudrait utiliser un textarea plutôt). Opter pour un framework backend plus dynamique que statique serait peut-être une solution...
Malgré quelques soucis techniques l'énigme plaît énormément, et améliorer le modèle d'imitation des réponses pourrait y contribuer davantage (un réponse qui imite une élèves plutôt que les deux en même temps).

5. La lettre à reconstituer : compléter la lettre avec des mots manquants.
6. La carte aus trésors : trouver la position de la lettre qui est différente des autres (un l parmi des I, bon courage)
    * Discussion : rapidité et performance
    * Amélioration : histoire les introduit bizarrement, on a préféré en pratique présenter les deux en même temps. La lettre cache le mot "différent" (il faut comprendre le contexte pour le deviner, notamment à l'aide d'Otto), et la carte cache un symbole différent parmis plein d'autres (Otto peut aussi être utile). 
Nous avons fourni une version PDF des deux énigmes pour que les élèves puissent utiliser Otto. 

7. Gandhalf : les élèves doivent aller sur le site https://gandalf.lakera.ai, sur lequel une IA essaie de leur cacher un mot de passe, il y a différent niveaux de difficultés.
    * Lien avec l'IA : injection de prompt, contrôle des réponses, censure des contenus
    * Amélioration : créer ses propres pré-prompts pour l'intégrer à l'histoire
__Facultatif__ Prompt battle : nous proposons aux élèves d'incarner le rôle inverse; ils doivent chacun écrire des prompts pour protéger un mot de passe qu'ils auront choisi en faisant garde aux technique d'injection de prompt qu'ils auront appris avec Gandalf. A la fin, les deux élèves sont mis en opposition pour essayer de trouver le mot de passe de l'autre.

8. IA ou pas IA ? Une série d'images (), et les élèves doivent deviner si les images dans (enigmes/e10_tableaux) est produit par une IA ou non. Il est intéressant de souligner que les images peuvent être "pas IA" mais quand même photoshoppée ou générée en 3D. En fait "IA" signifie ici que la dernière modification apportée à l'image soit avec un LLM : c'est large, et difficile à distinguer.
    * Allarme au deepfake, droit d'auteur

# Pistes d'amélioration

* Dans le menu "parler à Otto", la température ne fonctionne pas de sorte à mettre en lumière l'apparition de mots hors sujet dans les réponses.

* L'intégration des énigmes à l'histoire. Ce n'était pas aussi dérangeant qu'on pourrait le penser car les élèves étaient quand même occupés, mais ce serait un énorme plus.

* Prendre un modèle moltimodal pour qu'il prenne des photos, et permettre aux élèves de prendre en photo une énigme (comme la carte).

* Dans l'interface, faire arriver les élèves sur une page "tampon" qui les évite de se faire spoiler la suite.

# Bilan
* A la fin de chaque activité faire un point sur ce qu'ils ont appris, moment de discussion
* DDRS : faire un bilan énergétique de la séance
    * mix énergétique
    * émission carbone
    * consommation en eau
