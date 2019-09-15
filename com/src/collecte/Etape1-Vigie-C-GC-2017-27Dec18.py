# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 06:06:36 2014

@author: CetaData-Lainee
"""

# code d'extraction des données financières des communes et groupements communes depuis les fichiers html extraits par le scraper Javascript du portail des collectivités locales
# Premier calcul des segments de taille sur la base de la population permanente (correction par les populations totales en étape 2)

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

# Fonction de calcul du segment de taille d'une commune
def Taille(s):

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

# Fonction de validation de données a priori complètes de la commmune

def CheckDataC(Liste):
    Val=1
    try:
        for data in Liste:
            if data=="":
                Val=0
    except:
        Val=0
    return(Val)

# Fonction d'écriture d'un enregistrement dans un fichier
def writeCom(writer, line):
    writer.writerow(line)


# fonction de capture des données d'une commune à partir de la page web scrapée

def captureC(dom,NDep,NCom,Ind,IndiceGC):

    Tabid = ['Nom Com portail','Num Com', 'NumDep', 'NomDep', 'Pop_C', 'ResSec_C','PopTot_C','Taille_C','SegTaille_C','Ind_GC-SegTaille_C']

    NomCom = dom.find('span', attrs={"id": "gfp"}).contents[0].strip(u'\xe0').replace(u'\xa0','').replace(","," ")
    NomDep = dom.find('span', attrs={"id": "departement"}).contents[0].strip(u'\xe0').replace(u'\xa0',' ').replace("-", "")
    PopCom = dom.find('td', attrs={"id": "population"}).contents[0].strip(u'\xe0').replace(u'\xa0',' ').replace("Population légale en vigueur au 1er janvier de l'exercice : ", "").replace(" habitants - Budget principal seul", "").replace(' ','')
    TailleCom = dom.find('td', attrs={"id": "lieu"}).contents[0].strip(u'\xe0').replace(u'\xa0',' ').replace("Strate : ", "")

    #print("IndiceGC",str(IndiceGC),type(IndiceGC),type(str(IndiceGC)))

    # GroupeCom=dom.find_all('th',attrs={"style":"Font-size:8pt;"})[3].contents[2].replace(u'\xe0','a').replace(u'\xe9','e')
    # GroupeCom=GroupeCom[:GroupeCom.find(')')+1]
    Tabid[0] = NomCom
    Tabid[1] = NCom
    Tabid[2] = NDep
    Tabid[3] = NomDep
    Tabid[4] = int(PopCom)
    Tabid[7] = TailleCom
    Tabid[8] = Taille(int(PopCom))
    Tabid[9]=str(IndiceGC)+"-"+Tabid[8]

    #       Capture des données de revenus de fonctionnement
    #print(dom.find_all('td', attrs={"class": "montantpetit"}))
    RevFoncph = dom.find_all('td', attrs={"class": "montantpetit"})[1].contents[0].replace(' ', '').replace(u'\xa0','')
    RevFoncphref = dom.find_all('td', attrs={"class": "montantpetit"})[2].contents[0].replace(u'\xa0','').replace(' ', '')
    RevFoncCAFph = dom.find_all('td', attrs={"class": "montantpetit"})[4].contents[0].replace(' ', '').replace(u'\xa0','')
    RevFoncCAFphref = dom.find_all('td', attrs={"class": "montantpetit"})[5].contents[0].replace(u'\xa0','').replace(' ', '')
    ImpLocph = dom.find_all('td', attrs={"class": "montantpetit"})[19].contents[0].replace(u'\xa0','').replace(' ', '')
    ImpLocphref = dom.find_all('td', attrs={"class": "montantpetit"})[10].contents[0].replace(u'\xa0','').replace(' ', '')
    AutImpph = dom.find_all('td', attrs={"class": "montantpetit"})[14].contents[0].replace(u'\xa0','').replace(' ', '')
    AutImpphref = dom.find_all('td', attrs={"class": "montantpetit"})[15].contents[0].replace(u'\xa0','').replace(' ', '')
    DGFph = dom.find_all('td', attrs={"class": "montantpetit"})[19].contents[0].replace(u'\xa0','').replace(' ', '')
    DGFphref = dom.find_all('td', attrs={"class": "montantpetit"})[20].contents[0].replace(u'\xa0','').replace(' ', '')
    TabRevFonc = [RevFoncph, RevFoncCAFph,ImpLocph, AutImpph, DGFph]
    TabRevFoncref = [RevFoncphref, RevFoncCAFphref, ImpLocphref, AutImpphref, DGFphref]
    #print('Rev commune : ',TabRevFonc,'Rev ref : ',TabRevFoncref)

    #           Capture des données de dépenses de fonctionnement
    DepFoncph = dom.find_all('td', attrs={"class": "montantpetit"})[24].contents[0].replace(u'\xa0','').replace(' ', '')
    DepFoncphref = dom.find_all('td', attrs={"class": "montantpetit"})[25].contents[0].replace(u'\xa0','').replace(' ', '')
    DepFoncCAFph = dom.find_all('td', attrs={"class": "montantpetit"})[27].contents[0].replace(u'\xa0','').replace(' ', '')
    DepFoncCAFphref = dom.find_all('td', attrs={"class": "montantpetit"})[28].contents[0].replace(u'\xa0','').replace(' ', '')
    DepPersoph = dom.find_all('td', attrs={"class": "montantpetit"})[32].contents[0].replace(u'\xa0','').replace(' ', '')
    DepPersophref = dom.find_all('td', attrs={"class": "montantpetit"})[33].contents[0].replace(u'\xa0','').replace(' ', '')
    Achatph = dom.find_all('td', attrs={"class": "montantpetit"})[37].contents[0].replace(u'\xa0','').replace(' ', '')
    Achatphref = dom.find_all('td', attrs={"class": "montantpetit"})[38].contents[0].replace(u'\xa0','').replace(' ', '')
    ChFinph = dom.find_all('td', attrs={"class": "montantpetit"})[42].contents[0].replace(u'\xa0','').replace(' ', '')
    ChFinphref = dom.find_all('td', attrs={"class": "montantpetit"})[43].contents[0].replace(u'\xa0','').replace(' ', '')
    Contph = dom.find_all('td', attrs={"class": "montantpetit"})[47].contents[0].replace(u'\xa0','').replace(' ', '')
    Contphref = dom.find_all('td', attrs={"class": "montantpetit"})[48].contents[0].replace(u'\xa0','').replace(' ', '')
    DepSubph = dom.find_all('td', attrs={"class": "montantpetit"})[52].contents[0].replace(u'\xa0','').replace(' ', '')
    DepSubphref = dom.find_all('td', attrs={"class": "montantpetit"})[53].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDepFonc = [DepFoncph, DepFoncCAFph, DepPersoph, Achatph, ChFinph, Contph, DepSubph]
    TabDepFoncref = [DepFoncphref, DepFoncCAFphref, DepPersophref, Achatphref, ChFinphref, Contphref, DepSubphref]
    #print('DepFonc commune : ',TabDepFonc,'DepFonc ref : ',TabDepFoncref)

    #           Capture des données de revenus d'investissement
    RevInvph = dom.find_all('td', attrs={"class": "montantpetit"})[61].contents[0].replace(u'\xa0','').replace(' ', '')
    RevInvphref = dom.find_all('td', attrs={"class": "montantpetit"})[62].contents[0].replace(u'\xa0','').replace(' ', '')
    Empruntph = dom.find_all('td', attrs={"class": "montantpetit"})[64].contents[0].replace(u'\xa0','').replace(' ', '')
    Empruntphref = dom.find_all('td', attrs={"class": "montantpetit"})[65].contents[0].replace(u'\xa0','').replace(' ', '')
    Subrph = dom.find_all('td', attrs={"class": "montantpetit"})[69].contents[0].replace(u'\xa0','').replace(' ', '')
    Subrphref = dom.find_all('td', attrs={"class": "montantpetit"})[70].contents[0].replace(u'\xa0','').replace(' ', '')
    FCTVAph = dom.find_all('td', attrs={"class": "montantpetit"})[74].contents[0].replace(u'\xa0','').replace(' ', '')
    FCTVAphref = dom.find_all('td', attrs={"class": "montantpetit"})[75].contents[0].replace(u'\xa0','').replace(' ', '')
    Retourbiensph = dom.find_all('td', attrs={"class": "montantpetit"})[79].contents[0].replace(u'\xa0','').replace(' ', '')
    Retourbiensphref = dom.find_all('td', attrs={"class": "montantpetit"})[80].contents[0].replace(u'\xa0','').replace(' ',
                                                                                                                  '')
    TabRevInv = [RevInvph, Empruntph, Subrph, FCTVAph, Retourbiensph]
    TabRevInvref = [RevInvphref, Empruntphref, Subrphref, FCTVAphref, Retourbiensphref]
    #print('RevInv commune : ',TabRevInv,'RevInv ref : ',TabRevInvref)

    #           Capture des données de dépenses d'investissement
    DepInvph = dom.find_all('td', attrs={"class": "montantpetit"})[84].contents[0].replace(u'\xa0','').replace(' ', '')
    DepInvphref = dom.find_all('td', attrs={"class": "montantpetit"})[85].contents[0].replace(u'\xa0','').replace(' ', '')
    DepEquipph = dom.find_all('td', attrs={"class": "montantpetit"})[87].contents[0].replace(u'\xa0','').replace(' ', '')
    DepEquipphref = dom.find_all('td', attrs={"class": "montantpetit"})[88].contents[0].replace(u'\xa0','').replace(' ', '')
    RembEmpruntph = dom.find_all('td', attrs={"class": "montantpetit"})[92].contents[0].replace(u'\xa0','').replace(' ', '')
    RembEmpruntphref = dom.find_all('td', attrs={"class": "montantpetit"})[93].contents[0].replace(u'\xa0','').replace(' ', '')
    ChRepph = dom.find_all('td', attrs={"class": "montantpetit"})[97].contents[0].replace(u'\xa0','').replace(' ', '')
    ChRepphref = dom.find_all('td', attrs={"class": "montantpetit"})[98].contents[0].replace(u'\xa0','').replace(' ', '')
    Immoph = dom.find_all('td', attrs={"class": "montantpetit"})[102].contents[0].replace(u'\xa0','').replace(' ', '')
    Immophref = dom.find_all('td', attrs={"class": "montantpetit"})[103].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDepInv = [DepInvph, DepEquipph, RembEmpruntph, ChRepph, Immoph]
    TabDepInvref = [DepInvphref, DepEquipphref, RembEmpruntphref, ChRepphref, Immophref]
    #print('DepInv commune : ', TabDepInv, 'DepInv ref : ', TabDepInvref)

    #           Capture des données d'endettement
    EncoursDetteTotph = dom.find_all('td', attrs={"class": "montantpetit"})[134].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteTotphref = dom.find_all('td', attrs={"class": "montantpetit"})[135].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteBankph = dom.find_all('td', attrs={"class": "montantpetit"})[139].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteBankphref = dom.find_all('td', attrs={"class": "montantpetit"})[140].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteNToxph = dom.find_all('td', attrs={"class": "montantpetit"})[144].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteNToxphref = dom.find_all('td', attrs={"class": "montantpetit"})[145].contents[0].replace(u'\xa0','').replace(' ', '')
    AnDetteph = dom.find_all('td', attrs={"class": "montantpetit"})[149].contents[0].replace(u'\xa0','').replace(' ', '')
    AnDettephref = dom.find_all('td', attrs={"class": "montantpetit"})[150].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDette = [EncoursDetteTotph, EncoursDetteBankph,EncoursDetteNToxph,AnDetteph]
    TabDetteref = [EncoursDetteTotphref, EncoursDetteBankphref,EncoursDetteNToxphref, AnDettephref]
    #print('Dette commune : ', TabDette, 'Dette ref : ', TabDetteref)


    #           Capture des données de bases imposables
    BaseTHph = dom.find_all('td', attrs={"class": "montantpetit"})[157].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTHphref = dom.find_all('td', attrs={"class": "montantpetit"})[158].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPBph = dom.find_all('td', attrs={"class": "montantpetit"})[163].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPBphref = dom.find_all('td', attrs={"class": "montantpetit"})[164].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPNBph = dom.find_all('td', attrs={"class": "montantpetit"})[169].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPNBphref = dom.find_all('td', attrs={"class": "montantpetit"})[170].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTAPNBph = dom.find_all('td', attrs={"class": "montantpetit"})[175].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTAPNBphref = dom.find_all('td', attrs={"class": "montantpetit"})[176].contents[0].replace(u'\xa0','').replace(' ','')
    BaseTCEntph = dom.find_all('td', attrs={"class": "montantpetit"})[181].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTCEntphref = dom.find_all('td', attrs={"class": "montantpetit"})[182].contents[0].replace(u'\xa0','').replace(' ', '')
    TabBase = [BaseTHph, BaseTFPBph, BaseTFPNBph, BaseTAPNBph, BaseTCEntph]
    TabBaseref = [BaseTHphref, BaseTFPBphref, BaseTFPNBphref, BaseTAPNBphref, BaseTCEntphref]
    #print('Base impots commune : ', TabBase, 'Base impots ref : ', TabBaseref)

    #           Capture des données de montants d'impôts locaux
    MontTHph = dom.find_all('td', attrs={"class": "montantpetit"})[187].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTHphref = dom.find_all('td', attrs={"class": "montantpetit"})[188].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPBph = dom.find_all('td', attrs={"class": "montantpetit"})[192].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPBphref = dom.find_all('td', attrs={"class": "montantpetit"})[193].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPNBph = dom.find_all('td', attrs={"class": "montantpetit"})[197].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPNBphref = dom.find_all('td', attrs={"class": "montantpetit"})[198].contents[0].replace(u'\xa0','').replace(' ','')
    MontTAPNBph = dom.find_all('td', attrs={"class": "montantpetit"})[202].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTAPNBphref = dom.find_all('td', attrs={"class": "montantpetit"})[203].contents[0].replace(u'\xa0','').replace(' ','')
    MontTCEntph = dom.find_all('td', attrs={"class": "montantpetit"})[207].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTCEntphref = dom.find_all('td', attrs={"class": "montantpetit"})[208].contents[0].replace(u'\xa0','').replace(' ',
                                                                                                                 '')
    TabMont1 = [MontTHph, MontTFPBph, MontTFPNBph, MontTAPNBph, MontTCEntph]
    TabMont1ref = [MontTHphref, MontTFPBphref, MontTFPNBphref, MontTAPNBphref, MontTCEntphref]
    #print('Montant impots 1 commune : ', TabMont1, 'Montant impots 1 ref : ', TabMont1ref)

    #           Capture des données de montants d'impôts de répartition
    MontCVAEph = dom.find_all('td', attrs={"class": "montantpetit"})[212].contents[0].replace(u'\xa0','').replace(' ', '')
    MontCVAEphref = dom.find_all('td', attrs={"class": "montantpetit"})[213].contents[0].replace(u'\xa0','').replace(' ', '')
    MontEntResph = dom.find_all('td', attrs={"class": "montantpetit"})[217].contents[0].replace(u'\xa0','').replace(' ', '')
    MontEntResphref = dom.find_all('td', attrs={"class": "montantpetit"})[218].contents[0].replace(u'\xa0','').replace(' ','')
    MontSurComph = dom.find_all('td', attrs={"class": "montantpetit"})[222].contents[0].replace(u'\xa0','').replace(' ', '')
    MontSurComphref = dom.find_all('td', attrs={"class": "montantpetit"})[223].contents[0].replace(u'\xa0','').replace(' ', '')
    TabMont2 = [MontCVAEph, MontEntResph, MontSurComph]
    TabMont2ref = [MontCVAEphref, MontEntResphref, MontSurComphref]
    #print('Montant impots 2 commune : ', TabMont2, 'Montant impots 2 ref : ', TabMont2ref)

    TabRes = Tabid + TabRevFonc + TabDepFonc + TabRevInv + TabDepInv + TabDette + TabBase + TabMont1 + TabMont2 + TabRevFoncref + TabDepFoncref + TabRevInvref + TabDepInvref + TabDetteref + TabBaseref + TabMont1ref + TabMont2ref

    #print("Etape fin",NomCom, NomDep, PopCom, TailleCom,TabRes)
    #print()
    return TabRes


# fonction de capture des données d'un groupement de communes à partir de la page web scrapée

def captureGC(dom,NGCom):

    Tabid = ['', '', '', '','ResGC','PopTotGC']
    Contenu = dom.find('td', attrs={"id": "lieu"}).contents[0].strip(u'\xe0')
    NomGCom = Contenu[0:Contenu.find("Consolidation") - 19].replace(","," ")
    # Last=Nom[len(Nom)-1:len(Nom)]
    # print("Nom",Nom,len(Nom),"last=",Last)

    # print(NomGCom)
    NomDep = dom.find('span', attrs={"id": "departement"}).contents[0].replace("-", "").replace(u'\xa0', "")
    # print(NomDep)
    PopGCom = dom.find('td', attrs={"id": "population"}).contents[0].strip(u'\xe0').replace("Population : ","").replace(u'\xa0',"").replace(' habitants', "")
    # print(PopGCom)

    # GroupeCom=dom.find_all('th',attrs={"style":"Font-size:8pt;"})[3].contents[2].replace(u'\xe0','a').replace(u'\xe9','e')
    # GroupeCom=GroupeCom[:GroupeCom.find(')')+1]

    Tabid[0] = ""
    Tabid[1] = NomDep
    Tabid[2] = NomGCom
    Tabid[3] = PopGCom
    # print(Tabid)

    #       Capture des données de revenus de fonctionnement
    TotProdFonc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[1].contents[0].replace(' ', '').replace(u'\xa0','')
    RevFonc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[4].contents[0].replace(' ', '').replace(u'\xa0','')
    ImpLoc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[7].contents[0].replace(u'\xa0','').replace(' ', '')
    ImpLocRev_GC = dom.find_all('td', attrs={"class": "montantpetit"})[10].contents[0].replace(u'\xa0','').replace(' ', '')
    AutImp_GC = dom.find_all('td', attrs={"class": "montantpetit"})[13].contents[0].replace(u'\xa0','').replace(' ', '')
    DGF_GC = dom.find_all('td', attrs={"class": "montantpetit"})[16].contents[0].replace(u'\xa0','').replace(' ', '')
    TabRevFonc = [TotProdFonc_GC,RevFonc_GC, ImpLoc_GC, ImpLocRev_GC,AutImp_GC, DGF_GC]
    #print('Rev Gcommune : ',TabRevFonc)

    #           Capture des données de dépenses de fonctionnement
    TotDepFonc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[19].contents[0].replace(u'\xa0','').replace(' ', '')
    ChargesFonc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[22].contents[0].replace(u'\xa0','').replace(' ', '')
    DepPerso_GC = dom.find_all('td', attrs={"class": "montantpetit"})[25].contents[0].replace(u'\xa0','').replace(' ', '')
    Achat_GC = dom.find_all('td', attrs={"class": "montantpetit"})[28].contents[0].replace(u'\xa0','').replace(' ', '')
    ChFin_GC = dom.find_all('td', attrs={"class": "montantpetit"})[31].contents[0].replace(u'\xa0','').replace(' ', '')
    DepSub_GC = dom.find_all('td', attrs={"class": "montantpetit"})[34].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDepFonc = [TotDepFonc_GC,ChargesFonc_GC, DepPerso_GC, Achat_GC, ChFin_GC, DepSub_GC]
    #print('DepFonc Gcommune : ',TabDepFonc)


    #           Capture des données de revenus d'investissement
    RevInv_GC = dom.find_all('td', attrs={"class": "montantpetit"})[40].contents[0].replace(u'\xa0','').replace(' ', '')
    Emprunt_GC = dom.find_all('td', attrs={"class": "montantpetit"})[43].contents[0].replace(u'\xa0','').replace(' ', '')
    Subr_GC = dom.find_all('td', attrs={"class": "montantpetit"})[46].contents[0].replace(u'\xa0','').replace(' ', '')
    FCTVA_GC = dom.find_all('td', attrs={"class": "montantpetit"})[49].contents[0].replace(u'\xa0','').replace(' ', '')
    TabRevInv = [RevInv_GC, Emprunt_GC, Subr_GC, FCTVA_GC]
    #print('RevInv Gcommune : ',TabRevInv)

    #           Capture des données de dépenses d'investissement
    DepInv_GC = dom.find_all('td', attrs={"class": "montantpetit"})[52].contents[0].replace(u'\xa0','').replace(' ', '')
    DepEquip_GC = dom.find_all('td', attrs={"class": "montantpetit"})[55].contents[0].replace(u'\xa0','').replace(' ', '')
    RembEmprunt_GC = dom.find_all('td', attrs={"class": "montantpetit"})[58].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDepInv = [DepInv_GC, DepEquip_GC, RembEmprunt_GC]
    #print('DepInv Gcommune : ', TabDepInv)

    #           Capture des données d'endettement
    EncoursDette_GC = dom.find_all('td', attrs={"class": "montantpetit"})[67].contents[0].replace(u'\xa0','').replace(' ','')
    EncoursDetteBanc_GC = dom.find_all('td', attrs={"class": "montantpetit"})[70].contents[0].replace(u'\xa0','').replace(' ', '')
    EncoursDetteNetTox_GC = dom.find_all('td', attrs={"class": "montantpetit"})[73].contents[0].replace(u'\xa0','').replace(' ', '')
    AnDette_GC = dom.find_all('td', attrs={"class": "montantpetit"})[76].contents[0].replace(u'\xa0','').replace(' ', '')
    TabDette = [EncoursDette_GC,EncoursDetteBanc_GC, EncoursDetteNetTox_GC,AnDette_GC]
    #print('Dette Gcommune : ', TabDette)


    #           Capture des données de bases imposables
    BaseTH_GC = dom.find_all('td', attrs={"class": "montantpetit"})[79].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[82].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTFPNB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[85].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseTAPNB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[88].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseCFEAdd_GC = dom.find_all('td', attrs={"class": "montantpetit"})[91].contents[0].replace(u'\xa0','').replace(' ', '')
    BaseCFERes_GC = dom.find_all('td', attrs={"class": "montantpetit"})[94].contents[0].replace(u'\xa0','').replace(' ','')
    BaseCFEEol_GC = dom.find_all('td', attrs={"class": "montantpetit"})[96].contents[0].replace(u'\xa0','').replace(' ', '')
    TabBase = [BaseTH_GC, BaseTFPB_GC, BaseTFPNB_GC, BaseTAPNB_GC, BaseCFEAdd_GC,BaseCFERes_GC,BaseCFEEol_GC]
    #print('Base impots Gcommune : ', TabBase)


    #           Capture des données de montants d'impôts locaux
    MontTH_GC = dom.find_all('td', attrs={"class": "montantpetit"})[98].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[101].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTFPNB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[104].contents[0].replace(u'\xa0','').replace(' ', '')
    MontTAPNB_GC = dom.find_all('td', attrs={"class": "montantpetit"})[107].contents[0].replace(u'\xa0','').replace(' ', '')
    MontCFEAdd_GC = dom.find_all('td', attrs={"class": "montantpetit"})[110].contents[0].replace(u'\xa0','').replace(' ', '')
    MontCFERes_GC = dom.find_all('td', attrs={"class": "montantpetit"})[113].contents[0].replace(u'\xa0','').replace(' ', '')
    MontCFEEol_GC = dom.find_all('td', attrs={"class": "montantpetit"})[116].contents[0].replace(u'\xa0','').replace(' ', '')
    MontCVAE_GC = dom.find_all('td', attrs={"class": "montantpetit"})[119].contents[0].replace(u'\xa0','').replace(' ', '')
    MontForRes_GC = dom.find_all('td', attrs={"class": "montantpetit"})[122].contents[0].replace(u'\xa0','').replace(' ', '')
    MontSurfCo_GC = dom.find_all('td', attrs={"class": "montantpetit"})[125].contents[0].replace(u'\xa0','').replace(' ', '')
    TabMont = [MontTH_GC, MontTFPB_GC, MontTFPNB_GC, MontTAPNB_GC, MontCFEAdd_GC,MontCFERes_GC,MontCFEEol_GC,MontCVAE_GC,MontForRes_GC,MontSurfCo_GC]
    #print('Montant impots Gcommune : ', TabMont)

    TabResGC = Tabid + TabRevFonc + TabDepFonc + TabRevInv + TabDepInv + TabDette + TabBase + TabMont
    return TabResGC



# Ouverture des fichiers csv d'écriture des enregistrements scrapés et des urls incorrects

Annee='2017'
Today=str(date.today())


# Préparation des répertoires de résultats pour étape 1 et suivantes

Chemin='/Users/CetaData-Lainee/Dropbox/P2-Citoyen/8-Data/Communes/1-Script/Argus_2017/ScraperResults-Round6'
#print(Chemin)
os.chdir(Chemin)

try:
    dossier='Resultats'
    os.mkdir(dossier)
except:
    pass

CheminR=Chemin+'/Resultats'
os.chdir(CheminR)

for dossierDet in ('Etape1-Total','Etape2-Total','Etape3-Total'):
    if not os.path.isdir(dossierDet):
        os.makedirs(dossierDet)

os.chdir(Chemin)


# Création des fichiers de résultats étape 1

CheminR=Chemin+'/Resultats/Etape1-Total'
os.chdir(CheminR)
FichierDest1=open("Etape-1-Vigie-REpair-"+Annee+"-"+Today+".csv", "w")
FileVigie=csv.writer(FichierDest1)

FichierDest2=open("Etape-1-Vigie-Repair-NOK-"+Annee+"-"+Today+".csv", "w")
FileVigiedef=csv.writer(FichierDest2)

# Accès au fichier CSV. des codes départements et communes
# Seedurl = "url_et_appartenance-geo-communes-15.csv"
#Seedurl = "url_et_appartenance-geo-communes-manqueV1-2015.csv"


#file = open(Seedurl, "rU")
#reader = csv.reader(file)

# Ecriture de la ligne de titre du fichier résultats

#RevFonc_C	RevFoncCAF_C	ImpLoc_C	AutImp_C	DGF_C	DepFonc_C	DepFoncCAF_C	DepPerso_C	Achat_C	ChFin_C	Cont_C	DepSub_C	RevInv_C	Emprunt_C	Subr_C	FCTVA_C	Cont_C	DepInv_C	DepEquip_C	RembEmprunt_C	ChRep_C	Immo_C	EncoursDetteTot_C	EncoursDetteBank_C	EncoursDetteNTox_C	AnDette_C	BaseTH_C	BaseTFPB_C	BaseTFPNB_C	BaseTAPNB_C	BaseTCEnt_C	MontTH_C	MontTFPB_C	MontTFPNB_C	MontTAPNB_C	MontTCEnt_C	MontCVAE_C	MontEntRes_C	MontSurCom_C
#RevFoncref_C	RevFoncCAFref_C	ImpLocref_C	AutImpref_C	DGFref_C	DepFoncref_C	DepFoncCAFref_C	DepPersoref_C	Achatref_C	ChFinref_C	Contref_C	DepSubref_C	RevInvref_C	Empruntref_C	Subrref_C	FCTVAref_C	Contref_C	DepInvref_C	DepEquipref_C	RembEmpruntref_C	ChRepref_C	Immoref_C	EncoursDetteTotref_C	EncoursDetteBankref_C	EncoursDetteNToxref_C	AnDetteref_C	BaseTHref_C	BaseTFPBref_C	BaseTFPNBref_C	BaseTAPNBref_C	BaseTCEntref_C	MontTHref_C	MontTFPBref_C	MontTFPNBref_C	MontTAPNBref_C	MontTCEntref_C	MontCVAEref_C	MontEntResref_C	MontSurComref_C	Nom file_GC	NomDep_GC	Pop_GC	ResSec_GC	PopTot_GC	RevFonc_GC	ImpLoc_GC	ImpRev_GC	AutImp_GC	DGF_GC	DepFonc_GC	DepPerso_GC	Achat_GC	ChFin_GC	DepSub_GC	RevInv_GC	Emprunt_GC	Subr_GC	FCTVA_GC	DepInv_GC	DepEquip_GC	RembEmprunt_GC	EncoursDette_GC	EncoursDetteNetTox_GC	AnDette_GC	BaseTH_GC	BaseTFPB_GC	BaseTFPNB_GC	BaseTAPNB_GC	BaseCFEAdd_GC	BaseCFERes_GC	BaseCFEEol_GC	MontTH_GC	MontTFPB_GC	MontTFPNB_GC	MontTAPNB_GC	MontCFEAdd_GC	MontCFERes_GC	MonCFEEol_GC	MontCVAE_GC	MontEntRes_GC	MontSurCom_GC

Titre=['indice','NomC portail','NomGC portail','CodeGeo']

TitreC=['Nom_C_file','Num_C','NumDep_C','NomDep_C','Pop_C','ResSec_C','PopTot_C','Taille_C','SegTaille_C','Ind_GC-SegTaille_C']
TitreC=TitreC+['RevFonc_C','RevFoncCAF_C','ImpLoc_C','AutImp_C','DGF_C','DepFonc_C','DepFoncCAF_C','DepPerso_C','Achat_C','ChFin_C','DepCont_C','DepSub_C','RevInv_C','Emprunt_C','Subr_C','FCTVA_C','RInv_Cont_C','DepInv_C','DepEquip_C','RembEmprunt_C','ChRep_C','Immo_C','EncoursDetteTot_C','EncoursDetteBank_C','EncoursDetteNTox_C','AnDette_C','BaseTH_C','BaseTFPB_C','BaseTFPNB_C','BaseTAPNB_C','BaseTCEnt_C','MontTHp_C','MontTFPB_C','MontTFPNB_C','MontTAPNB_C','MontTCEnt_C','MontCVAE_C','MontEntRes_C','MontSurComp_C']
TitreC=TitreC+['RevFoncref_C','RevFoncCAF_Cref','ImpLocref_C','AutImpref_C','DGFref_C','DepFoncref_C','DepFoncCAF_Cref','DepPersoref_C','Achatref_C','ChFinref_C','Contref_C','DepSubref_C','RevInvref_C','Empruntref_C','Subrref_C','FCTVAref_C','Contref_C','DepInvref_C','DepEquipref_C','RembEmpruntref_C','ChRepref_C','Immoref_C','EncoursDetteTotref_C','EncoursDetteBankref_C','EncoursDetteNToxref_C','AnDetteref_C','BaseTHref_C','BaseTFPBref_C','BaseTFPNBref_C','BaseTAPNBref_C','BaseTCEntref_C','MontTHref_C','MontTFPBref_C','MontTFPNBref_C','MontTAPNBref_C','MontTCEntref_C','MontCVAEref_C','MontEntResref_C','MontSurComref_C']

TitreGC=['NumDep_GC','NomDep_GC','Nom_GC_file','Pop_GC','ResSec_GC','PopTot_GC']
TitreGC=TitreGC+['RevFonc_GC','RevFoncCAF_GC','ImpLoc_GC','ImpRev_GC','AutImp_GC','DGF_GC','DepFonc_GC','DefFoncCAF_GC','DepPerso_GC','Achat_GC','ChFin_GC','DepSub_GC','RevInv_GC','Emprunt_GC','Subr_GC','FCTVA_GC','DepInv_GC','DepEquip_GC','RembEmprunt_GC','EncoursDette_GC','EncoursDetteBanc_GC','EncoursDetteNetTox_GC','AnDette_GC','BaseTH_GC','BaseTFPB_GC','BaseTFPNB_GC','BaseTAPNB_GC','BaseCFEAdd_GC','BaseCFERes-HC','BaseCFEEol_GC','MontTH_GC','MontTFPB_GC','MontTFPNB_GC','MontTAPNB_GC','MontCFEAdd_GC','MontCFERes_GC','MonCFEEol_GC','MontCVAE_GC','MontEntRes_GC','MontSurCom_GC']

TitreTotal=Titre+TitreC+TitreGC

print("Titre total :",TitreTotal)
print()
writeCom(FileVigie, TitreTotal)


# Boucle de scraping
Nmin=1
Nmax=37000
ListenoGC=[]
ListeMissDataC=[]
CountnoGC=0

# Boucle sur les communes
count=0
Pas=500
CountPrint=1
os.chdir(Chemin)
NomIn = "log-repair.csv"
FichierIn = open(NomIn, "r")
FileIn = csv.reader(FichierIn)

for f in FileIn:
    #print(f)

    if (count>=Nmin and count<=Nmax):
        # Traitement des cas (rares) où le nom de la commune ou du groupement contient une virgule
        if count-Pas*int(float(count)/Pas)==0:
            print(count,"avant decoupe",type(f), len(f),f)
        chain=""
        for i in range(len(f)):
            chain=chain+str(f[i])
        f=chain.split(";")
        if count - Pas * int(float(count) / Pas) == 0:
            print(count,"apres decoupe",len(f),f)
        ValidGC=1
        ValidC = 1

#    if (count>=NMin):
        CodeC= f[0]
        NomC=f[1]
        FileNameC=CodeC+'.html'

        CodeGC=f[3]
        NomGC = f[4]
        if count - Pas * int(float(count) / Pas) == 0:
            print(count,'CodeGC',CodeGC,'NomGC:',NomGC)
        if NomGC=="N/D":
            FileNameGC="N/D"
            IndGC=0
        else:
            FileNameGC = CodeGC + '.html'
            if count - Pas * int(float(count) / Pas) == 0:
                print(count,'FileNameGC',FileNameGC)
            IndGC = 1

        NumDep=CodeC.split("*")[1]
        NumCom=f[8]
        #print('Noms',NomC,NomGC,CodeC,CodeGC,"File",FileNameC,FileNameGC)
        #print()

        Tabcommune=[count,f[1],f[4],"Codegeo"]

        # Recherche des communes et GC à partir des pages capturées
        try:
            #print("OK init0")
            CheminC = Chemin + '/Communes/'
            os.chdir(CheminC)
            if count-Pas*int(float(count)/Pas)==0:
                print("OK init",CodeC,FileNameC,CheminC)
            ListeFile = os.listdir(CheminC)
            #print("nombre de fichiers",len(ListeFile),FileNameC,ListeFile)
            if FileNameC in ListeFile:
                print(count,"fichier trouve",FileNameC)
                content_file = open(FileNameC, 'r')
            else:
                print(count,"fichier non trouve",FileNameC)

            #print("OK 0")
        except:
            print("erreur post OK 0",os.getcwd())
            print("erreur post OK 0", content_file)
        try:

            commune = content_file.read()
            #print("OK 1")
            content = BeautifulSoup(commune,"lxml")
            #print("OK 2")
            #print("BeautifulSoup OK")
            ResC=captureC(content,NumDep,NumCom,count,IndGC)
            #print("OK 3")
            #print("capture C OK")
            ValidC=CheckDataC(ResC)
            #print("OK 4")
            AffC="OK"
            if ValidC==0:
                AffC = "NOK"
                writeCom(FileVigiedef, ["Fichier C incomplet : ",str(NomC),str(NomGC),str(FileNameC),str(FilenNameGC)])
            #print('Commune",NomC," OK')
            #print(ResC)
        except:
            ValidC = 0
            AffC="non trouve"
            print("Fichier C non trouve : " + str(FileNameC))
            writeCom(FileVigiedef,["Fichier C non trouve : " ,str(NomC),str(NomGC),str(FileNameC),str(FileNameGC)])
            ResC=["na"]
            pass

        try:
            if ValidC==1 and NomGC=="N/D":
                ResGC=[]
                FileNameGC="N/D"
                CountnoGC=CountnoGC+1
                ListenoGC.append([NumDep,NomC])
                AffGC = "N/D"
                pass
            #elif ValidC==1 and FileNameGC=="72-00004.html":
            #    ResGC = ["72-00004.html"]
            #    AffGC="72-4"
            elif ValidC==1:
                CheminGC = Chemin + '/Groupements/'
                os.chdir(CheminGC)
                content_file2 = open(FileNameGC, 'rU')
                Gcommune = content_file2.read()
                content2 = BeautifulSoup(Gcommune,"lxml")
                ResGC=captureGC(content2, NomGC)
                AffGC="OK"
                #print('GCommune OK')
                #print(ResGC)
        except:
            ValidGC=0
            #if ValidC==1:
            #    AffGC="non trouve"
            #else:
            #    AffGC="C NOK"
            #print("Fichier GC non trouve : " + str(FilenNameGC))
            writeCom(FileVigiedef, ["Fichier GC non trouve : ",str(NomC),str(NomGC),str(FileNameC),str(FilenNameGC)])
            pass

        #print(count,CountPrint,"C:",AffC," GC:",AffGC)
        #print("FilenamGC",FileNameGC)
        if ValidC==1 and ValidGC==1:
            try:
                CheminR = Chemin+'/Resultats/Etape1-Total'
                os.chdir(CheminR)
                #print('Inputs appel traitement donnees',NumCom,NumDep,Num)
                #
                Tabcommune=Tabcommune+ResC+ResGC
                writeCom(FileVigie,Tabcommune)
                if count-Pas*int(float(count)/Pas)==0:
                    print("OK",count, CountPrint,"Ecriture : ",str(NomC),str(NomGC),str(FileNameC),str(FileNameGC))
                CountPrint=CountPrint+1
            except:
                print("NOK",count, CountPrint,"Erreur en écriture : "  + str(NomC)+"*"+str(FileNameC))
                print("NOK",count, CountPrint,"Erreur en écriture : "  + str(NomGC)+'*'+ str(FilenNameGC))
                pass
        else:
            print(NomC,CodeC,ValidC, ValidGC,"Non enregistré. Nbre total : ",count+1,'Nbre enregistres:',CountPrint)
    count=count+1

print("Nombre de commmunes sans GC",CountnoGC, " liste;")
for e in ListenoGC:
    print(e[0],e[1])

FichierDest1.close()
FichierDest2.close()

  
