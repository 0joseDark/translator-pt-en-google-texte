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
        self.root.title("Tradutor de Textos")
        self.root.geometry("800x600")
        self.translator = GoogleTranslator()
        self.current_file = None
        
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Entrada e saída de arquivos
        ttk.Label(main_frame, text="Arquivo de Entrada:").grid(row=0, column=0, sticky=tk.W)
        self.input_path = ttk.Entry(main_frame, width=50)
        self.input_path.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_input).grid(row=0, column=2)

        ttk.Label(main_frame, text="Arquivo de Saída:").grid(row=1, column=0, sticky=tk.W)
        self.output_path = ttk.Entry(main_frame, width=50)
        self.output_path.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_output).grid(row=1, column=2)

        # Área de texto
        self.text_area = tk.Text(main_frame, height=20, width=80, wrap=tk.WORD)
        self.text_area.grid(row=2, column=0, columnspan=3, pady=10)

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # Botões
        buttons = [
            ("Criar", self.create_new),
            ("Editar", self.edit_text),
            ("Modificar", self.modify_text),
            ("Sublinhar", self.underline_text),
            ("Copiar", self.copy_text),
            ("Guardar", self.save_file),
            ("Guardar Como", self.save_as_file),
            ("Traduzir", self.translate_text),
            ("Sair", self.root.quit)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=0, column=i, padx=5)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, filename)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, filename)

    def create_new(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None

    def edit_text(self):
        self.text_area.config(state=tk.NORMAL)

    def modify_text(self):
        # Implementar lógica de modificação específica aqui
        selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text_area.tag_ranges(tk.SEL) else ""
        if selected_text:
            modified_text = selected_text.upper()  # Exemplo: converter para maiúsculas
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, modified_text)

    def underline_text(self):
        if self.text_area.tag_ranges(tk.SEL):
            self.text_area.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.tag_config("underline", underline=True)

    def copy_text(self):
        selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text_area.tag_ranges(tk.SEL) else ""
        if selected_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)

    def save_file(self):
        if not self.current_file:
            self.save_as_file()
        else:
            text = self.text_area.get(1.0, tk.END)
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(text)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
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

    def translate_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            translated = self.translator.translate(text)
            if translated:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, translated)
                messagebox.showinfo("Sucesso", "Texto traduzido com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Por favor, insira algum texto para traduzir.")

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()