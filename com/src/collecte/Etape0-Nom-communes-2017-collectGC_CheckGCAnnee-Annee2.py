# -*- coding: utf-8 -*-
import sys
import traceback

import pkg_resources
import selenium.webdriver.support.ui as UI
import csv
import io
import os
from sys import platform
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pkg_resources.require("selenium==3.141.0")


# Commentaires

# Dossier/ données clés
# Chromedriver : ligne 88
# Année : ligne 309
# Fichiers résultats ligne 311

# lignes 235-236 écriture du fichier commune
# lignes 273-274 écriture du fichier grouepement
# ligne 169 emplacement de Chromedriver
# Ligne 54 emplacement de stockage des fichiers résultats
#  -------- Fonctions auxiliaires et d'analyse des données des pages extraites -------


def Norm3(var):
    """
    Normalisation d'un nombre entier en chaîne de 3 caractères
    :param var:
    :return:
    """
    if var <= 9:
        Res = '00' + str(var)
    elif var <= 99:
        Res = '0' + str(var)
    else:
        Res = str(min(var, 999))
    return Res


def clean1(str):
    """
    fonction de nettoyage des chaines scrapées par élimination de &nbsp
    :param str:
    :return:
    """
    cleanstr = str[:str.find('&nbsp')]
    return cleanstr


def get_data_commune(page_source: webdriver) -> str:
    """
    Fonction de collecte des données dans la page de la commune
    :param page_source:
    :return:
    """
    dom = BeautifulSoup(page_source)
    nom_commune = dom.find('span', attrs={"id": "gfp"}).contents[0].strip(u'\xe0')

    if " (commune nouvelle" in nom_commune:
        nom_commune = str(nom_commune)[0:str(nom_commune).find(" (commune nouvelle")]

    nom_departement = dom.find('span', attrs={"id": "departement"}).contents[0] \
        .strip(u'\xe0') \
        .replace("-", "")

    population_commune = dom.find('td', attrs={"id": "population"}).contents[0] \
        .strip(u'\xe0') \
        .replace("Population ", "") \
        .replace(" en vigueur au 1er janvier de l'exercice : ", "") \
        .replace(" habitants - Budget principal seul", "")

    res = nom_commune + "," + nom_departement + "," + population_commune
    return res


def open_main_page(url: str) -> webdriver:
    print("url=", url)
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--incognito")

    browser = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=chrome_options)
    browser.implicitly_wait(20)  # seconds
    browser.get(url)
    return browser


def getdep(page: webdriver):
    """
    Selection de la liste des départements
    :param page:
    :return:
    """
    return UI.Select(page.find_element_by_id('listeDepartements'))


def getalpha(page: webdriver):
    """
    Selection de la liste alphabétique des communes
    :param page:
    :return:
    """
    return page.find_elements_by_xpath(dbox + '/tbody/tr[1]/td[2]/p/a')


def identify_groupement_commune(page: webdriver) -> (str, str):
    """

    :param page:
    :return: Nom et reference du groupement de commune
    """
    # Identification du groupement de commune
    nomcc = page.find_element_by_xpath('// *[@id="gfp"]').text
    nomccs = str(nomcc).replace("/", "_")
    print("nomccs", nomccs, "nomcc", nomcc)
    # Si la cc à déjà été vue
    if nomcc in listecc:
        # Renvoie la référence
        idx = listecc.index(nomcc)
        return nomccs, refcc[idx]
    else:
        # Ajoute la cc dans la liste 'déjà vue' et envoie la référence
        idxcc = len(listecc)
        listecc.append(nomccs)
        refcc.append('*'.join((nomccs, nodep, str(idxcc).zfill(3))))
        return nomccs, refcc[-1]


