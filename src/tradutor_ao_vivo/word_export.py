from datetime import datetime

from docx import Document


def export_transcription(entries, speaker_name, destination, exported_at=None):
    exported_at = exported_at or datetime.now()
    document = Document()
    document.add_heading("VoxNexo | Transcrição traduzida", level=0)
    document.add_paragraph(f"Exportado em {exported_at:%d/%m/%Y às %H:%M}")
    document.add_paragraph(f"Saída de áudio: {speaker_name}")

    table = document.add_table(rows=1, cols=3)
    table.style = "Light Shading Accent 1"
    headers = table.rows[0].cells
    headers[0].text = "Horário"
    headers[1].text = "Original (inglês)"
    headers[2].text = "Tradução (português)"

    for entry in entries:
        cells = table.add_row().cells
        cells[0].text = entry["timestamp"]
        cells[1].text = entry["original"]
        cells[2].text = entry["translated"]

    document.save(destination)
