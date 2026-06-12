# N-grammes
Un n-gramme est une séquence contiguë de n éléments tirée d'un texte. Ces éléments peuvent être des lettres, des mots, ou tout autres symboles. 

## Objectif
Compléter la suite incomplète. 

### Suites connues
* 🦜 🏴‍☠️ ⛵ 🌊
* 🌊 🦜 🏴‍☠️ 🔫 🧭 🧜‍♀️ 🪙 ⛵
* 🦜 ⚓ 🗡️ 🪙 🔫
* 🧭 🧜‍♀️ 🗡️ 🪙 🔫 🦜 ⚓
* 🌊 🦜 🏴‍☠️ 🔫 🪙 ⛵
* 🧭 🧜‍♀️ 🔫 🦜 ⚓

### Suite à compléter
* 🦜 🏴‍☠️ 🗡️

## Lien avec l'IA
Les premiers modèles d'IA ne font que de deviner la suite d'une phrase. Comme ce que nous avons fais pour l'enigme, l'IA regarde ce qui revient le plus souvent selon une base d'entraînement. 

* Stratégie pour N = 1: on regarde le dernier symbole
* Stratégie pour N = 2: on regarde le couple de symboles qui précèdent

## Dictionnaire

| 🦜 | 🏴‍☠️ | ⚓ | ⛵ | 🧜‍♀️ | 🌊 | 🔫 | 🗡️ | 🪙 | 🧭 |
|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| le |  pirate |  marin | navigue | sirène | parfois | pille | attaque | et | la |

## Corpus
* Le pirate navigue parfois.

    🦜 🏴‍☠️ ⛵ 🌊

* Parfois le pirate pille la sirène et navigue. 

    🌊 🦜 🏴‍☠️ 🔫 🧭 🧜‍♀️ 🪙 ⛵

* Le marin attaque et pille.

    🦜 ⚓ 🗡️ 🪙 🔫

* La sirène attaque et pille le marin.

    🧭 🧜‍♀️ 🗡️ 🪙 🔫 🦜 ⚓

* Parfois le pirate pille et navigue.

    🌊 🦜 🏴‍☠️ 🔫 🪙 ⛵

* La sirène pille le marin

    🧭 🧜‍♀️ 🔫 🦜 ⚓

## Complétez la phrase

🦜 🏴‍☠️ 🗡️

## Réponse à l'enigme
Le pirate attaque (et pille le marin). 
🦜 🏴‍☠️ 🗡️ (🪙 🔫 🦜 ⚓)

## Indice
Faire deviner le prochain mot d'une phrase pour donner l'intuition.
* le mot qu'on entend le plus (de plus grande probabilité) est choisi
* dépend de la base d'entraînement
