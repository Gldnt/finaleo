# Configuración de la página - debe ser la primera instrucción ejecutable
import streamlit as st

st.set_page_config(page_title="Rastreador de ETFs", layout="wide")

# Importaciones necesarias
import pandas as pd
from datetime import datetime
from functionsappa import (
    get_etf_data, calculate_metrics, plot_performance,
    plot_comparative_performance, get_sector_allocation,
    plot_sector_allocation, plot_correlation_heatmap, validate_data,
    plot_monetary_returns_pie, simulate_long_term_growth
)
from user_management import load_users, save_user, hash_password, authenticate_user, user_exists
import matplotlib.pyplot as plt

# Diccionario con descripciones para los ETFs
etf_descriptions = {
    "FXI": "iShares China Large-Cap ETF (Empresas chinas grandes)",
    "EWT": "iShares MSCI Taiwan ETF (Mercado taiwanés)",
    "IWM": "iShares Russell 2000 ETF (Empresas estadounidenses pequeñas)",
    "EWZ": "iShares MSCI Brazil ETF (Mercado brasileño)",
    "EWU": "iShares MSCI United Kingdom ETF (Mercado del Reino Unido)",
    "XLF": "Financial Select Sector SPDR Fund (Sector financiero estadounidense)",
    "BKF": "iShares MSCI BRIC ETF (Mercados emergentes: Brasil, Rusia, India, China)",
    "EWY": "iShares MSCI South Korea ETF (Mercado surcoreano)",
    "AGG": "iShares Core U.S. Aggregate Bond ETF (Bonos agregados de EE.UU.)",
    "EEM": "iShares MSCI Emerging Markets ETF (Mercados emergentes)",
    "EZU": "iShares MSCI Eurozone ETF (Zona Euro)",
    "GLD": "SPDR Gold Trust (Oro)",
    "QQQ": "Invesco QQQ Trust (NASDAQ 100, tecnología estadounidense)",
    "AAXJ": "iShares MSCI All Country Asia ex Japan ETF (Asia excluyendo Japón)",
    "SHY": "iShares 1-3 Year Treasury Bond ETF (Bonos del tesoro a corto plazo)",
    "ACWI": "iShares MSCI ACWI ETF (Mercados globales desarrollados y emergentes)",
    "SLV": "iShares Silver Trust (Plata)",
    "EWH": "iShares MSCI Hong Kong ETF (Mercado de Hong Kong)",
    "SPY": "SPDR S&P 500 ETF Trust (S&P 500, mercado estadounidense)",
    "EWJ": "iShares MSCI Japan ETF (Mercado japonés)",
    "IBGL": "iShares International Treasury Bond ETF (Bonos internacionales)",
    "DIA": "SPDR Dow Jones Industrial Average ETF Trust (Dow Jones)",
    "EWQ": "iShares MSCI France ETF (Mercado francés)",
    "XOP": "SPDR S&P Oil & Gas Exploration & Production ETF (Exploración y producción de petróleo y gas)",
    "VWO": "Vanguard FTSE Emerging Markets ETF (Mercados emergentes)",
    "EWA": "iShares MSCI Australia ETF (Mercado australiano)",
    "EWC": "iShares MSCI Canada ETF (Mercado canadiense)",
    "ILF": "iShares Latin America 40 ETF (Mercado latinoamericano)",
    "XLV": "Health Care Select Sector SPDR Fund (Sector salud estadounidense)",
    "EWG": "iShares MSCI Germany ETF (Mercado alemán)",
    "ITB": "iShares U.S. Home Construction ETF (Construcción de viviendas en EE.UU.)"
}


# Mostrar logo
st.image(r"C:\Users\Goldenton\Desktop\M3Y\CODE\AllianzPatrimonial\allianzlogo.png", width=150)

# Inicializar el estado de sesión
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Función para cerrar sesión
def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

