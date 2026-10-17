# Decision log

Short dated entries for choices made where the instructions were open to more than one reading. Longer design decisions are in `docs/adr/`.

| Date | Context | Choice | Reason |
|---|---|---|---|
| 2026-10-17 | A fresh Windows checkout wrote extraction notes with CRLF, so every content hash failed | Pin `eol=lf` in `.gitattributes` and hash notes with line endings normalised to LF | The hash should protect the wording of a note, not the line ending convention of the machine that checked it out |
| 2026-10-17 | "Real organisation names" is not a closed list | The voice test blocks a fixed list kept in `tests/voice_rules.json`: public bodies, media outlets, companies and review persona organisations named in this project. Place names (UAE, Abu Dhabi), programme and strategy names, and software tooling (GitHub, Vercel, Google Fonts) are not blocked | Place and programme names describe the subject, not an organisation that could be read as endorsing the work. Tooling names describe how the site is built and hosted |
| 2026-10-17 | Source titles in `data/real/` name a model vendor and an academic institution (S13) | Keep them unchanged in data files and in the generated payload; never repeat them in prose | Changing a quoted source title would falsify provenance. Data files are exempt from the prose rules |
| 2026-10-17 | Links contain organisation and vendor names | The voice test ignores URLs | A URL is an identifier, not prose |
| 2026-10-17 | `docs/LEADS.md` named public bodies | Moved its content into `docs/CONTEXT.md` and kept `docs/LEADS.md` as a pointer | Real names are allowed in one context document only |
| 2026-10-17 | The em dash in `pipeline/verify_live.py` is part of a character table that maps dashes on fetched pages to a hyphen | Written as a Unicode escape sequence | Behaviour is unchanged and the file contains no em dash |
| 2026-10-17 | `verify-live` after editing note titles | Run without `--write` | The notes changed only in their title line; the verifier checks figures on the live pages, which the edit does not touch. Writing would churn `verification.json` dates without new information |
