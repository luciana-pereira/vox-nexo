import soundcard as sc


def main():
    default_speaker = sc.default_speaker()
    print(f"Saída padrão: {default_speaker.name}")
    print("Saídas disponíveis:")

    for index, speaker in enumerate(sc.all_speakers()):
        marker = " (padrão)" if speaker.name == default_speaker.name else ""
        print(f"{index}: {speaker.name}{marker}")


if __name__ == "__main__":
    main()
