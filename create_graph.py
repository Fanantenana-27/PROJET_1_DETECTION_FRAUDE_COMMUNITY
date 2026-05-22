import csv
import pandas as pd
from neo4j import GraphDatabase


from neo4j import GraphDatabase
import csv
uri = "bolt://localhost:7687"
user="neo4j"
password ="fanakely"
driver = GraphDatabase.driver(uri,auth=(user,password))


uri = "bolt://localhost:7687"
user="neo4j"
password ="fanakely"
driver = GraphDatabase.driver(uri,auth=(user,password))

#Supprimer les sommets et les aretes du graphe avant de le recréer 
def supprimer_graphe(tx):
    reqeute="""
    MATCH (n)
    DETACH DELETE n
    """
    tx.run(reqeute)   

#Créer un sommet avec les propriétés nom, id, communaute et status où 
# nom : le nom de l'étudiant
# id : l'identifiant de l'étudiant
# communaute : la communauté à laquelle appartient l'étudiant (initialement 0)
# status : le statut de l'étudiant (initialement "etudiant")
def creer_sommet(tx,nom,id):
    query="""
    CREATE (p:Personne {nom:$nom,communaute:0,id:$id,status:"etudiant"})
    """
    tx.run(query,nom=nom,id=id)

#Creer une arete entre deux sommets avec la relation "INTERAGIT_AVEC" où
# id1 : l'identifiant du premier sommet
# id2 : l'identifiant du deuxième sommet
def creer_aretes(tx,id1,id2):
    query="""
    MATCH (p1:Personne {id:$id1}),(p2:Personne {id:$id2})
    WHERE p1.id<>p2.id
    CREATE (p1)-[:INTERAGIT_AVEC  ]->(p2)
    """
    tx.run(query,id1=id1,id2=id2)

#Creer le graphe à partir des fichiers csv (liste_etudiant.csv et liste_amis.csv) où 
# les sommets sont les étudiants et les aretes sont les interactions entre les étudiants
def creer_graphe():
    with driver.session() as session:
        #supprimer le graphe avant de le recréer
        session.execute_write(supprimer_graphe)

       
        #Créer les sommets: personnes(étudiants)
        with open("liste_etudiant.csv","r") as fichier:
            lecteur = csv.reader(fichier)
            for ligne in lecteur:
                session.execute_write(creer_sommet,ligne[1],ligne[0])

        #Creer les aretes entre les sommets : les interactions entre les étudiants
        with open("liste_amis.csv","r") as fichier:
            lecteur = csv.reader(fichier)
            for ligne in lecteur:
                session.execute_write(creer_aretes,ligne[0],ligne[1])
    