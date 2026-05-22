
import create_graph
import communaute
import centralite_communaute


#Ce fichier main.py est le point d'entrée du projet.
#  Il permet de créer le graphe à partir des données, 
# de découper le graphe en communautés et 
# de chercher la personne centrale de chaque communauté.
create_graph.creer_graphe()
communaute.decoupage_en_communautes()
centralite_communaute.chercher_centralite_degre()



