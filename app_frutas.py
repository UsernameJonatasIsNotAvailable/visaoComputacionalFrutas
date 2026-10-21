import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------------
# Cores (tiradas do esboço)
# ----------------------------------------------------------------------------
COR_FUNDO = "#9AD9EA"      # azul claro do fundo
COR_PAINEL = "#FFFFFF"     # branco da barra lateral e do quadro da imagem
COR_BOA = "#22B14C"        # verde
COR_RUIM = "#ED1C24"       # vermelho
COR_TEXTO = "#222222"
COR_CINZA = "#C8C8C8"

TAM_IMAGEM = (320, 320)


# ----------------------------------------------------------------------------
# PLACEHOLDER do modelo
# Aqui entra depois o seu classificador (OpenCV + modelo treinado no FruitNet).
# Deve retornar: (nome_da_fruta, probabilidade_de_estar_boa entre 0 e 1)
# ----------------------------------------------------------------------------
def classificar_imagem(caminho: str):
    # TODO: substituir pela inferência real
    return "Banana", 0.75


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classificador de Frutas")
        self.geometry("1100x620")
        self.minsize(980, 560)
        self.configure(bg=COR_FUNDO)

        self.caminho_imagem = None
        self._foto = None  # mantém referência da imagem (senão o Tkinter apaga)

        self._criar_barra_lateral()
        self._criar_area_grafico()
        self._criar_area_imagem()
        self._desenhar_grafico(None)

    # ------------------------------------------------------------------ UI
    def _criar_barra_lateral(self):
        """Barra branca da esquerda: título + botões."""
        barra = tk.Frame(self, bg=COR_PAINEL, width=230)
        barra.pack(side="left", fill="y", padx=(12, 0), pady=12)
        barra.pack_propagate(False)

        tk.Label(barra, text="Classificador\nde Frutas", bg=COR_PAINEL,
                 fg=COR_TEXTO, font=("Segoe UI", 16, "bold"),
                 justify="left").pack(anchor="w", padx=16, pady=(20, 4))
        tk.Label(barra, text="Qualidade e tipo", bg=COR_PAINEL, fg="#666666",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=16)

        espaco = tk.Frame(barra, bg=COR_PAINEL)
        espaco.pack(fill="both", expand=True)

        botoes = tk.Frame(barra, bg=COR_PAINEL)
        botoes.pack(fill="x", padx=16, pady=(0, 24))

        self.btn_enviar = self._botao(botoes, "Enviar imagem", self.enviar_imagem)
        self.btn_classificar = self._botao(botoes, "Classificar", self.classificar,
                                           estado="disabled")
        self.btn_limpar = self._botao(botoes, "Limpar", self.limpar)

    def _botao(self, pai, texto, comando, estado="normal"):
        b = tk.Button(pai, text=texto, command=comando, state=estado,
                      font=("Segoe UI", 11), bg="#333333", fg="white",
                      activebackground="#555555", activeforeground="white",
                      relief="flat", cursor="hand2", pady=8)
        b.pack(fill="x", pady=6)
        return b

    def _criar_area_grafico(self):
        """Centro: gráfico de pizza (boa condição x condição ruim)."""
        centro = tk.Frame(self, bg=COR_FUNDO)
        centro.pack(side="left", fill="both", expand=True, padx=10, pady=12)

        self.fig = Figure(figsize=(4.6, 4.6), dpi=100, facecolor=COR_FUNDO)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=centro)
        self.canvas.get_tk_widget().configure(bg=COR_FUNDO, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.lbl_resultado = tk.Label(centro, text="", bg=COR_FUNDO,
                                      fg=COR_TEXTO, font=("Segoe UI", 14, "bold"))
        self.lbl_resultado.pack(pady=(0, 10))

    def _criar_area_imagem(self):
        """Direita: nome da fruta no topo e quadro com a imagem."""
        direita = tk.Frame(self, bg=COR_FUNDO)
        direita.pack(side="left", fill="y", padx=(0, 20), pady=12)

        self.lbl_fruta = tk.Label(direita, text="—", bg=COR_FUNDO, fg=COR_TEXTO,
                                  font=("Consolas", 20, "bold"))
        self.lbl_fruta.pack(pady=(40, 14))

        self.quadro = tk.Frame(direita, bg=COR_PAINEL,
                               width=TAM_IMAGEM[0] + 40, height=TAM_IMAGEM[1] + 40)
        self.quadro.pack()
        self.quadro.pack_propagate(False)

        self.lbl_imagem = tk.Label(self.quadro, text="Nenhuma imagem\nselecionada",
                                   bg=COR_PAINEL, fg="#888888",
                                   font=("Segoe UI", 11))
        self.lbl_imagem.pack(expand=True)

    # ------------------------------------------------------------- Gráfico
    def _desenhar_grafico(self, prob_boa):
        self.ax.clear()
        if prob_boa is None:
            self.ax.pie([1], colors=[COR_CINZA], startangle=90, counterclock=False,
                        wedgeprops={"edgecolor": "black", "linewidth": 2})
            self.ax.text(0, 0, "Sem dados", ha="center", va="center",
                         fontsize=11, color="#555555")
        else:
            valores = [1 - prob_boa, prob_boa]
            rotulos = [f"Condição ruim\n{valores[0]:.0%}",
                       f"Boa condição\n{valores[1]:.0%}"]
            # Ruim começa no topo e vai no sentido horário (quadrante superior
            # direito, como no esboço); o restante fica verde.
            self.ax.pie(valores, labels=rotulos, labeldistance=0.55,
                        colors=[COR_RUIM, COR_BOA], startangle=90,
                        counterclock=False,
                        wedgeprops={"edgecolor": "black", "linewidth": 2},
                        textprops={"fontsize": 10, "fontfamily": "monospace",
                                   "fontweight": "bold"})
        self.ax.set_aspect("equal")
        self.canvas.draw()

    # ------------------------------------------------------------- Ações
    def enviar_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Selecione a imagem da fruta",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp"),
                       ("Todos os arquivos", "*.*")])
        if not caminho:
            return
        try:
            img = Image.open(caminho).convert("RGB")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a imagem.\n\n{e}")
            return

        img.thumbnail(TAM_IMAGEM)
        self._foto = ImageTk.PhotoImage(img)
        self.lbl_imagem.configure(image=self._foto, text="")

        self.caminho_imagem = caminho
        self.btn_classificar.configure(state="normal")
        self.lbl_fruta.configure(text="—")
        self.lbl_resultado.configure(text="")
        self._desenhar_grafico(None)

    def classificar(self):
        if not self.caminho_imagem:
            return
        fruta, prob_boa = classificar_imagem(self.caminho_imagem)

        self.lbl_fruta.configure(text=fruta.upper())
        self._desenhar_grafico(prob_boa)

        if prob_boa >= 0.5:
            self.lbl_resultado.configure(text="Boa para consumo", fg="#14732E")
        else:
            self.lbl_resultado.configure(text="Imprópria para consumo", fg="#B3141B")

    def limpar(self):
        self.caminho_imagem = None
        self._foto = None
        self.lbl_imagem.configure(image="", text="Nenhuma imagem\nselecionada")
        self.lbl_fruta.configure(text="—")
        self.lbl_resultado.configure(text="")
        self.btn_classificar.configure(state="disabled")
        self._desenhar_grafico(None)


if __name__ == "__main__":
    App().mainloop()