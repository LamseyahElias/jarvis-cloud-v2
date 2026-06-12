# Peace Corps Training Materials — Public Domain Status

## Legal Basis
US Peace Corps training materials (including the Moroccan Arabic Textbook 2011) are **public domain** under 17 U.S.C. § 105 — works produced by US government officers/employees as part of official duties are not subject to copyright.

## Key Sources
- **Peace Corps official policy** (peacecorps.gov): "Unless otherwise indicated, information on the Peace Corps website is in the public domain and may be copied and distributed without permission."
- **Library of Congress** (Peace Corps web archive): "Documents in this collection that were prepared by officials of the United States as part of their official duties are in the public domain."
- **Internet Archive**: The Moroccan Arabic Textbook 2011 is hosted at archive.org/details/MoroccanArabicTextbook2011 under "Government Documents."
- **ERIC Database** (ED353812): Authoring institution listed as "Peace Corps, Rabat (Morocco)" — a US government entity.

## Commercial Use
- Public domain = no copyright restrictions, including commercial use
- No permission needed, no royalties owed
- Your modifications/additions ARE your own copyrightable work

## Restrictions (Trademark, NOT Copyright)
- Do NOT use Peace Corps name/logo suggesting official endorsement
- Remove "Peace Corps / Morocco" headers from pages
- Rewrite acknowledgements to remove direct Peace Corps attribution
- Remove or rewrite the "Describing the Peace Corps Mission" chapter (pages 120-123)

## Peace Corps References in the Moroccan Arabic Textbook 2011
- **Page headers:** "Peace Corps / Morocco" appears on ~90 even-numbered pages
- **Page 1 (Acknowledgements):** Credits Peace Corps language instructors
- **Page 4 (Introduction):** Multiple references to Peace Corps training
- **Pages 13, 63, 103:** Example sentences mentioning Peace Corps
- **Pages 120-123:** Entire chapter "Describing the Peace Corps Mission"
- **Page 197 (Index):** Peace Corps index entry
- **Arabic refs:** "hay'at s-salam" (هيئة السلام) on pages 13, 103, 120, 123

## Practical Approach (What We Did)
Since PDF text replacement is extremely complex (positioned glyphs, not editable text), we:
1. Created a new BeldiTalk branded cover page using ReportLab
2. Created a new attribution/about page
3. Skipped the original acknowledgements page (page 0)
4. Merged cover + attribution + remaining 196 pages using PyPDF2
5. Set PDF metadata to BeldiTalk Academy
6. Result: 198-page branded ebook at ~/belditalk-ebook/

## Risk Assessment
**Very low risk.** Clear-cut case of US government work in the public domain. The legal basis (17 USC 105) is well-established. Live Lingua's suggestion to "contact Peace Corps for commercial use permission" is a conservative recommendation, not a legal requirement.
