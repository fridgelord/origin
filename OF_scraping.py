# coding: utf-8

import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os

from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(
    '/usr/local/bin/chromedriver', chrome_options=options)
   # Optional argument, if not specified will search path.

# driver = webdriver.Chrome()  Optional argument, if not specified will search path.


def getproductsFromPage(listaOpon, dzis):

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')
    products = soup.findAll(True, {'class': 'prod-thumb prod-thumb-l '})
    for prod in products:
        if (1 == 1):
            try:
                link = re.search('href=\"(.+?)\" title',
                                 str(prod).replace("\n", "")).group(1)
            except:
                print('sprawdz brak linka')
                link = '_n/a'
            try:
                title = re.search('\" title=\"(.+?)\">',
                                  str(prod).replace("\n", "")).group(1)
            except:
                title = '_n/a'
            try:
                price = re.search('current-price\">(.+?) zł<',
                                  str(prod).replace("\n", "")).group(1)
                price = price.replace(chr(160), '')
                price = price.replace(chr(32), '')
                price = price.replace(',', '.')
                price = float(price)
            except:
                price = np.nan
                print("sprawdz brak ceny", link)
            try:
                listaOpon.append([
                    link,
                    title,
                    price,
                    dzis
                ])
            except:
                print("cos nie tek z dodawaniem do listy", title)
    try:
        element = driver.find_element_by_link_text('następna »')
        klasa = element.get_attribute('class')
        if klasa != 'jqs-pgn jqs-next pgn':
            raise
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("window.scrollBy(0,-250)", "")
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        sleep(0.5)
        element.click()
        sleep(4)
    except:
        return True
    else:
        getproductsFromPage(listaOpon, dzis)



listaOpon = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
adres = 'https://sklep.intercars.com.pl/szukaj/opony-i-felgi-2/'
try:
    driver.get(adres)
except:
    print("Nie udało się otworzyć adresu", adres)
sleep(3)
getproductsFromPage(listaOpon, dzis)

lista_Opon = pd.DataFrame(
    listaOpon, columns=['link', 'title', 'price', 'dateRetrieved'])
sciezka = 'datasets/pricesIC.csv'
if os.path.exists(sciezka):
    lista_Opon.to_csv(sciezka, sep=';', decimal=',', mode='a', header=False)
else:
    lista_Opon.to_csv(sciezka, sep=';', decimal=',')
try:
    sciezka2 = '/mnt/scraping/pricesIC.csv'
    if os.path.exists(sciezka2):
        lista_Opon.to_csv(
            sciezka2, sep=';', decimal=',', mode='a', header=False)
    else:
        lista_Opon.to_csv(sciezka2, sep=';', decimal=',')
except:
    print("Nie udało się zapisac na dysku sieciowym")




biezacaBazaOpon = pd.read_csv(
    'datasets/tireDataIC.csv', dtype='str', header=0, sep=';', usecols=[1])
