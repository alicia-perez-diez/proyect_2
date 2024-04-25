def leer_base_de_datos(url1, url2):
    import pandas as pd

    #cargamos la base de datos
    credits_df = pd.read_csv(url1)
    titles_df = pd.read_csv(url2)


    #Eliminamos los espacios en blanco al inicio y al final de las columnas 'name' y 'role' y lo dejamos todo en minuscula en el dataset de credits_df.
    credits_df["name"] = credits_df["name"].str.lower().str.strip()
    credits_df["role"] = credits_df["role"].str.lower().str.strip()

    #Eliminamos la columna character, ya que no es relevante para el objetivo del proyecto en el dataset de credits_df.
    columns_to_drop_credits = ["character"]
    credits_df = credits_df.drop(columns = columns_to_drop_credits, axis = 1)

    #Eliminamos SHOW de la columna 'type' en el dataset de titles_df.
    new_type = ["MOVIE"]
    titles_df = titles_df[titles_df["type"].isin(new_type) == True]

    #Calculamos la media de los dos tipos de valoraciones incluidos en el dataset y creamos una nueva columna con ese valor.
    titles_df["tmdb_score"] = titles_df["tmdb_score"].round(1)
    titles_df["score"] = titles_df[['imdb_score', 'tmdb_score']].mean(axis = 1).round(1)


    #Eliminamos las columnas 'type', 'seasons', 'age_certification' e 'imdb_id' del dataset titles_df porque no son relevantes para el objetivo del proyecto y 'imdb_score' y 'tmdb_score' ya que antes las hemos juntado en 'score'.
    columns_to_drop = ['imdb_score', 'tmdb_score', "type", "age_certification", "seasons", "imdb_id", "tmdb_popularity"]
    titles_df = titles_df.drop(columns = columns_to_drop, axis = 1)

    #Eliminamos el único título nulo que existe en el dataset de titles_df.
    titles_df = titles_df.dropna(subset = ["title"])
    titles_df["title"].isnull().sum()

    """ Eliminamos las filas que no tienen género:
    - Creamos un nuevo dataframe solo con las columnas 'title' y 'genres'.
    - Creamos una lista vacía para añadir el id de los registros sin género.
    - Quitamos corchetes y comillas de los géneros y creamos una lista nueva que tome cada palabra por separado.
    - Si la lista está vacía, la añadimos a la nueva lista.
    - Reseteamos el índice.
    - Eliminamos las filas sin género del dataframe principal.
    """
    grouped_2 = titles_df[["title", "genres"]].reset_index(drop = True)
    grouped_2

    id_to_erase = []

    for name in range(0, len(grouped_2)):
        l = grouped_2.iloc[name]["genres"].replace('[', "").replace("]", "").replace("'", "").split(", ")
        if l[0] == "":
            id_to_erase.append(name)

    titles_df.reset_index(drop = True, inplace = True)
    titles_df = titles_df.drop(id_to_erase, axis = 0).dropna(subset = "genres")
    titles_df = titles_df.reset_index(drop = True)

    #Transformamos los datos de 'genres' a una lista.
    list_genre = []
    for name in range(0, len(titles_df)):
        list_genre.append(titles_df.iloc[name]["genres"].replace('[', "").replace("]", "").replace("'", "").split(", "))
    
    titles_df["genres"] = list_genre

    #Transformamos los datos de production_countries a una lista.
    list_country = []

    for name in range(0, len(titles_df)):
        list_country.append(titles_df.iloc[name]["production_countries"].replace('[', "").replace("]", "").replace("'", "").split(", "))

    titles_df["production_countries"] = list_country

    #Eliminamos los espacios en blanco al inicio y al final y lo dejamos todo en minuscula en las columnas 'title' y 'description' en el dataset de titles_df.
    titles_df["title"] = titles_df["title"].str.lower().str.strip()
    titles_df["description"] = titles_df["description"].str.lower().str.strip()

    #Extraemos 1 vez cada id y lo metemos en una lista.
    id=credits_df.id.unique()

    #Creamos un nuevo data-frame con el id de la película y los nombres de actores y directores.
    df_unique_film = pd.DataFrame(index = id, columns = ["names","directors"])

    #Rellenamos las columnas de nobres de actores y de directores
    for i in df_unique_film.index:
        df_unique_film.loc[i,"names"] = list(credits_df[(credits_df["id"] == i) & (credits_df["role"] == "actor")]["name"])
        df_unique_film.loc[i,"directors"] = list(credits_df[(credits_df["id"] == i) & (credits_df["role"] == "director")]["name"])
    
    #Reseteamos el índice del dataset original.
    titles_df.set_index('id', inplace = True)

    #Unimos el nuevo dataset al original de titles_df para tener toda la información relevante para el objetivo del proyecto en un mismo dataframe.
    total_df = pd.merge(titles_df, df_unique_film, how = 'left', left_index = True, right_index = True)

    return total_df



