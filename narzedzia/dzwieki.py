#!/usr/bin/env python3
"""Generuje dźwięki gry Commando do gra/dzwieki/ (WAV, 22 050 Hz, mono, 16 bit).

Wszystkie próbki są syntetyczne (szum i proste fale), powstają z tego skryptu
i są na tej samej licencji co projekt (MIT). Uruchomienie: python3 narzedzia/dzwieki.py
"""
import math
import os
import random
import struct
import wave

CZESTOTLIWOSC = 22050
KATALOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gra", "dzwieki")


def zapisz(nazwa, probki):
    os.makedirs(KATALOG, exist_ok=True)
    with wave.open(os.path.join(KATALOG, nazwa), "wb") as plik:
        plik.setnchannels(1)
        plik.setsampwidth(2)
        plik.setframerate(CZESTOTLIWOSC)
        szczyt = max(1e-9, max(abs(p) for p in probki))
        dane = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, p / szczyt * 0.9)) * 32767)) for p in probki)
        plik.writeframes(dane)


def szum(sekundy, zanik, filtr, los):
    """Szum z wykładniczym zanikiem i prostym filtrem dolnoprzepustowym (0..1, mniej = ciemniej)."""
    n = int(sekundy * CZESTOTLIWOSC)
    wynik, poprzedni = [], 0.0
    for i in range(n):
        t = i / CZESTOTLIWOSC
        poprzedni += filtr * (los.uniform(-1, 1) - poprzedni)
        wynik.append(poprzedni * math.exp(-t * zanik))
    return wynik


def ton(od_hz, do_hz, sekundy, zanik=0.0, ksztalt="sin"):
    n = int(sekundy * CZESTOTLIWOSC)
    wynik, faza = [], 0.0
    for i in range(n):
        t = i / CZESTOTLIWOSC
        f = od_hz + (do_hz - od_hz) * (i / max(1, n - 1))
        faza += 2 * math.pi * f / CZESTOTLIWOSC
        fala = math.sin(faza) if ksztalt == "sin" else (1.0 if math.sin(faza) >= 0 else -1.0) * 0.6
        obwiednia = min(1.0, i / 80) * math.exp(-t * zanik)
        wynik.append(fala * obwiednia)
    return wynik


def main():
    los = random.Random(1985)
    zapisz("strzal.wav", szum(0.09, 45, 0.6, los))
    rzut = [s * 0.5 for s in szum(0.25, 6, 0.08, los)]
    zapisz("rzut.wav", rzut)
    huk = szum(0.9, 4.5, 0.05, los)
    trzask = szum(0.12, 30, 0.5, los)
    zapisz("wybuch.wav", [h + (trzask[i] * 0.6 if i < len(trzask) else 0.0) for i, h in enumerate(huk)])
    zapisz("trafienie.wav", [a + b * 0.4 for a, b in zip(ton(420, 160, 0.12, 18, "kw"), szum(0.12, 25, 0.4, los))])
    zapisz("smierc.wav", ton(520, 90, 0.7, 2.5, "kw"))
    zapisz("bonus.wav", ton(660, 660, 0.07, 0, "kw") + ton(880, 880, 0.07, 0, "kw") + ton(1320, 1320, 0.12, 8, "kw"))
    fanfara = []
    for hz, dl in ((392, 0.14), (523, 0.14), (659, 0.14), (784, 0.36)):
        fanfara += ton(hz, hz, dl, 3, "kw")
    zapisz("obszar.wav", fanfara)
    zapisz("koniec.wav", ton(392, 392, 0.25, 2, "kw") + ton(330, 330, 0.25, 2, "kw") + ton(262, 196, 0.6, 2, "kw"))
    with open(os.path.join(KATALOG, "ZRODLO.txt"), "w", encoding="utf-8") as plik:
        plik.write("Dźwięki wygenerowane syntetycznie przez narzedzia/dzwieki.py (szum i proste fale).\n"
                   "Licencja jak cały projekt: MIT.\n")
    print("Zapisano dźwięki w", os.path.normpath(KATALOG))


if __name__ == "__main__":
    main()