def boucle_commune(page: webdriver):
    global reprise, idxcomm, bclc, bclt
    # Calcul du nombre de table(s) dans la page
    nombre_tables = len(page.find_elements_by_xpath(dbox))

    # Boucle des tables
    for index_table in range(bclt, nombre_tables + 1):
        table = page.find_elements_by_xpath(dbox)[index_table - 1]
        nombre_communes = len(table.find_elements_by_class_name('libellepetit'))

        # Boucle des communes de la table
        for index_commune in range(bclc, nombre_communes):
            # Récupération du lien de la commune
            pth = dbox + '[' + str(index_table) + ']/tbody/tr/td/a'
            lien_commune = page.find_elements_by_xpath(pth)[index_commune * 2 + 1]

            print("page de la commune :", lien_commune.text)

            # Identification de la commune
            nom_commune = lien_commune.text
            nom_communes = str(nom_commune).replace("/", "_")
            if nom_commune not in missingCommunes:
                print(f"Skipping commune {nom_commune} in department {departmentNumber}")
                continue
            id_commune = '*'.join((nom_communes, nodep, alpha, str(idxcomm).zfill(3)))

            # Page de la commune
            lien_commune.click()

            # Budget principal
            page.find_element_by_xpath('//*[@id="bpcommune"]/a[2]').click()

            # recherche des liens par année
            # Vérification de la disponibilité des données
            infos = page.find_element_by_xpath('//*[@id="donnees"]').text

            # Si la page contient 'non disponibles' ou n'affiche pas les données de l'année
            if (infos.find(Annee) == -1) or (infos.find(u'non disponibles') > -1):
                # Renseigner la variable de disponibilité
                dispo_commune = 'N/D'
            else:
                # Sinon, se positionner à l'année souhaitée et ouvrir la page 'Fiche détaillée'
                print("exploration par annee")
                click_sur_fiche_departement_annee(page)
                #Attendre que la page 'Fiche detaille' s'affiche
                WebDriverWait(page, 20).until(EC.presence_of_element_located((By.ID, "tableaufichedetaillee")))

                # Enregistrer son contenu dans un fichier nommé
                # 'NoDépartement-PremiéreLettre-Index' dans le dossier 'Communes'
                with io.open(output_directory + 'Communes/' + id_commune + '.html', 'w') as f:
                    print("Saving html to {}", f.name)
                    f.write(page.page_source)

                #################################################
                # Ici votre code de traitement par commune avec #
                # les données de page.page_source               #
                resultat_commune = get_data_commune(page.page_source)
                #################################################
                dispo_commune = 'OK'

            # Retour à "Choix d'une commune"
            page.find_element_by_xpath('//*[@class="chemincontainer"]/a[3]').click()

            print()

            pth_tot = dbox + '/tbody/tr/td/div'
            liste_gc = page.find_elements_by_xpath(pth_tot)
            ta = 0
            try:
                long = len(liste_gc)
            except:
                long = 0
            print("nombre d'elements GC :", len(liste_gc) - 1)

            if long <= 1:
                tu0 = "na"
                pass
            if long == 2:
                tu0 = 1
            else:
                for tu in range(len(liste_gc)):
                    if liste_gc[tu].text.find(Annee) > -1 and ta == 0:
                        ta = 1
                        tu0 = tu
                    else:
                        tu0 = "na"

            # Traitement budget groupement
            idcc, nmcc, dispocc = ('N/D', 'N/D', 'N/D')
            # Si le lien vers le groupement existe...
            if tu0 == "na":
                pth = dbox + '/tbody/tr[3]/td/div/a[2]'
            else:
                pth = dbox + '/tbody/tr[3]/td/div/a[' + str(int(tu0 + 1)) + ']'

            if page.find_elements_by_xpath(pth):
                # ... le suivre
                page.find_element_by_xpath(pth).click()
                # print("page.find GC",page.find_element_by_xpath(pth).text)
                # Lecture de la page
                infos = page.find_element_by_xpath('//*[@id="donnees"]').text

                # Si la page contient 'non disponibles' ou n'affiche
                #   pas les données de l'année
                if (infos.find(Annee) == -1) or \
                        (infos.find(u'non disponibles') > -1):
                    # Renseigner la variable de disponibilité
                    dispocc = 'N/D'
                else:
                    # Sinon, ouvrir la page 'Fiche détaillée'
                    page.find_element_by_xpath(fiche_departement).click()

                    # Récupération des infos du groupement
                    nmcc, idcc = identify_groupement_commune(page)

                    # Enregistrer son contenu dans un fichier nommé
                    # 'NoDépartement-Index' dans le dossier 'Groupements'
                    with io.open('Groupements/' + idcc + '.html', 'w') as f:
                        f.write(page.page_source)

                    #################################################
                    # Ici votre code de traitement par CC avec      #
                    # les données de page.page_source
                    #
                    # Get_dataCC(page.page_source)
                    #################################################
                    dispocc = 'OK'

            lien2 = [id_commune, idcc, nom_commune, nmcc, long - 1, tu0]
            try:
                print("ResCommune", resultat_commune, lien2)
            except:
                print('pas de ResCommune', id_commune, idcc)
            LinkC_GC.writerow(lien2)

            # Retour à "Choix d'une commune"
            pth = '//*[@class="chemincontainer"]/a[2]'
            if page.find_elements_by_xpath(pth):
                page.find_element_by_xpath(pth).click()

            # Création des informations de boucle (utiles en cas de reprise)
            cursor = '-'.join((str(departmentNumber), str(a), str(index_table), str(index_commune), str(idxcomm)))
            # Création de la ligne à écrire dans le fichier log.csv
            logcomm = ';'.join((id_commune, nom_commune, dispo_commune,
                                idcc, nmcc, dispocc, str(long - 1), str(tu0), cursor))

            # Ne pas écrire la ligne en cas de reprise (elle existe déjà)
            if reprise:
                reprise = False
            else:
                print("ligne de log", logcomm)
                log.write(logcomm + '\n')
                log.flush()
            # Incrémentation de l'index des communes
            idxcomm += 1
        # Remise à défaut des variables de boucle
        bclc = 0
    bclt = 2
    idxcomm = 0


def click_sur_fiche_departement_annee(page: webdriver):
    elems = page.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        print("elem:", elem.get_attribute("href"))
        if Annee in elem.text:
            elem.click()
            break
    page.find_element_by_xpath(fiche_departement).click()


def get_path_to_chrome_driver() -> str:
    if platform == "linux" or platform == "linux2":
        return os.path.join(root_directory, "chrome/driver/chromedriver_linux")
    elif platform == "darwin":
        return os.path.join(root_directory, "chrome/driver/chromedriver_mac")
    else:
        raise EnvironmentError("Only supporting Linux & Mac")


def initFolders() -> None:
    os.makedirs(output_directory, exist_ok=True)
    print("Setting work directory to : {work_directory}".format(work_directory=os.getcwd()))
    os.chdir(output_directory)

    for dossier in ('Communes', 'Groupements'):
        os.makedirs(dossier, exist_ok=True)


