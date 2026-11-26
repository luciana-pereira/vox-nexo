from datetime import datetime

from docx import Document

from tradutor_ao_vivo.word_export import export_transcription


def test_exports_session_rows_to_word(tmp_path):
    destination = tmp_path / "translation.docx"
    entries = [
        {
            "timestamp": "00:00:04",
            "original": "Good morning.",
            "translated": "Bom dia.",
        }
    ]

    export_transcription(
        entries,
        "Default Speakers",
        destination,
        exported_at=datetime(2026, 11, 14, 10, 30),
    )

    document = Document(destination)
    row = document.tables[0].rows[1].cells
    assert [cell.text for cell in row] == ["00:00:04", "Good morning.", "Bom dia."]
    assert document.paragraphs[0].text == "VoxNexo | Transcrição traduzida"
    assert any("Default Speakers" in paragraph.text for paragraph in document.paragraphs)
