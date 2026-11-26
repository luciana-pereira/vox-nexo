import ctypes
import queue
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

import soundcard as sc

from . import __version__
from .live_translator import LiveTranslator
from .word_export import export_transcription

APP_FRAME_STYLE = "App.TFrame"
PANEL_FRAME_STYLE = "Panel.TFrame"
HEADER_FRAME_STYLE = "Header.TFrame"
SUBTITLE_LABEL_STYLE = "Subtitle.TLabel"
SECTION_LABEL_STYLE = "Section.TLabel"
HEADER_TITLE_STYLE = "HeaderTitle.TLabel"
HEADER_SUBTITLE_STYLE = "HeaderSubtitle.TLabel"
BRAND_MARK_STYLE = "BrandMark.TLabel"
HEADER_STATUS_STYLE = "HeaderStatus.TLabel"
ACCENT_BUTTON_STYLE = "Accent.TButton"
EXPORT_BUTTON_STYLE = "Export.TButton"
FONT_FAMILY = "Manrope"

NAVY = "#10243A"
NAVY_SOFT = "#193652"
BLUE = "#2563EB"
BLUE_HOVER = "#174FC4"
CYAN = "#35C6D8"
LIGHT = "#F2F7FC"
WHITE = "#FFFFFF"
INK = "#132B45"
MUTED = "#60758B"
BORDER = "#DCE7F1"
PALE_CYAN = "#E4F8FA"


