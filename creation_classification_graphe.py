import networkx as nx
import matplotlib.pyplot as plt
import random
import math
from itertools import combinations

###CREATION ALEATOIREMENT DU GRAPHE
"""
Création aléatoiremnt d'un graphe G en evitant les BOUCLES et les MULTIARÊTES:
G(V,p) Où : 
           |V| : La taille de graphe entré par l'utilisateur 
           p : Probabilité où deux sommets u et v de  V forment une arête  : p=ln(|V|)/|V|
"""
def creation_graphe():
    #Racuperer la taille du graphe saisit par l'utilisateur 
    taille = int(input("Entrez la taille du graphe : "))
    #Graphe G = {u:[v,w],....} : Le sommet u est relié à le sommet v et w
    G = {}      
    #Création des sommets
    for i in range(taille): 
        G[i]=[] #Par défaut la liste de voisin de i est vide
    #Création aléatoirement des arêtes selon la probabilité p , avec p=ln(|V|)/|V|
    p=math.log(taille)/taille                       #Calculer la probabilité où deux sommets u et v peut avoir un 
    for u in range(taille):
        for v in range(taille):
            if u<v and u not in G[v]:               #Pour eviter la boucle et le multiarête sur le graphe
                proba_u_et_v=random.uniform(0,1)
                if proba_u_et_v <= p:
                    G[u].append(v)
                    G[v].append(u)
    #Retoure : Graphe non orienté, sans boucle et pas de multiarête
    return G


"""
Verification si le graphe et connexe ou s'il n'est pas connexe , 
chercher le sous graphe connexe en utilisant le parcour en largeur 
Cette fonction return un  sous graphe connexe 
"""
def connexite(G):
    # On utilise BFS pour verifier la connexité du graphe G
    # On prend 0 comme sommet origine pour commencer le parcour  (BFS)
    sommet=0
    #Taille du graphe
    taille=len(G)
    # On utilise une couleur pour marqué le sommet :
    # green : Pour les sommetes qui ne sont pas encore visité
    # gray : Pour le somment en cour de traitement
    # black : Pour les sommets déjà visités 
    couleur=[]
    #File de sommets : Utiliser pour parcourir tous les voisins d'un sommet
    File=[]
    ###Le BFS : Initialisation 
        #Initialiser le coouleur de tous les somments par "white" sauf la couleur de sommet origine qui est "gray"
    for i in range(taille):
        couleur.append("green")
    couleur[0]="gray"
        #Le premier sommet exploré va être l'origine qui est 0
    File.append(sommet)
        #Recuperer dans des listes les sommets et les arêtes du graphe G
    sommets=[sommet for sommet in range(len(G))]
    aretes=[]
    for sommet in sommets:
        for voisin in G[sommet]:
            aretes.append((sommet,voisin))
    voisins=[]

    ### BFS en action
    while(File):
        sommet=File[0]
        #Recuperer tous les voisin d'un sommet 
        for (u,v) in aretes:
            if u==sommet :
                voisins.append(v)
            elif v==sommet :
                voisins.append(u)
        for voisin in voisins :
            if(couleur[voisin]=="green"):
                couleur[voisin]="gray"
                File.append(voisin)
        #Défiler File
        File.remove(sommet)
        couleur[sommet]="black"
        voisins.clear()
    # On retourne G_prime ,un sous graphe connexe de G 
    G_prime={}
    for i in range(len(couleur)):
        if couleur[i]=="black":
            G_prime[i]=G[i]
    return G_prime 
           

### CLASSIFICATION

# Pour vérifier si tous les sommets d'une liste sont connectés entre eux
def verifier_clique(sous_ensemble,G):
    for u in sous_ensemble:
        for v in sous_ensemble:
            if v!=u and v not in G[u]:
                clique=False
                return(False)
    return(True)

# On utilise DFS pour chercher tous les cliques dans un graphe 
def chercher_clique_dans_graphe(G):
    sommets=list(G.keys())
    liste_cliques = []
    pile=[([],sommets[:])]

    while (pile):
        clique,sommets_restant = pile.pop()

        if len(sommets_restant)==0:
            if len(clique) >= 2:
                liste_cliques.append(sorted(clique))
            continue

        for i,v in enumerate(sommets_restant):
            clique_1 = clique + [v]
            # On ajoute v seulement s'il est connecté à toute la clique courante
            if verifier_clique(clique_1,G):
                sommets_restant_1 = sommets_restant[i+1:]
                pile.append((clique_1,sommets_restant_1))
            else :
                if len(sommets_restant[i+1:]) ==0:
                    if len(clique)>=2:
                        liste_cliques.append(sorted(clique))
    return liste_cliques
    

"""
Detection de fraude :
Classifier chaque sommet selon :
    * Normale : pour le personne normale 
    * Consommateur 
    * Dealeur
    * Fournusseur 
Consommateur : peut être les personnes (sommets) forment un clique dans le graphe car elles ont de rélation bizarre.

Dealeur : peut être les personnes ayant plusieur relations (plusieur voisins) . Le status d'un sommet u est Dealeur si 
le degre de cet sommet u : deg(u)> (n-1)*p + 2 * Écart-type
=> deg(u)> (n-1)*p + 2 * sqrt((n-1)p)

"""

def classification_chaque_sommet(G):
    status_sommets={}
    liste_cliques = []
    degre_sommets={}
    taille=len(G)
    p=math.log(taille)/taille

    status_sommets.fromkeys(list(G.keys()),None)
    degre_sommets.fromkeys(list(G.keys()),None)

    for sommet in list(G.keys()):
        status_sommets[sommet]="Normale"

    liste_cliques=chercher_clique_dans_graphe(G)
    for clique in liste_cliques:
        if (len(clique)>2):
            for sommet in clique:
                status_sommets[sommet]="Consommateur"

    for sommet in list(G.keys()):
        degre=len(G[sommet])
        degre_sommets[sommet]=degre
    for sommet in list(G.keys()):
        if degre_sommets[sommet] > ((taille-1)*p + 2* math.sqrt((taille-1)*p)):
            status_sommets[sommet]="Dealeur" 
    
    return(status_sommets)

def presantation_de_graphe(G,*args):
    Graphe=nx.Graph()
    sommets=list(G.keys())
    aretes=[]
    couleur =[]
    if args :
        couleur = args[0]
    else :
        couleur=["black" for sommet in sommets ]
    for sommet in sommets:
        Graphe.add_node(sommet)
        for voisin in G[sommet]:
            aretes.append((sommet,voisin))
    
    Graphe.add_nodes_from(sommets)
    Graphe.add_edges_from(aretes)
    pos = nx.spring_layout(Graphe)
    plt.title("RESULTAT")
    nx.draw(Graphe,pos,with_labels=True,node_size=100,node_color=couleur,edge_color='blue',font_size=8,font_weight='bold',font_color='red',label="Jaune : Personne normale \n Vert : Consommateur \n Rouge : Dealeur")
    plt.legend(scatterpoints=1, loc=0)
    plt.show()


def main():
    couleur=[]
    G=creation_graphe()
    G=connexite(G)
    status_sommets=classification_chaque_sommet(G)

    couleur=["yellow" for sommet in list(G.keys())]

    for i,sommet in enumerate(list(G.keys())):
        if status_sommets[sommet]=="Consommateur":
            couleur[i]="green"
        elif status_sommets[sommet]=="Dealeur":
            couleur[i]="red"

    presantation_de_graphe(G,couleur)


main()