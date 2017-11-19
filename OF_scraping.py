
# coding: utf-8

# In[15]:


import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


# In[16]:


options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('/usr/local/bin/chromedriver',chrome_options=options)  # Optional argument, if not specified will search path.
# driver = webdriver.Chrome()  # Optional argument, if not specified will search path.


# In[35]:


def getproductsFromPage(listaOpon,dzis):
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source
    

    soup = BeautifulSoup(pageSource, 'html.parser')
#     f=open('datasets/soup','w')
#     s=str(soup)
#     f.write(s)
#     f.close()
    #print(soup,file='datasets/soup')
#    products = soup.findAll(True, {'class': 'gtm-item'})
    products = soup.findAll(True, {'class': 'prod-thumb prod-thumb-l '})
    #print(products[0])
    for prod in products:
        if(1==1):
            try:
                link = re.search('href=\"(.+?)\" title',str(prod).replace("\n","")).group(1)
            except:
                link = '_n/a'
            try:
                title = re.search('\" title=\"(.+?)\">', str(prod).replace("\n", "")).group(1)
            except:
                title = '_n/a'
#            try:
#                stock = int(re.search('\d+',re.search('(?<=class=\"stockLevel\">)(.*?)(?=w mag)', str(prod).replace("\n", "")).group(0)).group(0))
#            except:
##                 print("Nie udalo si pobrac stock dla", title)
#                stock=0
#    
#            runFlat=False
#            if str(prod).find('Run Flat') != -1:
#                runFlat=True
#            try:
#                LI = re.search('(?<=Indeks nośności )(.*?)(?= – maksymalne)', str(prod).replace("\n", "")).group(0)
#            except:
#                LI = 'n/a'
#            try:
#                SI = re.search('(?<=Indeks prędkości )(.*?)(?= – maksymalna)', str(prod).replace("\n", "")).group(0)
#            except:
#                SI = 'n/a'
#                
#            if str(prod).find('<span class="tooltip">Opona letnia z homologacją zimową.</span>') != -1:
#                season="allseason"
#            elif str(prod).find('<span class="tooltip">Opona na sezon letni.</span>') != -1:
#                season="summer"
#            elif str(prod).find('<span class="tooltip">Opona na sezon zimowy.</span>') != -1:
#                season="winter"
#            elif str(prod).find('<span class="tooltip">Opona całoroczna.</span>') != -1:
#                season="allseason"
#            else:
#                season="nieznany"
#                print("sprawdz nowy rodzaj sezonu", title)
#                
#            if str(prod).find('<strong>24h</strong>') != -1:
#                delivery='24h'
#            elif str(prod).find('<strong>już jutro!</strong>') != -1:
#                delivery='24h'
#            elif str(prod).find('Zapytaj o termin dostawy') != -1:
#                delivery='ask'
#            elif str(prod).find('Doręczymy') != -1:
#                delivery=re.search('(?<=Doręczymy  <strong>).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
#            elif str(prod).find('dni roboczych') != -1:
#                delivery=re.search('(?<=<strong class=\"\">).*? dni robocz(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
#            elif str(prod).find('<strong class=" futureSupply">') != -1:
#                delivery=re.search('(?<=<strong class=\" futureSupply\">).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
#            else:
#                delivery="nieznany"
#                print("sprawdz nowy rodzaj dostawy", title)
            
            try:
#                price = re.search('current-price nowrap\">(.+?) zł<', str(prod).replace("\n", "")).group(1)
                price = re.search('current-price\">(.+?) zł<', str(prod).replace("\n", "")).group(1)
                price = price.replace(chr(160),'')
                price = price.replace(chr(32),'')
                price = price.replace(',','.')
                price = float(price)
            except:
                price = np.nan
                print("sprawdz brak ceny", title)
                
# oponyExmp = pd.DataFrame(listaOpon, columns=['link', 'title', 'producer', 'model', 'size'\
#     , 'li', 'si', 'season', 'runFlat', 'price', "stock", 'delivery'])
                
            try:
                listaOpon.append([link,
                                  title, 
#                                  re.search('(?<=<span class=\"producer\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0), 
#                                  re.search('(?<=<span class=\"model\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0), 
#                                  re.search('(?<=<span class=\"size\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0), 
#                                  LI,
#                                  SI,
#                                  season,
#                                  runFlat,
                                  price,
#                                  stock,
#                                  delivery,
                                  dzis

                ])
            except:
                print("cos nie tek z dodawaniem do listy", title)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # sleep(2)

    try:
        try:
            close = driver.find_elements_by_xpath("//*[contains(text(), 'Zamknij i nie pokazuj')]")[0]
            close.click()
        except:
            pass
        element = driver.find_element_by_link_text('następna »')
        klasa=element.get_attribute('class')
        if klasa!='jqs-pgn jqs-next pgn':
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
        getproductsFromPage(listaOpon,dzis)
        



# In[5]:


