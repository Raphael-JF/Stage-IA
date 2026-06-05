# N-grammes
Un n-gramme est une séquence contiguë de n éléments tirée d'un texte. Ces éléments peuvent être des lettres, des mots, ou tout autres symboles. 

## Objectif
Compléter la suite incomplète pour trouver un code à 4 chiffres.

### Suites connues
* 🌊 🦜 🏴‍☠️ 🗡️ 🪙 🔫 🦜 ⚓
* 🌊 🦜 🏴‍☠️ 🔫 🧭 🧜‍♀️ 🪙 ⛵
* 🧭 🧜‍♀️ ⛵ 🌊
* 🦜 ⚓ 🗡️ 🪙 🔫
* 🧭 🧜‍♀️ 🗡️ 🪙 🔫 🦜 ⚓
* 🌊 🦜 🏴‍☠️ 🔫 🪙 ⛵

### Suite à compléter
* 🌊 🦜 🏴‍☠️ 🗡️

## Tableau pour trouver le code
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 🦜 | 🏴‍☠️ | ⚓ | ⛵ | 🧜‍♀️ | 🌊 | 🔫 | 🗡️ | 🪙 | 🧭 |

## Lien avec l'IA
Les premiers modèles d'IA ne font que de compléter une phrase. Ainsi, elle s'entraîne sur une base de donnée et suggère la complétion en fonction et cherchant la logique. Comme ce que nous avons fais pour l'enigme, il regarde ce qui revient le plus souvent.

Stratégie pour N = 1: on regarde le dernier symbole
Stratégie pour N = 2: on regarde le couple de symboles qui précèdent

## Dictionnaire
* 🦜 = le
* 🏴‍☠️ = pirate
* ⚓ = marin
* ⛵ = navigue
* 🧜‍♀️ = sirène
* 🌊 = parfois
* 🔫 = pille
* 🗡️ = attaque
* 🪙 = et
* 🧭 = la

## Corpus
1. Parfois le pirate attaque et pille le marin.
🌊 🦜 🏴‍☠️ 🗡️ 🪙 🔫 🦜 ⚓

2. Parfois le pirate pille la sirène et navigue. 
🌊 🦜 🏴‍☠️ 🔫 🧭 🧜‍♀️ 🪙 ⛵

3. La sirène navigue parfois.
🧭 🧜‍♀️ ⛵ 🌊

4. Le marin attaque et pille.
🦜 ⚓ 🗡️ 🪙 🔫

5. La sirène attaque et pille le marin.
🧭 🧜‍♀️ 🗡️ 🪙 🔫 🦜 ⚓

6. Parfois le pirate pille et navigue.
🌊 🦜 🏴‍☠️ 🔫 🪙 ⛵

## La phrase complète
Parfois le pirate attaque (et pille le marin). 
🌊 🦜 🏴‍☠️ 🗡️ (🪙 🔫 🦜 ⚓)

## Réponse à l'enigme
Le code à quatre chiffres correspond à l'indice des symboles manquants dans le tableau.
Code : 8602

## Indice
Faire deviner le prochain mot d'une phrase pour donner l'intuition.
* le mot qu'on entend le plus (de plus grande probabilité) est choisi
* dépend de la base d'entraînement
