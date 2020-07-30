import pandas as pd
import os
import tkinter as tk
from PIL import Image, ImageTk

compteur_pages_traitees = 0
valide = []

def chemin_image_html(chm):
    return '<img src="'+ chm + '" width="500">'+chm+'</img>'

def charger_page_random(n):

    pages = pd.read_html('PAGES.html',encoding='utf-8')

    selection = pages[0].sample(n,replace=False)
    
    return selection

def debut_labelisation(n,frame,label):

    global dataframe,longueur

    n = int(n.get())

    dataframe = charger_page_random(n)
    chm_premiere_image = dataframe['captures'].values[0]
    longueur = len(dataframe['captures'].values)
    

    im = Image.open(chm_premiere_image)
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

        chm_img = dataframe['captures'].values[compteur_pages_traitees]
        im = Image.open(chm_img)
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
            
            valide.append("valide")


        else:

            valide.append("non valide")


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