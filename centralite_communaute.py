from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community import modularity
import networkx as nx
import csv
import pandas as pd
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user="neo4j"
password ="fanakely"
driver = GraphDatabase.driver(uri,auth=(user,password))

#Calclul de centralité de dégré : 
# On cherche la personne qui a le plus d'interactions directes au sein de la communauté
def degre_d_un_sommet(tx,sommet):
    query="""
    MATCH (p:Personne),(p1:Personne {id:$sommet})-[:INTERAGIT_AVEC]-(p2:Personne) 
    RETURN count(p2) as degre , count(DISTINCT p) as nombre_total_personne
    """
    result=tx.run(query,sommet=sommet)
    for record in result:
        return record["degre"] , record["nombre_total_personne"]
    
#Fonction qui permet de retourner le nombre de voisin d'un sommet donné :
def nombre_voisin_d_un_sommet(tx,sommet):
    requete="""
    MATCH (p:Personne),(p1:Personne {id:$sommet})-[:INTERAGIT_AVEC]-(p2:Personne) 
    RETURN count(p2) as nombre_voisin
    """
    result=tx.run(requete,sommet=sommet)
    for record in result:
        return record["nombre_voisin"]

#Comptage du nombre de communauté dans le graphe à partir de la propriété "communaute" des sommets
def nombre_communaute(tx):
    requete="""
    MATCH (p:Personne)
    RETURN max(p.communaute) as communaute
    """
    result=tx.run(requete)
    for record in result:        
        maximum=record["communaute"]   
    return maximum

#Fonction qui retourne la liste des personnes dans une communauté donnée 
# à partir de la propriété "communaute" des sommets
def Personne_dans_chaque_communaute(tx , communaute):
    requet="""
    MATCH (p:Personne)
    WHERE p.communaute = $communaute 
    RETURN p.id as id
    """
    liste_personne=tx.run(requet,communaute=communaute)
    return liste_personne.data()

#Ajouter un label "Personne_Centrale" pour la personne centrale de chaque communauté
def ajouter_label_pour_personne_centrale(tx):
    reqeute="""
    MATCH (p:Personne)
    WHERE p.status="personne centrale"
    REMOVE p:Personne
    SET p:Personne_Centrale:Personne
    RETURN p
    """
    tx.run(reqeute)

#Chercher la personne centrale de chaque communauté en calculant la centralité de degré 
# pour chaque personne dans la communauté et en comparant les résultats pour trouver la personne 
# avec la centralité de degré maximale
def chercher_centralite_degre():
    with driver.session() as session:
        degre=[]

        #Obtenir le nombre de communauté dans le graphe
        nombre_de_communaute=session.execute_read(nombre_communaute)
        
        #Obtenir la liste des personnes dans chaque communauté
        communaute= session.execute_read(Personne_dans_chaque_communaute,0)

        for i in range(nombre_de_communaute+1):
            communaute= session.execute_read(Personne_dans_chaque_communaute,i)
            for personne in communaute:

                #Obtenir le nombre de voisin d'une personne et le nombre total de personne dans la communauté pour calculer la centralité de degré
                nombre_total_personne=session.execute_read(degre_d_un_sommet,personne["id"])[1]

                #Calculer la centralité de degré pour chaque personne dans la communauté 
                degre.append(session.execute_read(degre_d_un_sommet,personne["id"])[0]/nombre_total_personne)
            maximum=max(degre)

            #Trouver la personne centrale de la communauté en comparant les centralités de degré de chaque personne dans la communauté et en choisissant celle qui a la centralité de degré maximale
            centralite_degre_personne=[personne for personne in communaute if session.execute_read(degre_d_un_sommet,personne["id"])[0]/nombre_total_personne==maximum]
            maximum=0
            for personne in centralite_degre_personne:
                nombre_voisin=session.execute_read(nombre_voisin_d_un_sommet,personne["id"])
                if nombre_voisin>maximum:
                    maximum=nombre_voisin
                    personne_centrale=personne

            #Mettre à jour le statut de la personne centrale en "personne centrale" dans la base de données et ajouter le label "Personne_Centrale" pour cette personne
            session.run(""" MATCH (p:Personne {id:$id})
                            SET p.status="personne centrale"
                        """,id=personne_centrale["id"])
        session.execute_write(ajouter_label_pour_personne_centrale)
