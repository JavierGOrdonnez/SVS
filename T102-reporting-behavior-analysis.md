# T102: Reporting Behavior Analysis — Table Formats & Extraction Plan

**Status:** Format inspection complete. Ready for extractor development.

**Locations identified:**
- 2019 Partner violence: Page 109 (Tabla: Motivos para no denunciar VFSEM de la pareja)
- 2019 Outside-partner sexual violence: Page 169 (Tabla: Motivos para no denunciar)
- 2024 Partner violence: Page 143 (Tabla 9.7: Motivos para no denunciar la VFSEM de la pareja)
- 2024 Outside-partner sexual violence: Page 276 (Tabla 16.30: Motivos para no denunciar)

---

## Table Formats & Structure

### 2019 Partner Violence (Page 109)

**Tabla: Motivos para no denunciar la VFSEM de la pareja**

**Shape:** Label-then-numbers, multiple choice question (not a Sí/IC block)

**Columns:**
- Row label (reason for not reporting)
- "Pareja actual" (current partner): N, %
- "Parejas pasadas" (past partners): N, %

**Data type:** N values are sample counts; % are percentages of victims in each category

**Items:** 21 reasons listed (including NC - no clear)

**Key characteristics:**
- Clean wrapped-label structure (most labels fit on one line)
- Two population subgroups (current vs. past partner) — **differs from outside-partner which is violence-type-based**
- No suppression markers (2019 predates this convention)
- Numbers clearly tokenizable by `_split_tokens_2024` rules would work (space-separated)

### 2019 Outside-Partner Sexual Violence (Page 169)

**Tabla: Motivos para no denunciar la violencia sexual fuera de la pareja a lo largo de la vida**

**Shape:** Label-then-numbers, multiple choice question

**Columns:**
- Row label (reason for not reporting)
- "Violencia sexual" (all sexual violence): N, %
- "Violación" (rape only): N, %

**Data type:** N = sample counts; % = percentages of victims of that violence type who didn't report

**Items:** 14 reasons listed

**Key characteristics:**
- Violence-type breakdown (all types vs. rape specifically)
- No suppression markers
- Similar label structure to 2024 but smaller set of items
- Notably includes "Era menor, era una niña" (was a minor) — critical for age context

### 2024 Partner Violence (Page 143 - Tabla 9.7)

**Tabla 9.7: Motivos para no denunciar la VFSEM de la pareja**

**Shape:** Label-then-numbers, multiple choice question

**Columns:**
- Row label (reason for not reporting)
- "Pareja actual": %, N (population estimate)
- "Parejas pasadas": %, N (population estimate)
- "Cualquier pareja": %, N (population estimate)

**Data type:** % = percentages (of non-reporting victims); N = population estimates (not sample counts like 2019)

**Items:** 21 reasons listed (including NC)