def getproductsFromPage1(listaOpon,rozmiar,dzis,rozmiarySpecjalne):
    rozmiar1=rozmiar[1]+'-'+rozmiar[2]+'-r'+rozmiar[3]
    rozmiar1=rozmiar1.replace('.','-')
    if rozmiar1 in rozmiarySpecjalne:
        rozmiar1 = rozmiarySpecjalne[rozmiar1]
    #adres='http://www.oponeo.pl/wybierz-opony/r=1/'+rozmiar1
    adres_podstawowy='https://sklep.intercars.com.pl/szukaj/opony-201/?cf_szerokosc=195&cf_profil=65&cf_srednica=15%22&cf_sezon=zimowa'
#    adres='https://sklep.intercars.com.pl/szukaj/opony-201/#'
    adres='https://sklep.intercars.com.pl/szukaj/opony-i-felgi-2/'
#    adres='https://sklep.intercars.com.pl/szukaj/opony-201/#cf_srednica=16%22&cf_szerokosc=195&cf_profil=50'
#     adres='http://www.oponeo.pl/wybierz-opony/p=1/pirelli/r=1/195-55-r16' #test
#    try:
#        driver.get(adres_podstawowy)
#    except:
#        print("Nie udało się otworzyć adresu podstawowego")
#    sleep(3)
    try:
        driver.get(adres)
    except:
        print("Nie udało się otworzyć strony dla", rozmiar)
    sleep(3)
#     try:
#         szer=Select(driver.find_element_by_id("_ctTS_ddlDimWidth")).all_selected_options[0].text
#     except:
#         print("nie udalo sie sprawdzic szer dla", rozmiar)
#         raise
#     else:
#         if szer != rozmiar[1]: 
#             print("rozmiar", rozmiar, "niepoprawny")
#             raise
#    try:
#        driver.find_element_by_id("_ctTS_inpPF").clear()
#        driver.find_element_by_id("_ctTS_inpPF").send_keys("0" + "\n")
#    except:
#        print("Nie udało się wpisać min ceny dla", rozmiar)
#    sleep(3)
#    try:
#        driver.find_element_by_id("_ctTS_inpPT").clear()
#        driver.find_element_by_id("_ctTS_inpPT").send_keys("100000" + "\n")
#    except:
#        print("Nie udało się wpisać max ceny dla", rozmiar)
#    sleep(3)
    getproductsFromPage(listaOpon,dzis)


# In[6]:


listaOpon = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
#rozmiaryOpon = pd.read_csv('datasets/typy_opon.csv',dtype='str')
rozmiarySpecjalne = pd.read_csv('datasets/rozmiary_specjalne.csv',dtype='str',header=None)
rozmiarySpecjalne = dict(rozmiarySpecjalne.values)
#rozmiaryOpon1 = rozmiaryOpon.values.tolist()
rozmiaryOpon1 = [['0','195','55','16']] #test
# rozmiaryOpon1 = [['0','33','13.50','16']] #test
for i in rozmiaryOpon1: 
#     if '__OTHER__' not in i and '-' not in i:
    if '__OTHER__' not in i:
#        try:
        getproductsFromPage1(listaOpon,i,dzis,rozmiarySpecjalne)
#        except:
#            print("Nie udało się pobrać danych dla", i)
# listaOpon


# In[17]:


# biezacaBazaOpon = pd.read_csv('datasets/tireDataIC.csv',dtype='str',header=0, sep=';', usecols=[1])
# biezacaBazaOpon = biezacaBazaOpon['link'].values.tolist() 
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
daneOpon=[]
# for referencja in [['/produkty/1578739-pirelli-scorpion-atr-32555-r22-116-h']]:
# for referencja in [['/produkty/364392-pirelli-p-zero-corsa-asimmetrico-28530-r19-98-y-xl-mo-zr-fr']]:
# for referencja in [['/produkty/1221098-23540zr18-federal-asfalt-595-rs-r']]:
for referencja in listaOpon:
    odnosnik=referencja[0]
