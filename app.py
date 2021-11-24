# importando bibliotecas e pacotes
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as sct
from math import sqrt
import matplotlib.pyplot as plt
import seaborn as sns
#import statistics as st

import logging
import random
#import statistics
from dataclasses import dataclass
from datetime import timedelta
from itertools import groupby, product
import math
import simpy

#Bibliotecas de visualização de imagem
from PIL import Image

# configuração para não exibir os warnings
import warnings
warnings.filterwarnings("ignore")

class Hora:
  # formata tempo retornando horas, minutos, segundos
  def formatarTempo(tempo):
    hours = int(tempo / 60)
    minutes = int(tempo - hours * 60)
    seconds = int(round(tempo % 1 * 60))
    return round(hours), round(minutes), round(seconds)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def executar(equipamento):
	global dt  # Para poder acessar a variável dt declarada acima
	R = random.random()  # Pegue um número aleatório e armazene-o em R
	tempo = TEMPO_MANUTENCAO_MAX - TEMPO_MANUTENCAO_MINIMO  
	tempo_manutencao = TEMPO_MANUTENCAO_MINIMO + (tempo*R) # Distribuição uniforme
	# tempo_manutencao =  tempo_manutencao / 2
	yield env.timeout(tempo_manutencao) # deixe o tempo correr n minutos
	h, m, s = Hora.formatarTempo(tempo_manutencao)
	st.write("\o/  A manutencao do %s dura %.2f minutos ou (%s:%s:%s)" % (equipamento,tempo_manutencao, h, m, s))
	dt = dt + tempo_manutencao # Acumule os tempos de uso do i
 
def equipamento (env, name, fila ):
	global te
	global fin
	#	fHoras, fMinutos, fSegundos = formatarTempo(chega)
 	# fHora = fHoras + ":" + fMinutos + ":" + fSegundos
	h, m, s = Hora.formatarTempo(env.now)
	# hs = h + ":" + m + ":" + s
	chega = env.now # Salve o minuto de chegada do equipamento
	st.write("---> O (%s) chega em (%.2f) minutos ou (%s:%s:%s)" % (name, chega, h, m, s))
	# logging.debug(fila)
	with fila.request() as request: # Espere sua vez
		yield request # Obter a vez
		passa = env.now # Economize o minuto quando começar a ser atendido
		espera = passa - chega # Calcule o tempo que espero
		te = te + espera # Acumule tempos de espera
		h, m, s = Hora.formatarTempo(passa)
		st.write("**** %s começa a manutenção em  (%.2f)  minutos tendo esperado %.2f (%s:%s:%s) " % (name, passa, espera, h, m, s))
		yield env.process(executar(name)) # Invoca al proceso executar
		sai = env.now # Salva o minuto em que o processo de execucao termina
		h, m, s = Hora.formatarTempo(sai)
		st.write(" <--- %s deixou a oficina em minuto (%.2f) (%s:%s:%s) \n " % (name, sai, h, m, s))
		fin = sai # Preserva globalmente o último minuto da simulação
	
  #-------------------------------------------------------------------- ESTATISTICO ----------------------------------------------------------
def principal (env, fila):
	chegada = 0
	i = 0
	for i in range(TOT_EQUIPAMENTOS): # Para n equipamentos
		R = random.random()
		chegada = -T_CHEGADAS * math.log(R) # Distribuição exponencial
		yield env.timeout(chegada)  # Deixe passar um tempo entre um e outro
		i += 1
		env.process(equipamento(env, 'Equipamento  %d' % i, fila)) 

#st.set_page_config(page_title='Sistema de recomendação', page_icon = 'patrus_icon.png', layout="wide")
#st.set_page_config(page_title='Datatube', layout="wide")
st.set_page_config(layout="wide")
local_css('style.css')
col1, col2 = st.beta_columns((3,1))
col1.write("""# Simulação de Eventos Discretos""")
#col2.image('https://www.coppead.ufrj.br/wp-content/uploads/2020/09/logo_coppead_mobile.png')
datasetgerais= pd.read_excel('dados_gerais.xlsx')
dataset= pd.read_excel('duracao.xlsx')

logging.basicConfig(level=logging.DEBUG)

col1, col2, col3 = st.beta_columns((1,1,1))
TOT_EQUIPAMENTOS = col1.number_input('Número de equipamentos',min_value=1)
NUM_EMPREGADOS = col2.number_input('Número de empregados',min_value=1)
NUM_EMP_EQUIPE = col3.number_input('Número de empregados por equipe',min_value=1)


TEMPO_MANUTENCAO_MINIMO = 135   # minimo de (45 minutos)  3 pessoas 45 min para reparar, logo, 1 pessoa sozinha levaria 135min. 
TEMPO_MANUTENCAO_MAX = 390      # maximo de (130 minutos) 3 pessoas 130 min para reparar, logo, 1 pessoa sozinha levaria 390min.


T_CHEGADAS = 170                 # em média os equipamentos chegam a cada (120) min - 2:50 horas
TEMPO_SIMULACAO = 1440                  #24horas (1440)    
seed = 30                               # numero de blocos a cada bloco de simulacao


# calcular equipe
TEMPO_MANUTENCAO_MINIMO = TEMPO_MANUTENCAO_MINIMO / NUM_EMP_EQUIPE           
TEMPO_MANUTENCAO_MAX = TEMPO_MANUTENCAO_MAX / NUM_EMP_EQUIPE
EQUIPES = NUM_EMPREGADOS // NUM_EMP_EQUIPE
 
te  = 0.0 # tempo de espera total
dt  = 0.0 # duracao servico total
fin = 0.0 # minuto em que finaliza

col1, col2, col3 = st.beta_columns((1,1,1))
simular = col2.button('Simular')

if simular:
    random.seed (seed)  
    env = simpy.Environment() # Crie o objeto de ambiente de simulação
    fila = simpy.Resource(env, EQUIPES) # Crie os recursos (equipamentos)
    env.process(principal(env, fila)) # Invoque o processo principal
    #env.run() # Comece a simulação

    env.run(until = TEMPO_SIMULACAO)

    string = f'Para {TOT_EQUIPAMENTOS} equipamentos, Com {NUM_EMPREGADOS} empregados, colocando {NUM_EMP_EQUIPE} empregados em cada equipe, será formado {EQUIPES} equipes. |   o tempo manutenção será: {TEMPO_MANUTENCAO_MINIMO} à {TEMPO_MANUTENCAO_MAX} min'

    st.write(string)
