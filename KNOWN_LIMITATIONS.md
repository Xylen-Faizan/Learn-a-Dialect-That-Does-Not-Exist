# Known Limitations & Human Boundary Controls

1. **Pre-Transcribed Dialogue:** Audio interviews were processed from transcribed text rather than raw phoneme waveforms to maintain determinism within the take-home time limit.
2. **Compound Morphological Tokenization:** Multi-part agglutinative suffixes are matched using deterministic string patterns rather than a full BPE tokenizer.
3. **Decisions Requiring Human Review:** Resolving dialect variants between conflicting dictionaries and approving translations for untranslated cultural concepts.
