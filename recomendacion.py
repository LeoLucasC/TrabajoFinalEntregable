# recomendacion.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def preparar_datos():
    compras_df = pd.read_csv('compras.csv')
    productos_df = pd.read_csv('productos.csv')

    product_list = productos_df['id'].astype(str).tolist()
    user_product_matrix = pd.DataFrame(0, index=compras_df['id'], columns=product_list)

    for _, row in compras_df.iterrows():
        user_id = row['id']
        products = row['Historial'].split(',')
        user_product_matrix.loc[user_id, products] = 1

    return user_product_matrix, productos_df

def recomendar_productos(usuario_id, top_n=10):
    user_product_matrix, productos_df = preparar_datos()

    product_matrix = user_product_matrix.T
    similarity_matrix = cosine_similarity(product_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.columns, columns=user_product_matrix.columns)
    
    productos_comprados = user_product_matrix.loc[usuario_id]
    productos_comprados = productos_comprados[productos_comprados > 0].index.tolist()
    
    similaridades = similarity_df[productos_comprados].mean(axis=1)
    productos_comprados_set = set(productos_comprados)
    recomendaciones = similaridades.drop(index=productos_comprados_set).sort_values(ascending=False)
    
    top_recomendaciones = recomendaciones.head(top_n)
    return top_recomendaciones