#     if odnosnik not in biezacaBazaOpon then:
    try:
        adres='https://sklep.intercars.com.pl'+odnosnik
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
    soup=str(soup)
    f=open('datasets/pageBS','w')
    f.write(soup)
    f.close()
    try:
        szer = re.search('<td>Szerokość( \[mm\])?</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(2)
    except:
        print(sys.exc_info())
        szer = '_n/a'
    try:
        profil = re.search('<td>Profil</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        profil = '_n/a'
    try:
        osadzenie = re.search('<td>Średnica( \[mm\])?</td>\n<td class=\"jqs-cf-value\">(.+?)[\"<]<?/td>', soup).group(2)
    except:
        osadzenie = '_n/a'
    try:
        sezon = re.search('<td>Sezon</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if sezon == 'Letnia' or sezon == 'letnia':
            sezon = 'summer'
        elif sezon == 'zimowa':
            sezon = 'winter'
        elif sezon == 'całoroczna':
            sezon = 'allseason'
        else:
            print('Sprawdz nowy rodzaj sezonu dla',referencja)
            sezon = '_n/a'
    except:
        sezon = '_n/a'
    try:
        bieznik = re.search('<td>Bieżnik</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        try:
            bieznik = re.search('<td>Model bieżnika</td>\n<td class=\"jqs-cf-value\"><a class=\"accent\" href=\"(.+?)\">(.+?)</a></td>', soup).group(2)
        except:
            bieznik = '_n/a'
    try:
        zastosowanie = re.search('<td>Zastosowanie</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        zastosowanie = '_n/a'
    try:
        przeznaczenie = re.search('<td>Przeznaczenie</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if przeznaczenie == 'samochody osobowe':
            przeznaczenie = 'CAR'
        elif przeznaczenie == 'samochody dostawcze':
            przeznaczenie = 'LTR'
        elif przeznaczenie == 'samochody terenowe':
            przeznaczenie = 'SUV/4x4'
        else:
            print('Sprawdz nowy rodzaj sezonu dla',referencja)
            przeznaczenie = '_n/a'
    except:
        przeznaczenie = '_n/a'
    try:
        producent = re.search('<td>Producent</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        producent = '_n/a'
    try:
        prod_kod = re.search('<td>Kod producenta</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        prod_kod = '_n/a'
    try:
        LI = re.search('<td>Indeks nośności</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        LI = '_n/a'
    try:
        SI = re.search('<td>Indeks prędkości</td>\n<td class=\"jqs-cf-value\">(.+?) - (.+?)</td>', soup).group(1)
    except:
        SI = '_n/a'
    try:
        DOT = re.search('<td>Data produkcji</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        DOT = '_n/a'
    try:
        RR = re.search('<td>Opór toczenia</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        RR = '_n/a'
    try:
        WG = re.search('<td>Hamowanie na mokrej nawierzchni</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        WG = '_n/a'
    try:
        dB = re.search('<td>Liczba decybeli</td>\n<td class=\"jqs-cf-value\">(.+?) dB</td>', soup).group(1)
    except:
        dB = '_n/a'
    try:
        noise = re.search('<td>Poziom emisji hałasu</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        noise = '_n/a'
    try:
        EAN = re.search('<td>Kod EAN</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        EAN = '_n/a'
    try:
        indeks = re.search('<td>Indeks</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        indeks = '_n/a'
    try:
        rant = re.search('<td>Rant opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if 'Rant ochronny' in rant:
            rant = 'RPB'
        else:
            print('Sprawdz nowy rodzaj rantu dla',referencja)
            rant = '_n/a'
    except:
        rant = '_n/a'
    try:
        budowa = re.search('<td>Budowa opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if 'runflat' in budowa.lower():
            budowa = 'runflat'
        else:
            print('Sprawdz nowy rodzaj rof dla',referencja)
            budowa = '_n/a'
    except:
        budowa = '_n/a'
    try:
        XL = re.search('<td>Nośność opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if 'podwyższony' in XL:
            XL = 'XL'
        else:
            print('Sprawdz nowy rodzaj XL dla',referencja)
            XL = '_n/a'
    except:
        XL = '_n/a'
    try:
        cecha = re.search('<td>Cecha dodatkowa</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if cecha == 'XL - podwyższony indeks nośności':
            XL = 'XL'
            cecha = '_n/a'
    except:
        cecha = '_n/a'
    try:
        klasa = re.search('<td>Klasa opony</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
        if klasa == 'średnia':
            klasa = 'medium'
        elif klasa == 'premium':
            True
        elif klasa == 'budżet':
            klasa = 'budget'
        else:
            print('Sprawdz nowy rodzaj tieru dla',referencja)
            klasa = '_n/a'
    except:
        klasa = '_n/a'
    try:
        indeks = re.search('<td>Indeks</td>\n<td class=\"jqs-cf-value\">(.+?)</td>', soup).group(1)
    except:
        indeks = '_n/a'
    daneOpon.append([odnosnik,
                     szer,
                     profil,
                     osadzenie,
                     LI,
                     SI,
                     sezon,
                     bieznik,
                     zastosowanie,
                     przeznaczenie,
                     RR,
                     WG,
                     dB,
                     noise,
                     producent,
                     prod_kod,
                     EAN,
                     indeks,
                     rant,
                     budowa,
                     cecha,
                     XL,
                     DOT,
                     klasa,
                     dzis])


# In[ ]:


driver.close()


# In[82]:


dane_opon = pd.DataFrame(daneOpon, columns=['link',
                                            'width',
                                            'profile',
                                            'seat',
                                             'LI',
                                             'SI',
                                             'season',
                                             'pattern',
                                             'application',
                                             'tireType',
                                             'RR',
                                             'WG',
                                             'dB',
                                             'noise',
                                             'producer',
                                             'manuf_code',
                                             'EAN',
                                             'ICindex',
                                             'RBP',
                                             'ROF',
                                             'addFeature',
                                             'XL',
                                             'DOT',
                                             'tier',
                                             'dateRetrieved'])
sciezka='datasets/tireDataIC.csv'
if os.path.exists(sciezka):
    dane_opon.to_csv(sciezka,sep=';',decimal=',',mode='a',header=False)
else:
    dane_opon.to_csv(sciezka,sep=';',decimal=',')
    

