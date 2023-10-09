# Imports

import pandas as pd
import requests
import time
from colorama import Fore, Style
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

# Constantes

RESET = Style.RESET_ALL
URL = 'https://www.gasolinerasglp.com/listado-completo/'
GASOLINERAS = 'gasolineras.csv'
PRICES_FILE = 'prices.csv'
gasDB = []

# Funcs


def getURL():
    """Encuentra la dirección url de las gasolineras con GLP

    Returns:
        BeautifulSoup: html en formato BS
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    request = requests.get(URL, headers=headers)
    html = BeautifulSoup(request.text, 'html.parser')
    # with open('page.txt', 'w', encoding='utf-8') as f:
    #     f.write(html.text)
    return html


def getDateTime():
    """Da la fecha en el momento

    Returns:
        str: Año-Mes-Día Hora:Minuto:Segundos
    """
    now = datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    return date


def getGasolinera(ref: str, html):
    """Encuentra los datos de la gasolinera de la hiperreferencia del campo <a> de la web 

    Args:
        ref (str): Referencia de la gasolinera: <a href = "ref">

    Returns:
        identifier (str): Distintos datos de la gasolinera
        price (float): precio, en euros
    """
    # html = getURL()
    # h6 = html.find_all('a', href=ref)
    # identifier = [x.text for x in h6][1]
    # print(identifier.strip())
    try:
        h6 = html.find('a', href=ref).find_next_sibling().contents
    except:
        print(Fore.RED + '[!] Referencia no encontrada' + RESET)
        exit()
    # print(h6)
    price = h6[3].text.strip()
    identifier = h6[5].text.strip()
    return identifier, asPrice(price)


def addGasDB(ref: str, gasDB: pd.DataFrame):
    """Añade una gasolinera a la DB

    Args:
        ref (str): referencia de la gasolinera
        gasDB (pd.DataFrame): DataFrame de gasolineras antigua
    """
    html = getURL()
    identifier, _ = getGasolinera(ref, html)
    ids = [x.strip() for x in identifier.split(',')]
    new_row = {'Provincia': ids[-1],
               'Poblacion': ids[-2], 'Carretera': ids[0]}
    gasDB.loc[ref] = new_row
    saveGasDB(gasDB)


def asPrice(s_price: str):
    """Procesa el precio como lo da la web en formato float

    Args:
        s_price (str): precio en el formato devuelto por la web

    Returns:
        float: precio en formato float
    """
    price = s_price.split('€')[0].strip()
    price = float(price)
    return price


def saveGasDB(gasDB):
    """Guarda la DB de gasolineras en csv

    Args:
        gasDB (pd.DataFrame): DB de gasolineras
    """
    gasDB.to_csv(GASOLINERAS)


def readGasDB():
    """Lee el csv de la DB de gasolineras

    Returns:
        pd.DataFrame: DataBase de gasolineras
    """
    gasDB = pd.read_csv(GASOLINERAS, index_col='ref')
    # print(df.head())
    return gasDB


def getRefID(ref: str):
    """De la referencia completa devuelve solo el identificador

    Args:
        ref (str): referencia completa de la gasolinera

    Returns:
        str: número de identificación
    """
    return ref.split('/')[-2]


def getAllPrices(gasDB: pd.DataFrame):
    """Obtiene los precios de todas las gasolineras 

    Args:
        gasDB (pd.DataFrame): DB de gasolineras

    Returns:
        dict: Diccionario con los nuevos precios, sin Date
    """
    refs = list(gasDB.index)
    html = getURL()
    prices = {}
    for ref in refs:
        ids = getRefID(ref)
        _, prices[ids] = getGasolinera(ref, html)
    # print(prices)
    return prices


def readPrices():
    """Lee el csv con la DB de los precios

    Returns:
        pd.DataFrame: DB con los precios
    """
    pricesDB = pd.read_csv(PRICES_FILE, index_col='Date', parse_dates=True)
    return pricesDB


def actPrices(gasDB):
    """Actualiza los precios con unos nuevos y los guarda en csv

    Args:
        gasDB (pd.DataFrame): Base de datos de las gasolineras
    """
    pricesDB = readPrices()
    pricesDB.loc[getDateTime()] = getAllPrices(gasDB)
    # pricesDB = pd.concat([oldPricesDB, newPricesDB]).reset_index(drop=True)
    savePricesDB(pricesDB)


def savePricesDB(pricesDB: pd.DataFrame):
    """Guarda la DB de precios en CSV

    Args:
        pricesDB (pd.DataFrame): DB de precios
    """
    pricesDB.to_csv(PRICES_FILE)


def deleteFromPricesDB(ref: str):
    pricesDB = readPrices()
    if ref in pricesDB.columns:
        pricesDB.drop(ref, axis=1, inplace=True)
        savePricesDB(pricesDB)
        return True
    else:
        # print(Fore.YELLOW + '[!] Refencia no encontrada.' + RESET)
        return False


def deleteFromGasDB(ref: str):
    # Get row
    gasDB = readGasDB()
    for i in gasDB.index:
        if ref in i:
            gasDB.drop(i, inplace=True)
            saveGasDB(gasDB)
            return True
    else:
        # print(Fore.YELLOW + '[!] Refencia no encontrada.' + RESET)
        return False


def addNewGasToPrice(ref):
    """Añade una nueva gasolinera a la base de datos de los precios, rellenando los valores previos a añadirla
    con valores nan

    Args:
        ref (str): Referencia de la nueva Gasolinera
    """
    pricesDB = readPrices()
    ids = getRefID(ref)
    pricesDB[ids] = 'nan'
    savePricesDB(pricesDB)


def genGraphPrices(pricesDB: pd.DataFrame):
    plt.figure(figsize=(14, 10))
    # xlabels = [x[:8] for x in g.get_xticks()]
    gasDB = readGasDB()
    plotDB = pricesDB.copy()
    n_legend = []
    for i, row in gasDB.iterrows():
        leg = f'{row["Poblacion"]} - {getRefID(i)}'
        n_legend.append(leg)
    # sns.move_legend(g, loc='best', labels=n_legend)
    plotDB.columns = n_legend
    g = sns.lineplot(plotDB)
    # x_ticks = g.get_xticklabels()
    # x_labels = [str(i)[5:-6] for i in plotDB.index]
    plt.xlabel('Fecha')
    plt.ylabel('Precio [€]')
    plt.title('Precio del GLP en las gasolineras próximas.')
    plt.xticks(rotation=45)
    plt.savefig('graf.png')


def decoPrint(func):
    def wrapper(*args, **kwargs):
        print(Fore.LIGHTCYAN_EX + '-'*50 + RESET)
        func(*args, **kwargs)
        print(Fore.LIGHTCYAN_EX + '-'*50 + RESET)

    return wrapper

# Main Functions


def main():

    actions = {
        0: actionExit,
        1: actionShowGasSt,
        2: actionAddGasSt,
        3: actionActPrices,
        4: actionDeleteGasSt,
        5: actionGraphPrices,
        6: actionShowWeb,
        7: actionGetReference,
    }
    while True:
        printMenu()
        action = input(
            Fore.MAGENTA + '[*] Introduce la acción a realizar: ' + RESET)
        if action.isdigit():
            action = int(action)
            actions.get(action, actionDefault)()
        else:
            actionDefault()
        time.sleep(1)


@decoPrint
def actionDefault():
    print(Fore.YELLOW + '[!] Acción no disponible.' + RESET)


def actionExit():
    print(Fore.LIGHTCYAN_EX + '-'*50 + RESET)
    print(Fore.RED + '[*] Saliendo del programa.' + RESET)
    print(Fore.LIGHTCYAN_EX + '-'*50 + RESET)
    exit()


@decoPrint
def actionShowGasSt():
    gasDB = readGasDB()
    for index, gas in gasDB.iterrows():
        print(
            Fore.GREEN + f'{index:30}{gas["Poblacion"]:20}{gas["Provincia"]:20}{gas["Carretera"]}.' + RESET)


@decoPrint
def actionAddGasSt():
    ref = input(
        Fore.MAGENTA + '[*] Introduzca la referencia de la gasolinera: ' + RESET).strip()
    gasDB = readGasDB()
    addGasDB(ref, gasDB)
    addNewGasToPrice(ref)
    print(Fore.GREEN + '[!] Gasolinera introducida correctamente' + RESET)


@decoPrint
def actionActPrices():
    print(Fore.BLUE + '[...] Actualizando precios [...]' + RESET)
    gasDB = readGasDB()
    actPrices(gasDB)
    print(Fore.GREEN + '[!] Precios actualizados correctamente.' + RESET)


@decoPrint
def actionDeleteGasSt():
    ref = input(
        Fore.MAGENTA + 'Introduce la referencia de la gasolinera a eliminar: ' + RESET).strip()
    fromGas = deleteFromGasDB(ref)
    fromPrices = deleteFromPricesDB(ref)
    if fromGas and fromPrices:
        print(Fore.GREEN + f'[!] Gasolinera {ref} eliminada con exito.')
    else:
        print(Fore.YELLOW + f'[!] Refencia {ref} no encontrada.' + RESET)


@decoPrint
def actionGraphPrices():
    print(Fore.BLUE + '[...] Generando gráfica [...]' + RESET)
    pricesDB = readPrices()
    genGraphPrices(pricesDB)
    print(Fore.GREEN + '[!] Gráfica generada correctamente.' + RESET)


@decoPrint
def actionShowWeb():
    print(Fore.GREEN + f"[*] {URL}" + RESET)


@decoPrint
def actionGetReference():
    ref = input(Fore.MAGENTA + '[*] Introduce la referencia: ' + RESET)
    if ref.isdigit():
        gasDB = readGasDB()
        for index, row in gasDB.iterrows():
            if ref in index:
                print(Fore.GREEN +
                      f'[-] {row["Poblacion"]}, {row["Carretera"]}' + RESET)
                break
        else:
            print(Fore.RED + '[!] No se ha encontrado la referencia.')


@decoPrint
def printMenu():
    print(Fore.WHITE + '[1] - Mostrar las Gasolineras Guardadas' + RESET)
    print(Fore.WHITE + '[2] - Añadir Gasolinera' + RESET)
    print(Fore.WHITE + '[3] - Actualizar Precios' + RESET)
    print(Fore.WHITE + '[4] - Quitar Gasolinera' + RESET)
    print(Fore.WHITE + '[5] - Realizar Gráfica de Precios' + RESET)
    print(Fore.WHITE + '[6] - Mostrar URL' + RESET)
    print(Fore.WHITE + '[7] - Hallar referencia' + RESET)


if __name__ == '__main__':

    main()
