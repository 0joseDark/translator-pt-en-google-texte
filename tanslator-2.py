import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import urllib.parse
import time
import json
import os
from typing import Optional

class GoogleTranslator:
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'pt') -> Optional[str]:
        try:
            if not text.strip():
                return ""
                
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            encoded_params = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{encoded_params}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            if result and isinstance(result[0], list):
                translated_text = ''
                for item in result[0]:
                    if item[0]:
                        translated_text += item[0]
                return translated_text
            
            return None
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na tradução: {str(e)}")
            return None

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tradutor de Ficheiros")
        self.root.geometry("800x600")
        self.translator = GoogleTranslator()
        self.current_file = None
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Pasta de entrada e saída
        ttk.Label(main_frame, text="Pasta de Entrada:").grid(row=0, column=0, sticky=tk.W)
        self.input_path = ttk.Entry(main_frame, width=50)
        self.input_path.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_input_folder).grid(row=0, column=2)

        ttk.Label(main_frame, text="Pasta de Saída:").grid(row=1, column=0, sticky=tk.W)
        self.output_path = ttk.Entry(main_frame, width=50)
        self.output_path.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_output_folder).grid(row=1, column=2)

        # Lista de arquivos
        ttk.Label(main_frame, text="Arquivos para traduzir:").grid(row=2, column=0, sticky=tk.W)
        self.file_listbox = tk.Listbox(main_frame, width=70, height=15)
        self.file_listbox.grid(row=3, column=0, columnspan=3, pady=5)

        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

        # Status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=3)

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        # Botões
        buttons = [
            ("Selecionar Todos", self.select_all_files),
            ("Limpar Seleção", self.clear_selection),
            ("Traduzir Selecionados", self.translate_selected_files),
            ("Traduzir Todos", self.translate_all_files),
            ("Sair", self.root.quit)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=0, column=i, padx=5)

    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de entrada")
        if folder:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, folder)
            self.update_file_list()

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de saída")
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        input_folder = self.input_path.get()
        if os.path.exists(input_folder):
            files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
            for file in files:
                self.file_listbox.insert(tk.END, file)

    def select_all_files(self):
        self.file_listbox.select_set(0, tk.END)

    def clear_selection(self):
        self.file_listbox.selection_clear(0, tk.END)

    def translate_file(self, input_file: str, output_file: str) -> bool:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            translated_text = self.translator.translate(text)
            if translated_text:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(translated_text)
                return True
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar arquivo {input_file}: {str(e)}")
            return False

    def translate_selected_files(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Aviso", "Por favor, selecione alguns arquivos para traduzir.")
            return
        self.translate_files([self.file_listbox.get(idx) for idx in selected_indices])

    def translate_all_files(self):
        files = list(self.file_listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("Aviso", "Nenhum arquivo encontrado na pasta de entrada.")
            return
        self.translate_files(files)

    def translate_files(self, files):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()

        if not input_folder or not output_folder:
            messagebox.showwarning("Aviso", "Por favor, selecione as pastas de entrada e saída.")
            return

        total_files = len(files)
        successful = 0
        self.progress_var.set(0)

        for i, file in enumerate(files, 1):
            self.status_label.config(text=f"Traduzindo: {file}")
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, file)

            if self.translate_file(input_file, output_file):
                successful += 1

            self.progress_var.set((i / total_files) * 100)
            self.root.update()
            time.sleep(1)  # Delay para evitar bloqueio da API

        self.status_label.config(text=f"Concluído! {successful}/{total_files} arquivos traduzidos com sucesso.")
        messagebox.showinfo("Concluído", f"Tradução finalizada!\n{successful}/{total_files} arquivos traduzidos com sucesso.")

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()