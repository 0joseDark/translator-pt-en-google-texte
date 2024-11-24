import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import requests
import urllib.parse
import time
import json
import os
from typing import Optional

class ProgressDialog:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Progresso da Tradução")
        self.window.geometry("400x150")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configurar o diálogo
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)  # Impedir fechamento
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Labels
        self.file_label = ttk.Label(main_frame, text="Preparando...")
        self.file_label.pack(fill='x', pady=(0, 10))
        
        # Barra de progresso do arquivo atual
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(side='left', fill='x', expand=True)
        
        self.percent_label = ttk.Label(progress_frame, text="0%", width=6)
        self.percent_label.pack(side='left', padx=(5, 0))
        
        # Progresso total
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill='x', pady=(10, 0))
        
        self.total_label = ttk.Label(total_frame, text="Progresso Total:")
        self.total_label.pack(fill='x')
        
        total_progress_frame = ttk.Frame(total_frame)
        total_progress_frame.pack(fill='x', pady=5)
        
        self.total_var = tk.DoubleVar()
        self.total_bar = ttk.Progressbar(
            total_progress_frame,
            variable=self.total_var,
            maximum=100,
            mode='determinate',
            length=300
        )
        self.total_bar.pack(side='left', fill='x', expand=True)
        
        self.total_percent = ttk.Label(total_progress_frame, text="0%", width=6)
        self.total_percent.pack(side='left', padx=(5, 0))

    def update(self, file_name, progress, total_progress):
        self.file_label.config(text=f"Traduzindo: {file_name}")
        self.progress_var.set(progress)
        self.percent_label.config(text=f"{progress:.1f}%")
        self.total_var.set(total_progress)
        self.total_percent.config(text=f"{total_progress:.1f}%")
        self.window.update()

    def close(self):
        self.window.destroy()

class GoogleTranslator:
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

    def translate_with_progress(self, text: str, progress_callback=None) -> Optional[str]:
        if not text.strip():
            return ""

        # Dividir o texto em chunks para mostrar progresso
        chunks = text.split('\n')
        total_chunks = len(chunks)
        translated_chunks = []

        for i, chunk in enumerate(chunks, 1):
            if not chunk.strip():
                translated_chunks.append('')
                continue

            try:
                params = {
                    'client': 'gtx',
                    'sl': 'en',
                    'tl': 'pt',
                    'dt': 't',
                    'q': chunk
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
                    translated_chunks.append(translated_text)
                else:
                    translated_chunks.append(chunk)

                if progress_callback:
                    progress = (i / total_chunks) * 100
                    progress_callback(progress)

                time.sleep(0.5)  # Delay para evitar bloqueio

            except Exception as e:
                print(f"Erro ao traduzir chunk: {e}")
                translated_chunks.append(chunk)

        return '\n'.join(translated_chunks)

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
        # [Código do menu permanece o mesmo...]
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_command(label="Guardar Como", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Cortar", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", 
                            command=lambda: self.text_area.tag_add("sel", "1.0", "end"))

        translate_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tradução", menu=translate_menu)
        translate_menu.add_command(label="Traduzir Texto", command=self.translate_current_text)
        translate_menu.add_command(label="Traduzir Ficheiros", command=self.translate_batch)

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        # Área de texto
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(expand=True, fill='both', pady=5)

        self.text_area = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)

        self.text_area.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Traduzir", command=self.translate_current_text).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Traduzir Ficheiros", command=self.translate_batch).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Guardar", command=self.save_file).pack(side='left', padx=5)

        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def translate_batch(self):
        input_dir = filedialog.askdirectory(title="Selecione a pasta com os ficheiros para traduzir")
        if not input_dir:
            return

        output_dir = filedialog.askdirectory(title="Selecione a pasta para salvar as traduções")
        if not output_dir:
            return

        # Listar arquivos .txt
        files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        if not files:
            messagebox.showwarning("Aviso", "Nenhum arquivo .txt encontrado na pasta!")
            return

        # Criar diálogo de progresso
        progress_dialog = ProgressDialog(self.root)
        total_files = len(files)

        try:
            for i, file_name in enumerate(files, 1):
                input_path = os.path.join(input_dir, file_name)
                output_path = os.path.join(output_dir, file_name)

                # Ler arquivo
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Traduzir com progresso
                def update_progress(file_progress):
                    total_progress = ((i - 1) + (file_progress / 100)) / total_files * 100
                    progress_dialog.update(file_name, file_progress, total_progress)

                translated_text = self.translator.translate_with_progress(content, update_progress)

                # Salvar tradução
                if translated_text:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(translated_text)

            messagebox.showinfo("Sucesso", f"Tradução concluída!\n{total_files} arquivos traduzidos com sucesso.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a tradução: {str(e)}")

        finally:
            progress_dialog.close()

    def translate_current_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Por favor, insira algum texto para traduzir.")
            return

        progress_dialog = ProgressDialog(self.root)
        
        try:
            def update_progress(progress):
                progress_dialog.update("Texto atual", progress, progress)

            translated = self.translator.translate_with_progress(text, update_progress)
            
            if translated:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, translated)
                self.status_var.set("Tradução concluída!")
                messagebox.showinfo("Sucesso", "Texto traduzido com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a tradução: {str(e)}")

        finally:
            progress_dialog.close()

    # [Outros métodos permanecem os mesmos...]
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.status_var.set("Novo arquivo")

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
                self.status_var.set(f"Arquivo aberto: {file_path}")
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
                self.status_var.set(f"Arquivo salvo: {self.current_file}")
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

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()