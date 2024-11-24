import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
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
        self.root.geometry("1000x700")
        self.translator = GoogleTranslator()
        self.current_file = None
        self.setup_menu()
        self.setup_ui()

    def setup_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_command(label="Guardar Como", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Menu Editar
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Cortar", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", 
                            command=lambda: self.text_area.tag_add("sel", "1.0", "end"))

        # Menu Tradução
        translate_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tradução", menu=translate_menu)
        translate_menu.add_command(label="Traduzir Texto", command=self.translate_current_text)
        translate_menu.add_command(label="Traduzir Arquivos em Lote", 
                                 command=self.show_batch_translation)

    def setup_ui(self):
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Aba de edição
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text='Editor')

        # Área de texto com barra de rolagem
        text_frame = ttk.Frame(self.edit_frame)
        text_frame.pack(expand=True, fill='both', padx=5, pady=5)

        self.text_area = tk.Text(text_frame, wrap=tk.WORD, undo=True)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)

        self.text_area.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')

        # Frame de botões do editor
        button_frame = ttk.Frame(self.edit_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Traduzir", command=self.translate_current_text).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Guardar", command=self.save_file).pack(side='left', padx=5)

        # Aba de tradução em lote
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text='Tradução em Lote')
        self.setup_batch_ui()

        # Barra de status
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_batch_ui(self):
        # Frame principal para tradução em lote
        main_frame = ttk.Frame(self.batch_frame, padding="10")
        main_frame.pack(expand=True, fill='both')

        # Pasta de entrada e saída
        ttk.Label(main_frame, text="Pasta de Entrada:").pack(anchor='w')
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=5)
        self.input_path = ttk.Entry(input_frame)
        self.input_path.pack(side='left', expand=True, fill='x', padx=(0, 5))
        ttk.Button(input_frame, text="Procurar", command=self.browse_input_folder).pack(side='right')

        ttk.Label(main_frame, text="Pasta de Saída:").pack(anchor='w')
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill='x', pady=5)
        self.output_path = ttk.Entry(output_frame)
        self.output_path.pack(side='left', expand=True, fill='x', padx=(0, 5))
        ttk.Button(output_frame, text="Procurar", command=self.browse_output_folder).pack(side='right')

        # Lista de arquivos
        ttk.Label(main_frame, text="Arquivos para traduzir:").pack(anchor='w', pady=(10, 5))
        self.file_listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(expand=True, fill='both')

        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate', 
                                          variable=self.progress_var)
        self.progress_bar.pack(fill='x', pady=10)

        # Botões de controle
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=5)
        ttk.Button(button_frame, text="Selecionar Todos", 
                  command=self.select_all_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Limpar Seleção", 
                  command=self.clear_selection).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Traduzir Selecionados", 
                  command=self.translate_selected_files).pack(side='right', padx=5)

    def show_batch_translation(self):
        self.notebook.select(1)  # Muda para a aba de tradução em lote

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.status_bar.config(text="Novo arquivo")
        self.notebook.select(0)  # Muda para a aba do editor

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, file.read())
                self.current_file = file_path
                self.status_bar.config(text=f"Arquivo aberto: {file_path}")
                self.notebook.select(0)  # Muda para a aba do editor
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")

    def save_file(self):
        if not self.current_file:
            self.save_as_file()
        else:
            try:
                text = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(text)
                self.status_bar.config(text=f"Arquivo salvo: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()

    def translate_current_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            translated = self.translator.translate(text)
            if translated:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, translated)
                self.status_bar.config(text="Texto traduzido com sucesso")
        else:
            messagebox.showwarning("Aviso", "Por favor, insira algum texto para traduzir.")

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

    def translate_selected_files(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Aviso", "Por favor, selecione alguns arquivos para traduzir.")
            return
        
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()

        if not input_folder or not output_folder:
            messagebox.showwarning("Aviso", "Por favor, selecione as pastas de entrada e saída.")
            return

        total_files = len(selected_indices)
        successful = 0
        self.progress_var.set(0)

        for i, idx in enumerate(selected_indices, 1):
            file = self.file_listbox.get(idx)
            self.status_bar.config(text=f"Traduzindo: {file}")
            
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, file)

            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                translated_text = self.translator.translate(text)
                if translated_text:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(translated_text)
                    successful += 1

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar arquivo {file}: {str(e)}")

            self.progress_var.set((i / total_files) * 100)
            self.root.update()
            time.sleep(1)  # Delay para evitar bloqueio da API

        self.status_bar.config(text=f"Concluído! {successful}/{total_files} arquivos traduzidos com sucesso.")
        messagebox.showinfo("Concluído", f"Tradução finalizada!\n{successful}/{total_files} arquivos traduzidos com sucesso.")

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()