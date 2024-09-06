import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from PIL import Image, ImageTk
import pandas as pd

# Função para conectar ao banco de dados PostgreSQL
def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname="estoque",
            user="postgres",  # Substitua pelo seu usuário
            password="ketley2010@",  # Substitua pela sua senha
            host="localhost",
            port="5432",
            options="-c client_encoding=UTF8"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Erro de Conexão", str(e))
        return None

# Função para verificar login
def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    if usuario and senha:
        conn = conectar_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha))
                resultado = cur.fetchone()
                cur.close()
                conn.close()
                if resultado:
                    messagebox.showinfo("Sucesso", "Login bem-sucedido!")
                    tela_login.destroy()  # Fecha a tela de login
                    mostrar_tela_principal()  # Abre a tela principal
                else:
                    messagebox.showerror("Erro", "Usuário ou senha incorretos.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
    else:
        messagebox.showwarning("Entrada Inválida", "Preencha todos os campos")

# Função para exportar dados para Excel
def exportar_para_excel():
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, produto, quantidade, preco, categoria FROM estoque")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            # Criar um DataFrame do pandas
            df = pd.DataFrame(rows, columns=["ID", "Produto", "Quantidade", "Preço", "Categoria"])
            
            # Salvar o DataFrame em um arquivo Excel
            arquivo_excel = "estoque.xlsx"
            df.to_excel(arquivo_excel, index=False)
            
            messagebox.showinfo("Sucesso", f"Dados exportados para {arquivo_excel}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", str(e))

# Função para mostrar a tela principal após login
def mostrar_tela_principal():
    def adicionar_produto():
        produto = entry_produto.get()
        quantidade = entry_quantidade.get()
        preco = entry_preco.get()
        categoria = entry_categoria.get()

        if produto and quantidade and preco and categoria:
            try:
                quantidade = int(quantidade)  # Certifica que quantidade é um inteiro
                preco = float(preco)  # Certifica que preço é um decimal
            except ValueError:
                messagebox.showerror("Erro de Tipo", "Quantidade deve ser um número inteiro e Preço deve ser um número decimal.")
                return

            conn = conectar_db()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO estoque (produto, quantidade, preco, categoria) VALUES (%s, %s, %s, %s)",
                        (produto, quantidade, preco, categoria)
                    )
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
                    cur.close()
                    conn.close()
                    atualizar_lista()
                except Exception as e:
                    messagebox.showerror("Erro ao Inserir", str(e))
        else:
            messagebox.showwarning("Entrada Inválida", "Preencha todos os campos")

    def remover_produto():
        selected_item = tree.selection()
        if selected_item:
            produto_id = tree.item(selected_item)['values'][0]
            conn = conectar_db()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM estoque WHERE id = %s", (produto_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
                    atualizar_lista()
                except Exception as e:
                    messagebox.showerror("Erro ao Remover", str(e))
        else:
            messagebox.showwarning("Seleção Inválida", "Selecione um produto para remover")

    def registrar_entrada():
        selected_item = tree.selection()
        if selected_item:
            produto_id = tree.item(selected_item)['values'][0]
            quantidade = entry_quantidade.get()

            if quantidade:
                try:
                    quantidade = int(quantidade)
                except ValueError:
                    messagebox.showerror("Erro de Tipo", "Quantidade deve ser um número inteiro.")
                    return

                conn = conectar_db()
                if conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("UPDATE estoque SET quantidade = quantidade + %s WHERE id = %s", (quantidade, produto_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
                        atualizar_lista()
                    except Exception as e:
                        messagebox.showerror("Erro ao Registrar", str(e))
            else:
                messagebox.showwarning("Entrada Inválida", "Insira uma quantidade válida")
        else:
            messagebox.showwarning("Seleção Inválida", "Selecione um produto para registrar a entrada")

    def registrar_saida():
        selected_item = tree.selection()
        if selected_item:
            produto_id = tree.item(selected_item)['values'][0]
            quantidade = entry_quantidade.get()

            if quantidade:
                try:
                    quantidade = int(quantidade)
                except ValueError:
                    messagebox.showerror("Erro de Tipo", "Quantidade deve ser um número inteiro.")
                    return

                conn = conectar_db()
                if conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("SELECT quantidade FROM estoque WHERE id = %s", (produto_id,))
                        quantidade_atual = cur.fetchone()[0]

                        if quantidade > quantidade_atual:
                            messagebox.showwarning("Quantidade Insuficiente", "Não há quantidade suficiente em estoque.")
                            cur.close()
                            conn.close()
                            return

                        cur.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id = %s", (quantidade, produto_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")
                        atualizar_lista()
                    except Exception as e:
                        messagebox.showerror("Erro ao Registrar", str(e))
            else:
                messagebox.showwarning("Entrada Inválida", "Insira uma quantidade válida")
        else:
            messagebox.showwarning("Seleção Inválida", "Selecione um produto para registrar a saída")

    def atualizar_lista():
        for item in tree.get_children():
            tree.delete(item)

        conn = conectar_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, produto, quantidade, preco, categoria FROM estoque")
                rows = cur.fetchall()
                for row in rows:
                    tree.insert('', 'end', values=row)
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro ao Consultar", str(e))

    # Interface gráfica principal
    root = tk.Tk()
    root.title("Controle de Estoque")
    root.geometry("600x500")
    root.configure(bg="#f1f1f1")

    # Labels e entradas de texto
    label_produto = tk.Label(root, text="Produto:", bg="#f0f0f0")
    label_produto.pack(padx=10, pady=5, anchor='w')

    entry_produto = tk.Entry(root)
    entry_produto.pack(padx=10, pady=5, fill='x')

    label_quantidade = tk.Label(root, text="Quantidade:", bg="#f0f0f0")
    label_quantidade.pack(padx=10, pady=5, anchor='w')

    entry_quantidade = tk.Entry(root)
    entry_quantidade.pack(padx=10, pady=5, fill='x')

    label_preco = tk.Label(root, text="Preço:", bg="#f0f0f0")
    label_preco.pack(padx=10, pady=5, anchor='w')

    entry_preco = tk.Entry(root)
    entry_preco.pack(padx=10, pady=5, fill='x')

    label_categoria = tk.Label(root, text="Categoria:", bg="#f0f0f0")
    label_categoria.pack(padx=10, pady=5, anchor='w')

    entry_categoria = tk.Entry(root)
    entry_categoria.pack(padx=10, pady=5, fill='x')

    # Botões para adicionar, remover produtos, registrar entrada e saída
    frame_buttons = tk.Frame(root, bg="#f0f0f0")
    frame_buttons.pack(pady=10)

    button_add = tk.Button(frame_buttons, text="Adicionar Produto", command=adicionar_produto, bg="#4CAF50", fg="white")
    button_add.pack(side='left', padx=10)

    button_remove = tk.Button(frame_buttons, text="Remover Produto", command=remover_produto, bg="#F44336", fg="white")
    button_remove.pack(side='left', padx=10)

    button_entrada = tk.Button(frame_buttons, text="Registrar Entrada", command=registrar_entrada, bg="#1E88E5", fg="white")
    button_entrada.pack(side='left', padx=10)

    button_saida = tk.Button(frame_buttons, text="Registrar Saída", command=registrar_saida, bg="#FF9800", fg="white")
    button_saida.pack(side='left', padx=10)

    button_exportar = tk.Button(frame_buttons, text="Exportar para Excel", command=exportar_para_excel, bg="#FFC107", fg="black")
    button_exportar.pack(side='left', padx=10)

    # Tabela para exibir os produtos
    columns = ("ID", "Produto", "Quantidade", "Preço", "Categoria")
    tree = ttk.Treeview(root, columns=columns, show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Produto", text="Produto")
    tree.heading("Quantidade", text="Quantidade")
    tree.heading("Preço", text="Preço")
    tree.heading("Categoria", text="Categoria")

    tree.pack(fill='both', expand=True)

    # Inicializar a lista de produtos
    atualizar_lista()

    root.mainloop()

# Interface de Login
tela_login = tk.Tk()
tela_login.title("Login")
tela_login.geometry("300x300")
tela_login.resizable(False, False)

# Carregando a imagem de fundo usando Pillow
bg_image = Image.open("C:/Users/ketle/OneDrive/Documentos/estoque/img/52723533aa348f70a5bba4676998d7af.jpg")
bg_image = bg_image.resize((300, 300), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(tela_login, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Adicionando os campos de entrada e rótulos
label_usuario = tk.Label(tela_login, text="Usuário", bg="#00796B", fg="white")
label_usuario.place(x=50, y=90)
entry_usuario = tk.Entry(tela_login, bg="#E0E0E0", fg="black")
entry_usuario.place(x=50, y=110, width=200, height=25)

label_senha = tk.Label(tela_login, text="Senha", bg="#00796B", fg="white")
label_senha.place(x=50, y=140)
entry_senha = tk.Entry(tela_login, show='*', bg="#E0E0E0", fg="black")
entry_senha.place(x=50, y=160, width=200, height=25)

# Adicionando o botão de login
button_login = tk.Button(tela_login, text="Login", command=verificar_login, bg="#1E88E5", fg="white", relief="flat")
button_login.place(x=50, y=200, width=200, height=30)

tela_login.mainloop()
