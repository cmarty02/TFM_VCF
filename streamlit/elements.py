import streamlit as st
import pandas as pd
import io
from funciones import upload_to_gcs, transform_dataframe, get_player_images
import requests
import time  # Importar time para simular el progreso

### Código de elementos que se necesitan para construir la página de Streamlit ###
###Luego lo utilizaré para construir bien la página. Don't panic###

###TEST PARA VER SI FUNCIONA
# Configuración de la página
st.set_page_config(
    page_title="VCF Forecasting Scouting Model",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png",
    layout="wide"
)
###/TEST PARA VER SI FUNCIONA

###TEST PARA VER SI FUNCIONA
# Ruta a imágenes de jugadores 
#JUAN_CL -- ¿Esta ruta debería de estar en un bucket también no? Si no, sólo está en local.
players_csv = 'D:/Dropbox/Facu/EDEM/GitHub/GitHub_Repositorios/TFM_VCF/streamlit/img_players.csv'

# Sidebar
with st.sidebar:
    # Logo centrado en el sidebar
    st.markdown(
        """
        <style>
        .sidebar-logo {
            display: flex;
            justify-content: center;
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .sidebar-logo img {
            width: 100px; /* Ajusta el tamaño del logo según sea necesario */
        }
        </style>
        <div class="sidebar-logo">
            <img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png" alt="Valencia CF Logo">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.header("VCF Forecasting Scouting Model")
    st.divider()
    st.subheader("Settings")
    uploaded_file = st.file_uploader("Choose a XLSX file", type="xlsx")
    upload_button = st.button('Upload')
    run_button = st.button('Run Predictions')
    
    # Agregar barra de progreso en la barra lateral
    progress_bar = st.progress(0)  # Inicializar la barra de progreso

# Placeholder for messages in the sidebar
status_placeholder = st.sidebar.empty()
###/TEST PARA VER SI FUNCIONA



### Select box - Buscador de jugadores. 
option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"
     ),
    index=None,
    placeholder="Select contact method...",
)

st.write("You selected:", option)



### Visualizar imágenes
st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png", caption="Sunrise by the mountains")




### Visualizar datos
st.metric (label = "xxx", value=input , delta=input2, delta_color="off")



### Linechart para visualizar la cantidad de jugadores que tienen cada precio
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.line_chart(chart_data)


###Visualización de burbujas para ver el precio de los jugadores por posición
chart_data = pd.DataFrame(
    np.random.randn(20, 3), columns=["col1", "col2", "col3"]
)
chart_data["col4"] = np.random.choice(["A", "B", "C"], 20)

st.scatter_chart(
    chart_data,
    x="col1",
    y="col2",
    color="col4",
    size="col3",
)



### Stream data. Esto es solo para que quede más facherito. Que cuando elijas a un jugador lo cargue todo
### en modo stream porque si lo hace así parece que hay más hecho y UX ya tú sabe. Que en realidad para el
### día a día es un mierdón. Pero para una demo queda bacán.
_LOREM_IPSUM = """
Lorem ipsum dolor sit amet, **consectetur adipiscing** elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
"""


def stream_data():
    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)

    yield pd.DataFrame(
        np.random.randn(5, 10),
        columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    )

    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)


if st.button("Stream data"):
    st.write_stream(stream_data)


