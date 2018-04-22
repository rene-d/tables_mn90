# Tables MN90

[![License](https://img.shields.io/badge/license-MIT-71787A.svg)](https://choosealicense.com/licenses/mit)

## AVERTISSEMENT

Ceci n'est pas un outil de désaturation. Ne calculez pas de vraies désaturation avec. Ne plongez pas avec.

This is not a desaturation tool. Do not calculate true desaturation with. Do not dive with it.

## Introduction

Ceci est un travail d'approfondissement après le passage du [MF1](https://ffessm.fr/gestionenligne/manuel/14_MF%201.pdf), qui peut être utilisé à des fins pédagogiques ou par les plongeurs curieux et un peu mathématiciens.

## Les tables MN90

Les [tables MN90](https://www.plongee-plaisir.com/fr/book/tables-plongee/) sont les tables de désaturation utilisées en France pour l'enseignement de la plongée par la [FFESSM](https://ffessm.fr) et la plongée elle-même avant l'avènement des ordinateurs.

## Formules et feuille de calcul

L'onglet 'Tensions' utilise la [formule de Schreiner](http://www.deepocean.net/deepocean/index.php?science03.php) (et [ici](https://www.shearwater.com/wp-content/uploads/2012/08/Introductory-Deco-Lessons.pdf), [là](http://www.divetable.de/workshop/V1_e.htm), et encore [ici](http://wrobell.it-zone.org/decotengu/model.html), etc.) pour prendre en compte plus intelligemment la saturation pendant le changement de profondeur, ce que la formule d'Haldane ne peut pas faire.

Tout le reste est basé sur ce qu'on apprend au [N4](Téléchargez), avec un peu plus de math, notamment pour calculer la durée des paliers et la prise en compte de durées de saturation non multiples des périodes.

C'est une feuille Excel avec macros, si on ne les autorise pas à l'ouverture ça ne fonctionnera évidemment pas puisque tous les calculs sont faits dans un module VBA. Le changement de paramètres oblige à recalculer les valeurs, ce qu'Excel ne fait malheureusement pas automatiquement.
