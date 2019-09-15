# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 06:06:36 2014

@author: CetaData-Lainee
"""

# code de calcul des ratios notes et recommandations des communes et groupements
# from urllib.request import urlopen
import os
import csv
from bs4 import BeautifulSoup
# from lxml import html
# import requests
import sys
from datetime import date


# sys.setdefaultencoding('utf-8')

def cherche(a, b):
    s = 0
    for x in range(len(b)):
        if (s == 0 and b[x] == a):
            s = x
    if s == 0:
        s = len(b) + 1
    return s


def note(x,d1,d5,d9):
    x=float(x)
    d1=flat(d1)
    d5 = flat(d5)
    d9 = flat(d9)
    if d1=="ns" or d5=="ns" or d9=="ns":
        Note="ns"
    else:
        if x<=d1:
            Note=0
        elif x<=d5:
            Note=10*(x-d1)/(d5-d1)
        elif x<=d9:
            Note=10*(1+(x-d5)/(d9-d5))
        elif x>=d9:
            Note=20

    return Note

# Fonction d'écriture d'un enregistrement dans un fichier
def writeCom(writer, line):
    writer.writerow(line)


# Ouverture des fichiers csv d'écriture des enregistrements scrapés et des urls incorrects

Annee = '2017'
Today = str(date.today())

Chemin = '/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Argus_' + Annee + '/ScraperResults-Round5/'
# print(Chemin)
os.chdir(Chemin)

CheminR = Chemin + '/Resultats/Etape3-Total'
os.chdir(CheminR)
FichierDest1 = open("Etape-3-Vigie-" + Annee + "-" + Today + ".csv", "w")
FileVigie = csv.writer(FichierDest1)

FichierDest2 = open("Etape-3-Vigie-NOK-" + Annee + "-" + Today + ".csv", "w")
FileVigiedef = csv.writer(FichierDest2)

FichierDest4 = open("FileOutTest INSEE.csv", "w")
FileOutTest = csv.writer(FichierDest4)
writeCom(FileOutTest, ["Cle", "INSEE"])

FichierDest5 = open("File_Dist_Ratios_Segments_CetGC.csv", "w")
FileOutRatiosSegmentsC = csv.writer(FichierDest5)

Titre = ["Ind_GC-SegTaille_C", "Dep_Dec1__C", "Dep_Dec5__C", "Dep_Dec9__C", "Sante_Dec1__C", "Sante_Dec5__C",
         "Sante_Dec9__C", "Autof_Dec1__C", "Autof_Dec5__C", "Autof_Dec9__C", "Endet_Dec1__C", "Endet_Dec5__C",
         "Endet_Dec9__C", "RigStruc_Dec1__C", "RigStruc_Dec5__C", "RigStruc_Dec9__C", "PFisc_Dec1__C", "PFisc_Dec5__C",
         "PFisc_Dec9__C"]
Titre = Titre + ["Dep_Dec1__GC", "Dep_Dec5__GC", "Dep_Dec9__GC", "Sante_Dec1__GC", "Sante_Dec5__GC", "Sante_Dec9__GC",
                 "Autof_Dec1__GC", "Autof_Dec5__GC", "Autof_Dec9__GC", "Endet_Dec1__GC", "Endet_Dec5__GC",
                 "Endet_Dec9__GC", "RigStruc_Dec1__GC", "RigStruc_Dec5__GC", "RigStruc_Dec9__GC", "PFisc_Dec1__GC",
                 "PFisc_Dec5__GC", "PFisc_Dec9__GC"]
writeCom(FileOutRatiosSegmentsC, Titre)

FichierDest6 = open("File_Ratios_Notes_Recos_CetGC.csv", "w")
FileOutRatiosNotesC = csv.writer(FichierDest6)

TitreFile=["Indice","Nom_C_portail","Nom_GC_portail","numDep","NomDep","Pop_C","PopTot_C","Pop_GC","PopTot_GC","Ind_GC-SegTaille_C"]
TitreFile=TitreFile+["Note_Dep_C","Note_Sante_C","Note_Autof_C","Note_Endet_C","Note_RigStruc_C","Note_PFisc_C","Ratio_Dep_C","Ratio_Sante_C","Ratio_Autof_C","Ratio_Endet_C","Ratio_RigStruc_C","Ratio_PFisc_C"]
TitreFile=TitreFile+["Dep_Dec1__C","Dep_Dec5__C","Dep_Dec9__C","Sante_Dec1__C","Sante_Dec5__C","Sante_Dec9__C","Autof_Dec1__C","Autof_Dec5__C","Autof_Dec9__C", "Endet_Dec1__C","Endet_Dec5__C","Endet_Dec9__C", "RigStruc_Dec1__C","RigStruc_Dec5__C","RigStruc_Dec9__C", "PFisc_Dec1__C","PFisc_Dec5__C","PFisc_Dec9__C"]
TitreFile=TitreFile+["RevFonc_C","DepFonc_C","DepPerso_C","RembEmp_C","EncoursDetteTot_C","AnDette_C","MontTH_C","MontTF_C","MontTFNB_C","MontTFAdd_C","MontImpTot_C","PotFisc_C"]
TitreFile=TitreFile+["Note_Dep_GC","Note_Sante_GC","Note_Autof_GC","Note_Endet_GC","Note_RigStruc_GC","Note_PFisc_GC","Ratio_Dep_GC","Ratio_Sante_GC","Ratio_Autof_GC","Ratio_Endet_GC","Ratio_RigStruc_GC","Ratio_PFisc_GC"]
TitreFile=TitreFile+["Dep_Dec1__GC","Dep_Dec5__GC","Dep_Dec9__GC","Sante_Dec1__GC","Sante_Dec5__GC","Sante_Dec9__GC","Autof_Dec1__GC","Autof_Dec5__GC","Autof_Dec9__GC", "Endet_Dec1__GC","Endet_Dec5__GC","Endet_Dec9__GC", "RigStruc_Dec1__GC","RigStruc_Dec5__GC","RigStruc_Dec9__GC", "PFisc_Dec1__GC","PFisc_Dec5__GC","PFisc_Dec9__GC"]
TitreFile=TitreFile+["RevFonc_GC","DepFonc_GC","DepPerso_GC","RembEmp_GC","EncoursDetteTot_GC","AnDette_GC","MontTH_GC","MontTF_GC","MontTFNB_GC","MontTFAdd_GC","MontImpTot_GC","PotFisc_GC"]
writeCom(FileOutRatiosNotesC,TitreFile)



# Accès aux fichiers csv d'entrée  : donnnées financières des communes. des codes INSEE et des résidences secondaires

CheminR = '/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Argus_2017/ScraperResults-Round5/Resultats/Etape2-Total'
os.chdir(CheminR)
NomIn = "Etape-2-Vigie-2017-2019-05-06.csv"
FichierIn = open(NomIn, "r")
FileIn = csv.reader(FichierIn)


# Création du dictionnaire des noms de variables C et GC

count = 0
Titre = {}  # Dictionnaire des noms de colonnes dans le fichier de 2ème étape
DicTitreFile={}  # Dictionnaire des noms des colonnes du fichier de résultats
DicC = {}  # Dictionnaire des résultats C et GC de l'étape 2
DicRes = {}  # Dictionnaire des résultats C et GC de l'étape 3


# Lecture des titres des colonnes du fichier résultat
print("nombre de colonnes",len(TitreFile))

for i in range(len(TitreFile)):
    #print("colonne TitreFile",i, type(i),TitreFile[i])
    DicTitreFile[TitreFile[i]]=[i,TitreFile[i]]

# Lecture des titres des colonnes du fichier de l'étape 2 et Pré remplissage du dictionnaire des résultats de l'étape 3

NMin = 1
NMax = 37000
Titre = {}

for f in FileIn:
    f=f[0].split(";")
    if count == 0:
        count = count + 1
        for i in range(len(f)):
            Titre[str(f[i])] = [i, str(f[i])]
            print("colonne Titre",i,str(f[i]))
    elif (count >= NMin and count <= NMax):
        if len(f) == 1:  # traitement des lignes mal formattées
            print("controle 1 - mauvais formatttage",f)
        else:

            Indice = f[0]
            DicRes[Indice] = TitreFile
            DicC[Indice] = f
            for j in range(len(TitreFile)):
                try :
                    DicRes[Indice][j]=DicC[Indice][Titre[TitreFile[j][0]]]
                except:
                    pass
            #print(count, "f=",f)
    count=count+1

print("longeur de DicC / DicRes:", len(DicC))

# Calcul des ratios

print()
print("Debut de calcul des ratios")
Dic_Dep_C = {}  # Cle = indice GC x taille C - Dépenses Fonc C
Dic_Dep_GC = {}  # Cle = indice GC x taille C - Dépenses Fonc C+GC

Dic_Sante_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Dic_Sante_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Dic_Autof_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Dic_Autof_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Dic_Endet_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Dic_Endet_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Dic_RigStruc_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Dic_RigStruc_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Dic_PFisc_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Dic_PFisc_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

count = 0
ListeIndicesegments=[]

for f in DicC:
    #print("Dic",len(DicC[f]),DicC[f])
    Ind_GC_Taille=DicC[f][Titre["Ind_GC-SegTaille_C"][0]]
    #if Ind_GC_Taille=="1-2- 250-500" or Ind_GC_Taille=="0-2- 250-500":
    #    print("Check ", Ind_GC_Taille, len(DicC[f]),DicC[f])
    if Ind_GC_Taille in ListeIndicesegments:
        pass
    else:
        print("ListeIndicesegments",Ind_GC_Taille)
        ListeIndicesegments.append(Ind_GC_Taille)

    Indice_GC=int(Ind_GC_Taille[0])
    #print("Indice_GC",Indice_GC)
    try:
        RatioPop_C=float(DicC[f][Titre["Pop_C"][0]])/float(DicC[f][Titre["PopTot_C"][0]])
    except:
        RatioPop_C =1
    try:
        #print("pop GC",DicC[f][Titre["Pop_GC"][0]],DicC[f][Titre["PopTot_GC"][0]])
        RatioPop_GC=float(DicC[f][Titre["Pop_GC"][0]])/float(DicC[f][Titre["PopTot_GC"][0]])
    except:
        RatioPop_GC =1

    #print("index",count,"Nom",DicC[f][Titre["NomC portail"][0]],"indice",Ind_GC_Taille,"RatioPop_C",RatioPop_C,"RatioPop_GC",RatioPop_GC)

    try:
        RDep_C=int(DicC[f][Titre["DepFonc_C"][0]])*RatioPop_C
        #print(Ind_GC_Taille,"Calcul RDep_C", DicC[f][Titre["DepFonc_C"][0]], RatioPop_C,RDep_C)
        if Ind_GC_Taille in Dic_Dep_C:
            Dic_Dep_C[Ind_GC_Taille].append(RDep_C)
        else:
            Dic_Dep_C[Ind_GC_Taille]=[RDep_C]
        #print("OK n")
    except:
        RDep_C="na"
        print(f,"erreur RDep_C")
    #DicRes[DicTitreFile["Ratio_Dep_C"][0]]=RDep_C

    try:
        if Indice_GC==0:
            RDep_GC="ns"
        else:
            #print("check RDep_GC - C", DicC[f][Titre["NomC portail"][0]],Ind_GC_Taille, "Calcul RDep_GC", DicC[f][Titre["DepFonc_C"][0]], RatioPop_C)
            #print("GC",DicC[f][Titre["DepFonc_GC"][0]], RatioPop_GC)
            RDep_GC = float(DicC[f][Titre["DepFonc_C"][0]]) * RatioPop_C+float(DicC[f][Titre["DepFonc_GC"][0]]) * RatioPop_GC
        if Ind_GC_Taille in Dic_Dep_GC:
            Dic_Dep_GC[Ind_GC_Taille].append(RDep_GC)
        else:
            Dic_Dep_GC[Ind_GC_Taille]=[RDep_GC]
    except:
        RDep_GC = "na"
        print(f, "erreur RDep_GC")
    DicRes[DicTitreFile["Ratio_Dep_GC"][0]] = RDep_GC

    # Calcul ratios autofinancement
    try:
        #print("composants de RAutofC",int(DicC[f][Titre["DepFonc_C"][0]]),int(DicC[f][Titre["RembEmprunt_C"][0]]))
        RAutof_C=float(int(DicC[f][Titre["DepFonc_C"][0]])+int(DicC[f][Titre["RembEmprunt_C"][0]]))/float(DicC[f][Titre["RevFonc_C"][0]])
        if Ind_GC_Taille in Dic_Autof_C:
            Dic_Autof_C[Ind_GC_Taille].append(RAutof_C)
        else:
            Dic_Autof_C[Ind_GC_Taille]=[RAutof_C]
    except:
        RAutof_C="na"
        print(f,"erreur RAutof_C")
    DicRes[DicTitreFile["Ratio_Autof_C"][0]] = RAutof_C

    try:
        if Indice_GC==0:
            RAutof_GC="ns"
        else:
            #print("Check RAutof_GC",DicC[f][Titre["RembEmprunt_C"][0]],DicC[f][Titre["RembEmprunt_GC"][0]])
            NumRAutof_GC = (int(DicC[f][Titre["DepFonc_C"][0]])+int(DicC[f][Titre["RembEmprunt_C"][0]])) * RatioPop_C+(int(DicC[f][Titre["DepFonc_GC"][0]])+int(DicC[f][Titre["RembEmprunt_GC"][0]]))* RatioPop_GC
            DenRAutof_GC = int(DicC[f][Titre["RevFonc_C"][0]]) * RatioPop_C + int(DicC[f][Titre["RevFonc_GC"][0]]) * RatioPop_GC
            RAutof_GC=float(NumRAutof_GC)/DenRAutof_GC
        if Ind_GC_Taille in Dic_Autof_GC:
            Dic_Autof_GC[Ind_GC_Taille].append(RAutof_GC)
        else:
            Dic_Autof_GC[Ind_GC_Taille] = [RAutof_GC]
    except:
        RAutof_GC="na"
        print(f, "erreur RAutof_GC")
    DicRes[DicTitreFile["Ratio_Autof_GC"][0]] = RAutof_GC

    # Calcul ratios endettement
    try:
        REndet_C=float(DicC[f][Titre["EncoursDetteTot_C"][0]])/int(DicC[f][Titre["RevFonc_C"][0]])
        if Ind_GC_Taille in Dic_Endet_C:
            Dic_Endet_C[Ind_GC_Taille].append(REndet_C)
        else:
            Dic_Endet_C[Ind_GC_Taille]=[REndet_C]
    except:
        REndet_C="na"
        print(f,"erreur REndet_C")
    DicRes[DicTitreFile["Ratio_Endet_C"][0]] = REndet_C

    try:
        if Indice_GC==0:
            REndet_GC="ns"
        else:
            NumREndet_GC = int(DicC[f][Titre["EncoursDetteTot_C"][0]]) * RatioPop_C+int(DicC[f][Titre["EncoursDetteTot_GC"][0]])* RatioPop_GC
            DenREndet_GC = int(DicC[f][Titre["RevFonc_C"][0]]) * RatioPop_C + int(DicC[f][Titre["RevFonc_GC"][0]]) * RatioPop_GC
            REndet_GC=float(NumREndet_GC)/DenREndet_GC
        if Ind_GC_Taille in Dic_Endet_GC:
            Dic_Endet_GC[Ind_GC_Taille].append(REndet_GC)
        else:
            Dic_Endet_GC[Ind_GC_Taille]=[REndet_GC]
    except:
        REndet_GC="na"
        print(f, "erreur REndet_GC")
    DicRes[DicTitreFile["Ratio_Endet_GC"][0]] = REndet_GC

    # Calcul rigidité structurelle
    try:
        RRigStruc_C=float(int(DicC[f][Titre["DepPerso_C"][0]])+int(DicC[f][Titre["AnDette_C"][0]]))/int(DicC[f][Titre["RevFonc_C"][0]])
        if Ind_GC_Taille in Dic_RigStruc_C:
            Dic_RigStruc_C[Ind_GC_Taille].append(RRigStruc_C)
        else:
            Dic_RigStruc_C[Ind_GC_Taille]=[RRigStruc_C]
    except:
        RRigStruc_C='na"'
        print(f,"erreur RRigStruc_C")
    DicRes[DicTitreFile["Ratio_RigStruc_C"][0]] = RRigStruc_C

    try:
        if Indice_GC==0:
            RRigStruc_GC="ns"
        else:

            NumRRigStruc_GC = (int(DicC[f][Titre["DepPerso_C"][0]])+int(DicC[f][Titre["AnDette_C"][0]]))* RatioPop_C+(int(DicC[f][Titre["DepPerso_GC"][0]])+int(DicC[f][Titre["AnDette_GC"][0]]))* RatioPop_GC
            #print("NumRRigStruc_GC",NumRRigStruc_GC)
            DenRRigStruc_GC = int(DicC[f][Titre["RevFonc_C"][0]]) * RatioPop_C + int(DicC[f][Titre["RevFonc_GC"][0]]) * RatioPop_GC
            #print("DenRRigStruc_GC", DenRRigStruc_GC)
            RRigStruc_GC=float(NumRRigStruc_GC)/DenRRigStruc_GC
        if Ind_GC_Taille in Dic_RigStruc_GC:
            Dic_RigStruc_GC[Ind_GC_Taille].append(RRigStruc_GC)
        else:
            Dic_RigStruc_GC[Ind_GC_Taille]=[RRigStruc_GC]
    except:
        RRigStruc_GC='na"'
        print(f, "erreur RRigStruc_GC")
    DicRes[DicTitreFile["Ratio_RigStruc_GC"][0]] = RRigStruc_GC

    # Calcul pression fiscale
    try:
        #print('Titre["ImpotTot_C"][0]', Titre["ImpotTot_C"][0],Titre["PotFisc_C"][0],len(DicC[f]),DicC[f][138],type(DicC[f][138]),DicC[f][139])
        ImpTot_C=float(DicC[f][Titre["ImpotTot_C"][0]])
        PotFisc_C=float(DicC[f][Titre["PotFisc_C"][0]])
        #print("Impot total C",ImpTot_C,)
        #DicC[f][Titre["MontImpTot_C"][0]] = ImpTot_C
        try:
            if PotFisc_C==0:
                RPFisc_C="na"
            else:
                RPFisc_C=ImpTot_C/PotFisc_C
        except:
            print("erreur division Pot Disc C",DicC[f][1],PotFisc_C)
        if Ind_GC_Taille in Dic_PFisc_C and RPFisc_C!="na":
            Dic_PFisc_C[Ind_GC_Taille].append(RPFisc_C)
        elif RPFisc_C!="na":
            Dic_PFisc_C[Ind_GC_Taille]=[RPFisc_C]
        else:
            Dic_PFisc_C[Ind_GC_Taille] = []
    except:
        RPFisc_C='na"'
        print(f,"erreur RPFisc_C")
    DicRes[DicTitreFile["Ratio_PFisc_C"][0]] = RPFisc_C

    try:
        if Indice_GC==0:
            RPFisc_GC="ns"
        else:
            ImpTot_GC = float(DicC[f][Titre["ImpotTot_GC"][0]])
            NumRPFisc_GC = ImpTot_C* RatioPop_C+ ImpTot_GC* RatioPop_GC
            #print("NumRPFisc_GC",NumRPFisc_GC,type(NumRPFisc_GC))
            DenRPFisc_GC = float(DicC[f][Titre["PotFisc_C"][0]]) * RatioPop_C + float(DicC[f][Titre["PotFisc_GC"][0]]) * RatioPop_GC
            #print("DenRPFisc_GC",DenRPFisc_GC,type(DenRPFisc_GC))
            if DenRPFisc_GC==0:
                RPFisc_GC="na"
            else:
                RPFisc_GC=NumRPFisc_GC/DenRPFisc_GC
        if Ind_GC_Taille in Dic_PFisc_GC and RPFisc_GC!="na":
            Dic_PFisc_GC[Ind_GC_Taille].append(RPFisc_GC)
        elif RPFisc_GC!="na":
            Dic_PFisc_GC[Ind_GC_Taille]=[RPFisc_GC]
        else:
            Dic_PFisc_GC[Ind_GC_Taille] = []

    except:
        RPFisc_GC='na"'
        print(f, "erreur RPFisc_GC")
    DicRes[DicTitreFile["Ratio_PFisc_GC"][0]] = RPFisc_GC

        # Calcul Sante
    try:
        if RAutof_C=="na" or REndet_C=="na" or RRigStruc_C=="na" or RPFisc_C=="na":
            RSante_C="na"
        else:
            RSante_C = RAutof_C+REndet_C+RRigStruc_C+RPFisc_C
        if Ind_GC_Taille in Dic_Sante_C and RSante_C!="na":
            Dic_Sante_C[Ind_GC_Taille].append(RSante_C)
        elif RSante_C!="na":
            Dic_Sante_C[Ind_GC_Taille]=[RSante_C]
        else:
            Dic_Sante_C[Ind_GC_Taille]=[]
    except:
        RSante_C = 'na"'
        print(f, "erreur RSante_C")
    DicRes[DicTitreFile["Ratio_Sante_C"][0]] = RSante_C

    try:
        if RAutof_GC=="na" or REndet_GC=="na" or RRigStruc_GC=="na" or RPFisc_GC=="na" :
            RSante_GC ="na"
        else:
            RSante_GC = RAutof_GC+REndet_GC+RRigStruc_GC+RPFisc_GC
        if Ind_GC_Taille in Dic_Sante_GC and RSante_GC!="na":
            Dic_Sante_GC[Ind_GC_Taille].append(RSante_GC)
        elif RSante_GC!="na":
            Dic_Sante_GC[Ind_GC_Taille]=[RSante_GC]
        else:
            Dic_Sante_GC[Ind_GC_Taille]=[]
    except:
        RSante_GC = 'na"'
        print(f, DicC[f][1],"erreur RSante_GC",RAutof_GC,REndet_GC,RRigStruc_GC,RPFisc_GC)
    DicRes[DicTitreFile["Ratio_Sante_GC"][0]] = RSante_GC

# Affichage du décompte des ratios

for Index in ListeIndicesegments:
    try:
        print(Index,"Depenses C",len(Dic_Dep_C[Index]),"Depenses GC",len(Dic_Dep_GC[Index]),"Sante C",len(Dic_Sante_C[Index]),"Sante GC",len(Dic_Sante_GC[Index]))
    except:
        print("erreur d'affichage du décompte des segments :",Index)

# Calcul des déciles 1,5 et 9 pour les différents inidcateurs C er GC

Decile_Dep_C = {}  # Cle = indice GC x taille C - Dépenses Fonc C
Decile_Dep_GC = {}  # Cle = indice GC x taille C - Dépenses Fonc C+GC

Decile_Sante_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Decile_Sante_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Decile_Autof_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Decile_Autof_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Decile_Endet_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Decile_Endet_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Decile_RigStruc_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Decile_RigStruc_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

Decile_PFisc_C = {}  # Cle = indice GC x taille C - Ratio de santé financière C
Decile_PFisc_GC = {}  # Cle = indice GC x taille C - Ratio de santé financière C+GC

for i in Dic_Dep_C:
    Indice_GC=int(i[0])
    print("segment",i,"Communes",len(Dic_Dep_C[i]),len(Dic_Sante_C[i]),len(Dic_Autof_C[i]),len(Dic_Endet_C[i]),len(Dic_RigStruc_C[i]),len(Dic_PFisc_C[i]))
    print("segment",i,"G Communes",len(Dic_Dep_GC[i]),len(Dic_Sante_GC[i]),len(Dic_Autof_GC[i]),len(Dic_Endet_GC[i]),len(Dic_RigStruc_GC[i]),len(Dic_PFisc_GC[i]))

    Liste=sorted(Dic_Dep_C[i])
    Decile_Dep_C[i]=[Liste[int(float(len(Liste))/10)],Liste[int(float(len(Liste))/2)],Liste[int(9*float(len(Liste))/10)]]

    Liste = sorted(Dic_Sante_C[i])
    Decile_Sante_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

    Liste=sorted(Dic_Autof_C[i])
    Decile_Autof_C[i]=[Liste[int(float(len(Liste))/10)],Liste[int(float(len(Liste))/2)],Liste[int(9*float(len(Liste))/10)]]

    Liste=sorted(Dic_Endet_C[i])
    Decile_Endet_C[i]=[Liste[int(float(len(Liste))/10)],Liste[int(float(len(Liste))/2)],Liste[int(9*float(len(Liste))/10)]]

    Liste = sorted(Dic_RigStruc_C[i])
    Decile_RigStruc_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

    Liste = sorted(Dic_PFisc_C[i])
    Decile_PFisc_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

    if Indice_GC==1:
        Liste = sorted(Dic_Dep_GC[i])
        Decile_Dep_GC[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

        Liste = sorted(Dic_Sante_GC[i])
        Decile_Sante_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

        Liste = sorted(Dic_Autof_GC[i])
        Decile_Autof_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

        Liste = sorted(Dic_Endet_GC[i])
        Decile_Endet_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

        Liste = sorted(Dic_RigStruc_GC[i])
        Decile_RigStruc_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]

        Liste = sorted(Dic_PFisc_GC[i])
        Decile_PFisc_C[i] = [Liste[int(float(len(Liste)) / 10)], Liste[int(float(len(Liste)) / 2)],Liste[int(9 * float(len(Liste)) / 10)]]
    else:
        Decile_Dep_GC[i] = ["ns","ns","ns"]
        Decile_Sante_C[i] = ["ns","ns","ns"]
        Decile_Autof_C[i] = ["ns","ns","ns"]
        Decile_Endet_C[i] = ["ns","ns","ns"]
        Decile_RigStruc_C[i] = ["ns","ns","ns"]
        Decile_PFisc_C[i] = ["ns","ns","ns"]

# Calcul des notes des C er GC

for f in DicRes:

    IndTaille_GC=DicRes[f][DicTitreFile["IndGC-SegTaille"][0]]

    Note_Dep_C=note(DicRes[f][DicTitreFile["Ratio_Dep_C"][0]],Decile_Dep_C[IndTaille_GC][0],Decile_Dep_C[IndTaille_GC][1],Decile_Dep_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Dep_C"][0]]=Note_Dep_C

    Note_Dep_GC=note(DicRes[f][DicTitreFile["Ratio_Dep_GC"][0]],Decile_Dep_GC[IndTaille_GC][0],Decile_Dep_GC[IndTaille_GC][1],Decile_Dep_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Dep_GC"][0]]=Note_Dep_GC


    Note_Autof_C = note(DicRes[f][DicTitreFile["Ratio_Autof_C"][0]], Decile_Autof_C[IndTaille_GC][0],Decile_Autof_C[IndTaille_GC][1], Decile_Autof_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Autof_C"][0]] = Note_Autof_C

    Note_Autof_GC = note(DicRes[f][DicTitreFile["Ratio_Autof_GC"][0]], Decile_Autof_GC[IndTaille_GC][0],Decile_Autof_GC[IndTaille_GC][1], Decile_Autof_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Autof_GC"][0]] = Note_Autof_GC


    Note_Endet_C = note(DicRes[f][DicTitreFile["Ratio_Endet_C"][0]], Decile_Endet_C[IndTaille_GC][0],Decile_Endet_C[IndTaille_GC][1], Decile_Endet_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Endet_C"][0]] = Note_Endet_C

    Note_Endet_GC = note(DicRes[f][DicTitreFile["Ratio_Endet_GC"][0]], Decile_Endet_GC[IndTaille_GC][0],Decile_Endet_GC[IndTaille_GC][1], Decile_Endet_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Endet_GC"][0]] = Note_Endet_GC


    Note_RigStruc_C = note(DicRes[f][DicTitreFile["Ratio_RigStruc_C"][0]], Decile_RigStruc_C[IndTaille_GC][0],Decile_RigStruc_C[IndTaille_GC][1], Decile_RigStruc_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_RigStruc_C"][0]] = Note_RigStruc_C

    Note_RigStruc_GC = note(DicRes[f][DicTitreFile["Ratio_RigStruc_GC"][0]], Decile_RigStruc_GC[IndTaille_GC][0],Decile_RigStruc_GC[IndTaille_GC][1], Decile_RigStruc_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_RigStruc_GC"][0]] = Note_RigStruc_GC


    Note_PFisc_C = note(DicRes[f][DicTitreFile["Ratio_PFisc_C"][0]], Decile_PFisc_C[IndTaille_GC][0],Decile_PFisc_C[IndTaille_GC][1], Decile_PFisc_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_PFisc_C"][0]] = Note_PFisc_C

    Note_PFisc_GC = note(DicRes[f][DicTitreFile["Ratio_PFisc_GC"][0]], Decile_PFisc_GC[IndTaille_GC][0],Decile_PFisc_GC[IndTaille_GC][1], Decile_PFisc_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_PFisc_GC"][0]] = Note_PFisc_GC


    Note_Sante_C = note(DicRes[f][DicTitreFile["Ratio_Sante_C"][0]], Decile_Sante_C[IndTaille_GC][0],Decile_Sante_C[IndTaille_GC][1], Decile_Sante_C[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Sante_C"][0]] = Note_Sante_C

    Note_Sante_GC = note(DicRes[f][DicTitreFile["Ratio_Sante_GC"][0]], Decile_Sante_GC[IndTaille_GC][0],Decile_Sante_GC[IndTaille_GC][1], Decile_Sante_GC[IndTaille_GC][2])
    DicRes[f][DicTitreFile["Note_Sante_GC"][0]] = Note_Sante_GC


# Calcul des codes pour atribution des commmentaires

for f in DicRes:
    IndTaille_GC = DicRes[f][DicTitreFile["IndGC-SegTaille"][0]]

    if DicRes[f][DicTitreFile["Note_Dep_C"][0]]<=10:
        Symb_C="0-"
    else:
        Symb_C = "1-"

    if DicRes[f][DicTitreFile["Note_Sante_C"][0]]<=10:
        Symb_GC=Symb_C+"0-"
    else:
        Symb_GC =Symb_C+"1-"

    if DicRes[f][DicTitreFile["Ratio_Autof_C"][0]]>=1:
        Symb_C=Symb_C+"A-"
    elif DicRes[f][DicTitreFile["Ratio_Autof_C"][0]]>=0.95:
        Symb_C =Symb_C+"P-"
    else:
        Symb_C =Symb_C+"O-"

    if DicRes[f][DicTitreFile["Ratio_Endet_C"][0]]>=1.21:
        Symb_C=Symb_C+"A-"
    elif DicRes[f][DicTitreFile["Ratio_Endet_C"][0]]>=1.1:
        Symb_C =Symb_C+"P-"
    else:
        Symb_C =Symb_C+"O-"

    if DicRes[f][DicTitreFile["Ratio_RigStruc_C"][0]]>=0.66:
        Symb_C=Symb_C+"A-"
    elif DicRes[f][DicTitreFile["Ratio_RigStruc_C"][0]]>=0.6:
        Symb_C =Symb_C+"P-"
    else:
        Symb_C =Symb_C+"O-"

    if DicRes[f][DicTitreFile["Ratio_PFisc_C"][0]]>=1:
        Symb_C=Symb_C+"A-"
    elif DicRes[f][DicTitreFile["Ratio_PFisc_C"][0]]>=0.9:
        Symb_C =Symb_C+"P-"
    else:
        Symb_C =Symb_C+"O-"




    if DicRes[f][DicTitreFile["Note_Dep_GC"][0]] <= 10:
        Symb_GC = "0-"
    else:
        Symb_GC = "1-"

    if DicRes[f][DicTitreFile["Note_Sante_GC"][0]] <= 10:
        Symb_GC = Symb_GC + "0-"
    else:
        Symb_GC = Symb_GC + "1-"

    if DicRes[f][DicTitreFile["Ratio_Autof_GC"][0]] >= 1:
        Symb_GC = Symb_GC + "A-"
    elif DicRes[f][DicTitreFile["Ratio_Autof_GC"][0]] >= 0.95:
        Symb_GC = Symb_GC + "P-"
    else:
        Symb_GC = Symb_GC + "O-"

    if DicRes[f][DicTitreFile["Ratio_Endet_GC"][0]] >= 1.21:
        Symb_GC = Symb_GC + "A-"
    elif DicRes[f][DicTitreFile["Ratio_Endet_GC"][0]] >= 1.1:
        Symb_GC = Symb_GC + "P-"
    else:
        Symb_GC = Symb_GC + "O-"

    if DicRes[f][DicTitreFile["Ratio_RigStruc_GC"][0]] >= 0.66:
        Symb_GC = Symb_GC + "A-"
    elif DicRes[f][DicTitreFile["Ratio_RigStruc_GC"][0]] >= 0.6:
        Symb_GC = Symb_GC + "P-"
    else:
        Symb_GC = Symb_GC + "O-"

    if DicRes[f][DicTitreFile["Ratio_PFisc_GC"][0]] >= 1:
        Symb_GC = Symb_GC + "A-"
    elif DicRes[f][DicTitreFile["Ratio_PFisc_GC"][0]] >= 0.9:
        Symb_GC = Symb_GC + "P-"
    else:
        Symb_GC = Symb_GC + "O-"