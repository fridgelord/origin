
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from time import sleep
import re
import datetime
import os
import sys
import platform
import shutil


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


# In[2]:


hostname = platform.node()
chromePath = shutil.which('chromedriver')
options = webdriver.ChromeOptions()
if hostname == 'user-Vostro-260':
    options.add_argument('headless')
driver = webdriver.Chrome(chromePath, chrome_options=options)


# In[3]:


#driver = webdriver.Chrome('C:\chromedriver.exe')  # Optional argument, if not specified will search path.
# https://regex101.com/
#driver.get('http://www.oponeo.pl/wybierz-opony/s=1/letnie/t=1/osobowe/r=1/195-55-r16')


# In[4]:


def getproductsFromPage(listaOpon,dzis):
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')
    products = soup.findAll(True, {'class': 'product'})
    for prod in products:
        if('class="productName"' in str(prod)):
            try:
                title = re.search('(?<=\" title=\")(.*?)(?=\">)', str(prod).replace("\n", "")).group(0)
            except:
                title = 'n/a'
            try:
                stock = int(re.search('\d+',re.search('(?<=class=\"stockLevel\">)(.*?)(?=w mag)', str(prod).replace("\n", "")).group(0)).group(0))
            except:
#                print("Nie udalo si pobrac stock dla", title)
                stock=0
    
            runFlat=False
            if str(prod).find('Run Flat') != -1:
                runFlat=True
            try:
                LI = re.search('(?<=Indeks nośności )(.*?)(?= – maksymalne)', str(prod).replace("\n", "")).group(0)
            except:
                LI = 'n/a'
            try:
                SI = re.search('(?<=Indeks prędkości )(.*?)(?= – maksymalna)', str(prod).replace("\n", "")).group(0)
            except:
                SI = 'n/a'
                
            if str(prod).find('<span class="tooltip">Opona letnia z homologacją zimową.</span>') != -1:
                season="allseason"
            elif str(prod).find('<span class="tooltip">Opona na sezon letni.</span>') != -1:
                season="summer"
            elif str(prod).find('<span class="tooltip">Opona na sezon zimowy.</span>') != -1:
                season="winter"
            elif str(prod).find('<span class="tooltip">Opona całoroczna.</span>') != -1:
                season="allseason"
            else:
                season="nieznany"
                print("sprawdz nowy rodzaj sezonu", title)
                
            if str(prod).find('<strong>24h</strong>') != -1:
                delivery='24h'
            elif str(prod).find('<strong>już jutro!</strong>') != -1:
                delivery='24h'
            elif str(prod).find('Zapytaj o termin dostawy') != -1:
                delivery='ask'
            elif str(prod).find('Doręczymy') != -1:
                delivery=re.search('(?<=Doręczymy  <strong>).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('dzień roboczy') != -1:
                delivery=re.search('(?<=<strong>).*? dzień roboczy(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('dni robocz') != -1:
                try:
               	    delivery=re.search('(?<=<strong class=\"\">).*? dni robocz(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
                except:
                    delivery=re.search('(?<=<strong>).*? dni robocz(?=.*?<\/strong>)', str(prod).replace("\n", "")).group(0)
            elif str(prod).find('<strong class=" futureSupply">') != -1:
                delivery=re.search('(?<=<strong class=\" futureSupply\">).*?(?=<\/strong>)', str(prod).replace("\n", "")).group(0)
            else:
                delivery="nieznany"
                print("sprawdz nowy rodzaj dostawy", title)
            
            try:
                price = re.search('(?<=<span class=\"price size-[0-9]\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
                price = price.replace(chr(160),'')
                price = int(price)
            except:
                price = np.nan
                print("sprawdz brak ceny", title)

            try:
                link = re.search('(?<=<a href=\")(.*?)(?=\" title)', str(prod).replace("\n", "")).group(0)
            except:
                link = 'n/a'
                print("sprawdz brak linka", title)
            try:
                producer = re.search('(?<=<span class=\"producer\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0) 
            except:
                producer = 'n/a'
                print("sprawdz brak producenta", title)
            try:
                model = re.search('(?<=<span class=\"model\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
            except:
                model = 'n/a'
                print("sprawdz brak modelu", title)
            try:
                size = re.search('(?<=<span class=\"size\">)(.*?)(?=</span>)', str(prod).replace("\n", "")).group(0)
            except:
                size = 'n/a'
                print("sprawdz brak rozmiaru", title)
                
# oponyExmp = pd.DataFrame(listaOpon, columns=['link', 'title', 'producer', 'model', 'size'\
#     , 'li', 'si', 'season', 'runFlat', 'price', "stock", 'delivery'])
                
            try:
                listaOpon.append([link,
                                  title, 
                                  producer,
                                  model,
                                  size,
                                  LI,
                                  SI,
                                  season,
                                  runFlat,
                                  price,
                                  stock,
                                  delivery,
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
        element = driver.find_element_by_id("_ctPgrp_pgtnni")
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
    adres='http://www.oponeo.pl/wybierz-opony/r=1/'+rozmiar1
#     adres='http://www.oponeo.pl/wybierz-opony/p=1/pirelli/r=1/195-55-r16' #test
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
    try:
        driver.find_element_by_id("_ctTS_inpPF").clear()
        driver.find_element_by_id("_ctTS_inpPF").send_keys("0" + "\n")
    except:
        print("Nie udało się wpisać min ceny dla", rozmiar)
    sleep(3)
    try:
        driver.find_element_by_id("_ctTS_inpPT").clear()
        driver.find_element_by_id("_ctTS_inpPT").send_keys("100000" + "\n")
    except:
        print("Nie udało się wpisać max ceny dla", rozmiar)
    sleep(3)
    getproductsFromPage(listaOpon,dzis)


# In[6]:


# %%time
listaOpon = []
now = datetime.datetime.now()
dzis = now.isoformat()[:10]
rozmiaryOpon = pd.read_csv('datasets/typy_opon.csv',dtype='str')
rozmiarySpecjalne = pd.read_csv('datasets/rozmiary_specjalne.csv',dtype='str',header=None)
rozmiarySpecjalne = dict(rozmiarySpecjalne.values)
rozmiaryOpon1 = rozmiaryOpon.values.tolist()
#rozmiaryOpon1 = [['0','195','55','16'],['1','255','50','18']] #test
#rozmiaryOpon1 = [['1','185','60','15']] #test
#rozmiaryOpon1 = [['0','33','13.50','16']] #test
for i in rozmiaryOpon1: 
#     if '__OTHER__' not in i and '-' not in i:
    if '__OTHER__' not in i:
        try:
             getproductsFromPage1(listaOpon,i,dzis,rozmiarySpecjalne)
        except:
            print("Nie udało się pobrać danych dla", i)
# listaOpon


driver.quit()


oponyExmp = pd.DataFrame(listaOpon, columns=['link', 'title', 'producer', 'model', 'size', 'li', 'si', 'season', 'runFlat', 'price', "stock", 'delivery', 'date'])
sciezka='datasets/oponyExmp2.csv'
if os.path.exists(sciezka):
    oponyExmp.to_csv(sciezka,mode='a',header=False,sep=';',decimal=',')
else:
    oponyExmp.to_csv(sciezka,sep=';',decimal=',')
sciezka2='/mnt/scraping/oponyExmp2.csv'
try:
    if os.path.exists(sciezka2):
        oponyExmp.to_csv(sciezka2,mode='a',header=False,sep=';',decimal=',')
    else:
        oponyExmp.to_csv(sciezka2,sep=';',decimal=',')
except:
    print("Nie udalo sie zapisac na dysku sieciowym")

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