biezacaBazaOpon = biezacaBazaOpon['link'].values.tolist()
daneOpon = []
# for referencja in [['/produkty/1578739-pirelli-scorpion-atr-32555-r22-116-h']]:
for referencja in listaOpon:
    odnosnik = referencja[0]
    if odnosnik not in biezacaBazaOpon:
        try:
            adres = 'https://sklep.intercars.com.pl' + odnosnik
            driver.get(adres)
            sleep(2)
        except:
            print("Nie udało się otworzyć strony dla", odnosnik)
        pageSource = driver.page_source
        soup = BeautifulSoup(pageSource, 'html.parser')
        try:
            productInfo = soup.findAll(True, {'class': 'tab-content'})
        except:
            print("Nie udało się znaleźć klasy tab-content dla", odnosnik)
        soup = productInfo
        soup = str(soup)
        try:
            szer = re.search(
                '<td>Szerokość( \[mm\])?</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(2)
        except:
            szer = '_n/a'
        try:
            profil = re.search(
                '<td>Profil</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            profil = '_n/a'
        try:
            osadzenie = re.search(
                '<td>Średnica( \[mm\])?</td>\n<td class=\"jqs-cf-value\">(.+?)[\"<]<?/td>',
                soup).group(2)
        except:
            osadzenie = '_n/a'
        try:
            sezon = re.search(
                '<td>Sezon</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if sezon == 'Letnia' or sezon == 'letnia':
                sezon = 'summer'
            elif sezon == 'zimowa':
                sezon = 'winter'
            elif sezon == 'całoroczna':
                sezon = 'allseason'
            else:
                print('Sprawdz nowy rodzaj sezonu dla', referencja)
                sezon = '_n/a'
        except:
            sezon = '_n/a'
        try:
            bieznik = re.search(
                '<td>Bieżnik</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            try:
                bieznik = re.search(
                    '<td>Model bieżnika</td>\n<td class=\"jqs-cf-value\"><a class=\"accent\" href=\"(.+?)\">(.+?)</a></td>',
                    soup).group(2)
            except:
                bieznik = '_n/a'
        try:
            zastosowanie = re.search(
                '<td>Zastosowanie</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            zastosowanie = '_n/a'
        try:
            przeznaczenie = re.search(
                '<td>Przeznaczenie</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if przeznaczenie == 'samochody osobowe':
                przeznaczenie = 'CAR'
            elif przeznaczenie == 'samochody dostawcze':
                przeznaczenie = 'LTR'
            elif przeznaczenie == 'samochody terenowe':
                przeznaczenie = 'SUV/4x4'
            else:
                print('Sprawdz nowy rodzaj sezonu dla', referencja)
                przeznaczenie = '_n/a'
        except:
            przeznaczenie = '_n/a'
        try:
            producent = re.search(
                '<td>Producent</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            producent = '_n/a'
        try:
            prod_kod = re.search(
                '<td>Kod producenta</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            prod_kod = '_n/a'
        try:
            LI = re.search(
                '<td>Indeks nośności</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            LI = '_n/a'
        try:
            SI = re.search(
                '<td>Indeks prędkości</td>\n<td class=\"jqs-cf-value\">(.+?) - (.+?)</td>',
                soup).group(1)
        except:
            SI = '_n/a'
        try:
            DOT = re.search(
                '<td>Data produkcji</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            DOT = ''
        try:
            RR = re.search(
                '<td>Opór toczenia</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            RR = '_n/a'
        try:
            WG = re.search(
                '<td>Hamowanie na mokrej nawierzchni</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            WG = '_n/a'
        try:
            dB = re.search(
                '<td>Liczba decybeli</td>\n<td class=\"jqs-cf-value\">(.+?) dB</td>',
                soup).group(1)
        except:
            dB = '_n/a'
        try:
            noise = re.search(
                '<td>Poziom emisji hałasu</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            noise = '_n/a'
        try:
            EAN = re.search(
                '<td>Kod EAN</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            EAN = '_n/a'
        try:
            rant = re.search(
                '<td>Rant opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if 'Rant ochronny' in rant:
                rant = 'RPB'
            else:
                print('Sprawdz nowy rodzaj rantu dla', referencja)
                rant = '_n/a'
        except:
            rant = ''
        runflat = False
        try:
            budowa = re.search(
                '<td>Budowa opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if 'runflat' in budowa.lower():
                runflat = True
            else:
                print('Sprawdz nowy rodzaj rof dla', referencja)
        try:
            XL = re.search(
                '<td>Nośność opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if 'podwyższony' in XL:
                XL = 'XL'
            else:
                print('Sprawdz nowy rodzaj XL dla', referencja)
                XL = ''
        except:
            XL = ''
        try:
            cecha = re.search(
                '<td>Cecha dodatkowa</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if cecha == 'XL - podwyższony indeks nośności':
                XL = 'XL'
                cecha = ''
        except:
            cecha = ''
        try:
            klasa = re.search(
                '<td>Klasa opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
            if klasa == 'średnia':
                klasa = 'medium'
            elif klasa == 'premium':
                True
            elif klasa == 'budżet':
                klasa = 'budget'
            else:
                print('Sprawdz nowy rodzaj tieru dla', referencja)
                klasa = '_n/a'
        except:
            klasa = '_n/a'
        try:
            indeks = re.search(
                '<td>Indeks</td>\n<td class=\"jqs-cf-value\">(.+?)</td>',
                soup).group(1)
        except:
            indeks = '_n/a'
        daneOpon.append([
            odnosnik, szer, profil, osadzenie, LI, SI, sezon, bieznik,
            zastosowanie, przeznaczenie, RR, WG, dB, noise, producent,
            prod_kod, EAN, indeks, rant, runflat, cecha, XL, DOT, klasa, dzis
        ])

driver.quit()

dane_opon = pd.DataFrame(
    daneOpon,
    columns=[
        'link', 'width', 'profile', 'seat', 'LI', 'SI', 'season', 'pattern',
        'application', 'tireType', 'RR', 'WG', 'dB', 'noise', 'producer',
        'manuf_code', 'EAN', 'ICindex', 'RBP', 'ROF', 'addFeature', 'XL',
        'DOT', 'tier', 'dateRetrieved'
    ])

def zapiszDfDoCsv(dataFr, sciezka):
    if os.path.exists(sciezka):
        dataFr.to_csv(sciezka, sep=';', decimal=',', mode='a', header=False)
    else:
        dataFr.to_csv(sciezka, sep=';', decimal=',')

sciezka = 'datasets/tireDataIC.csv'
sciezkaNewTires = 'datasets/tireDataICNew.csv'
sciezkaRemote = '/mnt/scraping/tireDataIC.csv'
sciezkaRemoteNewTires = '/mnt/scraping/tireDataICNew.csv'
listaSciezek = [sciezka, sciezkaNewTires, sciezkaRemote, sciezkaNewTires]
for i in listaSciezek:
    try:
        zapiszDfDoCsv(dane_opon, i)
    except:
        print("Nie udalo sie zapisac w", i)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