if __name__ == '__main__':
    departmentNumbers = ["82", "83", "85", "87", "88"]
    missingCommunes = {"ABBEVILLE", "ABONDANCE", "ADRETS-DE-L'ESTEREL (LES)", "ALÇAY-ALÇABEHETY-SUNHARETTE",
                       "ALGOLSHEIM", "ALTENACH", "ALTKIRCH", "AMMERSCHWIHR", "ANDOLSHEIM", "ANNOVILLE", "APPENWIHR",
                       "ARTZENHEIM", "ASPACH", "ASPACH-LE-BAS", "ASPACH-MICHELBACH", "ATTENSCHWILLER", "AUBURE",
                       "BECORDEL-BECOURT", "BECQUIGNY", "BEHEN", "BEHENCOURT", "BELLANCOURT", "BELLEUSE",
                       "BELLOY-EN-SANTERRE", "BELLOY-SAINT-LEONARD", "BELLOY-SUR-SOMME", "BEON", "BERGICOURT",
                       "BERMESNIL", "BERNATRE", "BERNAVILLE", "BERNAY-EN-PONTHIEU", "BERNES", "BERNEUIL",
                       "BERNY-EN-SANTERRE", "BERTANGLES", "BERTEAUCOURT-LES-DAMES", "BERTEAUCOURT-LES-THENNES",
                       "BERTRANCOURT", "BERZY-LE-SEC", "BETHENCOURT-SUR-MER", "BETHENCOURT-SUR-SOMME", "BETTEMBOS",
                       "BETTENCOURT-RIVIERE", "BETTENCOURT-SAINT-OUEN", "BEUVRAIGNES", "BIACHES", "BIARRE", "BIENCOURT",
                       "BILLANCOURT", "BINSON-ET-ORQUIGNY", "BLANGY-SOUS-POIX", "BLANGY-TRONVILLE", "BOISBERGUES",
                       "BOISLE (LE)", "BOISMONT", "BONNAY", "BONNEVILLE", "BOSQUEL", "BOUCHAVESNES-BERGEN", "BOUCHOIR",
                       "BOUCHON", "BOUFFLERS", "BOUGAINVILLE", "BOUILLANCOURT-EN-SERY", "BOUILLANCOURT-LA-BATAILLE",
                       "BOUQUEMAISON", "BOURDON", "BOURSEVILLE", "BOUSSICOURT", "BOUTTENCOURT",
                       "BOUVAINCOURT-SUR-BRESLE", "BOUVINCOURT-EN-VERMANDOIS", "BOUZINCOURT", "BOVELLES", "BOVES",
                       "BRACHES", "BRAILLY-CORNEHOTTE", "BRASSY", "BRAY-LES-MAREUIL", "BRAY-SUR-SOMME", "BREILLY",
                       "BRESLE", "BREUIL", "BREUIL-BARRET", "BREVILLERS", "BRIE", "BRIQUEMESNIL-FLOXICOURT", "BROCOURT",
                       "BROUCHY", "BRUCAMPS", "BRUTELLES", "BUIGNY-L'ABBE", "BUIGNY-LES-GAMACHES",
                       "BUIGNY-SAINT-MACLOU", "BUIRE-COURCELLES", "BUIRE-SUR-L'ANCRE", "BUS-LA-MESIERE",
                       "BUS-LES-ARTOIS", "BUSSU", "BUSSUS-BUSSUEL", "BUSSY-LES-DAOURS", "BUSSY-LES-POIX", "BUVERCHY",
                       "CACHY", "CAGNY", "CAHON", "CAIX", "CAMBRON", "CAMON", "CAMPS-EN-AMIENOIS", "CANAPLES", "CANCHY",
                       "CANDAS", "CANNESSIERES", "CANTIGNY", "CAOURS", "CAPPY", "CARDONNETTE", "CARDONNOIS (LE)",
                       "CARNOY-MAMETZ", "CARREPUIS", "CARTIGNY", "CAULIERES", "CAVILLON", "CAYEUX-EN-SANTERRE",
                       "CAYEUX-SUR-MER", "CERISY", "CERISY-BULEUX", "CHAMPIEN", "CHAPELLE-AUX-LYS (LA)", "CHAULNES",
                       "CHAUSSEE-TIRANCOURT (LA)", "CHAUSSOY-EPAGNY", "CHAVATTE (LA)", "CHENIMENIL", "CHEPY",
                       "CHERMISEY", "CHILLY", "CHIPILLY", "CHIRMONT", "CHUIGNES", "CHUIGNOLLES", "CIRCOURT",
                       "CIRCOURT-SUR-MOUZON", "CITERNE", "CIZANCOURT", "CLAIRY-SAULCHOIX", "CLAUDON", "CLEREY-LA-COTE",
                       "CLERJUS (LE)", "CLERY-SUR-SOMME", "CLEURIE", "CLEZENTAINE", "COCQUEREL", "COIGNEUX", "COINCHES",
                       "COISY", "COLINCAMPS", "COMBLES", "COMBRIMONT", "CONDE-FOLIE", "CONTALMAISON", "CONTAY",
                       "CONTEVILLE", "CONTRE", "CONTREXEVILLE", "CONTY", "CORBIE", "CORCIEUX", "CORNIMONT", "COTTENCHY",
                       "COULLEMELLE", "COULONVILLERS", "COURCELETTE", "COURCELLES-AU-BOIS", "COURCELLES-SOUS-CHATENOIS",
                       "COURCELLES-SOUS-MOYENCOURT", "COURCELLES-SOUS-THOIX", "COURTEMANCHE", "CRAINVILLIERS",
                       "CRAMONT", "CRECY-EN-PONTHIEU", "CREMERY", "CRESSY-OMENCOURT", "CREUSE", "CROIX-AUX-MINES (LA)",
                       "CROIX-MOLIGNEAUX", "CROIXRAULT", "CROTOY (LE)", "CROUY-SAINT-PIERRE", "CULOZ", "CURCHY",
                       "CURLU", "DAMERY", "DANCOURT-POPINCOURT", "DAOURS", "DARGNIES", "DAVENESCOURT", "DEMUIN",
                       "DERNANCOURT", "DEVISE", "DOINGT", "DOMART-EN-PONTHIEU", "DOMART-SUR-LA-LUCE", "DOMESMONT",
                       "DOMINOIS", "DOMLEGER-LONGVILLERS", "DOMMARTIN", "DOMPIERRE-BECQUINCOURT",
                       "DOMPIERRE-SUR-AUTHIE", "DOMQUEUR", "DOMVAST", "DONGES", "DOUDELAINVILLE", "DOUILLY", "DOULLENS",
                       "DREFFEAC", "DREUIL-LES-AMIENS", "DRIENCOURT", "DROMESNIL", "DRUCAT", "DURY",
                       "EAUCOURT-SUR-SOMME", "ECHELLE-SAINT-AURIN (L')", "ECLUSIER-VAUX", "EMBREVILLE", "ENGLEBELMER",
                       "ENNEMAIN", "EPAGNE-EPAGNETTE", "EPAUMESNIL", "EPECAMPS", "EPEHY", "EPENANCOURT", "EPLESSIER",
                       "EPPEVILLE", "EQUANCOURT", "EQUENNES-ERAMECOURT", "ERCHES", "ERCHEU", "ERCOURT", "ERGNIES",
                       "ERONDELLE", "ESCLAINVILLERS", "ESMERY-HALLON", "ESSERTAUX", "ESTREBOEUF", "ESTREES-DENIECOURT",
                       "ESTREES-LES-CRECY", "ESTREES-MONS", "ESTREES-SUR-NOYE", "ETALON", "ETELFAY", "ETERPIGNY",
                       "ETINEHEM-MERICOURT", "ETOILE (L')", "ETREJUST", "ETRICOURT-MANANCOURT", "FALOISE (LA)", "FALVY",
                       "FAMECHON", "FAVEROLLES", "FAVIERES", "FAY", "FERRIERES", "FESCAMPS", "FEUILLERES",
                       "FEUQUIERES-EN-VIMEU", "FIEFFES-MONTRELET", "FIENVILLERS", "FIGNIERES", "FINS", "FLAUCOURT",
                       "FLERS", "FLERS-SUR-NOYE", "FLESSELLES", "FLEURY", "FLIXECOURT", "FLUY", "FOLIES", "FOLLEVILLE",
                       "FONCHES-FONCHETTE", "FONTAINE-LES-CAPPY", "FONTAINE-LE-SEC", "FONTAINE-SOUS-MONTDIDIER",
                       "FONTAINE-SUR-MAYE", "FONTAINE-SUR-SOMME", "FONTCLAIREAU", "FORCEVILLE", "FORCEVILLE-EN-VIMEU",
                       "FOREST-L'ABBAYE", "FOREST-MONTIERS", "FORT-MAHON-PLAGE", "FOSSEMANANT",
                       "FOUCAUCOURT-EN-SANTERRE", "FOUCAUCOURT-HORS-NESLE", "FOUENCAMPS", "FOUILLOY", "FOUQUESCOURT",
                       "FOURCIGNY", "FOURDRINOY", "FRAMERVILLE-RAINECOURT", "FRAMICOURT", "FRANCIERES", "FRANLEU",
                       "FRANQUEVILLE", "FRANSART", "FRANSU", "FRANSURES", "FRANVILLERS", "FRECHENCOURT", "FREMONTIERS",
                       "FRESNES-MAZANCOURT", "FRESNES-TILLOLOY", "FRESNEVILLE", "FRESNOY-ANDAINVILLE", "FRESNOY-AU-VAL",
                       "FRESNOY-EN-CHAUSSEE", "FRESNOY-LES-ROYE", "FRESSENNEVILLE", "FRETTECUISSE", "FRETTEMEULE",
                       "FRIAUCOURT", "FRICAMPS", "FRICOURT", "FRISE", "FRIVILLE-ESCARBOTIN", "FROHEN-SUR-AUTHIE",
                       "FROYELLES", "FRUCOURT", "GAMACHES", "GAPENNES", "GAUVILLE", "GENTELLES", "GEZAINCOURT",
                       "GINCHY", "GLISY", "GORENFLOS", "GORGES", "GOYENCOURT", "GRANDCOURT", "GRAND-LAVIERS",
                       "GRATIBUS", "GRATTEPANCHE", "GREBAULT-MESNIL", "GRIVESNES", "GRIVILLERS", "GROUCHES-LUCHUEL",
                       "GRUNY", "GUERBIGNY", "GUESCHART", "GUEUDECOURT", "GUIGNEMICOURT", "GUILLAUCOURT", "GUILLEMONT",
                       "GUIZANCOURT", "GUYENCOURT-SAULCOURT", "GUYENCOURT-SUR-NOYE", "HAILLES", "HALLENCOURT",
                       "HALLIVILLERS", "HALLOY-LES-PERNOIS", "HALLU", "HAM", "HAMELET", "HAMEL (LE)", "HANCOURT",
                       "HANGARD", "HANGEST-EN-SANTERRE", "HANGEST-SUR-SOMME", "HARBONNIERES", "HARDECOURT-AUX-BOIS",
                       "HARPONVILLE", "HATTENCOURT", "HAUTVILLERS-OUVILLE", "HAVERNAS", "HEBECOURT", "HEDAUVILLE",
                       "HEILLY", "HEM-HARDINVAL", "HEM-MONACU", "HENENCOURT", "HERBECOURT", "HERISSART", "HERLEVILLE",
                       "HERLY", "HERVILLY", "HESBECOURT", "HESCAMPS", "HEUCOURT-CROQUOISON", "HEUDICOURT", "HEUZECOURT",
                       "HIERMONT", "HOMBLEUX", "HONOR-DE-COS (L')", "HORNOY-LE-BOURG", "HUCHENNEVILLE", "HUMBERCOURT",
                       "HUPPY", "HYPERCOURT", "IGNAUCOURT", "INVAL-BOIRON", "IRLES", "JUMEL", "KALHAUSEN", "KANFEN",
                       "KAPPELKINGER", "KEDANGE-SUR-CANNER", "KEMPLICH", "KERBACH", "KERLING-LES-SIERCK",
                       "KERPRICH-AUX-BOIS", "KIRSCH-LES-SIERCK", "KIRSCHNAUMEN", "KIRVILLER", "KLANG", "KNUTANGE",
                       "KOENIGSMACKER", "KUNTZIG", "LABARTHE", "LABASTIDE-DE-PENNE", "LABASTIDE-DU-TEMPLE",
                       "LABASTIDE-SAINT-PIERRE", "LABOISSIERE-EN-SANTERRE", "LABOURGADE", "LACAPELLE-LIVRON",
                       "LACHAPELLE", "LACOUR", "LACOURT-SAINT-PIERRE", "LAFITTE", "LAFRANÇAISE",
                       "LAFRESGUIMONT-SAINT-MARTIN", "LAGUEPIE", "LAHOUSSOYE", "L'AIGUILLON-LA-PRESQU'ILE", "LALEU",
                       "LAMAGISTERE", "LAMARONDE", "LAMOTHE-CAPDEVILLE", "LAMOTHE-CUMONT", "LAMOTTE-BREBIERE",
                       "LAMOTTE-BULEUX", "LAMOTTE-WARFUSEE", "LANCHERES", "LANCHES-SAINT-HILAIRE",
                       "LANGUEVOISIN-QUIQUERY", "LAPENCHE", "LARRAZET", "LAUCOURT", "LAUZERTE", "LAVAURETTE",
                       "LAVIEVILLE", "LAVIT", "LAWARDE-MAUGER-L'HORTOY", "LEALVILLERS", "LEOJAC", "LESBOEUFS",
                       "LIANCOURT-FOSSE", "LICOURT", "LIERAMONT", "LIERCOURT", "LIGESCOURT", "LIGNIERES",
                       "LIGNIERES-CHATELAIN", "LIGNIERES-EN-VIMEU", "LIHONS", "LIMEUX", "LINGREVILLE", "LIOMER",
                       "LIZAC", "LONG", "LONGAVESNES", "LONGPRE-LES-CORPS-SAINTS", "LONGUEAU", "LONGUEVAL",
                       "LONGUEVILLETTE", "L'OREE-D'ECOUVES", "LOUVENCOURT", "LOUVRECHY", "LOZE", "LUCHEUX", "MACHIEL",
                       "MACHY", "MAILLY-MAILLET", "MAILLY-RAINEVAL", "MAISNIERES", "MAISON-PONTHIEU", "MAISON-ROLAND",
                       "MAIZICOURT", "MALAUSE", "MALPART", "MANSLE", "MANSONVILLE", "MARCELCAVE", "MARCHE-ALLOUARDE",
                       "MARCHELEPOT-MISERY", "MARESTMONTIERS", "MAREUIL-CAUBERT", "MARICOURT", "MARIEUX", "MARIGNAC",
                       "MARLERS", "MARQUAIX", "MARQUIVILLERS", "MARSAC", "MARTAINNEVILLE", "MAS-GRENIER", "MATIGNY",
                       "MAUBEC", "MAUCOURT", "MAUMUSSON", "MAUREPAS", "MAZIS (LE)", "MEAULTE", "MEAUZAC", "MEHARICOURT",
                       "MEIGNEUX", "MEILLARD (LE)", "MENESLIES", "MEREAUCOURT", "MERELESSART", "MERICOURT-EN-VIMEU",
                       "MERICOURT-L'ABBE", "MERLES", "MERS-LES-BAINS", "MESGE (LE)", "MESNIL-BRUNTEL",
                       "MESNIL-DOMQUEUR", "MESNIL-EN-ARROUAISE", "MESNIL-MARTINSART", "MESNIL-SAINT-GEORGES",
                       "MESNIL-SAINT-NICAISE", "METIGNY", "MEZEROLLES", "MEZIERES-EN-SANTERRE", "MIANNAY",
                       "MILLENCOURT", "MILLENCOURT-EN-PONTHIEU", "MIRABEL", "MIRAMONT-DE-QUERCY", "MIRAUMONT",
                       "MIRVAUX", "MOISLAINS", "MOISSAC", "MOLIERES", "MOLLIENS-AU-BOIS", "MOLLIENS-DREUIL", "MONBEQUI",
                       "MONCHY-LAGACHE", "MONCLAR-DE-QUERCY", "MONS-BOUBERT", "MONSURES", "MONTAGNE-FAYEL",
                       "MONTAGUDET", "MONTAIGU-DE-QUERCY", "MONTAIN", "MONTALZAT", "MONTASTRUC", "MONTAUBAN",
                       "MONTAUBAN-DE-PICARDIE", "MONTBARLA", "MONTBARTIER", "MONTBETON", "MONTDIDIER", "MONTECH",
                       "MONTEILS", "MONTESQUIEU", "MONTFERMIER", "MONTGAILLARD", "MONTIGNY-LES-JONGLEURS",
                       "MONTIGNY-SUR-L'HALLUE", "MONTJOI", "MONTONVILLERS", "MONTPEZAT-DE-QUERCY", "MONTRICOUX",
                       "MORCHAIN", "MORCOURT", "MOREUIL", "MORISEL", "MORLANCOURT", "MORVILLERS-SAINT-SATURNIN",
                       "MOUFLERS", "MOUFLIERES", "MOYENCOURT", "MOYENCOURT-LES-POIX", "MOYENNEVILLE", "MUILLE-VILLETTE",
                       "NAMPONT", "NAMPS-MAISNIL", "NAMPTY", "NAOURS", "NAYEMONT-LES-FOSSES", "NEGREPELISSE", "NESLE",
                       "NESLE-L'HOPITAL", "NESLETTE", "NEUFCHATEAU", "NEUFMOULIN", "NEUILLY-LE-DIEN",
                       "NEUILLY-L'HOPITAL", "NEUVEVILLE-DEVANT-LEPANGES (LA)", "NEUVEVILLE-SOUS-CHATENOIS (LA)",
                       "NEUVEVILLE-SOUS-MONTFORT (LA)", "NEUVILLE-AU-BOIS", "NEUVILLE-COPPEGUEULE",
                       "NEUVILLE-LES-BRAY (LA)", "NEUVILLERS-SUR-FAVE", "NEUVILLE-SIRE-BERNARD (LA)", "NEUVILLETTE",
                       "NIBAS", "NOHIC", "NOMEXY", "NOMPATELIZE", "NONVILLE", "NONZEVILLE", "NORROY", "NOSSONCOURT",
                       "NOUVION", "NOYANT-ET-ACONIN", "NOYELLES-EN-CHAUSSEE", "NOYELLES-SUR-MER", "NURLU", "OCCOCHES",
                       "OCHANCOURT", "O-DE-SELLE", "OFFIGNIES", "OFFOY", "OISEMONT", "OISSY", "ONEUX", "OPPY",
                       "ORESMAUX", "ORGUEIL", "ORVILLE", "OSTREVILLE", "OURTON", "OUST-MAREST", "OUTREAU", "OUTREBOIS",
                       "OUVE-WIRQUIN", "OVILLERS-LA-BOISSELLE", "OYE-PLAGE", "PARGNY", "PARISOT",
                       "PARVILLERS-LE-QUESNOY", "PENDE", "PERNOIS", "PERONNE", "PERVILLE", "PICQUIGNY",
                       "PIENNES-ONVILLERS", "PIERREGOT", "PIN (LE)", "PIQUECOS", "PISSY", "PLACHY-BUYON",
                       "PLESSIER-ROZAINVILLERS (LE)", "POEUILLY", "POIX-DE-PICARDIE", "POMMEVIC", "POMPIGNAN",
                       "PONCHES-ESTRUVAL", "PONT-DE-METZ", "PONTHOILE", "PONT-NOYELLES", "PONT-REMY", "PORT-LE-GRAND",
                       "POTTE", "POULAINVILLE", "POUPAS", "POZIERES", "PROUVILLE", "PROUZEL", "PROYART", "PUCHEVILLERS",
                       "PUNCHY", "PUYCORNET", "PUYGAILLARD-DE-LOMAGNE", "PUYGAILLARD-DE-QUERCY", "PUYLAGARDE",
                       "PUYLAROQUE", "PUZEAUX", "PYS", "QUEND", "QUERRIEU", "QUESNE (LE)", "QUESNEL (LE)",
                       "QUESNOY-LE-MONTANT", "QUESNOY-SUR-AIRAINES", "QUEVAUVILLERS", "QUIRY-LE-SEC", "QUIVIERES",
                       "RAHON", "RAINCHEVAL", "RAINNEVILLE", "RAMBURELLES", "RAMBURES", "RANCHOT", "RANCOURT",
                       "RAVILLOLES", "REALVILLE", "RECANOZ", "REGNIERE-ECLUSE", "REITHOUSE", "RELANS", "REMAISNIL",
                       "REMAUGIES", "REMIENCOURT", "REPOTS (LES)", "RETHONVILLERS", "REVELLES", "REVIGNY", "REYNIES",
                       "RIBEAUCOURT", "RIBEMONT-SUR-ANCRE", "RIENCOURT", "RIVERY", "RIX", "RIXOUSE (LA)",
                       "ROCHEFORT-SUR-NENON", "ROGY", "ROIGLISE", "ROISEL", "ROLLOT", "ROMAIN", "ROMANGE", "RONSSOY",
                       "ROQUECOR", "ROSAY", "ROSIERES-EN-SANTERRE", "ROTALIER", "ROTHONAY", "ROUFFANGE",
                       "ROUSSES (LES)", "ROUVREL", "ROUVROY-EN-SANTERRE", "ROUY-LE-GRAND", "ROUY-LE-PETIT", "ROYE",
                       "RUBEMPRE", "RUBESCOURT", "RUE", "RUFFEY-SUR-SEILLE", "RUMIGNY", "RYE", "SAILLY-FLIBEAUCOURT",
                       "SAILLY-LAURETTE", "SAILLY-LE-SEC", "SAILLY-SAILLISEL", "SAINS-EN-AMIENOIS", "SAINT-ACHEUL",
                       "SAINT-AIGNAN", "SAINT-AMANS", "SAINT-AMANS-DE-PELLAGAL", "SAINT-AMANS-DU-PECH",
                       "SAINT-ANTONIN-NOBLE-VAL", "SAINT-ARROUMEX", "SAINT-AUBIN-MONTENOY", "SAINT-AUBIN-RIVIERE",
                       "SAINT-BEAUZEIL", "SAINT-BLIMONT", "SAINT-CHRIST-BRIOST", "SAINT-CIRICE", "SAINT-CIRQ",
                       "SAINT-CLAIR", "SAINTE-JULIETTE", "SAINTE-SEGREE", "SAINT-ETIENNE-DE-TULMONT", "SAINT-FUSCIEN",
                       "SAINT-GEORGES", "SAINT-GERMAIN-SUR-BRESLE", "SAINT-GRATIEN", "SAINT-JEAN-DU-BOUZET",
                       "SAINT-LEGER-LES-AUTHIE", "SAINT-LEGER-LES-DOMART", "SAINT-LEGER-SUR-BRESLE", "SAINT-LOUP",
                       "SAINT-MARD", "SAINT-MARTIAL-SUR-ISOP", "SAINT-MARTIN-DE-JUSSAC", "SAINT-MARTIN-LE-MAULT",
                       "SAINT-MARTIN-LE-VIEUX", "SAINT-MARTIN-TERRESSUS", "SAINT-MATHIEU", "SAINT-MAULVIS",
                       "SAINT-MAURICE-LES-BROUSSES", "SAINT-MAXENT", "SAINT-MEARD", "SAINT-MICHEL", "SAINT-NAUPHARY",
                       "SAINT-NAZAIRE-DE-VALENTANE", "SAINT-NICOLAS-DE-LA-GRAVE", "SAINT-OUEN",
                       "SAINT-OUEN-SUR-GARTEMPE", "SAINT-PARDOUX-LE-LAC", "SAINT-PAUL", "SAINT-PAUL-D'ESPIS",
                       "SAINT-PORQUIER", "SAINT-PRIEST-LIGOURE", "SAINT-PRIEST-SOUS-AIXE", "SAINT-PRIEST-TAURION",
                       "SAINT-PROJET", "SAINT-QUENTIN-EN-TOURMONT", "SAINT-QUENTIN-LA-MOTTE-CROIX-AU-BAILLY",
                       "SAINT-RIQUIER", "SAINT-SARDOS", "SAINT-SAUFLIEU", "SAINT-SAUVEUR", "SAINT-SORNIN-LA-MARCHE",
                       "SAINT-SORNIN-LEULAC", "SAINT-SULPICE-LAURIERE", "SAINT-SULPICE-LES-FEUILLES", "SAINT-SYLVESTRE",
                       "SAINT-VAAST-EN-CHAUSSEE", "SAINT-VALERY-SUR-SOMME", "SAINT-VICTURNIEN",
                       "SAINT-VINCENT-D'AUTEJAC", "SAINT-VINCENT-LESPINASSE", "SAINT-VITTE-SUR-BRIANCE",
                       "SAINT-YRIEIX-LA-PERCHE", "SAINT-YRIEIX-SOUS-AIXE", "SAINT-YTHAIRE", "SAISSEVAL", "SALEUX",
                       "SALLES-LAVAUGUYON (LES)", "SALOUEL", "SALVETAT-BELMONTET (LA)", "SANCOURT",
                       "SAULCHOY-SOUS-POIX", "SAUVETERRE", "SAUVIAT-SUR-VIGE", "SAUVILLERS-MONGIVAL", "SAVENES",
                       "SAVEUSE", "SENARPONT", "SENLIS-LE-SEC", "SENTELIE", "SEPTFONDS", "SEREILHAC", "SERIGNAC",
                       "SEUX", "SISTELS", "SOLIGNAC", "SOREL", "SOREL-EN-VIMEU", "SOUES", "SOURDON", "SOYECOURT",
                       "SURCAMPS", "SURDOUX", "SUZANNE", "TAILLY", "TALMAS", "TARDIERE (LA)", "TEMPLEUX-LA-FOSSE",
                       "TEMPLEUX-LE-GUERARD", "TERRAMESNIL", "TERTRY", "THENNES", "THEZY-GLIMONT", "THIEPVAL",
                       "THIEULLOY-L'ABBAYE", "THIEULLOY-LA-VILLE", "THIEVRES", "THOIX", "THORY", "TILLOLOY",
                       "TILLOY-FLORIVILLE", "TINCOURT-BOUCLY", "TITRE (LE)", "TOEUFLES", "TOUFFAILLES",
                       "TOURS-EN-VIMEU", "TOUTENCOURT", "TRANSLAY (LE)", "TREJOULS", "TREUX", "TROIS-RIVIERES", "TULLY",
                       "UGNY-L'EQUIPEE", "VADENCOURT", "VAIRE-SOUS-CORBIE", "VAISSAC", "VALEILLES", "VALENCE",
                       "VALINES", "VAREN", "VARENNES", "VAUCHELLES-LES-AUTHIE", "VAUCHELLES-LES-DOMART",
                       "VAUCHELLES-LES-QUESNOY", "VAUDRICOURT", "VAUVILLERS", "VAUX-EN-AMIENOIS", "VAUX-MARQUENNEVILLE",
                       "VAUX-SUR-SOMME", "VAZERAC", "VECQUEMONT", "VELENNES", "VERCOURT", "VERDUN-SUR-GARONNE",
                       "VERFEIL", "VERGIES", "VERLHAC-TESCOU", "VERMANDOVILLERS", "VERPILLIERES", "VERS-SUR-SELLES",
                       "VICOGNE (LA)", "VIGNACOURT", "VIGUERON", "VILLEBRUMIER", "VILLECOURT",
                       "VILLE-DIEU-DU-TEMPLE (LA)", "VILLE-LE-MARCLET", "VILLEMADE", "VILLEROY", "VILLERS-AUX-ERABLES",
                       "VILLERS-BOCAGE", "VILLERS-BRETONNEUX", "VILLERS-CAMPSART", "VILLERS-CARBONNEL",
                       "VILLERS-FAUCON", "VILLERS-LES-ROYE", "VILLERS-SOUS-AILLY", "VILLERS-SOUS-CHATILLON",
                       "VILLERS-SUR-AUTHIE", "VILLERS-TOURNELLE", "VILLE-SUR-ANCRE", "VIRONCHAUX", "VISMES",
                       "VITZ-SUR-AUTHIE", "VOYENNES", "VRAIGNES-EN-VERMANDOIS", "VRAIGNES-LES-HORNOY", "VRELY", "VRON",
                       "WARGNIES", "WARLOY-BAILLON", "WARLUS", "WARSY", "WIENCOURT-L'EQUIPEE", "WIRY-AU-MONT",
                       "WOIGNARUE", "WOINCOURT", "WOIREL", "Y", "YAUCOURT-BUSSUS", "YONVAL", "YVRENCH", "YVRENCHEUX",
                       "YZENGREMER", "YZEUX",
                       }

    try:
        # Boucle départements
        # Selection et page du département
        for departmentNumber in departmentNumbers:
            # Année de recherche des données
            Annee = '2023'
            root_directory = os.path.join(os.path.dirname(__file__), '../../../')
            path_to_chromedriver = get_path_to_chrome_driver()
            output_directory = os.path.join(root_directory, 'output/' + str(Annee) + '/' + str(departmentNumber) + '/ScraperResults-Round0/')
            initFolders()

            # -------- Initialisation des variables -------
            # Lien vers le site
            url = 'https://www.impots.gouv.fr/cll/zf1/cll/zf1/accueil/flux.ex?_flowId=accueilcclloc-flow'
            # Paths les plus utilisés dans la recherche de liens
            dbox = '//*[@id="donneesbox"]/table'
            fiche_departement = '//*[@id="pavegestionguichets"]/table[2]/tbody/tr/td[5]/a'
            # Variables de boucles utiles au premier lancement...
            # ... sinon elle sont alimentées par le fichier de log
            bcld, bcla, bclt, bclc, idxcomm = (1, 0, 2, 0, 0)
            alpha = ''
            listecc, refcc = ([], [])
            reprise = False


            # Gestion du fichier log
            # S'il existe
            if os.path.isfile('log.csv'):
                # L'ouvrir en lecture
                log = io.open('log.csv', 'r')
                nbline = 0
                oldd = 1
                # Lire jusqu'a la derniére ligne afin de trouver où reprendre la boucle
                for line in log:
                    print(line)
                    cols = line.split(';')
                    print(cols)
                    # Ne pas lire la première ligne (en-tête)
                    if nbline != 0:
                        # Récupérer les variables de boucles à partir de la colonne 'Boucle'
                        bcld, bcla, bclt, bclc, idxcomm = [int(i) for i in cols[8].replace('\n', "").split('-')]
                        # Si changement de département...
                        if bcld != oldd:
                            # ...vider la liste des cc
                            listecc, refcc = ([], [])
                            oldd = bcld
                        # Si la cc n'est pas dans la liste...
                        if cols[4] not in listecc:
                            # ... l'ajouter
                            listecc.append(cols[4])
                            refcc.append(cols[3])
                    nbline += 1
                log.close()
                reprise = True
            else:
                # S'il n'existe pas le créer et écrire l'en-tête
                log = io.open('log.csv', 'w')
                log.write(u'IdCommunes;Nom_C;Dispo;IDGroupement;Nom_GC;Dispo;Boucle;Nbre_GC;Indice_GC\n')
                log.close()

            # Réouvrir le fichier de log afin de l'alimenter avec les nouvelles entrées
            log = io.open('log.csv', 'a')
            try:
                Nreprise = nbline
            except:
                Nreprise = 0

            # Ouverture du fichier csv d'écriture des liens communes - groupement de communes
            # FichierDest1=open("Lien-C-GC"+str(Annee)+"-"+str(date.today())+".csv", "w")
            FichierDest1 = open("Lien-C-GC" + str(Annee) + "-" + str(Nreprise) + ".csv", "w")
            LinkC_GC = csv.writer(FichierDest1)

            Titre = ["Id C", "Id GC", "Nom C", "Nom GC", "Nbre GC", "Indice GC " + str(Annee)]
            LinkC_GC.writerow(Titre)

            # Ouverture des fichiers csv d'écriture des enregistrements scrapés et des urls incorrects
            # FichierDest1=open("Scraper-Data finance communes-"+str(Annee)+"-"+str(date.today())+".csv", "wb")
            FichierDest1 = open("Scraper-Data finance communes-" + str(Annee) + "-" + str(Nreprise) + ".csv", "wb")
            FileVigie = csv.writer(FichierDest1)

            # FichierDest2=open("ScraperCom"+str(Annee)+"-communes_incorrectes"+str(date.today())+".csv", "wb")
            FichierDest2 = open("ScraperCom-communes incorrectes" + str(Annee) + "-" + str(Nreprise) + ".csv", "wb")
            Fileurldef = csv.writer(FichierDest2)

            # Lancer Chrome et ouvrir le site
            page = open_main_page(url)

            try:
                departmentIndex = next(i for i, option in enumerate(getdep(page).options) if departmentNumber in option.text)
                getdep(page).select_by_index(departmentIndex)
            except:
                print(page, departmentNumber)
            print("d=", departmentNumber)
            print("page")
            print(page)
            # Click sur OK
            page.find_element_by_name('_eventId_validercommunesetgroupts').click()
            # Log du département
            nodep = page.find_element_by_xpath(dbox + '[1]/tbody/tr[1]/td[1]/p').text
            nodep = nodep.split(' ')[0]
            # Remise à zéro de la liste des cc
            listecc = []
            refcc = []
            # Boucle alphabétique
            for a in range(bcla, len(getalpha(page))):
                try:
                    lkalpha = getalpha(page)[a]
                    alpha = lkalpha.text
                    lkalpha.click()
                except:
                    print("erreur", bcla, len(getalpha(page)))

                # Boucle des communes
                boucle_commune(page)
        bcla = 0
        # retour aux départements
        page.find_element_by_xpath('//*[@id="formulaire"]/div[2]/a[1]').click()

        print("Finished crawling for department " + " ".join(departmentNumbers))
        log.close()
    except Exception as error:
        if 'page' in locals():
            page.close()
        print("Restarting the script because of " + traceback.format_exc())
        os.system("python3 /home/jean/Work/projects/Collecte-donnees-collectivites-copy/com/src/collecte/Etape0-Nom"
                  "-communes-2017-collectGC_CheckGCAnnee-Annee2.py " + " ".join(departmentNumbers))
