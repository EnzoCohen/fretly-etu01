# Audit de sécurité initial

Avant de faire le moindre commit, j'ai analysé l'archive telle que l'ancienne équipe l'a laissée, avec Trivy en mode système de fichiers. J'ai activé les trois scanners : dépendances, secrets et mauvaises configurations.

```bash
trivy fs --scanners vuln,secret,misconfig .
```

## Constats et corrections

Trivy a remonté deux problèmes. En relisant les fichiers à la main, j'en ai trouvé deux autres qu'il n'a pas vus (dernières lignes du tableau).

| Élément | Type | Gravité | Risque concret pour Fretly | Correction appliquée |
|---|---|---|---|---|
| `python-multipart==0.0.6` dans `requirements.txt` (9 CVE, dont CVE-2024-24762, CVE-2024-53981, CVE-2026-24486, CVE-2026-42561 et CVE-2026-53539) | Vulnérabilité de dépendance | 5 HIGH, 1 MEDIUM, 3 LOW | C'est la bibliothèque qui lit les fichiers envoyés sur `POST /shipments/import`. Avec une requête bien construite, un attaquant peut faire tomber l'API, ou même écrire un fichier où il veut sur le serveur. | Passage à la version `0.0.32`. |
| Clé privée RSA en clair dans `legacy/deploy_manuel.sh` | Secret | HIGH | N'importe qui ayant accès au dépôt peut se connecter en SSH au serveur de production. Il peut alors récupérer les données des clients ou remplacer le code qui tourne. | Script supprimé, car il ne sert plus et le pipeline le remplace. `legacy/` et les fichiers de clés sont ajoutés au `.gitignore`. |
| Fichier `.env` avec la clé d'API et le mot de passe PostgreSQL en clair (non détecté par Trivy) | Secret | Non évalué par Trivy | Avec la clé d'API, n'importe qui peut créer ou modifier des expéditions. Avec le mot de passe, il peut accéder directement à la base. | `.env` ajouté au `.gitignore`. Je versionne à la place un `.env.dist` avec des valeurs d'exemple. |
| IP et utilisateur du serveur de production (`ubuntu@15.237.x.x`, masquée ici volontairement) dans le même script (non détectés par Trivy) | Information sensible | Non évaluée par Trivy | On donne directement la cible à un attaquant. | Supprimés avec le script. |

Après ces corrections, j'ai relancé le même scan : il ne remonte plus rien, ni HIGH ni CRITICAL. Les deux sorties sont en annexe.

## Et si la clé avait été poussée sur GitHub ?

Supprimer le fichier dans un nouveau commit ne suffirait pas. Le fichier disparaît de la dernière version, mais la clé reste dans l'historique. On la retrouve dans chaque clone et dans les forks déjà faits. Des robots parcourent GitHub en permanence pour récupérer ce genre de clé, souvent quelques minutes après le push. À partir du moment où elle a été publiée, il faut partir du principe qu'elle est compromise.

Voici ce que je ferais, dans cet ordre :

1. Révoquer la clé tout de suite, en retirant la clé publique du fichier `authorized_keys` sur le serveur. C'est la seule action qui supprime vraiment le risque, donc elle passe avant tout le reste.
2. Générer une nouvelle paire de clés et la stocker uniquement dans les secrets GitHub.
3. Vérifier dans les journaux SSH du serveur si quelqu'un s'est connecté depuis la publication. Si c'est le cas, je considère le serveur comme compromis.
4. Nettoyer l'historique avec `git filter-repo` (ou BFG), forcer le push, demander à GitHub de vider son cache et faire re-cloner le dépôt par toute l'équipe.
5. Éviter que ça se reproduise : scan de secrets bloquant dans la CI, protection contre le push de secrets sur GitHub et un `.gitignore` correct.

## Un fichier est-il sans risque quand Trivy ne remonte rien ?

Non, et l'audit le montre bien : le `.env` et l'adresse du serveur sont passés sans alerte.

Trivy repère les secrets grâce à des motifs connus, comme un en-tête de clé privée ou un format de token AWS ou GitHub. Un mot de passe choisi par quelqu'un, ou une adresse IP, ne ressemble à aucun de ces motifs.

Pour les dépendances, il ne connaît que les vulnérabilités déjà publiées. Un résultat propre aujourd'hui ne dit rien de la CVE qui sortira la semaine prochaine. C'est pour ça que le scan doit tourner à chaque exécution du pipeline.

Enfin, il ne lit pas la logique du code. Une erreur de calcul, une route oubliée sans authentification ou une injection ne le concernent pas. Et quand on filtre ses résultats (`--severity`, `--ignore-unfixed`), on choisit soi-même de ne pas voir une partie des problèmes.

## Annexes

- [Sortie Trivy avant correction](annexes/trivy-avant.txt)
- [Sortie Trivy après correction](annexes/trivy-apres.txt)
