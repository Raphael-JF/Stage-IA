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
1. Le pirate navigue parfois.
🦜 🏴‍☠️ ⛵ 🌊

2. Parfois le pirate pille la sirène et navigue. 
🌊 🦜 🏴‍☠️ 🔫 🧭 🧜‍♀️ 🪙 ⛵

3. Le marin attaque et pille.
🦜 ⚓ 🗡️ 🪙 🔫

4. La sirène attaque et pille le marin.
🧭 🧜‍♀️ 🗡️ 🪙 🔫 🦜 ⚓

5. Parfois le pirate pille et navigue.
🌊 🦜 🏴‍☠️ 🔫 🪙 ⛵

6. La sirène pille le marin
🧭 🧜‍♀️ 🔫 🦜 ⚓

## Réponse à l'enigme
Le pirate attaque (et pille le marin). 
🦜 🏴‍☠️ 🗡️ (🪙 🔫 🦜 ⚓)

## Indice
Faire deviner le prochain mot d'une phrase pour donner l'intuition.
* le mot qu'on entend le plus (de plus grande probabilité) est choisi
* dépend de la base d'entraînement