def graf_paises(df):
    import plotly.graph_objects as go

    #Convertirmos los valores de la columna 'production_countries' en una lista.
    paises = df["production_countries"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")

    pais_total = paises.sum()

    pais_15 = pais_total.sort_values(ascending = False).head(15)

    #En este gráfico circular podemos observar los principales mercados de producción de películas para Netflix.

    fig = go.Figure(data = [go.Pie(labels = list(pais_15.index), values = list(pais_15.values))])

    fig.show()


def graf_cir_generos(df):
    import plotly.graph_objects as go

    #Convertirmos los valores de la columna 'genres' en una lista.
    generos_df = df["genres"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")
    generos_sum = generos_df.sum()

    fig = go.Figure(data = [go.Pie(labels = list(generos_sum.index), values = list(generos_sum.values))])

    fig.show()



def graf_generos(df):
    import pandas as pd
    import numpy as np
    import plotly.express as px

    generos_df = df["genres"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")
    generos_sum = generos_df.sum()
    genero_df = pd.merge(generos_df, df, how = 'left', left_index = True, right_index = True)
    
    result_df = genero_df[list(generos_sum.index)].multiply(genero_df['score'], axis='index').replace(0.0, np.nan).mean().reset_index()

    sum_df = genero_df[list(generos_sum.index)].multiply(genero_df['imdb_votes'], axis='index').replace(0.0, np.nan).sum().reset_index()

    su_resul_df = result_df.merge(sum_df, how='left', left_on='index', right_on='index').rename(columns={'0_x': 'score', '0_y': 'votes'})

    su_resul_df["prom_relative"] = su_resul_df['score'] * (su_resul_df['votes'] / sum(su_resul_df['votes']))

    fig = px.scatter(su_resul_df, x="score", y="votes", size="prom_relative", color="index",
           hover_name="index", log_x=True, size_max=60)
    # Adjust the layout
    fig.update_layout(
        height=800,  # Set the height of the graph
        width=1400   # Set the width of the graph
    )
    fig.show()


def graf_duracion(df):
    import plotly.express as px

    fig = px.scatter(df, x="score", y="runtime", color="release_year",
           hover_name="title", log_x=True)
    # Adjust the layout
    fig.update_layout(
        height=800,  # Set the height of the graph
        width=1800   # Set the width of the graph
    )
    fig.show()

def graf_cir_actores(df):
    import plotly.graph_objects as go
    total_df_not_null = df.dropna(subset = "names")

    actors = total_df_not_null["names"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")

    actor_sum = actors.sum()

    actor_sum_30 = actor_sum.sort_values(ascending = False).head(30)

    fig = go.Figure(data = [go.Pie(labels = list(actor_sum_30.index), values = list(actor_sum_30.values))])
    fig.show()



def graf_actores(df):
    import numpy as np
    import plotly.express as px

    total_df_not_null = df.dropna(subset = "names")

    actors = total_df_not_null["names"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")

    actor_sum = actors.sum()

    actors_score = actors.merge(total_df_not_null[['score', 'imdb_votes']], how="left", left_index=True, right_index=True)

    actor_prome = actors_score[list(actor_sum.index)].multiply(actors_score['score'], axis='index').replace(0, np.nan).mean().reset_index()

    actor_prome = actor_prome.sort_values(by=0, ascending=False).rename(columns={0:"score"})

    actor_vote = actors_score[list(actor_sum.index)].multiply(actors_score['imdb_votes'], axis='index').replace(0, np.nan).sum().reset_index()
    
    ac_resul_df = actor_prome.merge(actor_vote, how='left', left_on='index', right_on='index').rename(columns={0: 'votes'})

    ac_resul_df["prom_relative"] = ac_resul_df['score'] * (ac_resul_df['votes'] / sum(ac_resul_df['votes']))

    ac_resul_df = ac_resul_df.sort_values(by='prom_relative', ascending=False)

    fig = px.histogram(ac_resul_df.head(30), x="index", y="prom_relative", color="prom_relative", marginal="rug", # can be `box`, `violin`
                         hover_data="prom_relative")
    fig.show()


def graf_cir_directores(df):
    import plotly.graph_objects as go

    total_df_not_null = df.dropna(subset = "directors")

    dire = total_df_not_null["directors"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")

    dire_sum = dire.sum()

    dire_sum_30 = dire_sum.sort_values(ascending = False).head(30)
    
    fig = go.Figure(data = [go.Pie(labels = list(dire_sum_30.index), values = list(dire_sum_30.values))])
    fig.show()



def graf_directores(df):
    import numpy as np
    import plotly.express as px

    total_df_not_null = df.dropna(subset = "directors")

    dire = total_df_not_null["directors"].apply(lambda x: ','.join(x)).str.get_dummies(sep = ",")

    dire_sum = dire.sum()

    director_score = dire.merge(total_df_not_null[['score', 'imdb_votes']], how="left", left_index=True, right_index=True)

    director_prome = director_score[list(dire_sum.index)].multiply(director_score['score'], axis='index').replace(0, np.nan).mean().reset_index()
    director_prome = director_prome.sort_values(by=0, ascending=False).rename(columns={0:"score"})

    director_vote = director_score[list(dire_sum.index)].multiply(director_score['imdb_votes'], axis='index').replace(0, np.nan).sum().reset_index()

    dir_resul_df = director_prome.merge(director_vote, how='left', left_on='index', right_on='index').rename(columns={0: 'votes'})

    dir_resul_df["prom_relative"] = dir_resul_df['score'] * (dir_resul_df['votes'] / sum(dir_resul_df['votes']))

    dir_resul_df = dir_resul_df.sort_values(by='prom_relative', ascending=False)

    fig = px.histogram(dir_resul_df.head(30), x="index", y="prom_relative", color="prom_relative", marginal="rug", # can be `box`, `violin`
                         hover_data="score")
    fig.show()