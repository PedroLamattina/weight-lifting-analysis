def Transformación_Medallas(df):
    # Use pd.melt to transform the medal columns into rows
    df_melted = pd.melt(df, id_vars=['Eventos', 'Año', 'Genero'], 
                        value_vars=['Oro', 'Plata', 'Bronce'], 
                        var_name='Medalla', value_name='Atleta')
    
    # Select and order columns in the desired format
    df = df_melted[['Eventos', 'Año', 'Genero', 'Medalla', 'Atleta']]
    
    return df

def Eventos_Fechas(df):
    # Split 'Eventos' into 'Eventos' and 'Fechas' columns
    df_aux = pd.DataFrame(df['Eventos'].str.split('(').to_list(), columns=['Eventos', 'Fechas'])
    df_aux['Fechas'] = df_aux['Fechas'].str.replace(')', '', regex=False)
    
    # Update the original DataFrame with split values
    df['Eventos'] = df_aux['Eventos']
    df['Fechas'] = df_aux['Fechas']
    
    # Combine 'Fechas' with 'Año' and format dates
    df['Fechas'] = df['Fechas'] + '.' + df['Año'].astype(str)
    df['Fechas'] = df['Fechas'].str.replace('.', '-')
    
    # Convert 'Fechas' to datetime format
    df['Fechas'] = pd.to_datetime(df['Fechas'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
    
    return df  

def extract_athlete_info(df):
    name_pattern = r'(^\w+ )'  # First name
    last_name_pattern = r'^\w+\s+(\w+)'  # Last name
    # country_pattern = r"([A-Za-záéíóúÁÉÍÓÚñÑ]+)"
    
    country_pattern = r"([A-Za-záéíóúÁÉÍÓÚñÑ]+)\s+\d+"  # Country before a number
    category_pattern = r'(\d+)'  # Category (numeric) in Eventos column

    # Additional replacement for 'AIN' variants to 'Bielorusia'
    # df['Atleta'] = df['Atleta'].str.replace(r"AIN(?:\s+AIN)?(?:\s+\[a 1\])?", 'Bielorrusia', regex=True)

    # Remove bracketed numbers and replace "Reino Unido" with "ReinoUnido"
    df['Atleta'] = df['Atleta'].str.replace(r"\[\d+\]", '', regex=True)
    df['Atleta'] = df['Atleta'].str.replace(r"Reino Unido", 'ReinoUnido', regex=True)

    #     
    # df['Atleta'] = df['Atleta'].str.replace(r"AIN AIN\[\s*a\s*1\s*\]", 'Bielorrusia', regex=True)
    for column in ['Atleta']:
        # Remove any remaining '[a 1]' in the 'Atleta' column
        df[column] = df[column].str.replace(r'\[a 1\]', '', regex=True)
        # Additional replacement for 'AIN' variants to 'Bielorrusia'
        df[column] = df[column].str.replace(r"AIN AIN\[\s*a\s*1\s*\]", 'Bielorrusia', regex=True)


    # Extract Name, Last Name, and Country
    df['Nombre'] = df['Atleta'].str.extract(name_pattern)
    df['Apellido'] = df['Atleta'].str.extract(last_name_pattern)
    df['Pais'] = df['Atleta'].str.extract(country_pattern)

    # Fill NaN values in 'Pais' with 'Bielorrusia'
    df['Pais'] = df['Pais'].fillna('Bielorrusia')

    # Extract Category from Eventos column
    df['Categoria'] = df['Eventos'].str.extract(category_pattern)

    # Display the DataFrame structure and a preview of the data
    print(df.info())
    return df

def puntaje_atleta(df):
    # Define the patterns for extraction
    arrancada_pattern = r'(\d+)'                     # Captures any initial number
    dos_tiempos_pattern = r'\d+\s*\+\s*(\d+)'        # Captures any number after '+'

    # Standardize the format: add a space after '+' only if missing
    df['Atleta'] = df['Atleta'].str.replace(r'\+(\d+)', r'+ \1', regex=True)

    # Extract 'Arrancada' and 'Dos tiempos' values
    df['Arrancada'] = df['Atleta'].str.extract(arrancada_pattern)
    df['Dos tiempos'] = df['Atleta'].str.extract(dos_tiempos_pattern)

    # Calculate the 'Resultado' by summing 'Arrancada' and 'Dos tiempos'
    df['Resultado'] = df['Arrancada'].astype(float) + df['Dos tiempos'].astype(float)
    
    #Renombramos columna resultado a total
    df = df.rename(columns={'Resultado':'Total'})

    return df

def medalla_categorical(df):
    #Pasamos Columna medalla a categorical
    df['Medalla'] = pd.Categorical(df['Medalla'], categories=['Oro', 'Plata', 'Bronce'], ordered=True)
   
    #Sanity check para comprobar si efectivamente se transformó
    print(df.info())
    return df

def types(df):
    #A las columnas deseadas elejimos el Type
    df['Fechas'] = pd.to_datetime(df['Fechas'], format='%Y-%m-%d')
    df['Arrancada'] = df['Arrancada'].astype('Int64')
    df['Dos tiempos'] = df['Dos tiempos'].astype('Int64')
    df['Total'] = df['Total'].astype('Int64')

    #Ordenamos las columas según requisito
    df = df.reindex(['Genero','Categoria','Fechas','Medalla','Nombre','Apellido','Pais','Arrancada','Dos tiempos','Total'],axis=1)
    return df

def orden_final(df):
    df = df.sort_values(by=['Genero','Fechas','Categoria','Medalla'], ascending=True)
    return df

def analisis_mediana_puntajes(df,variable_x,variable_y):
    sns.boxplot(
    data=df,
    x=variable_x,
    y=variable_y)

def graficar_correlacion(df, variable_x, variable_y):
    # Convert columns to float to ensure compatibility with Plotly
    df[variable_x] = df[variable_x].astype(float)
    df[variable_y] = df[variable_y].astype(float)
    # Crear el gráfico de dispersión usando Plotly Express para visualizar la correlación
    fig = px.scatter(df, x=variable_x, y=variable_y,
                     trendline='ols',  # Añade una línea de regresión
                     labels={variable_x: variable_x, variable_y: variable_y},
                     title=f'Correlación entre {variable_x} y {variable_y}')

    # Actualizar el fondo del gráfico a blanco y ajustar la cuadrícula
    fig.update_layout({
        'plot_bgcolor': 'rgba(255, 255, 255, 1)',
        'xaxis': {'showgrid': True, 'gridcolor': 'lightgrey'},
        'yaxis': {'showgrid': True, 'gridcolor': 'lightgrey'}
    })

    # Mostrar el gráfico
    fig.show()


#Como ya es Categorical, el orden de Medallas ya está armado
def medallas_ganadas(df):
    df_ordenado = (df
               .sort_values(by=['Pais', 'Medalla'], ascending=[True, False])
               .groupby('Pais')['Medalla']
               .value_counts()
               .unstack(fill_value=0)
               .sort_values(by=['Oro', 'Plata', 'Bronce'], ascending=False))



# Mostrar el DataFrame ordenado
    return df_ordenado

def equidad_genero (df):
    #Filtro según groupby, Pais y Genero
    df_genero = df.groupby(['Pais','Genero']).size().unstack(fill_value=0)
    df_genero.columns = ['Masculino','Femenino']
    #Genero nuevas columnas para comparar
    df_genero['Total'] = df_genero.Masculino + df_genero.Femenino
    df_genero['Proporción_Masculino'] = (df_genero.Masculino/df_genero.Total).round(2)
    df_genero['Proporción_Femenino'] = (df_genero.Femenino/df_genero.Total).round(2)
    df_genero['Equidad_Fem_Masc'] = (df_genero.Femenino/df_genero.Masculino).round(2)
    df_genero['Equidad_Masc_Fem'] = (df_genero.Masculino/df_genero.Femenino).round(2)
    df_genero['Equidad_Min_Max'] = (df_genero[['Femenino','Masculino']].min(axis=1) / df_genero[['Femenino','Masculino']].max(axis=1)).round(2)
    #Ordeno por la columna Equidad Min y Max, para no sesgar y tener un punto de vista más neutro
    df_genero_ordenado = df_genero.sort_values(by='Equidad_Min_Max',ascending=False)
    return df_genero_ordenado

def diferencia_puntos_genero(df):
    df_puntos_totales = df.groupby(['Pais','Genero']).agg(
    puntos=('Total','mean')
).reset_index()

# df_puntos_totales.columns = ['Masculino','Femenino']

# Step 2: Pivot the table to create separate columns for Masculino and Femenino
    df_pivot = df_puntos_totales.pivot(index='Pais', columns='Genero', values='puntos').reset_index()

# Step 3: Fill NaN values with 0 (optional)
    df_pivot.fillna(0, inplace=True)

# Step 4: Rename the columns for clarity
    df_pivot.columns.name = None  # Remove the categories name
    df_pivot.rename(columns={'Femenino': 'Total_Femenino', 'Masculino': 'Total_Masculino'}, inplace=True)
#Filtrar por valores absolutos
    df_pivot['Diferencia_Genero'] = abs(df_pivot['Total_Masculino'] - df_pivot['Total_Femenino'])
    df_pivot

    df_pivot_ordenado = df_pivot.sort_values(by='Diferencia_Genero',ascending=True).round(2)

    return(df_pivot_ordenado)


def exploracion_inicial(df, tipo = None):
   if tipo == 'version_lite':
       print("¿Cuántas filas y columnas hay en el conjunto de datos?")
       num_filas, num_columnas = df.shape
       print("\tHay {:,} filas y {:,} columnas.".format(num_filas, num_columnas))


       print("¿Cuáles son las primeras dos filas del conjunto de datos?")
       display(df.head(2))
       print('\n########################################################################################')
   else:
       print("¿Cuántas filas y columnas hay en el conjunto de datos?")
       num_filas, num_columnas = df.shape
       print("\tHay {:,} filas y {:,} columnas.".format(num_filas, num_columnas))
       print('\n########################################################################################')


       print("¿Cuáles son las primeras cinco filas del conjunto de datos?")
       display(df.head())
       print('\n########################################################################################')


       print("¿Cuáles son las últimas cinco filas del conjunto de datos?")
       display(df.tail())
       print('\n########################################################################################')


       print("¿Cómo puedes obtener una muestra aleatoria de filas del conjunto de datos?")
       display(df.sample(n = 5))
       print('\n########################################################################################')


       print("¿Cuáles son las columnas del conjunto de datos?")
       for i in list(df.columns):
           print('\t - ' + i)
       print('\n########################################################################################')


       print("¿Cuál es el tipo de datos de cada columna?")
       print(df.dtypes)
       print('\n########################################################################################')


       print("¿Cuántas columnas hay de cada tipo de datos?")
       print(df.dtypes.value_counts())
       print('\n########################################################################################')


       print("¿Cómo podríamos obtener información más completa sobre la estructura y el contenido del DataFrame?")
       print(df.info())
       print('\n########################################################################################')


       print("¿Cuántos valores únicos tiene cada columna?")
       print(df.nunique())
       print('\n########################################################################################')


       print("¿Cuáles son las estadísticas descriptivas básicas de todas las columnas?")
       display(df.describe(include = 'all').fillna(''))
       print('\n########################################################################################')


       print("¿Hay valores nulos en el conjunto de datos?")
       print(df.isnull().sum().sort_values(ascending = False))
       print('\n########################################################################################')


       print("¿Cuál es el porcentaje de valores nulos en cada columna?")
       print(round((df.isnull().sum()/len(df)*100), 2).sort_values(ascending = False))
       print('\n########################################################################################')