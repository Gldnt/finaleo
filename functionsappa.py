import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def validate_data(df, ticker):
    """Valida si los datos descargados son suficientes para análisis."""
    if df.empty:
        st.warning(f"El ETF {ticker} no tiene datos disponibles para el período seleccionado.")
        return False
    if 'Close' not in df.columns:
        st.warning(f"El ETF {ticker} no tiene información de precios (columna 'Close') en los datos.")
        return False
    return True

@st.cache_data
def get_etf_data(tickers, period="5y", start_date=None, end_date=None):
    """Obtiene datos históricos para los tickers seleccionados desde Yahoo Finance."""
    period_mapping = {
        "1 año": "1y",
        "3 años": "3y",
        "5 años": "5y",
        "10 años": "10y",
        "Desde inicio de año": "ytd"
    }
    if period in period_mapping:
        period = period_mapping[period]
    
    data = {}
    valid_tickers = []
    for ticker in tickers:
        try:
            etf = yf.Ticker(ticker)
            if start_date and end_date:
                history = etf.history(start=start_date, end=end_date)
            else:
                history = etf.history(period=period)

            if history.empty or 'Close' not in history.columns:
                st.warning(f"No se encontraron datos válidos para {ticker}.")
                data[ticker] = pd.DataFrame()
            else:
                data[ticker] = history
                valid_tickers.append(ticker)
        except Exception as e:
            st.error(f"Error al descargar datos para {ticker}: {e}")
            data[ticker] = pd.DataFrame()

    if not valid_tickers:
        st.warning("Ningún ticker tiene datos válidos para el período seleccionado. Verifique el rango de tiempo o cambie los tickers.")
    
    return data

def calculate_metrics(df):
    """Calcula métricas clave para un DataFrame de precios."""
    if df.empty or 'Close' not in df.columns:
        return {'Average Return': None, 'Volatility': None, 'Cumulative Return': None}

    returns = df['Close'].pct_change().dropna()
    avg_return = np.mean(returns) if not returns.empty else None
    volatility = np.std(returns) if not returns.empty else None
    cumulative_return = (df['Close'][-1] / df['Close'][0]) - 1 if not df.empty else None
    return {'Average Return': avg_return, 'Volatility': volatility, 'Cumulative Return': cumulative_return}

def plot_performance(df, title="Desempeño del ETF"):
    """Genera un gráfico de la historia de precios de un ETF."""
    if df.empty or 'Close' not in df.columns:
        st.warning(f"Datos insuficientes para graficar {title}.")
        return None

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Precio de Cierre', color='blue')
    plt.title(title)
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend()
    plt.grid()
    return plt

def plot_comparative_performance(data, tickers):
    """Genera un gráfico comparativo del desempeño de múltiples ETFs."""
    plt.figure(figsize=(12, 6))
    for ticker in tickers:
        if ticker in data and not data[ticker].empty:
            plt.plot(data[ticker].index, data[ticker]['Close'], label=ticker)
        else:
            st.warning(f"Datos faltantes para {ticker}. No se incluirá en la comparación.")
    plt.title("Desempeño Comparativo de los ETFs Seleccionados")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend()
    plt.grid()
    return plt

def plot_correlation_heatmap(data, tickers):
    """Genera una matriz de correlación entre los ETFs seleccionados."""
    valid_tickers = [ticker for ticker in tickers if not data[ticker].empty]
    if not valid_tickers:
        st.warning("No hay datos válidos para generar la matriz de correlación.")
        return None

    combined_data = pd.concat([data[ticker]['Close'] for ticker in valid_tickers], axis=1)
    combined_data.columns = valid_tickers

    correlation = combined_data.pct_change().corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={"shrink": .8})
    plt.title("Matriz de Correlación")
    return plt

def get_sector_allocation(ticker):
    """Obtiene la asignación sectorial de un ETF desde Yahoo Finance."""
    try:
        etf = yf.Ticker(ticker)
        sector_weights = etf.fund_sector_weightings  # Obtener los pesos sectoriales
        if not sector_weights:
            st.warning(f"No se encontró información sectorial para {ticker}.")
            return None
        sectors = list(sector_weights.keys())
        allocations = [sector_weights[sector] * 100 for sector in sectors]
        return pd.DataFrame({'Sector': sectors, 'Asignación (%)': allocations})
    except Exception as e:
        st.error(f"Error al obtener la asignación sectorial para {ticker}: {e}")
        return None

def plot_sector_allocation(sector_allocation):
    """Genera un gráfico de barras para la asignación sectorial."""
    if sector_allocation is None or sector_allocation.empty:
        st.warning("Datos insuficientes para graficar asignación sectorial.")
        return None

    plt.figure(figsize=(8, 6))
    plt.bar(sector_allocation['Sector'], sector_allocation['Asignación (%)'], color='skyblue')
    plt.title("Asignación Sectorial")
    plt.ylabel("Asignación (%)")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    return plt

def plot_monetary_returns_pie(labels, values, total_investment):
    """Genera un gráfico de pastel para los retornos monetarios."""
    # Validar entradas
    if not labels or not values or total_investment <= 0:
        st.warning("Datos insuficientes para generar el gráfico de pastel. Verifique los valores proporcionados.")
        return None

    # Normalizar valores
    normalized_values = [value / total_investment * 100 if total_investment > 0 else 0 for value in values]

    # Filtrar valores inválidos
    filtered_labels = []
    filtered_values = []
    for label, value in zip(labels, normalized_values):
        if not (pd.isna(value) or np.isinf(value) or value <= 0):
            filtered_labels.append(label)
            filtered_values.append(value)

    if not filtered_labels or not filtered_values:
        st.warning("No hay datos válidos para generar el gráfico de pastel.")
        return None

    # Generar el gráfico
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        filtered_values, labels=filtered_labels, autopct='%1.1f%%', startangle=90
    )
    for i, text in enumerate(texts):
        text.set_text(f"\n\n${values[i]:,.2f}\n({filtered_values[i]:.2f}%)")
    plt.title('Distribución de Retornos Monetarios', fontsize=16)
    plt.axis('equal')  # Asegurar que el gráfico sea circular
    return fig

def simulate_long_term_growth(initial_amount, periodic_contribution, annual_return, years):
    """Simula el crecimiento de una inversión con contribuciones periódicas."""
    amounts = [initial_amount]
    for year in range(1, years + 1):
        final_amount = amounts[-1] * (1 + annual_return) + periodic_contribution
        amounts.append(final_amount)
    return amounts
