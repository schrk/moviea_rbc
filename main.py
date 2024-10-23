import pandas as pd
import tkinter as tk
from pandastable import Table
import numpy as np

# Pré-processamento dos Dados
df = pd.read_csv('movies.csv', delimiter=',', quotechar='"', encoding='utf-8', on_bad_lines='skip')

# Limpeza das colunas de texto
text_columns = ['Released_Year', 'Runtime', 'IMDB_Rating', 'Series_Title', 'Genre', 'Director', 'Star1']
for col in text_columns:
    df[col] = df[col].astype(str).str.strip()

# Converter 'Released_Year' para numérico
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
df.dropna(subset=['Released_Year'], inplace=True)
df['Released_Year'] = df['Released_Year'].astype(int)

# Processar 'Runtime'
df['Runtime'] = df['Runtime'].str.replace(' min', '', regex=False)
df['Runtime'] = pd.to_numeric(df['Runtime'], errors='coerce')
df.dropna(subset=['Runtime'], inplace=True)
df['Runtime'] = df['Runtime'].astype(int)

# Converter 'IMDB_Rating' para numérico
df['IMDB_Rating'] = pd.to_numeric(df['IMDB_Rating'], errors='coerce')
df.dropna(subset=['IMDB_Rating'], inplace=True)

# Resetar o índice
df.reset_index(drop=True, inplace=True)

# Funções auxiliares
def obter_titulo_por_indice(indice):
    return df.loc[indice, 'Series_Title']

def obter_indice_por_titulo(titulo):
    resultado = df[df['Series_Title'].str.lower() == titulo.lower()]
    if len(resultado) == 0:
        return None
    else:
        return resultado.index.values[0]

# Solicitar entrada do usuário
filme_entrada = input("Digite o título de um filme: ")

# Obter índice do filme de entrada
indice_entrada = obter_indice_por_titulo(filme_entrada)
if indice_entrada is None:
    print("Filme não encontrado no conjunto de dados.")
    exit()

# Obter os dados do filme de entrada
filme_entrada_dados = df.loc[indice_entrada]

# Cálculo das Similaridades Individuais
similaridades = []

# Máximas diferenças para normalização
max_diff_year = df['Released_Year'].max() - df['Released_Year'].min()
max_diff_runtime = df['Runtime'].max() - df['Runtime'].min()
max_diff_rating = 10  # IMDB Rating varia de 0 a 10

# Lista de gêneros únicos para normalização (opcional)
# unique_genres = set()
# for genres in df['Genre']:
#     unique_genres.update(genres.split(', '))

for indice, linha in df.iterrows():
    # Inicializar dicionário para armazenar similaridades
    sim = {}

    # 1. Similaridade de Released_Year (Ano de Lançamento)
    ano_caso = linha['Released_Year']
    ano_entrada = filme_entrada_dados['Released_Year']
    sim_ano = 1 - abs(ano_caso - ano_entrada) / max_diff_year
    sim['Similaridade_Ano'] = sim_ano

    # 2. Similaridade de Runtime (Duração)
    duracao_caso = linha['Runtime']
    duracao_entrada = filme_entrada_dados['Runtime']
    sim_duracao = 1 - abs(duracao_caso - duracao_entrada) / max_diff_runtime
    sim['Similaridade_Duracao'] = sim_duracao

    # 3. Similaridade de Genre (Gênero)
    generos_caso = set(linha['Genre'].split(', '))
    generos_entrada = set(filme_entrada_dados['Genre'].split(', '))

    intersecao = generos_caso.intersection(generos_entrada)
    uniao = generos_caso.union(generos_entrada)

    if len(uniao) > 0:
        sim_genero = len(intersecao) / len(uniao)
    else:
        sim_genero = 0
    sim['Similaridade_Genero'] = sim_genero

    # 4. Similaridade de IMDB_Rating (Nota IMDB)
    rating_caso = linha['IMDB_Rating']
    rating_entrada = filme_entrada_dados['IMDB_Rating']
    sim_rating = 1 - abs(rating_caso - rating_entrada) / max_diff_rating
    sim['Similaridade_Rating'] = sim_rating

    # 5. Similaridade de Director (Diretor)
    diretor_caso = linha['Director']
    diretor_entrada = filme_entrada_dados['Director']
    sim_diretor = 1.0 if diretor_caso.lower() == diretor_entrada.lower() else 0.0
    sim['Similaridade_Diretor'] = sim_diretor

    # 6. Similaridade de Star1 (Ator Principal)
    ator_caso = linha['Star1']
    ator_entrada = filme_entrada_dados['Star1']
    sim_ator = 1.0 if ator_caso.lower() == ator_entrada.lower() else 0.0
    sim['Similaridade_Ator'] = sim_ator

    # Cálculo da Similaridade Total (média das similaridades individuais)
    sim_total = np.mean(list(sim.values()))
    sim['Similaridade_Total'] = sim_total

    # Adicionar informações do filme e similaridades à lista
    similaridades.append({
        'Título': linha['Series_Title'],
        'Gênero': linha['Genre'],
        'Diretor': linha['Director'],
        'Ator Principal': linha['Star1'],
        'Ano de Lançamento': linha['Released_Year'],
        'Duração (min)': linha['Runtime'],
        'IMDB Rating': linha['IMDB_Rating'],
        'Similaridade_Ano': sim_ano,
        'Similaridade_Duracao': sim_duracao,
        'Similaridade_Genero': sim_genero,
        'Similaridade_Rating': sim_rating,
        'Similaridade_Diretor': sim_diretor,
        'Similaridade_Ator': sim_ator,
        'Similaridade_Total': sim_total
    })

# Converter a lista em um DataFrame
df_similaridade = pd.DataFrame(similaridades)

# Ordenar os filmes pela Similaridade Total em ordem decrescente
df_similaridade.sort_values(by='Similaridade_Total', ascending=False, inplace=True)

# Exibir a tabela em uma GUI
root = tk.Tk()
root.title("Filmes Similares")

# Definir o tamanho da janela
root.geometry("1200x600")

# Criar um frame para a tabela
frame = tk.Frame(root)
frame.pack(fill='both', expand=True)

# Criar a tabela usando pandastable
tabela = Table(frame, dataframe=df_similaridade, showtoolbar=True, showstatusbar=True)
tabela.show()

# Iniciar o loop da GUI
root.mainloop()