def load_brand_font():
    if sys.platform != "win32":
        return False

    font_path = Path(__file__).parent / "assets" / "fonts" / "Manrope-Variable.ttf"
    if not font_path.is_file():
        return False

    return bool(ctypes.windll.gdi32.AddFontResourceExW(str(font_path), 0x10, 0))


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VoxNexo | Desktop Audio Translator")
        self.root.geometry("1160x780")
        self.root.minsize(900, 600)
        self.root.configure(bg=LIGHT)

        self.events = queue.Queue()
        self.worker = None
        self.is_running = False
        self.entries = []
        self.speakers = self._get_speakers()
        self.speaker_names = [speaker.name for speaker in self.speakers]
        self.speaker_name = tk.StringVar(value=self._default_speaker_name())
        self.status_text = tk.StringVar(value="Pronto para iniciar")

        self._configure_style()
        self._build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self._poll_events)

    def _get_speakers(self):
        try:
            return sc.all_speakers()
        except Exception:
            return []

    def _default_speaker_name(self):
        try:
            return sc.default_speaker().name
        except Exception:
            return self.speaker_names[0] if self.speaker_names else ""

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(APP_FRAME_STYLE, background=LIGHT)
        style.configure(PANEL_FRAME_STYLE, background=WHITE)
        style.configure(HEADER_FRAME_STYLE, background=NAVY)
        style.configure(
            BRAND_MARK_STYLE,
            background=CYAN,
            foreground=NAVY,
            font=(FONT_FAMILY, 13, "bold"),
            padding=(10, 9),
        )
        style.configure(
            HEADER_TITLE_STYLE,
            background=NAVY,
            foreground=WHITE,
            font=(FONT_FAMILY, 23, "bold"),
        )
        style.configure(
            HEADER_SUBTITLE_STYLE,
            background=NAVY,
            foreground="#B9CCDF",
            font=(FONT_FAMILY, 9),
        )
        style.configure(
            HEADER_STATUS_STYLE,
            background=NAVY_SOFT,
            foreground=CYAN,
            font=(FONT_FAMILY, 9, "bold"),
            padding=(11, 7),
        )
        style.configure(
            SUBTITLE_LABEL_STYLE,
            background=LIGHT,
            foreground=MUTED,
            font=(FONT_FAMILY, 9),
        )
        style.configure(
            SECTION_LABEL_STYLE,
            background=WHITE,
            foreground=NAVY,
            font=(FONT_FAMILY, 9, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=LIGHT,
            foreground=BLUE,
            font=(FONT_FAMILY, 9, "bold"),
        )
        style.configure("TButton", font=(FONT_FAMILY, 9, "bold"), padding=(12, 8))
        style.configure(
            ACCENT_BUTTON_STYLE,
            background=BLUE,
            foreground=WHITE,
            font=(FONT_FAMILY, 9, "bold"),
            padding=(13, 9),
        )
        style.map(
            ACCENT_BUTTON_STYLE,
            background=[("active", BLUE_HOVER), ("disabled", "#9AB4E8")],
            foreground=[("disabled", WHITE)],
        )
        style.configure(
            EXPORT_BUTTON_STYLE,
            background=PALE_CYAN,
            foreground=NAVY,
            font=(FONT_FAMILY, 9, "bold"),
            padding=(13, 9),
        )
        style.map(EXPORT_BUTTON_STYLE, background=[("active", "#C9F0F4")])
        style.configure("Treeview", rowheight=32, font=(FONT_FAMILY, 9))
        style.configure("Treeview.Heading", font=(FONT_FAMILY, 9, "bold"))
        style.configure(
            "TCombobox",
            padding=8,
            font=(FONT_FAMILY, 9),
            fieldbackground=WHITE,
            foreground=INK,
        )

    def _build_interface(self):
        page = ttk.Frame(self.root, style=APP_FRAME_STYLE, padding=(28, 22, 28, 18))
        page.pack(fill="both", expand=True)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)

        header = ttk.Frame(page, style=HEADER_FRAME_STYLE, padding=(20, 17))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="VN", style=BRAND_MARK_STYLE).grid(
            row=0, column=0, rowspan=2, sticky="w", padx=(0, 14)
        )
        ttk.Label(header, text="VoxNexo", style=HEADER_TITLE_STYLE).grid(
            row=0, column=1, sticky="sw"
        )
        ttk.Label(
            header,
            text=f"DESKTOP AUDIO TRANSLATOR  ·  INGLÊS → PORTUGUÊS  ·  v{__version__}",
            style=HEADER_SUBTITLE_STYLE,
        ).grid(row=1, column=1, sticky="nw", pady=(2, 0))
        ttk.Label(header, textvariable=self.status_text, style=HEADER_STATUS_STYLE).grid(
            row=0, column=2, rowspan=2, sticky="e", padx=(18, 0)
        )

        controls = ttk.Frame(page, style=PANEL_FRAME_STYLE, padding=(16, 14))
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="SAÍDA DE ÁUDIO", style=SECTION_LABEL_STYLE).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.speaker_picker = ttk.Combobox(
            controls,
            textvariable=self.speaker_name,
            values=self.speaker_names,
            state="readonly" if self.speaker_names else "disabled",
            width=36,
        )
        self.speaker_picker.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self.start_button = ttk.Button(
            controls,
            text="Iniciar tradução",
            style=ACCENT_BUTTON_STYLE,
            command=self._start,
        )
        self.start_button.grid(row=0, column=2, padx=(0, 8))
        self.stop_button = ttk.Button(
            controls,
            text="Parar",
            command=self._stop,
            state="disabled",
        )
        self.stop_button.grid(row=0, column=3, padx=(0, 8))
        self.export_button = ttk.Button(
            controls,
            text="Exportar Word",
            command=self._export_word,
            state="disabled",
        )
        self.export_button.grid(row=0, column=4)

        transcript_panel = ttk.Frame(page, style=PANEL_FRAME_STYLE, padding=(16, 14))
        transcript_panel.grid(row=2, column=0, sticky="nsew")
        transcript_panel.columnconfigure(0, weight=1)
        transcript_panel.rowconfigure(1, weight=1)
        ttk.Label(
            transcript_panel,
            text="TRANSCRIÇÃO E TRADUÇÃO",
            style=SECTION_LABEL_STYLE,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.transcript = scrolledtext.ScrolledText(
            transcript_panel,
            wrap="word",
            state="disabled",
            bg=WHITE,
            fg=INK,
            insertbackground=BLUE,
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=16,
            font=(FONT_FAMILY, 10),
            spacing1=3,
            spacing3=10,
        )
        self.transcript.grid(row=1, column=0, sticky="nsew")
        self.transcript.tag_configure("timestamp", foreground=MUTED, font=(FONT_FAMILY, 8))
        self.transcript.tag_configure(
            "original_label", foreground=MUTED, font=(FONT_FAMILY, 8, "bold")
        )
        self.transcript.tag_configure("original", foreground=INK, font=(FONT_FAMILY, 10))
        self.transcript.tag_configure(
            "translation_label", foreground=BLUE, font=(FONT_FAMILY, 8, "bold")
        )
        self.transcript.tag_configure(
            "translation", foreground=NAVY, font=(FONT_FAMILY, 11, "bold")
        )
        self.transcript.tag_configure("separator", foreground=BORDER)
        self.transcript.tag_configure("empty", foreground=MUTED, font=(FONT_FAMILY, 10))
        self.transcript.configure(state="normal")
        self.transcript.insert(
            "end",
            "Sua sessão aparecerá aqui\n\nSelecione a saída de áudio e inicie a tradução.",
            "empty",
        )
        self.transcript.configure(state="disabled")

        footer = ttk.Frame(page, style=APP_FRAME_STYLE)
        footer.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(
            footer,
            text="Captura exclusiva do áudio de reprodução. Nenhum microfone é aberto.",
            style=SUBTITLE_LABEL_STYLE,
        ).grid(row=0, column=0, sticky="w")
        self.count_text = tk.StringVar(value="0 trechos")
        ttk.Label(footer, textvariable=self.count_text, style=SUBTITLE_LABEL_STYLE).grid(
            row=0, column=1, sticky="e"
        )

    def _start(self):
        if not self.speaker_name.get():
            messagebox.showerror(
                "Saída de áudio indisponível",
                "Não encontrei dispositivos de reprodução. Conecte uma saída de áudio e reabra o aplicativo.",
            )
            return

        self.worker = LiveTranslator(self.speaker_name.get(), self.events.put)
        self.worker.start()
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.speaker_picker.configure(state="disabled")
        self.status_text.set("Iniciando captura local...")

    def _stop(self):
        if self.worker:
            self.worker.stop()
        self.status_text.set("Encerrando captura...")
        self.stop_button.configure(state="disabled")

    def _poll_events(self):
        while True:
            try:
                event_type, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event_type == "status":
                self.status_text.set(payload["message"])
            elif event_type == "result":
                self._append_result(payload)
            elif event_type == "error":
                self.status_text.set("Falha na captura")
                messagebox.showerror("Não foi possível iniciar", payload["message"])
            elif event_type == "stopped":
                self.is_running = False
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
                self.speaker_picker.configure(
                    state="readonly" if self.speaker_names else "disabled"
                )
                if self.status_text.get() != "Falha na captura":
                    self.status_text.set("Captura parada")

        self.root.after(100, self._poll_events)

    def _append_result(self, result):
        first_result = not self.entries
        self.entries.append(result)
        self.transcript.configure(state="normal")
        if first_result:
            self.transcript.delete("1.0", "end")
        self.transcript.insert("end", f"{result['timestamp']}\n", "timestamp")
        self.transcript.insert("end", "ORIGINAL · INGLÊS\n", "original_label")
        self.transcript.insert("end", f"{result['original']}\n", "original")
        self.transcript.insert("end", "TRADUÇÃO · PORTUGUÊS\n", "translation_label")
        self.transcript.insert("end", f"{result['translated']}\n", "translation")
        self.transcript.insert("end", "────────────────────────────────────────\n", "separator")
        self.transcript.see("end")
        self.transcript.configure(state="disabled")
        self.count_text.set(f"{len(self.entries)} trechos")
        self.export_button.configure(state="normal")

    def _export_word(self):
        if not self.entries:
            return

        destination = filedialog.asksaveasfilename(
            title="Exportar tradução para Word",
            defaultextension=".docx",
            filetypes=(("Documento do Word", "*.docx"),),
            initialfile=f"voxnexo_transcricao_{datetime.now():%Y%m%d_%H%M}.docx",
        )
        if not destination:
            return

        try:
            export_transcription(self.entries, self.speaker_name.get(), destination)
            messagebox.showinfo("Exportação concluída", f"Documento salvo em:\n{destination}")
        except Exception as error:
            messagebox.showerror("Falha na exportação", str(error))

    def _close(self):
        if self.worker:
            self.worker.stop()
        self.root.destroy()


def main():
    load_brand_font()
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