# Interfaz de inicio de sesión/registro
if not st.session_state["authenticated"]:
    st.sidebar.title("Inicio de Sesión")
    menu = st.sidebar.radio("Selecciona una opción", ["Iniciar Sesión", "Registrarse"])

    if menu == "Registrarse":
        st.title("Registro")
        new_username = st.text_input("Elige un nombre de usuario")
        new_password = st.text_input("Elige una contraseña", type="password")
        confirm_password = st.text_input("Confirma tu contraseña", type="password")

        if st.button("Registrar"):
            if new_password != confirm_password:
                st.error("¡Las contraseñas no coinciden!")
            elif user_exists(new_username):
                st.error("¡El nombre de usuario ya existe! Por favor elige otro.")
            else:
                save_user(new_username, hash_password(new_password))
                st.success("¡Usuario registrado exitosamente! Ahora inicia sesión.")

    elif menu == "Iniciar Sesión":
        st.title("Iniciar Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Entrar"):
            if authenticate_user(username, password):
                st.success(f"¡Bienvenido, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
            else:
                st.error("Usuario o contraseña inválidos.")
else:
    # Crear pestañas
    tabs = st.tabs(["Resumen de Allianz", "Análisis de ETFs", "Simulador de Rendimientos", "Indicadores Técnicos", "Proyecciones a Largo Plazo", "Resumen de Rendimiento"])

    # Pestaña 1: Resumen de Allianz
with tabs[0]:
    st.markdown("<h1 style='text-align: center; color: navy;'>Resumen de Allianz Patrimonial</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px;">
    <p><b>Allianz Patrimonial</b> es una institución global de confianza con más de 130 años de experiencia en la industria financiera.</p>
    <p>Con una fuerte presencia en más de 70 países, Allianz se dedica a ofrecer servicios de inversión y gestión patrimonial de alta calidad, permitiendo a los clientes alcanzar sus objetivos financieros.</p>
    
    <h3>Historia</h3>
    <ul>
        <li><b>1889:</b> Fundación de Allianz en Berlín.</li>
        <li><b>1950s:</b> Expansión internacional en Europa y América.</li>
        <li><b>2000s:</b> Creación de productos financieros innovadores como ETFs y fondos indexados.</li>
    </ul>

    <h3>Valores Fundamentales</h3>
    <ol>
        <li><b>Integridad:</b> Siempre actuamos en el mejor interés de nuestros clientes.</li>
        <li><b>Innovación:</b> Lideramos con soluciones financieras modernas.</li>
        <li><b>Excelencia:</b> Nos esforzamos por superar expectativas.</li>
    </ol>

    <h3>Datos Relevantes</h3>
    <ul>
        <li><b>Fondos Bajo Gestión:</b> $500,000,000 USD.</li>
        <li><b>Presencia Global:</b> Más de 70 países.</li>
        <li><b>Productos:</b> ETFs, fondos de inversión, seguros, y más.</li>
    </ul>

    <h3>Contactos</h3>
    <ul>
        <li><b>Teléfono:</b> +1 (800) 123-4567</li>
        <li><b>Email:</b> contacto@allianz.com</li>
        <li><b>Sitio Web:</b> <a href='https://www.allianz.com' target='_blank'>www.allianz.com</a></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ETFs Disponibles")
    etf_summary = pd.DataFrame.from_dict(etf_descriptions, orient='index', columns=['Descripción'])
    etf_summary.index.name = "Ticker"
    st.table(etf_summary)

    # Pestaña 2: Análisis de ETFs
    with tabs[1]:
        st.sidebar.header("Configurar Análisis")

        tickers_seleccionados = st.sidebar.multiselect(
            "Selecciona uno o más ETFs",
            list(etf_descriptions.keys()),
            default=["FXI", "SPY"]
        )

        periodo = st.sidebar.selectbox("Selecciona el período de tiempo", ["1 año", "3 años", "5 años", "10 años", "Desde inicio de año"])

        monto_inversion = st.sidebar.number_input("Monto total a invertir ($)", min_value=0.0, max_value=10000000.0, step=100.0, value=10000.0, key="monto_inversion")
        asignacion = {ticker: st.sidebar.slider(f"Porcentaje para {ticker} (%)", 0, 100, 0, key=f"slider_{ticker}") for ticker in tickers_seleccionados}

        # Cargar y procesar datos
        datos = get_etf_data(tickers_seleccionados, period=periodo)

        # Gráfica comparativa
        st.write("### Gráfica Comparativa de los ETFs Seleccionados")
        fig = plot_comparative_performance(datos, tickers_seleccionados)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("No se pudo generar la gráfica comparativa.")

        # Métricas clave y matriz de correlación
        if len(tickers_seleccionados) > 1:
            st.write("### Matriz de Correlación")
            heatmap = plot_correlation_heatmap(datos, tickers_seleccionados)
            if heatmap:
                st.pyplot(heatmap)

    # Pestaña 3: Simulador de Rendimientos
    with tabs[2]:
        st.markdown("## Simulador de Rendimientos")
        monto_inicial = st.number_input("Monto Inicial ($)", min_value=0.0, value=10000.0, key="monto_inicial_simulador")
        ticker_simulado = st.selectbox("Selecciona un ETF para Simular", tickers_seleccionados, key="simulador_ticker")

        if ticker_simulado:
            data_simulado = datos[ticker_simulado]
            if validate_data(data_simulado, ticker_simulado):
                retorno = calculate_metrics(data_simulado)['Cumulative Return']
                monto_final = monto_inicial * (1 + retorno)
                st.write(f"**Monto Final Estimado:** ${monto_final:,.2f}")

    # Pestaña 4: Indicadores Técnicos
    with tabs[3]:
        st.markdown("## Indicadores Técnicos")
        ticker_indicador = st.selectbox("Selecciona un ETF", tickers_seleccionados, key="indicadores_ticker")
        if ticker_indicador:
            data_indicador = datos[ticker_indicador]
            if validate_data(data_indicador, ticker_indicador):
                st.write("### Media Móvil Simple")
                media_movil = data_indicador['Close'].rolling(window=20).mean()
                plt.figure(figsize=(12, 6))
                plt.plot(data_indicador['Close'], label='Precio de Cierre', color='blue')
                plt.plot(media_movil, label='Media Móvil (20 días)', color='orange')
                plt.legend()
                st.pyplot(plt)

    # Pestaña 5: Proyecciones a Largo Plazo
    with tabs[4]:
        st.markdown("## Proyecciones a Largo Plazo")
        monto_inicial = st.number_input("Monto Inicial ($)", min_value=0.0, value=10000.0, key="monto_inicial_proyecciones")
        contribucion_periodica = st.number_input("Contribución Periódica ($)", min_value=0.0, value=500.0, key="contribucion_proyecciones")
        horizonte = st.number_input("Horizonte de Tiempo (años)", min_value=1, max_value=50, value=10, key="horizonte_proyecciones")
        ticker_simulado = st.selectbox("Selecciona un ETF para Simular", list(etf_descriptions.keys()), key="proyecciones_ticker")

        if ticker_simulado:
            datos = get_etf_data([ticker_simulado], period="10 años")
            retorno_historico = calculate_metrics(datos[ticker_simulado])['Average Return']
            if retorno_historico:
                proyeccion = simulate_long_term_growth(monto_inicial, contribucion_periodica, retorno_historico, horizonte)
                st.write(f"**Monto Final Estimado después de {horizonte} años:** ${proyeccion[-1]:,.2f}")

                plt.figure(figsize=(12, 6))
                plt.plot(proyeccion, label="Crecimiento Proyectado")
                plt.title(f"Proyección de Crecimiento para {ticker_simulado}")
                plt.xlabel("Años")
                plt.ylabel("Monto Acumulado ($)")
                plt.legend()
                st.pyplot(plt)

# Pestaña 6: Resumen de Rendimiento
with tabs[5]:
    st.markdown("## Resumen de Rendimiento")
    st.write("Próximamente: Información detallada sobre el rendimiento general.")
