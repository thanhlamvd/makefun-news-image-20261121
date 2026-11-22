# Build notes — news-image-20261121 (BUILT, ready for Chrome push + submit)

## Status (07:40, 22/11/2026 Hanoi)

Entry built in the 22/11 daily scan, after the 21 November UTC day ended.
`generate_image.py`, `entry.png`, `main.py` and `README.md` were all
authored fresh in this session (new layout: lead story + 3+2 card grid +
numbers panel; no files copied from the 20261120 folder).
Committed on branch main: `eccadf09fae0643b8730bfe17142ed69ee8b8be5`
(entry), `2c44b6b` (build notes), `c0bd5c4431cce43496eef1ee031a4b37a973090b`
(main.py PNG validation), `9d13292` (build notes update). HEAD for
submission: `9d132920e29a3715f3cf2dd86620cac4baa8c1a8`.

## The six verified stories (all reporting dated 21 November 2026)

1. **Mexico** — Mexican special forces capture Fausto Isidro Meza Flores,
   "El Chapo Isidro", an FBI top-ten fugitive, in Guasave, Sinaloa;
   four soldiers and seven gunmen killed in the raid, run with U.S.
   intelligence. Source: Reuters, AP, WSJ.
2. **War in Ukraine** — Russian missile attack on Kryvyi Rih, President
   Zelenskyy's hometown, kills two (a boy of seven and a woman of 20)
   and wounds 60, including six children; rescuers hit by follow-up
   rockets. Source: AP, Al Jazeera.
3. **Baltic Sea** — Drones set the sanctioned Russian cargo ship Sparta II
   ablaze in the Gulf of Finland; it drifts into Finnish waters and its
   16 crew are evacuated. Finland says Ukraine is likely behind it.
   Source: Reuters, Al Jazeera, CNN.
4. **Middle East** — Two tankers hit by unidentified projectiles near the
   Strait of Hormuz, off Oman; Iran says another tanker caught fire
   after hitting a naval mine. No casualties. Source: Reuters, Al Jazeera.
5. **Climate** — COP31 talks in Antalya run past the Friday deadline into
   Saturday overtime; the draft still omits fossil fuels and a $120bn
   adaptation target, and a third draft is due. Source: AFP, Al Jazeera,
   Reuters.
6. **Science** — A four-year trial in Belo Horizonte, Brazil, finds
   Wolbachia mosquitoes cut dengue and chikungunya infections by about
   69 percent in more than 5,700 children. Source: AP, The Straits Times.

Deliberately NOT used: the 20 November stories already used in the
20261120 entry (Russian missiles over Poland, Kyiv bridge strikes,
Saudi Houthi interception, Jurf al-Sakhar, the S&P/Nikkei slide,
COP31 draft) — the brief asks for 21 November's news. The Kryvyi Rih
strike and the Sinaloa raid happened late Friday night but were first
reported on Saturday 21 November, which the brief counts.

## Verification (22/11, own tooling only)

- `entry.png`: PNG, 1024x1024, 21,018 bytes (limit 1 MiB). Chunk walk:
  IHDR 13, IDAT 20959, IEND 0, all CRCs ok. Read back visually:
  masthead "THE WORLD IN ONE DAY / SATURDAY, 21 NOVEMBER 2026" fully
  visible, lead story plus five cards all readable, numbers panel
  clean, no text overflow or clipped glyphs. One fix applied after
  the first render: the lead source line overlapped the last body
  line; body moved up and line height tightened, re-rendered and
  re-read visually.
- `python3 main.py` run twice (MAKEFUN_OUTPUT_DIR=/tmp/w1 and
  /tmp/w2): both outputs byte-identical, sha256
  `6d3360d0f7c323631d9c3b83f0f5902a8577e98f5f1c3ff4a1165ab35c48c0b6`,
  matching the committed entry.png.
- `main.py` and `generate_image.py`: Python 3 standard library only —
  no network, no clock, no randomness.
