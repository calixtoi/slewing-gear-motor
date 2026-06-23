# Formula Visualization Enhancement

## 🎯 Problem Solved

**Before:** Dense LaTeX notation was difficult to read on web
```latex
$$i_{\text{tot}} = i_{\text{gb}} \times i_{\text{slew}} = 38 \times 121 = 4598$$
```
Hard to parse, no clear distinction between formula and values.

---

## ✨ Solution: Jupyter Notebook-Style Display

### Visual Layout

Each calculation step now displays in a professional multi-layer format:

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Total Reduction Ratio                      │
│ Combine gearbox and slewing ring ratios             │
├─────────────────────────────────────────────────────┤
│ 📌 Input Values                                     │
│ ┌──────────┐ ┌──────────┐                          │
│ │ i_gb     │ │ i_slew   │                          │
│ │ 38 :1    │ │ 121 :1   │                          │
│ │ datasheet│ │ constant │                          │
│ └──────────┘ └──────────┘                          │
├─────────────────────────────────────────────────────┤
│ 📐 Formula Definition  (Blue background)           │
│                                                     │
│        i_tot = i_gb × i_slew                       │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ➜ Substitution & Calculation  (Orange background)  │
│                                                     │
│        i_tot = 38 × 121 = 4598.00                  │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ✓ Result  (Green background)                       │
│                                                     │
│        i_tot = 4598.00  :1                         │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ✔ Validation Constraints                           │
│ ✔ Used to calculate final crane slewing speed      │
└─────────────────────────────────────────────────────┘
```

### Key Visual Features

#### 1. **Color-Coded Sections**
- 🔵 **Blue**: Formula definition (generic, no numbers)
- 🟠 **Orange**: Substitution with actual values plugged in
- 🟢 **Green**: Final result highlighted
- 🟡 **Yellow**: Constraints and validation

#### 2. **Input Values Grid**
Each input displays in a clean card:
```
┌─────────────────────┐
│ n_mot               │
│ 1500  rpm           │
│ Motor datasheet     │
└─────────────────────┘
```
- **Label**: Mathematical symbol
- **Value**: Large, bold number
- **Unit**: Clearly marked
- **Source**: Where it comes from

#### 3. **Formula Display**
Formulas render with:
- **Large font size** (1.3-1.8rem for better readability)
- **Professional spacing** between symbols
- **Proper mathematical notation** with fractions, subscripts, etc.
- **Display mode** (not cramped inline)
- **Generous padding** for breathing room

#### 4. **Step-by-Step Flow**
```
Input Values  →  Formula Definition  →  Substitution  →  Result
                                           ↓
                                       Validation
```

---

## 📊 Example: Complete Calculation Flow

### **Step 2: GM Output Speed**

**Inputs:**
- n_mot = 1500 rpm (Motor datasheet)
- i_gb = 38 :1 (Motor datasheet)

**Generic Formula (Blue card with padding):**
```
n_gm = n_mot / i_gb
```

**With Values Substituted (Orange card with calculation):**
```
n_gm = 1500 / 38 = 39.47 rpm
```

**Result (Green card with large output):**
```
n_gm = 39.47 rpm
```

**Validation:**
- ✔ Acceptable window: 30–60 rpm
- ✔ Check: 30 ≤ 39.47 ≤ 60 → ✓ PASS

---

## 🎨 CSS Styling Details

### `.jupyter-formula` Classes
- **Base**: Light gray background with subtle border
- **definition**: Blue gradient (0056b3 theme)
- **substitution**: Orange gradient (ffa500 theme)
- **result**: Green gradient (28a745 theme)

### Typography
- **Formula text**: 1.3–1.8rem font
- **Input labels**: 0.85rem, muted
- **Input values**: 1.4rem, bold, monospace
- **Section headers**: 0.85rem, uppercase, small-caps style

### Spacing
- **Padding in formula cards**: 1.5rem × 2rem (spacious)
- **Minimum formula height**: 80px (no cramping)
- **Gap between sections**: 1.5rem (clear visual separation)

---

## 🔧 Technical Implementation

### KaTeX Integration
```javascript
// Auto-render all .jupyter-formula divs with proper display mode
document.querySelectorAll('.jupyter-formula').forEach(function (el) {
  katex.render(mathContent, el, {
    displayMode: true,  // Large, centered display
    throwOnError: false,
    macros: { "\\text": "\\mathrm{#1}" }
  });
});
```

### Template Structure
```html
<!-- Step wrapper with numbered badge -->
<div class="formula-step-card">
  <div class="formula-step-header">
    <div class="step-number">1</div>  <!-- Blue circle -->
    <h5>Formula Title</h5>
  </div>

  <!-- Input values in responsive grid -->
  <div class="input-values-grid">
    <div class="input-value-card">...
  </div>

  <!-- Formula display with jupyter styling -->
  <div class="jupyter-formula definition">$$...$$</div>
  <div class="jupyter-formula substitution">$$...$$</div>
  <div class="jupyter-formula result">$$...$$</div>

  <!-- Validation with check icons -->
  <ul>
    <li><i class="bi bi-check-lg"></i> Constraint...</li>
  </ul>
</div>
```

---

## 📈 Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Formula visibility** | Cramped, hard to scan | Large, spacious, easy to read |
| **Input clarity** | Mixed with text | Card-based, clearly labeled |
| **Color coding** | None | Blue (def), Orange (subst), Green (result) |
| **Steps separation** | Card boundaries only | Numbered badges + color + spacing |
| **Constraints display** | Plain text list | Check icons + visual grouping |
| **Mobile friendly** | Cramped | Responsive grid layout |
| **Jupyter style** | ❌ Dense | ✅ Spacious and readable |

---

## 🎯 Usage Examples

### Formula Verifier Page (`/formulas/verify/`)
Submit any motor parameters and see:
- All 6+ calculation steps with this visualization
- Sub-calculations for torque transformations
- Validation results with clear visual feedback

### Formula Reference Page (`/formulas/reference/`)
Browse all formulas with:
- Large display of each formula
- Variable definitions in professional tables
- Constraints highlighted in color-coded boxes
- Examples with actual system values

---

## 🚀 Future Enhancements

Possible improvements:
- **Dark mode**: For nighttime viewing
- **Formula comparison**: Side-by-side view of multiple calculations
- **Annotation tooltips**: Hover to explain notation
- **Export to PDF**: Preserve formatting for reports
- **Step animation**: Show calculation flow with transitions

---

## ✅ Quality Assurance

All 9 routes verified with new visualization:
- ✓ Home (/)
- ✓ Motors - PF Standard
- ✓ Motors - PF-XXL
- ✓ Formulas Overview
- ✓ Formula Reference
- ✓ Formula Verifier (**NEW VISUALIZATION**)
- ✓ Acceptance Ranges
- ✓ Motor Comparison
- ✓ System Requirements

---

## 📝 Design Principles

1. **Clarity**: Each element has one clear purpose
2. **Hierarchy**: Step numbers, section labels, values have visual precedence
3. **Spacing**: Generous padding prevents visual overcrowding
4. **Color**: Strategic use guides the eye through the calculation
5. **Consistency**: Same style across all formula displays
6. **Jupyter style**: Inspired by scientific notebook readability

This visualization makes complex motor validation calculations accessible and engaging!
