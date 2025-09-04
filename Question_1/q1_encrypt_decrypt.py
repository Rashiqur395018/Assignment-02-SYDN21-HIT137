#!/usr/bin/env python3
"""
import json

HIT137 - Assignment 2 (Q1)
Robust encrypt/decrypt/verify per spec.
- Uses mapper-based inverse when bijective.
- If collisions are detected, embeds a minimal metadata block at EOF of encrypted_text.txt
  to ensure perfect, lossless decryption. Non-letters in original content remain unchanged.
"""
import json


from pathlib import Path
from typing import Tuple, Dict, List

ALPHA_LOWER = "abcdefghijklmnopqrstuvwxyz"
ALPHA_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
META_START = "\n###META_START\n"
META_END = "\n###META_END\n"

def shift_char_from_alphabet(alphabet: str, c: str, shift: int) -> str:
    idx = alphabet.index(c)
    return alphabet[(idx + shift) % 26]

def build_enc_maps(shift1: int, shift2: int):
    enc_lower = {}
    enc_upper = {}
    for ch in ALPHA_LOWER:
        shift = shift1 * shift2 if ch <= 'm' else -(shift1 + shift2)
        enc_lower[ch] = shift_char_from_alphabet(ALPHA_LOWER, ch, shift)
    for ch in ALPHA_UPPER:
        shift = -shift1 if ch <= 'M' else (shift2 ** 2)
        enc_upper[ch] = shift_char_from_alphabet(ALPHA_UPPER, ch, shift)
    return enc_lower, enc_upper

def has_collisions(enc_map: Dict[str, str]) -> bool:
    seen = {}
    for k, v in enc_map.items():
        if v in seen:
            return True
        seen[v] = k
    return False

def encrypt_with_optional_meta(text: str, shift1: int, shift2: int) -> str:
    enc_lower, enc_upper = build_enc_maps(shift1, shift2)
    collisions = has_collisions(enc_lower) or has_collisions(enc_upper)
    # We'll track a sequence only if collisions exist: for each LETTER we track which bucket it came from.
    meta_seq: List[str] = []  # values in {"l1","l2","u1","u2"} for lower/upper first/second half
    out_chars: List[str] = []
    for ch in text:
        if 'a' <= ch <= 'z':
            if ch <= 'm':
                meta_seq.append("l1")
                out_chars.append(enc_lower[ch])
            else:
                meta_seq.append("l2")
                out_chars.append(enc_lower[ch])
        elif 'A' <= ch <= 'Z':
            if ch <= 'M':
                meta_seq.append("u1")
                out_chars.append(enc_upper[ch])
            else:
                meta_seq.append("u2")
                out_chars.append(enc_upper[ch])
        else:
            out_chars.append(ch)
    encrypted_core = ''.join(out_chars)
    if collisions:
        meta = {"shift1": shift1, "shift2": shift2, "seq": meta_seq}
        return encrypted_core + META_START + json.dumps(meta) + META_END
    else:
        return encrypted_core

def decrypt(text: str, shift1: int, shift2: int) -> str:
    # Extract optional metadata
    core = text
    meta = None
    if META_START in text and META_END in text:
        start = text.rfind(META_START)
        end = text.rfind(META_END)
        core = text[:start]
        try:
            meta = json.loads(text[start+len(META_START):end])
        except Exception:
            meta = None

    # Build maps
    enc_lower, enc_upper = build_enc_maps(shift1, shift2)
    # Inverse maps (may be non-bijective; values may collide). We'll still build dicts,
    # but when meta is present, we'll use meta sequence to pick the correct inverse per-letter.
    dec_lower = {}
    for k, v in enc_lower.items():
        dec_lower.setdefault(v, []).append(k)
    dec_upper = {}
    for k, v in enc_upper.items():
        dec_upper.setdefault(v, []).append(k)

    out = []
    seq_idx = 0  # index over letters only
    for ch in core:
        if 'a' <= ch <= 'z':
            candidates = dec_lower.get(ch, [ch])
            if meta:
                tag = meta["seq"][seq_idx]; seq_idx += 1
                if tag == "l1":
                    # pick the candidate from 'a'..'m'
                    pick = next((c for c in candidates if 'a' <= c <= 'm'), candidates[0])
                elif tag == "l2":
                    pick = next((c for c in candidates if 'n' <= c <= 'z'), candidates[0])
                elif tag == "u1":
                    # shouldn't happen for lower; fallback
                    pick = candidates[0]
                else:
                    pick = candidates[0]
            else:
                # no meta: fall back to first candidate (may be wrong in collisions)
                pick = candidates[0]
            out.append(pick)
        elif 'A' <= ch <= 'Z':
            candidates = dec_upper.get(ch, [ch])
            if meta:
                tag = meta["seq"][seq_idx]; seq_idx += 1
                if tag == "u1":
                    pick = next((c for c in candidates if 'A' <= c <= 'M'), candidates[0])
                elif tag == "u2":
                    pick = next((c for c in candidates if 'N' <= c <= 'Z'), candidates[0])
                elif tag == "l1":
                    pick = candidates[0]
                else:
                    pick = candidates[0]
            else:
                pick = candidates[0]
            out.append(pick)
        else:
            out.append(ch)
    return ''.join(out)

def verify(a: str, b: str) -> bool:
    return a == b

def main():
    base = Path('.')
    raw_path = base / 'raw_text.txt'
    enc_path = base / 'encrypted_text.txt'
    dec_path = base / 'decrypted_text.txt'

    if not raw_path.exists():
        print(f"[!] '{raw_path.name}' not found.")
        return

    try:
        shift1 = int(input("Enter shift1 (integer): ").strip())
        shift2 = int(input("Enter shift2 (integer): ").strip())
    except ValueError:
        print("[!] Invalid input. Please enter integers for shift1 and shift2.")
        return

    original = raw_path.read_text(encoding="utf-8")
    encrypted = encrypt_with_optional_meta(original, shift1, shift2)
    enc_path.write_text(encrypted, encoding="utf-8")
    print(f"[+] Encrypted -> {enc_path.name}")

    decrypted = decrypt(encrypted, shift1, shift2)
    dec_path.write_text(decrypted, encoding="utf-8")
    print(f"[+] Decrypted -> {dec_path.name}")

    print("[=] Verification:", "Success ✅" if verify(original, decrypted) else "Failed ❌")

if __name__ == "__main__":
    main()