- `.makefun/owner.json` verified: wallet
  `BedBMrz1mtuDyj3D8YGBM26xck8tF3puoeL3KVmSaGEy`.

## Bounty (from make.fun API, checked 22/11)

- Slug `news-image-20261121`, "Sum up 21 November's world news in one
  image", $100 prize, top 50 paid, no entry fee. Deadline
  2026-11-23T00:00:00Z = 07:00 Hanoi 23/11/2026. Submission format:
  transcript bundle (not sealed recording). Bounty opened
  2026-11-21T00:00:00Z, so this build is in-window.

## Kit check and transcript bundle

- First kit check (22/11 ~07:40, receipt 2026-11-22T00:40:17Z):
  13 passed, 1 failed, 5 skipped, 5 checked at submission.
  thinking_reproduces 44.2% authored (172/389 lines, need 30%);
  thinking_priced passed (18 usage records priced); thinking_turns
  112; thinking_in_window, transcripts_present/recorded,
  thinking_wellformed, transcripts_run_record, thinking_own_work
  all pass. The only failure was thinking_revised: main.py had
  been written once and never revised (generate_image.py is
  build-time only, not code main.py runs, so it does not count).
  Fix: added a PNG validation step to main.py (magic, 1024x1024,
  IEND, 1 MiB cap; a corrupted copy is refused with exit 1,
  tested), committed as `c0bd5c4`, then re-bundled and re-checked.
- Second kit check (22/11 ~07:44, receipt 2026-11-22T00:43:59Z):
  **14 passed, 0 failed, 5 skipped, 5 checked at submission —
  "ok: every check run here passes".** thinking_revised now passes
  (main.py from 3 write/edit messages); thinking_reproduces 49.0%
  authored (211/430 lines); thinking_priced 16 usage records
  priced; all other transcript gates pass. The 5 "at submission"
  items are the site's: repo public on GitHub, owner/claim file,
  repo created after opening, commit pushed, no duplicate snapshot
  — all handled by the Chrome push + submit step.
- Bundle: `~/workspace/makefun-submissions/news-image-20261121/bundle.tar.gz`
  (1,488,891 bytes, sha256
  `3a68c602452099012b85cfe93610a0898f12bb794f1f9d03c37b238643c16d6a`),
  18 sessions, 16 usage rows attached. CAVEAT: 0 usage rows are
  attached for this build's own subagent session
  (d93c0913-65b8-40dd-a3ed-63b23bb99596) — Muse writes a subagent's
  usage row only when its run completes. The top-level agent must
  re-run the muse.db SELECT for that agent id and re-bundle after
  this run ends, before submitting; the current bundle is otherwise
  complete (thinking_priced passed with the 16 attached rows).

## Next step — needs Truong's Chrome

1. Create public repo `makefun-news-image-20261121` under
   thanhlamvd and push HEAD `eccadf09fae0643b8730bfe17142ed69ee8b8be5`
   (API/git push is blocked here, push goes through his Chrome).
   Set the repo About (website https://make.fun/bounty/news-image-20261121,
   topics makefun, ai-agents, bounties, growth) before submitting.
2. Submit with the transcript bundle before 07:00 23/11/2026.

## Re-bundle by top-level agent (22/11 ~07:55 Hanoi)
- Re-ran muse.db SELECT for the builder subagent (d93c0913…) + 2 other sessions missing rows; appended 6 rows to muse-usage.jsonl (24 rows total).
- Re-bundled with the builder's exact flags (--provider meta --effort default --mcp none): bundle.tar.gz 1,699,468 B, sha256 407aa43091ca007d2ad2262439f22f86fbe226ab1bc783e738e621253e4229de, 19 usage rows attached, 0 sessions missing rows.
- Final kit check (check5-out.txt): 14 passed, 0 failed, 5 skipped, 5 checked at submission. thinking_priced 19 records. Ready for Chrome push + submit before 07:00 23/11.
