import streamlit as st
import pandas as pd
import random
import folium
from streamlit_folium import st_folium

# Quitar tildes
def quitar_tildes(texto):
    return texto.translate(str.maketrans('áéíóúüÁÉÍÓÚÜ', 'aeiouuAEIOUU'))

# Título principal
st.title("🗺️ Juego de los concejos de Asturias")

datos = pd.read_csv("concejos.csv")
tab_capital, tab_mapa = st.tabs(["🏛️ Adivinar capital", "📍 Situar en mapa"])

# --- PESTAÑA 1: ADIVINAR LA CAPITAL ---
with tab_capital:
    st.header("¿Sabes cuál es su capital?")

    # 1. Inicializamos las variables de memoria
    if 'concejo_elegido' not in st.session_state:
        st.session_state.concejo_elegido = random.choice(datos['Concejo'].tolist())
    if 'mensaje_resultado' not in st.session_state:
        st.session_state.mensaje_resultado = ""

    concejo = st.session_state.concejo_elegido
    capital_correcta = datos[datos['Concejo'] == concejo]['Capital'].values[0]

    # 2. EL CALLBACK DEL ENTER
    def comprobar_capital():
        respuesta = st.session_state.caja_capital 
        if respuesta.strip() != "":
            if quitar_tildes(respuesta.strip().lower()) == quitar_tildes(capital_correcta.lower()):
                st.session_state.mensaje_resultado = "¡Correcto! 🎉"
                st.session_state.concejo_elegido = random.choice(datos['Concejo'].tolist())
                st.session_state.caja_capital = "" 
            else:
                st.session_state.mensaje_resultado = "¡Borra y prueba otra vez! ❌"

    # EL CALLBACK DEL BOTÓN SALTAR
    def saltar_concejo():
        st.session_state.concejo_elegido = random.choice(datos['Concejo'].tolist())
        st.session_state.caja_capital = ""      # Vaciamos la caja
        st.session_state.mensaje_resultado = "" # Borramos los mensajes de error

    st.subheader(f"Concejo: **{concejo}**")

    # 3. La caja de texto permanente
    st.text_input(
        "Escribe la capital y pulsa Enter para comprobar:", 
        key="caja_capital", 
        on_change=comprobar_capital
    )

    # 4. Mostramos el mensaje (Correcto o Error)
    if st.session_state.mensaje_resultado == "¡Correcto! 🎉":
        st.success(st.session_state.mensaje_resultado)
    elif st.session_state.mensaje_resultado != "":
        st.error(st.session_state.mensaje_resultado)

    # 5. El botón de saltar ahora usa "on_click"
    st.button("No me la sé, prefiero pasar ➡️", on_click=saltar_concejo)

# --- PESTAÑA 2: EL MAPA ---
with tab_mapa:
    st.header("📍 Sitúa el concejo")

    if 'concejo_mapa' not in st.session_state:
        st.session_state.concejo_mapa = random.choice(datos['Concejo'].tolist())
    
    concejo_objetivo = st.session_state.concejo_mapa
    st.subheader(f"Encuentra en el mapa: **{concejo_objetivo}**")

    mapa_asturias = folium.Map(
        location=[43.32, -5.85], 
        zoom_start=8, 
        tiles="CartoDB positron nolabels" 
    )

    folium.GeoJson(
        "asturias.geojson",
        name="Concejos",
        style_function=lambda x: {
            'fillColor': '#3186cc',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.1
        },
        highlight_function=lambda x: {
            'fillOpacity': 0.5
        }
    ).add_to(mapa_asturias)

    # Altura reducida para evitar scroll
    respuesta_mapa = st_folium(
        mapa_asturias, 
        width=700, 
        height=400, 
        key=f"mapa_{st.session_state.concejo_mapa}", 
        return_on_hover=False
    )

    if respuesta_mapa and respuesta_mapa.get("last_active_drawing"):
        concejo_clicado = respuesta_mapa["last_active_drawing"]["properties"]["mun_name"]
        
        if quitar_tildes(concejo_clicado.lower()) == quitar_tildes(concejo_objetivo.lower()):
            st.success(f"¡Correcto! Has hecho clic en {concejo_clicado} 🎉")
        else:
            st.error(f"Ese es {concejo_clicado}. ¡Sigue buscando **{concejo_objetivo}**! ❌")

    if st.button("Siguiente concejo 🗺️"):
        st.session_state.concejo_mapa = random.choice(datos['Concejo'].tolist())
        st.rerun()


# python -m streamlit run app.py
# Se sale de ahí haciendo Control + C