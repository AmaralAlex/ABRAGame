#-------------------------------Algoritmo ABRAgame----------------------------------------------.

import pandas as pd
from matplotlib import pyplot as plt
import keyboard
import os
import time
from collections import deque
import matplotlib.ticker as ticker

#------------------------------------------------------------------------------------------------

def ruta_archivo_csv(ruta_a_pruebaABRA):                 
    contenido = os.listdir(ruta_a_pruebaABRA)             
    seGeneroArchivo = len(contenido)                     
    print(seGeneroArchivo,"Archivo en el directorio pruebaABRA")    
    while seGeneroArchivo !=2:
        contenido = os.listdir(ruta_a_pruebaABRA)       
        seGeneroArchivo = len(contenido)         
    print("Ahora hay ",seGeneroArchivo,"archivos :",contenido) 
    for archivo in contenido:
        if archivo != 'input.ini':
            a = 'C:\pruebaABRA'+ '\\'+archivo      
    return a

#------------------------------------------------------------------------------------------------

def lee_UltimaLinea_csv(ruta_al_csv):
    data = open(ruta_al_csv)
    last_line = data.readlines()[-1]
    data.close()
    return last_line

#------------------------------------------------------------------------------------------------

def cambio_de_linea(ruta_csv):
    starTime = time.time()
    finArchivo = False
    last_line = lee_UltimaLinea_csv(ruta)
    last_last_line = last_line
    while last_last_line == last_line and (finArchivo == False):
        last_last_line = lee_UltimaLinea_csv(ruta)
        tiempo_trascurrido = time.time()-starTime
        finArchivo = (tiempo_trascurrido > 10)
    return [finArchivo,last_last_line]

#------------------------------------------------------------------------------------------------

def inicializacion_colaLatencia_Y_Area(last_line,cola_latencia,area):
    nombreLista = last_line.split(',')
    AverageNetworkLatency = int(nombreLista[9])
    cola_latencia.append(AverageNetworkLatency)
    area = area + AverageNetworkLatency
    return [cola_latencia,area]

#------------------------------------------------------------------------------------------------

def inicialización_colaEstimatedBandwidth(last_line,colaEstimatedBandwidth,EstBand):
    estBand = EstBand
    nombreLista = last_line.split(',')
    receivedBytes = int(nombreLista[0])
    estBand = receivedBytes*16 + estBand
    colaEstimatedBandwidth.append(receivedBytes*16)
    return [estBand,colaEstimatedBandwidth]
   
#------------------------------------------------------------------------------------------------       

def actuaclización_cola_Latencia(last_line, colaLatencia , area):
    nombreLista = last_line.split(',')
    AverageNetworkLatency = int(nombreLista[9])
    sacoDLaCola = colaLatencia.popleft()
    nuevoEnCola = AverageNetworkLatency
    colaLatencia.append(nuevoEnCola)
    area = area + nuevoEnCola - sacoDLaCola
    return[colaLatencia,area] 

#------------------------------------------------------------------------------------------------

def actualizacion_cola_estimatedBand(last_line,colaEstimatedBandwidth,EstBand):
    colaEStBand = colaEstimatedBandwidth
    nombreLista = last_line.split(',')
    estBand = EstBand 
    nuevoByte = int(nombreLista[0])
    sacoEstBand = colaEStBand.popleft()     
    colaEStBand.append(nuevoByte*16)        
    estBand = estBand + nuevoByte*16-sacoEstBand
    return [estBand,colaEStBand]    

#------------------------------------------------------------------------------------------------

def bajar_tasa(cantidad_bajadas):
    for q in range(cantidad_bajadas):
        keyboard.press("F8")
        time.sleep(0.02)

#------------------------------------------------------------------------------------------------

