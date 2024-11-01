import tkinter as tk
from tkinter import messagebox
from librouteros import connect
from librouteros.exceptions import TrapError, FatalError
from librouteros.login import plain

def login():
    router_id = entry_router_id.get()
    username = entry_username.get()
    password = entry_password.get()
    
    try:
        global api  # Definir api como global para ser usada em outras funções
        api = connect(
            username=username,
            password=password,
            host=router_id,
            port=8728,  # Porta padrão para API
            login_method=plain,
            timeout=10
        )
        messagebox.showinfo("Success", "Connected to the router successfully!")
        root.destroy()
        open_dashboard()  # Passando o nome do roteador como argumento
    except (TrapError, FatalError) as e:
        messagebox.showerror("Error", f"Failed to connect to the router: {e}")


def clear():
    entry_router_id.delete(0, tk.END)
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

def open_dashboard():
    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("600x400")

    try:
        command = '/system/identity/print'
        router_name = list(api(cmd=command))[0]['name']
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve router name: {e}")
    
    
    tk.Label(dashboard, text=f"Router Name: {router_name}", font=("Helvetica", 12)).pack(pady=10)  # Exibe o nome do roteador
    tk.Label(dashboard, text="Welcome to the router dashboard!", font=("Helvetica", 12)).pack(pady=5)
    
    button_frame = tk.Frame(dashboard)  # Frame para os botões
    button_frame.pack()

    # Botões na horizontal
    tk.Button(button_frame, text="Interfaces", command=show_interfaces).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="OSPF", command=show_ospf).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Firewall", command=show_firewall).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Close", command=dashboard.destroy).pack(side=tk.LEFT, padx=5)

    global result_text
    result_text = tk.Text(dashboard, height=15, width=70)
    result_text.pack(pady=10)
    result_text.config(state=tk.DISABLED)  # Define a caixa de texto como somente leitura


def show_interfaces():
    try:
        command = '/ip/route/print'
        results = list(api(cmd=command))
        filtered_results = []

        count = 0
        for result in results:
            if count != 0:
                filtered_result = {
                    'Interface': result.get('gateway'),
                    'IP da Interface': result.get('pref-src'),
                    'Network': result.get('dst-address')
                }
                filtered_results.append(filtered_result)
            
            count += 1

        # Formatar os resultados para exibição
        display_text = "Interface \t\t IP da Interface \t\t Network \n"
        for res in filtered_results:
            display_text += f"{res['Interface']} \t\t {res['IP da Interface']} \t\t {res['Network']}\n"

        # Exibir os resultados na caixa de texto
        result_text.config(state=tk.NORMAL)  # Habilita a edição temporariamente para inserir texto
        result_text.delete(1.0, tk.END)  # Limpa o texto anterior
        result_text.insert(tk.END, display_text)
        result_text.config(state=tk.DISABLED)  # Define a caixa de texto como somente leitura novamente

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve interfaces: {e}")

def show_ospf():
    try:
        command_instance = '/routing/ospf/instance/print'
        results_instance = list(api(cmd=command_instance))

        display_text = "OSPF Configuration:\n"

        for instance in results_instance:
            instance_name = instance.get('name')
            router_id = instance.get('router-id')
            distribution = instance.get('distribute-default')

            display_text += f"\nInstance: {instance_name}, Router ID: {router_id}, Distribution: {distribution}\n"

            # Comando para obter as redes associadas à instância OSPF
            command_network = f'/routing/ospf/network/print'
            results_network = list(api(cmd=command_network))

            # Adiciona as redes à exibição
            for network in results_network:
                network_address = network.get('network')
                display_text += f"\tNetwork: {network_address}\n"

        # Exibir os resultados na caixa de texto
        result_text.config(state=tk.NORMAL)  # Habilita a edição temporariamente para inserir texto
        result_text.delete(1.0, tk.END)  # Limpa o texto anterior
        result_text.insert(tk.END, display_text)
        result_text.config(state=tk.DISABLED)  # Define a caixa de texto como somente leitura novamente

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve OSPF configuration: {e}")

def show_firewall():
    try:
        command = '/ip/firewall/filter/print'
        results = list(api(cmd=command))
        filtered_results = []

        for result in results:
            filtered_result = {
                'Chain': result.get('chain'),
                'Action': result.get('action'),
                'Src Address': result.get('src-address'),
                'Dst Address': result.get('dst-address')
            }
            filtered_results.append(filtered_result)

        # Formatar os resultados para exibição
        display_text = "Firewall Configuration:\n"
        for res in filtered_results:
            display_text += f"\n Chain: {res['Chain']}, Action: {res['Action']}, Src Address: {res['Src Address']}, Dst Address: {res['Dst Address']}\n"

        # Exibir os resultados na caixa de texto
        result_text.config(state=tk.NORMAL)  # Habilita a edição temporariamente para inserir texto
        result_text.delete(1.0, tk.END)  # Limpa o texto anterior
        result_text.insert(tk.END, display_text)
        result_text.config(state=tk.DISABLED)  # Define a caixa de texto como somente leitura novamente

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve firewall configuration: {e}")

# Criação da janela principal
root = tk.Tk()
root.title("Mikrotik")

# Centralizar a janela
window_width = 300
window_height = 210
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Título
title_label = tk.Label(root, text="Mikrotik", font=("Helvetica", 16))
title_label.pack(pady=10)

# Frame para os campos de entrada
frame = tk.Frame(root)
frame.pack(pady=10)

# Campo ID Router
label_router_id = tk.Label(frame, text="ID Router:")
label_router_id.grid(row=0, column=0, padx=5, pady=5)
entry_router_id = tk.Entry(frame)
entry_router_id.grid(row=0, column=1, padx=5, pady=5)

# Campo Username
label_username = tk.Label(frame, text="Username:")
label_username.grid(row=1, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame)
entry_username.grid(row=1, column=1, padx=5, pady=5)

# Campo Password
label_password = tk.Label(frame, text="Password:")
label_password.grid(row=2, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame, show='*')
entry_password.grid(row=2, column=1, padx=5, pady=5)

# Frame para os botões
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Botão Login
login_button = tk.Button(button_frame, text="Login", command=login)
login_button.grid(row=0, column=0, padx=10)

# Botão Clear
clear_button = tk.Button(button_frame, text="Clear", command=clear)
clear_button.grid(row=0, column=1, padx=10)

# Inicia a aplicação
root.mainloop()

