# premise_selection

Contient l'ensemble des contributions du stage de master 2 "Déduction modulo théorie pour la géométrie" par Baptiste Lemoine, encadré par David Delahaye.

Proposant une utilisation du deep learning pour sélectionner les prémisses nécessaires (axiomes, lemmes et règles de réécrire) à la preuve d'un théorème de géométrie.


## Nous utilisons :
  * l'axiomatique de Tarski. 
  * la bibliothéque GeoCoq (https://geocoq.github.io/GeoCoq/) fournissant la formalisation des théorèmes des 16 premiers chapitres du livre "Metamathematische Methoden in der Geometrie" écrit par Schwabhäuser, W & Szmielew, W & Tarski, A.
  * le logiciel de preuve automatique zipperposition (https://github.com/c-cube/zipperposition)
  
## Contenu :

### Le dossier "datas" contient l'ensemble des données nécessaires au bon fonctionnement des scripts :  
  * ax_th_def.zf : définitions des théorèmes et axiomes
  * rew_def.zf : définitions des règles de réécriture
  * rew_type.zf : typage des règles de réécriture
  * rew_type.json : typage des règles de réécriture utiles à la preuve (ex : ne contient pas les structures primitives comme les points) sous forme json
  * config_struct.json : donne la structure des dossiers contenants les fichiers de dependances (.dep) et de preuves (.dep)
  (ex : {"Ch02_cong": ["cong_reflexivity"], "Ch03_bet": ["bet_col"]} : cong_reflexivity se trouve dans le dossier Ch02_cong)
  (demande EXACTEMENT un seul niveau de profondeur)
  
### Le dossier "source" :
contient l'ensemble du code suivant :
  * Classes :
    * "dataManager" gère les données :
      * la récupération (depuis le dossier datas)
      * le traitement (de données brutes vers un ensemble de couple donnée => labels)
    * "reseau" gère le réseau de neurone impliqué a partir des données envoyées par le dataManager :
      * le prétraitement des données
      * la création et l'entrainement du réseau de neurones impliqué
      * gestion primitive des prédictions
      * posséde des options de sauvegarde et chargement de l'ensemble des structures impliquées (tokenizer, multi_label_binarizer, architecture et poids du réseau)
    * "predictionManager" fait le lien entre le dataManager et le reseau :
      * Traitement plus fin des prédictions du réseau (selection des k plus grandes valeurs de la prédiction (top_k) ou des valeurs supérieurs à un seuil donné (seuil))
      * Apporte des statistiques sur les performances des prédictions
      * produit des fichiers de preuves à partir des prédictions
    * "zipper_utils" permet de paralléliser les appels au solveur zipperposition et de renvoyer des statistiques sur les résultats obtenus
    * "utils" contient un ensemble de fonctions ne nécessitants pas un environnement particulier

  * Scripts (executables) pour des informations plus précises sur les paramêtres utiliser le flag "-h" :
    * zipper_exec :
      * Appel Zipperposition sur l'ensemble des théorèmes (ou un sous ensemble spécifié par th_to_prove_file) du dossier zf_dir (structuré tel qu'indiqué dans le fichier config_struct), stocke la liste des théorèmes prouvés dans th_valid_file
    * train.py :
      * Créé et entraine un réseau sur l'ensemble des théorèmes spécifiés par le fichier th_valid, dont les prémisses sont données dans le dossier dep_dir. Ce réseau est ensuite sauvegarder dans le dossier save_network_dir
    * tactic_top_k
      * Technique des k plus grandes valeurs : Utilise le réseau sauvegardé dans le dossier network_save pour prédire les prémisses de l'ensemble des théorèmes du fichiers ax_th_def.zf. A chaque itération, génére, a partir des prémisses prédites et d'un k donné, des fichiers zf, stockés dans le dossier zf_dir. Zipperposition est appelé sur l'ensemble des zf générés, la prochaine itération ne s'applique que sur les théorèmes non prouvés par les itérations précédentes
      * k allant de 0 au nombre de prémisses connues par le réseau. A chaque itération, k est augmenté du résultat de la division euclidienne de k par 10 auquel on ajoute 1.
    * tactic_seuil
      * Technique du seuil : Utilise le réseau sauvegardé dans le dossier network_save pour prédire les prémisses de l'ensemble des théorèmes du fichiers ax_th_def.zf. A chaque itération, génére, a partir des prémisses prédites et d'un seuil donné, des fichiers zf, stockés dans le dossier zf_dir. Zipperposition est appelé sur l'ensemble des zf générés, la prochaine itération ne s'applique que sur les théorèmes non prouvés par les itérations précédentes
      * seuil allant de 0.9 à 1e-7 en le divisant par 1.2 à chaque itération.
      
    * tactic_data_to_th_proved_file
      * Converti un fichier data (créé par un des scripts tactique) en un fichier contenant la liste des noms des théorèmes prouvés par cette tactique
      
    * zf_dir_to_dep_dir
      * Converti un dossier contenant des fichiers zf en un dossier contenant les fichiers dep correspondant, ces derniers coniennent l'ensemble des noms des lemmes, axiomes et règles de réécritures apparaissant dans le fichiers zf associé.
      * Les fichiers dep sont utilisés pour l'apprentissage d'un réseau, il est donc nécessaire de convertir les zf, résultant de l'application d'une tactique, en dep pour pouvoir entrer une réseau sur les nouvelles prémisses trouvées.
      
    * display_data
      * Demande un fichier data (résultant de l'application d'un tactique) et la liste des théorèmes ayant servi lors de l'apprentissage du réseau. Affiche un graphe correspondant à l'évolution des théorèmes prouvés en fonction du paramètre de la tactique (seuil ou top_k). Donne la proportion de théorèmes prouvés parmi ceux ayant servi lors de l'apprentissage et la proportion de théorème prouvés parmi les autres (prémisses complétement inconnues)
    

### Une utilisation classique:
Se positionner dans le dossier source :
```
python zipper_exec.py "../resultat/geocoq_extract/zf/" "../resultat/geocoq_extract/th_proved.json" "../datas/config_struct.json"

python train.py "../resultat/geocoq_extract/th_proved.json" "../resultat/geocoq_extract/dependencies/" "../resultat/network/geocoq_extract_network/"

python tactic_seuil.py "../resultat/network/geocoq_extract_network/" "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil2/tactic_datas.pickle" -si 0.05 -sm 0.02

python tactic_top_k.py "../resultat/network/geocoq_extract_network/" "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil2/tactic_datas.pickle" -ki 2 -km 30

python tactic_data_to_th_proved_file.py "../resultat/tactic_seuil/tactic_seuil_datas.pickle" "../resultat/tactic_seuil/th_proved.json"

python zf_dir_to_dep_dir.py "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil/dependencies/"

python display_data.py "../resultat/tactic_seuil/tactic_seuil_datas.pickle" "../resultat/geocoq_extract/th_proved.json"
```

