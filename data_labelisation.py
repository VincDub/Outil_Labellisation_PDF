import pandas as pd
import os
import tkinter as tk
from PIL import Image, ImageTk
import pdfplumber

compteur_pages_traitees = 0
valide = []

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


def extraction_data_page(chemin):

    noms_fichiers = fichiers_cibles(chemin)
    liste_pages = []
    numeros_pages = []
    chemins = []

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
                    
                        #capture_ecran = page.to_image(resolution=95)
                        nom_tronc = os.path.split(nom)
                        #chemin_capture = os.path.join("IMAGES_DUMP",(nom_tronc[-1]+str(cpt_pages)+".png"))
                        #capture_ecran.save(chemin_capture)
                        #chemins_captures_html.append(chemin_image_html(chemin_capture))


        except:

            continue

    pages = pd.DataFrame(dict(chemin_fichier=chemins,numero_page=numeros_pages, caractères=liste_pages))

    html = pages.to_html(escape=False)

    with open("PAGES.html", "w", encoding="utf-8") as file:
        file.write(html)

    return pages


def charger_page_random(n,pages):

    selection = pages.sample(n,replace=False)
    
    return selection

def debut_labelisation(n,frame,label):

    global dataframe,longueur

    n = int(n.get())

    pages = extraction_data_page('PDF_TEST')

    dataframe = charger_page_random(n,pages)

    f_origine = dataframe['chemin_fichier'].values[0]
    n_page= dataframe['numero_page'].values[0]
    longueur = len(dataframe['chemin_fichier'].values)

    with pdfplumber.open(f_origine) as pdf:

        fst_page = pdf.pages[n_page-1]
        im = (fst_page.to_image(resolution=95)).original
    

    im.thumbnail((600,600),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(im)
    frame.configure(image=img)
    frame.image = img
    label['text'] = ("PAGES LABELISEES : 0 / " + str(longueur))

def suivant(resultat,frame,label):

    global compteur_pages_traitees

    print(compteur_pages_traitees)

    if compteur_pages_traitees < longueur and compteur_pages_traitees != (longueur-1):

        compteur_pages_traitees += 1

        f_path = dataframe['chemin_fichier'].values[compteur_pages_traitees]
        n_page= dataframe['numero_page'].values[compteur_pages_traitees]

        with pdfplumber.open(f_path) as pdf:

            page = pdf.pages[n_page-1]
            im = (page.to_image(resolution=95)).original

        im.thumbnail((600,600),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(im)

        if resultat == 1:
            
            valide.append(1)


        else:

            valide.append(0)


        frame.configure(image=img)
        frame.image = img

        label['text'] = ("PAGES LABELISEES : " + str(compteur_pages_traitees) + " / " + str(longueur))

    else:

        if resultat == 1:
            
            valide.append(1)


        else:

            valide.append(0)


        img = ImageTk.PhotoImage(Image.open('default.png'))
        frame.configure(image=img)
        frame.image = img

        dataframe["valide"] = valide
        pd.set_option('display.max_colwidth', -1)

        html = dataframe.to_html(escape=False)

        with open("PAGES_LABELS.html", "w", encoding="utf-8") as file:
            file.write(html)

        label['text'] = "Labelisation terminée"
    

### GUI ###

fen = tk.Tk()

fen.title('Outil de labelisation de pages de PDF')
fen.geometry('700x1000')

## inputs

frame_input = tk.Frame(fen,relief = tk.FLAT)
frame_input.pack(pady=20)

frame_image = tk.Frame(fen,relief = tk.FLAT)
frame_image.pack(pady=20)

capture = ImageTk.PhotoImage(Image.open('default.png'))
capture_label = tk.Label(frame_image, image=capture)
capture_label.pack()

frame_labels = tk.LabelFrame(fen, text="Différents Labels")
frame_labels.pack(pady=10)

log = tk.Label(frame_labels,text="PAGES LABELISEES : .../...",fg = '#FF0000',bg = '#e6e6e6')
log.pack(padx=5)

btn_0 = tk.Button(frame_labels, relief = tk.GROOVE, text="Valide",command=(lambda : suivant(1,capture_label,log)))
btn_0.pack(pady=20)

btn_1 = tk.Button(frame_labels, relief = tk.GROOVE, text="Non-valide",command=(lambda : suivant(0,capture_label,log)))
btn_1.pack(pady=20)


samples = tk.LabelFrame(frame_input,text="Nombre d'échantillons à labeliser")
samples.pack(fill=tk.X, expand = 'yes', pady=10)

n_samples = tk.Spinbox(samples, from_=2 ,to=90000000)
n_samples.pack(pady=10)

btn_start = tk.Button(frame_input, relief = tk.GROOVE,text='Démarrer la labelisation',bg='green', command=(lambda : debut_labelisation(n_samples,capture_label,log)))
btn_start.pack(pady=10)
fen.mainloop()