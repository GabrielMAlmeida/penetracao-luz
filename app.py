import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulação de Penetração de Luz (Monte Carlo)")

# 🔬 FUNÇÃO PRINCIPAL
def simular(mu_a, mu_s, g, n, n_fotons):
    mu_t = mu_a + mu_s
    profundidades = []

    # reflexão na interface (ar -> tecido)
    def refletancia(n1, n2):
        return ((n1 - n2) / (n1 + n2))**2

    # espalhamento Henyey-Greenstein (simplificado)
    def espalhamento(g):
        if g == 0:
            return 2*np.random.rand() - 1
        xi = np.random.rand()
        return (1/(2*g)) * (1 + g**2 - ((1 - g**2)/(1 - g + 2*g*xi))**2)

    R = refletancia(1.0, n)

    for _ in range(n_fotons):

        # reflexão inicial
        if np.random.rand() < R:
            continue

        z = 0
        peso = 1

        while peso > 0.01:
            passo = -np.log(np.random.rand()) / mu_t
            z += passo

            # absorção
            absorvido = peso * (mu_a / mu_t)
            peso -= absorvido

            # espalhamento
            cos_theta = espalhamento(g)
            z += passo * cos_theta

            # saiu do tecido
            if z < 0:
                break

        profundidades.append(z)

    return profundidades

# 🔽 PARÂMETROS (mu_a, mu_s, g, n)
parametros = {
    "Mucosa": {
        660: (0.2, 15, 0.9, 1.37),
        808: (0.1, 12, 0.9, 1.37),
        904: (0.08, 10, 0.9, 1.37),
    },
    "Osso": {
        660: (0.15, 20, 0.9, 1.5),
        808: (0.08, 15, 0.9, 1.5),
        904: (0.05, 12, 0.9, 1.5),
    }
}

# 🔽 INTERFACE
tipo = st.selectbox("Tipo de tecido", ["Mucosa", "Osso"])
modo = st.radio("Modo", ["Individual", "Comparação"])

lambda_nm = None
if modo == "Individual":
    lambda_nm = st.selectbox("Comprimento de onda (nm)", [660, 808, 904])

n_fotons = st.slider("Número de fótons", 1000, 50000, 10000)

st.subheader("Parâmetros Ópticos")

if modo == "Individual" and lambda_nm is not None:
    # Parâmetros padrão para o comprimento de onda selecionado
    mu_a_padrao, mu_s_padrao, g_padrao, n_padrao = parametros[tipo][lambda_nm]

    col1, col2 = st.columns(2)

    with col1:
        mu_a = st.slider(f"μa (absorção) - {lambda_nm} nm", 0.0, 1.0, float(mu_a_padrao), 0.01)
        mu_s = st.slider(f"μs (espalhamento) - {lambda_nm} nm", 0.0, 30.0, float(mu_s_padrao), 0.1)

    with col2:
        g = st.slider(f"g (anisotropia) - {lambda_nm} nm", 0.0, 1.0, float(g_padrao), 0.01)
        n = st.slider(f"n (refração) - {lambda_nm} nm", 1.0, 2.0, float(n_padrao), 0.01)

elif modo == "Comparação":
    # Para cada comprimento de onda, criar sliders e armazenar valores
    parametros_comp = {}
    for wl in [660, 808, 904]:
        mu_a_padrao, mu_s_padrao, g_padrao, n_padrao = parametros[tipo][wl]
        st.markdown(f"### {wl} nm")
        col1, col2 = st.columns(2)
        with col1:
            mu_a = st.slider(f"μa (absorção) - {wl} nm", 0.0, 1.0, float(mu_a_padrao), 0.01, key=f"mu_a_{wl}")
            mu_s = st.slider(f"μs (espalhamento) - {wl} nm", 0.0, 30.0, float(mu_s_padrao), 0.1, key=f"mu_s_{wl}")
        with col2:
            g = st.slider(f"g (anisotropia) - {wl} nm", 0.0, 1.0, float(g_padrao), 0.01, key=f"g_{wl}")
            n = st.slider(f"n (refração) - {wl} nm", 1.0, 2.0, float(n_padrao), 0.01, key=f"n_{wl}")

        parametros_comp[wl] = (mu_a, mu_s, g, n)

# 🔽 EXECUÇÃO
if st.button("Rodar Simulação"):

    fig, ax = plt.subplots()

    if modo == "Individual":
        st.subheader("Parâmetros Utilizados")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("μa (absorção)", mu_a)
        col2.metric("μs (espalhamento)", mu_s)
        col3.metric("g (anisotropia)", g)
        col4.metric("n (refração)", n)

        with st.spinner("Simulando..."):
            dados = simular(mu_a, mu_s, g, n, n_fotons)

        ax.hist(dados, bins=100, alpha=0.7, density=True, label=f"{lambda_nm} nm")

    else:  # Comparação
        st.subheader("Parâmetros Utilizados (Comparação)")
        for wl in [660, 808, 904]:
            mu_a, mu_s, g, n = parametros_comp[wl]

            st.write(f"### {wl} nm")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("μa (absorção)", mu_a)
            col2.metric("μs (espalhamento)", mu_s)
            col3.metric("g (anisotropia)", g)
            col4.metric("n (refração)", n)

            with st.spinner(f"Simulando {wl} nm..."):
                dados = simular(mu_a, mu_s, g, n, n_fotons)

            ax.hist(dados, bins=100, alpha=0.4, density=True, label=f"{wl} nm")

    ax.set_title(f"{tipo} - Distribuição de Penetração da Luz")
    ax.set_xlabel("Profundidade")
    ax.set_ylabel("Frequência")
    ax.legend()

    st.pyplot(fig)