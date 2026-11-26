import queue
import re
import threading
import time

import argostranslate.package
import argostranslate.translate
import av
import numpy as np
import soundcard as sc
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
WINDOW_SECONDS = 3
OVERLAP_SECONDS = 2
BLOCK_SECONDS = 0.25


def remove_repeated_prefix(previous_text, current_text):
    previous_words = previous_text.split()
    current_words = current_text.split()
    previous_normalized = [re.sub(r"\W", "", word).casefold() for word in previous_words]
    current_normalized = [re.sub(r"\W", "", word).casefold() for word in current_words]

    for overlap in range(min(len(previous_words), len(current_words)), 0, -1):
        if previous_normalized[-overlap:] == current_normalized[:overlap]:
            return " ".join(current_words[overlap:]).strip()

    if " ".join(previous_normalized) == " ".join(current_normalized):
        return ""
    return current_text.strip()


def get_local_translation():
    try:
        return argostranslate.translate.get_translation_from_codes("en", "pt")
    except Exception:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package = next(
            (
                item
                for item in available_packages
                if item.from_code == "en" and item.to_code == "pt"
            ),
            None,
        )
        if package is None:
            raise RuntimeError("Não foi encontrado o modelo local inglês-português.")
        package_path = package.download()
        argostranslate.package.install_from_path(package_path)
        return argostranslate.translate.get_translation_from_codes("en", "pt")


class LiveTranslator:
    def __init__(self, speaker_name, event_callback):
        self.speaker_name = speaker_name
        self.event_callback = event_callback
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _emit(self, event_type, **payload):
        self.event_callback((event_type, payload))

    def _run(self):
        try:
            self.started_at = time.monotonic()
            self.previous_window_text = ""
            self._emit("status", message="Carregando reconhecimento de fala...")
            model = WhisperModel("distil-small.en", compute_type="int8")

            self._emit("status", message="Preparando tradução offline...")
            translation = get_local_translation()

            speaker = sc.get_speaker(self.speaker_name)
            loopback = sc.get_microphone(
                id=str(speaker.name),
                include_loopback=True,
            )
            if not loopback.isloopback:
                raise RuntimeError("A entrada selecionada não é um loopback de áudio.")

            self._emit(
                "status",
                message=f"Capturando somente o áudio de reprodução: {speaker.name}",
            )
            self._capture_loopback(loopback, model, translation)
        except Exception as error:
            self._emit("error", message=str(error))
        finally:
            self.stop_event.set()
            self._emit("stopped")

    def _capture_loopback(self, loopback, model, translation):
        channel_count = min(int(loopback.channels), 2)
        if channel_count < 1:
            raise RuntimeError("O dispositivo de reprodução não oferece canais de áudio.")

        errors = []
        for source_rate in (48000, 44100, 16000):
            if self.stop_event.is_set():
                return
            windows = queue.Queue(maxsize=1)
            capture_errors = queue.Queue(maxsize=1)
            capture_thread = threading.Thread(
                target=self._capture_windows,
                args=(loopback, source_rate, channel_count, windows, capture_errors),
                daemon=True,
            )
            capture_thread.start()

            while not self.stop_event.is_set():
                try:
                    window = windows.get(timeout=0.2)
                except queue.Empty:
                    if not capture_thread.is_alive():
                        break
                    continue
                self._transcribe_window(window, source_rate, model, translation)

            capture_thread.join(timeout=1)
            if not capture_errors.empty():
                errors.append(f"{source_rate} Hz: {capture_errors.get()}")
                continue
            return

        raise RuntimeError("Não foi possível abrir o loopback. " + " | ".join(errors))

    def _capture_windows(
        self,
        loopback,
        source_rate,
        channel_count,
        windows,
        capture_errors,
    ):
        block_frames = max(1024, int(source_rate * BLOCK_SECONDS))
        window_frames = int(source_rate * WINDOW_SECONDS)
        overlap_frames = int(source_rate * OVERLAP_SECONDS)
        audio_buffer = np.empty(0, dtype=np.float32)
        try:
            with loopback.recorder(
                samplerate=source_rate,
                channels=list(range(channel_count)),
                blocksize=block_frames,
            ) as recorder:
                while not self.stop_event.is_set():
                    audio_block = recorder.record(numframes=block_frames)
                    if audio_block.size == 0:
                        continue

                    mono_block = np.asarray(audio_block, dtype=np.float32).mean(axis=1)
                    audio_buffer = np.concatenate((audio_buffer, mono_block))
                    if len(audio_buffer) < window_frames:
                        continue

                    window = audio_buffer[-window_frames:].copy()
                    try:
                        windows.put_nowait(window)
                    except queue.Full:
                        try:
                            windows.get_nowait()
                        except queue.Empty:
                            pass
                        windows.put_nowait(window)

                    audio_buffer = audio_buffer[-overlap_frames:]
        except Exception as error:
            capture_errors.put(error)

    def _transcribe_window(self, window, source_rate, model, translation):
        audio_16khz = self._resample(window, source_rate)
        segments, _ = model.transcribe(
            audio_16khz,
            language="en",
            beam_size=3,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 400},
            condition_on_previous_text=False,
        )
        current_text = " ".join(
            segment.text.strip() for segment in segments if segment.text.strip()
        ).strip()
        new_text = remove_repeated_prefix(self.previous_window_text, current_text)
        self.previous_window_text = current_text

        if new_text:
            translated_text = translation.translate(new_text)
            elapsed = int(time.monotonic() - self.started_at)
            self._emit(
                "result",
                timestamp=time.strftime("%H:%M:%S", time.gmtime(elapsed)),
                original=new_text,
                translated=translated_text,
            )

    @staticmethod
    def _resample(audio, source_rate):
        if source_rate == SAMPLE_RATE:
            return audio

        frame = av.AudioFrame.from_ndarray(
            audio.reshape(1, -1),
            format="fltp",
            layout="mono",
        )
        frame.sample_rate = source_rate
        resampler = av.AudioResampler(
            format="fltp",
            layout="mono",
            rate=SAMPLE_RATE,
        )
        converted = resampler.resample(frame)
        converted.extend(resampler.resample(None))
        return np.concatenate([item.to_ndarray()[0] for item in converted])
