from socket import create_server
from sqlite3 import Cursor
from datetime import date, datetime
from time import strftime
import mysql.connector
from mysql.connector import errorcode
import textwrap
#
#modulo da requisiçãp
from this import d
import requests
#dicionario da requisição
import json
#modulo para imprimir o dicionario
import pprint
#
import urllib.parse
import pyodbc

from api2 import CurrentConditionsAPIUrl, CurrentConditionsResponse, LocationAPIUrl
#inserir o token para poder ter acesso aos dados de temperatura
# connection_string = textwrap.dedent
# cnxn:pyodbc.Connection = pyodbc.connect(connection_string) 

# global crsr
# crsr = cnxn.cursor()
# print("Conectado ao banco de dados:")



try:
    db_connection = mysql.connector.connect(host='localhost', user='root', password='#Gf232623', database='climaTempo')
    print("Conexão realizada!")
except mysql.connector.Error as error:
    if error.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database não existe")
    
    elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Nome ou senha estão erradas")
    
    else:
        print(error)

else:
    db_connection.close()


accuweatherAPIKey = "OxVdox0q0JSGnDBNArhMooEvrJXGg3ZA"
mapboxToken = "pk.eyJ1IjoiYXJvbm5pIiwiYSI6ImNsOW9pODVxZDA5MWozcG8weDIzcHZmbDAifQ.-b2S4BKL5xZrbNeb9YPDvA"

dias_semana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']

def pegarCoordenadas():
    r = requests.get('http://www.geoplugin.net/json.gp')
    #verificação de localização, baseado na numeração de erro 200
    if(r.status_code != 200):
        print('Não foi possivel obter a localização.')
        return None
    else:
        try:
            #print(r.text) - dados da requisição http
            localizacao = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = localizacao['geoplugin_latitude']
            coordenadas['log'] = localizacao['geoplugin_longitude']
            return coordenadas
        except:
            return None

def pegarCodigoLocal(lat,long):
    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=" + accuweatherAPIKey + "&q=" + lat + "%2C" + long + "&language=pt-br"

    r = requests.get(LocationAPIUrl)
    if(r.status_code == 401):
        print('Não autorizado.')
    elif(r.status_code != 200):
        print('Não foi possível obter a localização.')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['LocalizedName'] + "," + locationResponse['AdministrativeArea']['LocalizedName'] + "." + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None

def pegarTempoAgora(codigoLocal, nomeLocal):
    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br"

    r = requests.get(CurrentConditionsAPIUrl)
    if(r.status_code != 200):
        print('Não foi possivel obter o clima atual')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoClima = {}
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            return infoClima
        except:
            return None

def pegarPrevisao5Dias(codigoLocal):
    DailyAPIUrl = " http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br&metric=true"

    r = requests.get(DailyAPIUrl)
    if(r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5Dias = []
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['max']=dia['Temperature']['Maximum']['Value']
                climaDia['min']=dia['Temperature']['Maximum']['Value']
                climaDia['clima']=dia['Day']['IconPhrase']
                diaSemana = int(date.fromtimestamp(dia['EpochDate']).strftime("%w"))
                climaDia['dia']=dias_semana[diaSemana]
                infoClima5Dias.append(climaDia)
            return infoClima5Dias
        except:
            return None
    
    ##Inicio do código

def InserindoLeitura(lat, long):
    print("Inserindo leitura no banco...")
    datahora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(datahora)
    try:
        local = pegarCodigoLocal(lat, long)
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])
        crsr.execute('''
        INSERT INTO Local (idLocal, nomeLocal) VALUES (?,?)''', local)
        crsr.commit()
        print("Leitura inserida no banco")
    
    except pyodbc.Error as err:
        cnxn.rollback()
        print("Algo aconteceu: {}".format(err))
