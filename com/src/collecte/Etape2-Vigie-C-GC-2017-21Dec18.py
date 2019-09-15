# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 06:06:36 2014

@author: CetaData-Lainee
"""

# code d'ajout des codes INSEE, des résidences secondaires, du calcul des segments post ajout des résidences secondaires, et de calcul des potentiels fiscaux des Communes avec leurs groupements

#from urllib.request import urlopen
import os
import csv
from bs4 import BeautifulSoup
#from lxml import html
#import requests
import sys
from datetime import date
#sys.setdefaultencoding('utf-8')

def cherche(a,b):
    s=0
    for x in range(len(b)):
        if (s==0 and b[x]==a):
            s=x
    if s==0:
        s=len(b)+1
    return s

def String(s,p):
    Res=str(p)
    if s<len(p):
        Res=p[len(p)-s:]
    elif s>len(p):
        for i in range(s-len(p)):
            Res="0"+Res
    return Res

# Fonction de calcul du segment de taille d'une commune
def Taille(s):
    s=int(s)
    #print("entree taille",s, type(s))
    if s<=250:
        T="1- <=250"
    elif s<=500:
        T="2- 250-500"
    elif s <= 2000:
        T = "3- 500-2000"
    elif s<=3500:
        T="4- 2000-3500"
    elif s<= 5000:
        T = "5- 3500-5000"
    elif s<= 10000:
        T= "6- 5000-10000"
    elif s<=20000:
        T="7- 10000-20000"
    elif s<=50000:
        T="8- 20000-50000"
    elif s<=100000:
        T="9- 50000-100000"
    else:
        T="10- >100000"
    #print("Taille=",s,T)
    return(T)


# Fonction d'écriture d'un enregistrement dans un fichier
def writeCom(writer, line):
    writer.writerow(line)

# Normalisation d'un nombre entier en chaîne de 3 caractères
def Norm3(var):
    if var<=9:
        Res='00'+str(var)
    elif var<=99:
        Res='0'+str(var)
    else:
        Res=str(min(var,999))
    return Res

# fonction de nettoyage des chaines scrapées par élimination de &nbsp
def clean1(str):
    cleanstr=str[:str.find('&nbsp')]
    return cleanstr    

# Ouverture des fichiers csv d'écriture des enregistrements complétés

Annee='2017'
Today=str(date.today())

Chemin='/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Argus_'+Annee+'/ScraperResults-Round6/'
#print(Chemin)
os.chdir(Chemin)

CheminR=Chemin+'/Resultats/Etape2-Total'
os.chdir(CheminR)
FichierDest1=open("Etape-2-Vigie-"+Annee+"-"+Today+".csv", "w")
FileVigie=csv.writer(FichierDest1)

FichierDest2=open("Etape-2-Vigie-NOK-"+Annee+"-"+Today+".csv", "w")
FileVigiedef=csv.writer(FichierDest2)

FichierDest4=open("FileOutTest INSEE.csv", "w")
FileOutTest=csv.writer(FichierDest4)
writeCom(FileOutTest,["Cle","INSEE"])

FichierDest5=open("File_Taux_Impots_CetGC.csv", "w")
FileOutTaux=csv.writer(FichierDest5)
writeCom(FileOutTaux,["Ind_GC-SegTaille-C","Taux_TH_C","Taux_TF_C","Taux_TFNB_C","Taux_TFAdd_C","Taux_TH_GC","Taux_TF_GC","Taux_TFNB_GC","Taux_TFAdd_GC"])



# Accès aux fichiers csv d'entrée  : donnnées financières des communes. des codes INSEE et des résidences secondaires

CheminDataSupport='/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Data support'
os.chdir(CheminDataSupport)

NomFileResSec="base-cc-logement-2014.csv"
file2 = open(NomFileResSec, "rU")
FileResSec = csv.reader(file2)

NomFileINSEE="Match_Communes-pour_INSEE-2018-12-17-Final.csv"
file1 = open(NomFileINSEE, "rU")
FileINSEE = csv.reader(file1)


CheminR='/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Argus_2017/ScraperResults-Round6/Resultats/Etape1-Total'
os.chdir(CheminR)

NomIn = "Etape-1-Vigie-2017- totalFin.csv"
FichierIn = open(NomIn, "r")
FileIn = csv.reader(FichierIn)


# Création du dictionnaire DicNomVar des noms de variables C et du dictionnaire DicC des données des communes

count=0
DicNomVar={}    # Dictionnaire des noms de colonnes dans le fichier de 1ère étape
DicC={}         # Dictionnaire des données des communes

NMin=1
NMax=37000
Titre=[]

for f in FileIn:
    #f=f[0].split(";")
    if count==0:
        count = count + 1
        for i in range(len(f)):
            DicNomVar[str(f[i])]=[i,str(f[i])]
            Titre.append(str(f[i]))
        Titre.append("PotFisc_C")
        DicNomVar["PotFisc_C"] = [len(f), "PotFisc_C"]
        Titre.append("ImpotTot_C")
        DicNomVar["ImpotTot_C"] = [len(f)+1, "MontImpTot_C"]
        Titre.append("PotFisc_GC")
        DicNomVar["PotFisc_GC"] = [len(f)+2, "PotFisc_GC"]
        Titre.append("ImpotTot_GC")
        DicNomVar["ImpotTot_GC"] = [len(f)+3, "MontImpTot_GC"]

        #for i in DicNomVar:
        #    print(i,DicNomVar[i])

        writeCom(FileVigie, Titre)
    elif (count >= NMin and count <= NMax):
        if len(f)==1:
            print(f)
        f.append("na")
        f.append("na")
        f.append("na")
        f.append("na")
        Indice = f[0]
        DicC[Indice] = f
    count=count+1
    if count<=2:
        print(f)

print("Nombre de communes :", len(DicC))
print("Nombre de variables par commune :", len(DicNomVar))
for var in DicNomVar:
    print(var, DicNomVar[var])


# Creation du dictionnaire des codes INSEE.

print()
print("Debut de creation dictionnaire codes INSEE")
DicINSEE={}       # Cle = num département - nom commune, contenu : code INSEE
count=0

for f in FileINSEE:
    if count==0:
        pass
    else :
        f=f[0].split(";")
        try:
            Nom_C_Vigie = str(f[2])
        except:
            #print(count,f)
            pass
        NumDep=str(f[6])
        CodeINSEE=str(f[7])
        Cle = NumDep + "-" + Nom_C_Vigie
        try:
            DicINSEE[Cle] = str(CodeINSEE)
            if count<=100:
                print(count,"recherche codes INSEE",Cle,DicINSEE[Cle])
            writeCom(FileOutTest,[Cle,CodeINSEE])
        except:
            print("erreur fichier INSEE",NumDep,Npm_C_Vigie,CodeINSEE, Cle)
    count=count+1

print("Fin de creation dictionnaire codes INSEE",len(DicINSEE)," entrees")
print()


# Creation du dictionnaire DicResSecC des résidences secondaires par commune

DicResSecC={}       # Clé : code INSEE, contenu : nombre de résidences secondaires 2014
count=0

print()
print("Debut de creation dictionnaire des residences secondaires")

for f in FileResSec:
    if count==0:
        count=count+1
    else:
        f=f[0].split(";")
        try:
            if count<=100:
                print(count,"recherche res secondaires",str(f[1]),int(f[7]))
            DicResSecC[str(f[1])]=int(f[7])
        except:
            DicResSecC[str(f[1])] = 0
        count=count+1

print("Fin de creation dictionnaire des residences secondaires", len(DicResSecC)," entrees")
print()


# Creation du dictionnaire DicResSecGC des résidences secondaires par groupement de communes

DicResSecGC={}       # Clé : code INSEE, contenu : nombre de résidences secondaires 2014
count=0
countNoINSEE=0

for f in DicC:
    #print("indice",f,"Dicc",DicC[f])
    NomC = DicC[f][DicNomVar["NomC portail"][0]]
    NumDep = str(DicC[f][DicNomVar["NumDep_C"][0]])
    if count<=100:
        print("NomC",NomC,"NumDep",NumDep)
    try:
        if NumDep=="2A" or NumDep=="2B":
            pass
        elif int(NumDep)>=100:
            NumDep="97"
    except:
        #print("erreur en lecture de DicC",NomC,NumDep)
        pass
    Cle=NumDep+"-"+NomC
    try:
        CodeINSEE=DicINSEE[Cle]
    except:
        if count<=100:
            print("cle Dic non dispo dans DicINSEE",Cle)
        pass
    NomGC = DicC[f][DicNomVar["NomGC portail"][0]]
    try:
        if NomGC in DicResSecGC:
            DicResSecGC[NomGC] = DicResSecGC[NomGC] + DicResSecC[CodeINSEE]
        else:
            DicResSecGC[NomGC] = DicResSecC[CodeINSEE]
    except :
        countNoINSEE = countNoINSEE+1
        if NMin-1<=countNoINSEE and countNoINSEE<=NMax:
            IndResSecC="NOK"
            if Cle in DicINSEE:
                IndINSEE="OK"
                if DicINSEE[Cle] in DicResSecC:
                    IndResSecC="OK"
            else:
                IndINSEE = "NOK"
            #print("Absence de code INSEE",countNoINSEE,NumDep, NomC,"ind Cle",IndINSEE,"Ind ResSecC:",IndResSecC)
            #if IndINSEE=="NOK":
            #    print("Absence de code INSEE", countNoINSEE, NumDep, NomC, "ind Cle", IndINSEE)

for NomGC in DicResSecGC:
    #print("Check Res Sec GC",NomGC, DicResSecGC[NomGC])
    pass
# Boucle sur les communes pour insérer les codes INSEE, populations et résidences secondairees C et GC

count=0
CountFail=0
PopFail=0
CountFailGC=0
NMin=1
NMax=37000

print()
print('Debut de boucle')

for f in DicC:
    #print(f)

    if (count>=NMin-1 and count<=NMax):
#    if (count>=NMin):
        NomC=DicC[f][DicNomVar["NomC portail"][0]]
        NumDep=DicC[f][6]
        #print("NumDep:",NumDep)
        if NumDep=="2A" or NumDep=="2B":
            pass
        elif int(NumDep)>=100:
            NumDep=97
        else:
            NumDep=int(NumDep)
        cle=str(NumDep)+"-"+NomC

        if str(DicC[f][2])=="N/D":
            IndGC=0
        else:
            IndGC=1
    
        try:
            DicC[f][DicNomVar["CodeGeo"][0]] = DicINSEE[cle]
        except:
            DicC[f][DicNomVar["CodeGeo"][0]] ="na"
            print("Code INSEE non disponible en lecture du fichier Vigie dans le fichier matchcommunes",NomC,NumDep)
        try:
            DicC[f][DicNomVar["ResSec_C"][0]]=int(DicResSecC[DicINSEE[cle]])
            #print("Res Sec commune",DicC[f][DicNomVar["NomC portail"][0]],DicC[f][DicNomVar["ResSec_C"][0]],"OK1")
            DicC[f][DicNomVar["PopTot_C"][0]] = int(DicC[f][DicNomVar["Pop_C"][0]])+DicC[f][DicNomVar["ResSec_C"][0]]
            #print("Res Sec C",DicC[f][DicNomVar["ResSec_C"][0]],"Pop Tot commune", DicC[f][DicNomVar["PopTot_C"][0]],type(DicC[f][DicNomVar["PopTot_C"][0]]), "OK2")
            DicC[f][DicNomVar["SegTaille_C"][0]]=Taille(DicC[f][DicNomVar["PopTot_C"][0]])
            #print("Taille commune", DicC[f][DicNomVar["SegTaille_C"][0]], "OK3")
            DicC[f][DicNomVar["Ind_GC-SegTaille_C"][0]] =str(IndGC)+"-"+str(DicC[f][DicNomVar["SegTaille_C"][0]])
            #print("Res Sec commune", DicC[f][DicNomVar["SegTaille_C"][0]], "OK4")
            #print(count,"Res Sec",DicC[f][1],DicC[f][9],DicC[f][10])
        except:
            DicC[f][DicNomVar["ResSec_C"][0]] = "na"
            DicC[f][DicNomVar["PopTot_C"][0]] = DicC[f][DicNomVar["Pop_C"][0]]
            CountFail = CountFail + 1
            PopFail = PopFail +int(DicC[f][DicNomVar["Pop_C"][0]])
            #print("Commune sans donnes de residences secondaires : ",NomC,NumDep,"INSEE : ",DicINSEE[cle],type(DicINSEE[cle]),DicC[f][DicNomVar["Pop_C"][0]],"habitants")

        NomGC = DicC[f][DicNomVar["NomGC portail"][0]]
        try:
            DicC[f][DicNomVar["ResSec_GC"][0]] = DicResSecGC[NomGC]
            DicC[f][DicNomVar["PopTot_GC"][0]] = int(DicC[f][DicNomVar["Pop_GC"][0]]) + int(DicResSecGC[NomGC])
            #print("OK Res Sec GC")
        except:
            DicC[f][DicNomVar["ResSec_GC"][0]] = "na"
            DicC[f][DicNomVar["PopTot_GC"][0]] = DicC[f][DicNomVar["Pop_GC"][0]]
            if CountFailGC<=100:
                CountFailGC = CountFailGC + 1

                #print(CountFailGC, "echec resSecGC", cle)

        #print('Noms',FileNameC,FileNameGC)

    count=count+1

print(CountFail, "communes sans donnees de residences secondaires sur",count," communes avec",PopFail," habitants")


# Boucle sur les communes pour calculer les potentiels fiscaux

print()
print("Boucle sur les communes pour calculer les potentiels fiscaux")

count=0
DicTH_C={} #Dictionnaire Base, montant, taux de la taxe d'habitation C par classe de sit GC - taille C
DicTF_C={}
DicTFNB_C={}
DicTFAdd_C={}
DicTH_GC={}    #Dictionnaire Base, montant, taux de la taxe d'habitation GC par classe de sit GC - taille C
DicTF_GC={}
DicTFNB_GC={}
DicTFAdd_GC={}
CountErreur=0

for f in DicC:
    #print(f)

    try:
        Ind_GC_Taille=DicC[f][13]
        #print(Ind_GC_Taille,type(Ind_GC_Taille))
        Ind_GC=int(Ind_GC_Taille[0])
        #print(Ind_GC_Taille,Ind_GC)
    except:
        print("erreur cles")
    try:
        Base_TH_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTH_C"][0]])
        Base_TF_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTFPB_C"][0]])
        Base_TFNB_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTFPNB_C"][0]])
        Base_TFAdd_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTAPNB_C"][0]])
        #Base_TFAdd_C=int(DicC[f][8])*int(DicC[f][40])
        #Base_TF_C=int(DicC[f][8])*int(DicC[f][43])
        Mont_TH_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTHp_C"][0]])
        Mont_TF_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTFPB_C"][0]])
        Mont_TFNB_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTFPNB_C"][0]])
        Mont_TFAdd_C=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTAPNB_C"][0]])

        #print(Ind_GC_Taille,Ind_GC,"OK, calcul bases et montants C",DicC[f][8],DicC[f][40],DicC[f][45])
        #print(int(DicC[f][8]),int(DicC[f][117]),int(DicC[f][118]),int(DicC[f][119]),int(DicC[f][120]))
        if Ind_GC==0:
            Base_TH_GC = 0
            Base_TF_GC = 0
            Base_TFNB_GC = 0
            Base_TFAdd_GC = 0
            Mont_TH_GC = 0
            Mont_TF_GC = 0
            Mont_TFNB_GC = 0
            Mont_TFAdd_GC = 0
        else:
            try:
                Base_TH_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTHph"][0]])
            except:
                Base_TH_GC =0
            try:
                Base_TF_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTFPBph"][0]])
            except:
                Base_TF_GC =0
            try:
                Base_TFNB_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTFPNBph"][0]])
            except:
                Base_TFNB_GC =0
            try:
                Base_TFAdd_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["BaseTAPNBph"][0]])
            except:
                Base_TFAdd_GC =0
            try:
                Mont_TH_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTHph"][0]])
            except:
                Mont_TH_GC =0
            try:
                Mont_TF_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTFPBph"][0]])
            except:
                Mont_TF_GC =0
            try:
                Mont_TFNB_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTFPNBph"][0]])
            except:
                Mont_TFNB_GC =0
            try:
                Mont_TFAdd_GC=int(DicC[f][DicNomVar["Pop_C"][0]])*int(DicC[f][DicNomVar["MontTAPNBph"][0]])
            except:
                Mont_TFAdd_GC =0

        # print("OK, calcul bases et montants GC", DicC[f][8],DicC[f][120],DicC[f][128])

        if Ind_GC_Taille in DicTH_C:
            OK=0
            DicTH_C[Ind_GC_Taille]=[DicTH_C[Ind_GC_Taille][0]+Base_TH_C,DicTH_C[Ind_GC_Taille][1]+Mont_TH_C,'']
            OK=1
            DicTF_C[Ind_GC_Taille] = [DicTF_C[Ind_GC_Taille][0] + Base_TF_C, DicTF_C[Ind_GC_Taille][1] + Mont_TF_C, '']
            OK=2
            DicTFNB_C[Ind_GC_Taille] = [DicTFNB_C[Ind_GC_Taille][0] + Base_TFNB_C, DicTFNB_C[Ind_GC_Taille][1] + Mont_TFNB_C, '']
            OK=3
            DicTFAdd_C[Ind_GC_Taille] = [DicTFAdd_C[Ind_GC_Taille][0] + Base_TFAdd_C, DicTFAdd_C[Ind_GC_Taille][1] + Mont_TFAdd_C, '']
            OK=4
            DicTH_GC[Ind_GC_Taille]=[DicTH_GC[Ind_GC_Taille][0]+Base_TH_GC,DicTH_C[Ind_GC_Taille][1]+Mont_TH_GC,'']
            OK=5
            DicTF_GC[Ind_GC_Taille] = [DicTF_GC[Ind_GC_Taille][0] + Base_TF_GC, DicTF_GC[Ind_GC_Taille][1] + Mont_TF_GC, '']
            OK=6
            DicTFNB_GC[Ind_GC_Taille] = [DicTFNB_GC[Ind_GC_Taille][0] + Base_TFNB_GC, DicTFNB_GC[Ind_GC_Taille][1] + Mont_TFNB_GC, '']
            OK=7
            DicTFAdd_GC[Ind_GC_Taille] = [DicTFAdd_GC[Ind_GC_Taille][0] + Base_TFAdd_GC, DicTFAdd_GC[Ind_GC_Taille][1] + Mont_TFAdd_GC, '']
        else:
            OK="na"
            DicTH_C[Ind_GC_Taille]=[Base_TH_C,Mont_TH_C,'']
            DicTF_C[Ind_GC_Taille] = [Base_TF_C, Mont_TF_C, '']
            DicTFNB_C[Ind_GC_Taille] = [Base_TFNB_C, Mont_TFNB_C, '']
            DicTFAdd_C[Ind_GC_Taille] = [Base_TFAdd_C, Mont_TFAdd_C, '']

            DicTH_GC[Ind_GC_Taille]=[Base_TH_GC,Mont_TH_GC,'']
            DicTF_GC[Ind_GC_Taille] = [Base_TF_GC, Mont_TF_GC, '']
            DicTFNB_GC[Ind_GC_Taille] = [Base_TFNB_GC, Mont_TFNB_GC, '']
            DicTFAdd_GC[Ind_GC_Taille] = [Base_TFAdd_GC, Mont_TFAdd_GC, '']
    except:
        CountErreur = CountErreur+1
        print(OK, CountErreur,"erreur(s) calcul dicos TH, TF...",f,int(DicC[f][8]),Base_TFAdd_GC,Mont_TFAdd_GC)
        print("Erreur, calcul bases et montants GC", DicC[f][8],DicC[f][1], DicC[f][120], DicC[f][128])

print()
print("Calcul des taux moyens par segment par impot")

for ind in DicTH_C:
    try:
        DicTH_C[ind][2]=round(DicTH_C[ind][1]/DicTH_C[ind][0],3)
    except:
        DicTH_C[ind][2]=0
    try:
        DicTF_C[ind][2]=round(DicTF_C[ind][1]/DicTF_C[ind][0],3)
    except:
        DicTF_C[ind][2]=0
    try:
        DicTFNB_C[ind][2]=round(DicTFNB_C[ind][1]/DicTFNB_C[ind][0],3)
    except:
        DicTFNB_C[ind][2]=0
    try:
        DicTFAdd_C[ind][2]=round(DicTFAdd_C[ind][1]/DicTFAdd_C[ind][0],3)
    except:
        DicTFAdd_C[ind][2]=0

    try:
        DicTH_GC[ind][2]=round(DicTH_GC[ind][1]/DicTH_GC[ind][0],3)
    except:
        DicTH_GC[ind][2]=0
    try:
        DicTF_GC[ind][2]=round(DicTF_GC[ind][1]/DicTF_GC[ind][0],3)
    except:
        DicTF_GC[ind][2]=0
    try:
        DicTFNB_GC[ind][2]=round(DicTFNB_GC[ind][1]/DicTFNB_GC[ind][0],3)
    except:
        DicTFNB_GC[ind][2]=0
    try:
        DicTFAdd_GC[ind][2]=round(DicTFAdd_GC[ind][1]/DicTFAdd_GC[ind][0],3)
    except:
        DicTFAdd_GC[ind][2]=0

    Res=[ind,DicTH_C[ind][2],DicTF_C[ind][2],DicTFNB_C[ind][2],DicTFAdd_C[ind][2],DicTH_GC[ind][2],DicTF_GC[ind][2],DicTFNB_GC[ind][2],DicTFAdd_GC[ind][2]]
    writeCom(FileOutTaux,Res)

print("Debut d'impression des taux moyens par segment")
print()

for ind in DicTH_C:
    print(ind,DicTH_C[ind],DicTF_C[ind],DicTFNB_C[ind],DicTFAdd_C[ind])

for ind in DicTH_GC:
    print(ind, DicTH_GC[ind], DicTF_GC[ind], DicTFNB_GC[ind], DicTFAdd_GC[ind])


print("Fin d'impression des taux moyens par segment")
print()


    # Calcul des potentiels fiscaux par commune

print("Calcul des potentiels fiscaux")

count=0
countfail=0

for f in DicC:
    count=count+1
    if (count>=NMin-1 and count<=NMax):

        Ind_GC_Taille=DicC[f][DicNomVar["Ind_GC-SegTaille_C"][0]]
        Ind_GC=int(Ind_GC_Taille[0]) # 1 ou 0 suivant que la commune est ou non dans un groupement de communes

        #print(count, Ind_GC_Taille,DicC[f][5],DicC[f][40],DicTH_C[Ind_GC_Taille][2], DicC[f][118],DicTH_GC[Ind_GC_Taille][2])

        PotFisc_C=round(float(DicC[f][DicNomVar["BaseTH_C"][0]])*DicTH_C[Ind_GC_Taille][2]+float(DicC[f][DicNomVar["BaseTFPB_C"][0]])*DicTF_C[Ind_GC_Taille][2]+float(DicC[f][DicNomVar["BaseTFPNB_C"][0]])*DicTFNB_C[Ind_GC_Taille][2]+float(DicC[f][DicNomVar["BaseTAPNB_C"][0]])*DicTFAdd_C[Ind_GC_Taille][2],1)
        Impot_C=float(DicC[f][DicNomVar["MontTHp_C"][0]])+float(DicC[f][DicNomVar["MontTFPB_C"][0]])+float(DicC[f][DicNomVar["MontTFPNB_C"][0]])+float(DicC[f][DicNomVar["MontTAPNB_C"][0]])

        # Remise à blanc des indicateurs de calcul des potentiels fiscaux

        a="na"
        a1="na"
        a2="na"
        b="na"
        b1="na"
        b2="na"
        c="na"
        c1="na"
        c2="na"
        d="na"
        d1="na"
        d2="na"
        try:
            if DicC[f][DicNomVar["BaseTHph"][0]]=="":
                a=0
                a1=0
                a2=0
            else:
                a=DicC[f][DicNomVar["BaseTHph"][0]]
                a1=DicTH_GC[Ind_GC_Taille][2]
                a2=DicC[f][DicNomVar["MontTHph"][0]]
            if DicC[f][DicNomVar["BaseTFPBph"][0]]=="":
                b=0
                b1=0
                b2=0
            else:
                b=DicC[f][DicNomVar["BaseTFPBph"][0]]
                b1=DicTF_GC[Ind_GC_Taille][2]
                b2=DicC[f][DicNomVar["MontTFPBph"][0]]
            if DicC[f][DicNomVar["BaseTFPNBph"][0]]=="":
                c=0
                c1=0
                c2=0
            else:
                c=DicC[f][DicNomVar["BaseTFPNBph"][0]]
                c1=DicTFNB_GC[Ind_GC_Taille][2]
                c2=DicC[f][DicNomVar["MontTFPNBph"][0]]
            if DicC[f][DicNomVar["BaseTAPNBph"][0]]=="":
                d=0
                d1=0
                d2=0
            else:
                d=DicC[f][DicNomVar["BaseTAPNBph"][0]]
                d1=DicTFAdd_GC[Ind_GC_Taille][2]
                d2=DicC[f][DicNomVar["MontTAPNBph"][0]]
            PotFisc_GC=round(float(a)*float(a1)+float(b)*float(b1)+float(c)*float(c1)+float(d)*float(d1),1)
            Impot_GC = float(a2) + float(b2) + float(c2) + float(d2)
            #if count <= 100:
            #    print("success",count,DicC[f][1],a,a1,a2,b,b1,b2,c,1,c2,d,d1,d2)
        except:
            #print("erreur PotFisc_GC")
            PotFisc_GC =0
            countfail=countfail+1
            if countfail <= 100:
                print("fail 1",countfail,count,DicC[f][1],DicC[f][2],Ind_GC_Taille,"*",a,a1,a2,"*",b,b1,b2,"*",c,c1,c2,"*",d,d1,d2)
                print("fail 2",DicC[f])

        DicC[f][DicNomVar["PotFisc_C"][0]]=PotFisc_C
        DicC[f][DicNomVar["ImpotTot_C"][0]] = Impot_C
        DicC[f][DicNomVar["PotFisc_GC"][0]]=PotFisc_GC
        DicC[f][DicNomVar["ImpotTot_GC"][0]] = Impot_GC


# Enregistrement des résultats

os.chdir(CheminR)
for f in DicC:
    #print(DicC[f])
    writeCom(FileVigie,DicC[f])

    # Calcul des indicateurs de dépense et santé par commune
print("Calcul des indicateurs de dépense et santé par commune - a faire")

FichierDest1.close()
FichierDest2.close()

  
