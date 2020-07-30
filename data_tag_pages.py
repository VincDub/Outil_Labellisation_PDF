import pdfplumber
import os
import pandas as pd
import PIL
from PIL import Image
import unidecode
import pdfminer


def fichiers_cibles(chm):

        dossier = str(chm)
        liste_fichiers = os.listdir(dossier)
        noms_fichiers = list()
        for entry in liste_fichiers:
            chemin = os.path.join(dossier,entry)
            if os.path.isdir(chemin):
                noms_fichiers = noms_fichiers + fichiers_cibles(chemin)
            else:
                noms_fichiers.append(chemin)          
        return noms_fichiers

def chemin_image_html(chm):
    
    return '<img src="'+ chm + '" width="500">'+chm+'</img>'

def extraction_data_page(chemin):

    noms_fichiers = fichiers_cibles(chemin)
    liste_pages = []
    numeros_pages = []
    chemins = []
    chemins_captures_html = []

    for nom in noms_fichiers:

        try:

            with pdfplumber.open(nom) as pdf:

                pages_doc = pdf.pages
                cpt_pages = 0


                for page in pages_doc:
                    
                    cpt_pages +=1

                    if len(page.chars) > 0:

                        df = pd.DataFrame.from_dict(page.chars)

                        car = list(df['text'].values)
                        x_car = list(df['x0'].values)
                        y_car = list(df['y0'].values)
                        size_car = list(df['size'].values)

                        df_chars = pd.DataFrame(dict(caractere=car,x_car=x_car,y_car=y_car,size_car=size_car))
                        
                        csv_char = df_chars.to_csv(index=False)

                        liste_pages.append(csv_char)

                        chemins.append(nom)
                        
                        numeros_pages.append(cpt_pages)
                    
                        capture_ecran = page.to_image(resolution=120)
                        nom_tronc = os.path.split(nom)
                        chemin_capture = os.path.join("IMAGES_DUMP",(nom_tronc[-1]+str(cpt_pages)+".png"))
                        capture_ecran.save(chemin_capture)
                        chemins_captures_html.append(chemin_image_html(chemin_capture))


        except:

            continue

    pages = pd.DataFrame(dict(chemin_fichier=chemins,numero_page=numeros_pages, caractères=liste_pages))

    pages["captures"] = chemins_captures_html

    pd.set_option('display.max_colwidth', -1)

    html = pages.to_html(escape=False)

    with open("PAGES.html", "w", encoding="utf-8") as file:
        file.write(html)

    return pages

print(extraction_data_page('PDF'))