**Key characteristics:**
- **Three columns: current, past, and pooled** (differs from 2019's binary split)
- Uses suppression (`.`) and small-sample (`¨`) markers
- Population estimates instead of raw sample N
- "-" marker for items not applicable to current partner (e.g., "Se separó/terminó la relación")
- Row 9 "Se separó/terminó la relación" has "-" for pareja actual (naturally so — can't break up current if still current)

### 2024 Outside-Partner Sexual Violence (Page 276 - Tabla 16.30)

**Tabla 16.30: Motivos para no denunciar la violencia sexual fuera de la pareja**

**Shape:** Numbered list with label-then-numbers, multiple choice question

**Columns:**
- Row label with number (e.g., "1. Le dio muy poca importancia...")
- "Violaciones": %¹
- "Intentos de violación": %²
- "Otras formas de violencia sexual": %³

**Data type:** % only (no N column); footnotes explain each % is relative to the respective violence-type subgroup

**Items:** 13 reasons listed

**Key characteristics:**
- Violence-type breakdown (rape / attempted rape / other sexual violence) — **different from 2019's all/rape split**
- Population estimate narrative provided separately in prose (page 276 bullet points)
- Uses suppression (`.`) and small-sample (`¨`) markers
- No N column in the table itself; population context from prose above table
- Shorter item set than partner violence tables (13 vs. 21)

---

## Structural Differences Requiring Careful Parsing

### Partner vs. Outside-Partner Schemas Are Different

**Partner violence:** Splits on **partner status** (current/past/any), not violence type
- Same reasons listed for both current and past partners
- Different prevalence rates because different victim populations
- Certain items skipped for current partner (relationship status reason)

**Outside-partner violence:** Splits on **violence type** (rape/attempted/other), not victim group
- Same victim population (women who experienced outside-partner sexual violence)
- Different prevalence of each reason across severity tiers

### Suppression & Small-Sample Handling (2024 only)

- `.` = suppressed (sample < 6) → must stay `None` (do not coerce to 0)
- `¨` = flagged small sample (6-19) → keep the number, mark as potentially unreliable
- `-` = item not applicable to this category → treat as `None` (different from suppression)

### 2019 vs. 2024 Metric Types

| Year | Partner | Outside-Partner |
|------|---------|-----------------|
| 2019 | N, % (sample-based) | N, % (sample-based) |
| 2024 | %, N (population estimates) | % only (prose narration gives context) |

---

## Recommended Schema & Extractor

### New Output Type: ReportingStat

```python
class ReportingStat(BaseModel):
    """Reporting behavior: reasons for not reporting sexual/partner violence."""
    category: str                # 'reasons_for_not_reporting' | 'satisfaction' | ... (future)
    reason: str                  # specific reason text, e.g. "vergüenza"
    reason_key: str | None = None # normalized key for joining across waves, e.g. "shame" / "lack_importance"
    
    # Context: which population this applies to
    violence_type: str           # 'any' | 'rape' | 'attempted_rape' | 'other' (outside-partner)
                                 # vs. 'vfsem_pareja' (partner-violence-specific)
    partner_status: str | None = None  # 'current' | 'past' | 'any' (partner violence only)
    
    # Data
    pct: float | None = None     # percentage of non-reporting victims citing this reason
    population_estimate: int | None = None  # (2024 only) population count
    sample_n: int | None = None  # (2019 only) raw survey sample size
    
    # Data quality flags
    suppressed: bool = False     # (2024 only) '.' marker — sample too small
    small_sample: bool = False   # (2024 only) '¨' marker — 6-19 observations
```

### Extraction Strategy

**For both 2019 and 2024, both chapters:**

1. **Locate page** using `_locate_page` with keywords:
   - Partner: `["MOTIVOS", "DENUNCIAR", "PAREJA"]` (chapter 9)
   - Outside: `["MOTIVOS", "DENUNCIAR", "SEXUAL"]` (chapter 16)
   - Anchor past chapter start (V48) before searching

2. **Extract text window** with `_page_window_text(pdf, start_page, n_pages=2)` to handle table spans

3. **Split by violence type/partner status** using `_section` markers (row headers or subtable titles)

4. **Parse rows** using `_ordered_rows` or wrapped-label pattern:
   - Extract row labels (e.g., "Por vergüenza...")
   - Extract numeric tokens using `_split_tokens_2024` (already handles suppression/small-sample markers)
   - Join via position-based matching (labels vs. tokens)

5. **Build stat objects** with appropriate schema fields based on wave/chapter/violence-type combo

### Implementation Order

1. Write `parse_reporting_reasons_2019_partner()` — simplest structure
2. Write `parse_reporting_reasons_2019_outside_partner()` — adds violence-type split
3. Write `parse_reporting_reasons_2024_partner()` — adds population estimates + markers
4. Write `parse_reporting_reasons_2024_outside_partner()` — adds % only (prose extraction separate)

Add all four to both `Macroencuesta2019Parser.parse()` and `Macroencuesta2024Parser.parse()`, output via new `MacroencuestaReport.reporting` list field.

---

## Signal Detection Plan (Future — T102 Phase 2)

Once extracted, compare distributions across waves:

**Partner violence:** Look for shifts in reason *distributions* even where overall non-reporting rate is flat:
- More "se solucionó de otra manera" / "resolvió sola"? → behavior shift toward informal resolution
- More "miedo al agresor"? → different perpetrator/victim relationship characteristics
- Less "vergüenza" / "pensó era su culpa"? → cultural shift in victim perception

**Outside-partner:** Analogous distribution shifts, plus:
- Age effect in "era menor, era una niña" — if 2024 wave has older average victim age, % should drop
- Intergenerational knowledge ("eran otros tiempos") — expect drop if reporting culture shifted

---

## Format Verification Checklist

- [x] 2019 partner violence: page 109, label-then-numbers structure confirmed
- [x] 2019 outside-partner: page 169, violence-type columns confirmed
- [x] 2024 partner violence: page 143, three-column structure with population estimates confirmed
- [x] 2024 outside-partner: page 276, violence-type columns (% only) confirmed
- [x] Suppression/small-sample markers identified and rules understood
- [x] Partner-status vs. violence-type schema differences documented
- [x] Wrapped-label and multi-page boundary cases identified (none found this session)
