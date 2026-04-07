import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

def simular(mu_a, mu_s, g, n_fotons=10000):
    mu_t = mu_a + mu_s
    profundidades = []

    for _ in range(n_fotons):
        z = 0
        peso = 1

        while peso > 0.01:
            passo = -np.log(np.random.rand()) / mu_t
            z += passo

            absorvido = peso * (mu_a / mu_t)
            peso -= absorvido

            if np.random.rand() < 0.5:
                z += passo * g
            else:
                z -= passo * g

            if z < 0:
                z = 0

        profundidades.append(z)

    return profundidades


def rodar_simulacoes():
    casos = {
        "Mucosa 660nm": (0.2, 15, 0.9),
        "Mucosa 808nm": (0.1, 12, 0.9),
        "Mucosa 904nm": (0.08, 10, 0.9),
        "Osso 660nm": (0.15, 20, 0.9),
        "Osso 808nm": (0.08, 15, 0.9),
        "Osso 904nm": (0.05, 12, 0.9),
    }

    for nome, (mu_a, mu_s, g) in casos.items():
        print(f"Rodando: {nome}")
        dados = simular(mu_a, mu_s, g)

        plt.figure()
        plt.hist(dados, bins=100)
        plt.title(nome)
        plt.xlabel("Profundidade")
        plt.ylabel("Frequência")
        plt.savefig(nome + ".png")
        plt.close()


if __name__ == "__main__":
    rodar_simulacoes()