def graficas(tiempos_de_prediccion):
    df = pd.read_csv(ruta)
    df =df.assign(miEstimaciónAnchoDeBand =0)
    filtro = df['estimatedBandWidth'] > 0
    df=df[filtro]
    df['miEstimaciónAnchoDeBand']= df['estimatedBandWidth'].rolling(25).mean()
    
    def formatoHora(entrada):
        import math
        a= entrada
        b = (a/3600000)
        hora = math.floor(b)
        c= (b-hora)*60-math.floor((df.iloc[0,7]/3600000-math.floor(df.iloc[0,7]/3600000))*60)
        minuto = math.floor(c)
        d =(c-minuto)*60
        segundo = math.floor(d)
        milis=math.floor((d-segundo)*1000)
        horaf =str(str(minuto) + ":"+ str(segundo) +  ":"+ str(str(milis) + "ms"))
        return horaf
    
    for i in range(100):
        df.iloc[i,18]= df.iloc[100,18]
        
    df['AverageNetworkLatency']= df['AverageNetworkLatency'].rolling(25).mean()
    for i in range(100):
        df.iloc[i,9]= df.iloc[100,9]
    
    plt.rcParams["figure.figsize"] = [40, 40]
    plt.rcParams["figure.autolayout"] = True
    fig, axs = plt.subplots(3)
    
    [fin,y]= df.shape
    maximaLatencia = max(df['AverageNetworkLatency'].max(),0)
    maximoAnchoDeBanda =max(df['AvgBitrate'].max(),df['miEstimaciónAnchoDeBand'].max())
    
    axs[0].plot(df['timestamEstadisticas'],df['framesLost'])
    axs[0].set_title('Frames Lost', fontsize = 70)
    axs[0].set_ylim(0,df['framesLost'].max()+2)
    axs[0].grid()
    tiks_t =ticker.FuncFormatter(lambda x, pos: formatoHora(x))
    axs[0].xaxis.set_major_formatter(tiks_t) 
    axs[0].tick_params(labelsize = 30)              
    axs[0].set_xlim(df.iloc[0,7],df.iloc[fin-1,7])
    
    axs[1].plot(df['timestamEstadisticas'], df['AverageNetworkLatency'],color='k',linewidth= 3)
    axs[1].set_title('Average Network Latency (ms)', fontsize = 70)
    axs[1].set_ylim(0,maximaLatencia+0.1*maximaLatencia)
    axs[1].set_xlim(df.iloc[0,7],df.iloc[fin-1,7])
    axs[1].grid()
    axs[1].xaxis.set_major_formatter(tiks_t)
    axs[1].tick_params(labelsize = 30)              
    
    axs[2].plot(df['timestamEstadisticas'], df['AvgBitrate'],color='darkblue',linewidth= 3, label = "AvgBitrate")
    axs[2].plot(df['timestamEstadisticas'],df['miEstimaciónAnchoDeBand'],color='k',linewidth= 4,label = " ABRAGame_estimatedBandWidth")
    axs[2].set_ylim(0,maximoAnchoDeBanda+0.1*maximoAnchoDeBanda)
    axs[2].set_xlim(df.iloc[0,7],df.iloc[fin-1,7])
    axs[2].grid()
    axs[2].set_title('Estimated Bandwidth (bit/s)',fontsize = 70)
    axs[2].xaxis.set_major_formatter(tiks_t)
    axs[2].tick_params(labelsize = 30)              
    
    for i in range(len(tiempos_de_prediccion)):
        detectoAlgo=int(tiempos_de_prediccion.popleft())
        axs[0].axvline(detectoAlgo,color='Purple',ls=':',linewidth= 4)
        axs[0].text(detectoAlgo, 0.8*df['framesLost'].max()+1, 'Prediction', fontsize=40, color='purple', rotation=90)
        axs[1].axvline(detectoAlgo,color='Purple',ls=':',linewidth= 4)
        axs[1].text(detectoAlgo, 0.8*maximaLatencia, 'Prediction', fontsize=40, color='purple', rotation=90)
        axs[2].axvline(detectoAlgo,color='Purple',ls=':',linewidth= 4)
        axs[2].text(detectoAlgo, 0.8*maximoAnchoDeBanda, 'Prediction', fontsize=40, color='purple', rotation=90)
    
    plt.legend(fontsize = 35)
    plt.show()
    
#------------------------------------------------------------------------------------------------

area = 0
umbral =2000
colaEstimatedBandwidth = deque()
colaDeDegradaciones= deque()
cola_latencia = deque()
almenosUna = False
EstBand = 0
j=0
#------------------------------------------------------------------------------------------------

ruta = ruta_archivo_csv('C:\pruebaABRA')
no_es_finArchivo = False
down_bitrate_step = 500000
margenBanda = 1500000
inicial_avgBitrate = 10000000/1.2
tiempo_Inicial = 0

#------------------------------------------------------------------------------------------------
for i in range(25):
    last_line = cambio_de_linea(ruta)[1]
    datos_utilesE = inicialización_colaEstimatedBandwidth(last_line,colaEstimatedBandwidth,EstBand)
    datos_utilesA = inicializacion_colaLatencia_Y_Area(last_line,cola_latencia,area)
    EstBand = datos_utilesE[0]
    colaEstimatedBandwidth = datos_utilesE[1]
    area = datos_utilesA[1]
    cola_latencia = datos_utilesA[0]
    j= j+1

#------------------------------------------------------------------------------------------------

while (no_es_finArchivo)== False:
    j=j+1
    datos_utiles = cambio_de_linea(ruta)
    no_es_finArchivo = datos_utiles[0]
    t_valido = datos_utiles[1].split(',')[7]
    latenciaMinima =int(datos_utiles[1].split(',')[9])
    if t_valido!='0' and j > 500 :
        varAuxLatencia = actuaclización_cola_Latencia(datos_utiles[1], cola_latencia , area)
        area = varAuxLatencia[1]
        cola_latencia = varAuxLatencia[0]
        varAuxEstBand = actualizacion_cola_estimatedBand(datos_utiles[1],colaEstimatedBandwidth,EstBand)
        EstBand = varAuxEstBand[0]
        AvgBitrate = int(datos_utiles[1].split(',')[14])
        colaEstimatedBandwidth = varAuxEstBand[1]
        tiempo_transcurrido = time.time()-tiempo_Inicial

        if area > umbral and t_valido!='0' and tiempo_transcurrido > 2:
            colaDeDegradaciones.append(int(t_valido))
            almenosUna = True
        
            cantidad_Bajadas = int((AvgBitrate-EstBand+margenBanda)/(down_bitrate_step*0.85))
            bajar_tasa(cantidad_Bajadas)
        
            tiempo_Inicial = time.time()        
            print(j, " | EstBW =",EstBand," | AvgBitrate =",AvgBitrate," | Cantidad de bajadas = ",cantidad_Bajadas)
                   
        else:
            tiempo_transcurrido = time.time()-tiempo_Inicial
            if latenciaMinima<80 and almenosUna and tiempo_transcurrido > 20:
                keyboard.press("F9")
                tiempo_Inicial = time.time()
                print("Subiendo la tasa. Aumenta el AvgBitRate en 0.5 Mbits ")
                print(j,"|AvgBitrate = ",AvgBitrate," | EstBW =",EstBand)
                
    
graficas(colaDeDegradaciones)

print("................................ABRAGame.............................")
print("..............................END THE GAME...........................")

