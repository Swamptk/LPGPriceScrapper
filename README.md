# LPG Price Scrapper
CLI app for scrapping and graphing the storical price of Liquified Petroleum Gas in spanish gas stations, thus the app is in spanish.

## Project Description
Easy to use CLI app made with Python which main purpose is to find the live prices of LPG in spanish gas stations. This is done through web scrapping using `requests` and `bs4`.

Data is stored into `.csv` files and managed using `numpy` and `pandas`.

It can be shown to the user with graphs using `matplotlib.pyplot` and `seaborn`, producing a `.png` file. 

## Requirements
In order to run the app you will need the mentioned libraries as well as `colorama` installed in your preferred Python environment (required Python 3.7 or above).

To install the packages in an operative Python environment, run the following `pip` commands:

```bash
pip install numpy
pip install pandas
pip install requests
pip install beautifulsoup4
pip install matplotlib
pip install seaborn
pip install colorama
```

Once all the libraries have been installed, just run the following command to run the app while in the same folder as the `main.py` file:

```bash
python main.py
```

## How to use
Once the app is running, you will see the menu of the app showing the available commands. 

### Adding Gas Stations
The first thing to do when you run the app for the first time is to add the gas stations you want to follow. This is done through the url that is retrieved using the command `[6]`, or the [following link](https://www.gasolinerasglp.com/listado-completo/).

Once in the webpage, find the gas station you want to add and click on it. This will send you to the gas station profile, where you can find its reference in the link. For example, for the following gas station profile link:

https://www.gasolinerasglp.com/alicante/repsol/3478/

The reference would be `3478`.

After getting this reference, go to the app menu and enter command `[2]` to add the gas station by reference.

### Check Followed Gas Stations
Each gas station will be saved in the `gasolineras.csv` file, including:

- `ref`: Its reference, used by the app to retrieve the price data.
- `Provincia`: Spanish province where it is located.
- `Poblacion`: Spanish municipe where it is located.
- `Carretera`: Street where it is located.

You can check this data by opening the file using any text editor, or more specialiced software like `Excel` or `LibreOffice Calc`.

You can also check it using the app menu command `[1]`.

Finally, you can also retrieve a saved gas station information by reference using app menu command `[7]`.

### Update Prices and Graph
Once the desired gas stations are stored and in order to update your data, you just need to run the app menu commands `[3]` and `[5]`.

`[3]` will create (or update if the file already exists) the `prices.csv`, where the price data will be stored. This file contains the following columns:

- `Date`: date when the data was retrieved
- References: a column with the reference number of each gas station followed.

`[5]` will use the data stored in `prices.csv` to generate a graph in the `graph.png` file, which can be open with any image viewer app.

### Unfollow a Gas Station
In order to unfollow a gas station, just enter the app menu command `[4]` and introduce the gas station reference.

## TODO List

- [ ] Translate app to english
- [ ] Several bugfixes
