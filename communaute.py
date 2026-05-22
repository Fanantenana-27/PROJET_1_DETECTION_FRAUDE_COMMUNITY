from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community import modularity
import csv
import networkx as nx
import pandas as pd
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user="neo4j"
password ="fanakely"
driver = GraphDatabase.driver(uri,auth=(user,password))


#Ajouter une personne dans sa communauté en mettant à jour la propriété "communaute" 
# selon l'identifiant de la communauté à laquelle elle appartient
def ajouter_dans_communaute(tx,sommet,id_communaute):
    query="""
    MATCH (p1:Personne)
    WHERE p1.id=toString($sommet)
    SET p1.communaute=$id_communaute
    RETURN p1
    """
    tx.run(query,sommet=sommet,id_communaute=id_communaute)

#Creer un sommet pour chaque communauté avec la propriété id qui correspond à l'identifiant de la communauté
def creer_communaute(transaction,id_COMMUNAUTE):
    var="""
    CREATE (c:Communaute {id:$id_COMMUNAUTE})
    """
    transaction.run(var,id_COMMUNAUTE=id_COMMUNAUTE)

#Ajouter un même label pour chaque personne dans la même communauté 
def ajouter_label_pour_chaque_communaute(tx,communaute):
    reqeute=f"""
    MATCH (p:Personne)
    WHERE p.communaute=$communaute
    SET p:Communaute_{communaute}
    RETURN p
    """
    tx.run(reqeute,communaute=communaute)

#Ajouter une relation entre les personnes dans la même communauté et la communauté à laquelle elles appartiennent
def ajouter_relation_entre_personne_et_communaute(tx,communaute):
    requete=f"""
    MATCH (p:Personne),(c:Communaute)
    WHERE p.communaute=$communaute AND c.id=$communaute
    CREATE (p)-[:APPARTIENT_A]->(c)
    """
    tx.run(requete,communaute=communaute)

def inverser_label(transaction,communaute):
    requete=f"""
    MATCH (p:Personne)
    WHERE p.communaute=$communaute
    REMOVE p:Personne
    SET p:Communaute_{communaute}:Personne
    """
    transaction.run(requete,communaute=communaute)
    
#Découpage du graphe en communautés à l'aide de l'algorithme de Girvan-Newman et 
# ajout des labels pour chaque communauté
def decoupage_en_communautes():
    df=pd.read_csv('liste_amis.csv',sep=',')
    G=nx.from_pandas_edgelist(df,'source', 'cible')
    compte_communities=girvan_newman(G)

    communities=next(compte_communities)

    #modularité : mesure de la qualité du découpage en communautés, plus elle est élevée, meilleur est le découpage
    mod=modularity(G,communities)
    while (mod<0.9):
        communities=next(compte_communities)
        mod=modularity(G,communities)

    #Ajouter les personnes dans leur communauté
    for i , community  in enumerate(communities):
        with driver.session() as session :
            session.execute_write(creer_communaute,i)
        for sommet in community:
            with driver.session() as session :
                session.execute_write(ajouter_dans_communaute,sommet,i)
                
    #Ajouter un même label pour chaque personne dans la même communauté 
    # et ajouter une relation entre les personnes dans la même communauté et 
    # la communauté à laquelle elles appartiennent
    for i , community  in enumerate(communities):
        with driver.session() as session :
            session.execute_write(ajouter_label_pour_chaque_communaute,i)
            session.execute_write(ajouter_relation_entre_personne_et_communaute,i)
    for i , community  in enumerate(communities):
        with driver.session() as session :
            session.execute_write(inverser_label,i)