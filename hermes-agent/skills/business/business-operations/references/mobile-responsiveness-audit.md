# Mobile Responsiveness Audit — Next.js Sites

A repeatable drill for auditing and fixing horizontal overflow / mobile layout bugs on Next.js (or any React) websites.

## Quick Detection

Open the site on a phone or resize your browser to 375px wide. Look for:
- Horizontal scrollbar at the bottom
- Content cut off / pushed off-screen
- Text overflowing its container
- White/black strip on the right side

## Systematic Fix Pipeline

### 1. Foundation: html/body reset (globals.css)

The most common cause of side-scrolling: no `overflow-x: hidden` on the root elements.

```css
html {
  overflow-x: hidden;
  width: 100%;
}
body {
  overflow-x: hidden;
  width: 100%;
  position: relative;
}
```

Without `position: relative`, positioned children can still cause overflow on some browsers.

### 2. Find all `text-[Npx]` decorative elements

These large Arabic/script decorative texts (`text-[300px]`, `text-[250px]`, etc.) extend far beyond the viewport on mobile. Each one is inside a `<section>` that needs `overflow-hidden`:

```bash
grep -rn 'text-\[2-9][0-9]\{2\}px' src/app/ --include='*.tsx' | grep -v node_modules
```

Check EVERY section containing these:
- If the section does NOT have `overflow-hidden` in its className, add it
- Example: `<section className="relative py-24 sm:py-32 overflow-hidden">`

### 3. Find all blur circle decorative elements

```bash
grep -rn 'w-\[' src/app/ --include='*.tsx' | grep -v node_modules
```

Any section with a `w-[800px]` or larger absolutely-positioned circle/halo element MUST have `overflow-hidden`. Without it, the circle extends past the viewport creating a scrollable area.

### 4. Check all section tags systematically

```bash
grep -rn '<section' src/app/ --include='*.tsx' | grep -v node_modules | grep -v 'overflow'
```

Every line returned needs `overflow-hidden` added (unless the section truly has no decorative absolute elements — which is rare).

### 5. Grid fixes for mobile

**Two-column tables/grids that don't stack on mobile:**
```jsx
// BAD — forces two columns even on 320px screens
className="grid grid-cols-2 gap-4"

// GOOD — stacks on mobile, two columns on sm+
className="grid grid-cols-1 sm:grid-cols-2 gap-4"
```

**Comparison tables:**
```jsx
// Wrapping in scrollable container
<div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
  <div className="min-w-[480px]">
    {/* table content */}
  </div>
</div>
```

The `-mx-4 px-4` trick allows the scrollable area to extend past the parent padding on mobile but snap back on desktop (sm:mx-0 sm:px-0).

### 6. Arabic / large text sizing

Text that works on desktop can overflow on mobile:
```jsx
// BAD
className="text-2xl"

// GOOD
className="text-xl sm:text-2xl break-words"
```

The `break-words` class handles edge cases where even the smaller size overflows.

### 7. Deploy and verify

```bash
cd /path/to/project
git add -A && git commit -m "fix: mobile responsiveness"
npx vercel --token "$VERCEL_TOKEN" --prod
```

Then verify:
- Open on actual phone (or Chrome DevTools responsive mode at 320px, 375px, 414px)
- Scroll every page top-to-bottom
- Check each CTA/footer section
- Ensure no horizontal scrollbar

## Common Culprits Checklist

- [ ] html/body missing `overflow-x: hidden`
- [ ] Sections with `w-[800px]`+ circles missing `overflow-hidden`
- [ ] Sections with `text-[200px]`+ decorative text missing `overflow-hidden`
- [ ] Two-column grids not stacking (`grid-cols-2` without `grid-cols-1 sm:`)
- [ ] Comparison tables without scrollable wrapper
- [ ] Arabic/prose text without responsive sizing
- [ ] Absolutely positioned elements (`-top-40`, `-left-40`, etc.) outside viewport
- [ ] Fixed-width elements (`w-[400px]`, `min-w-[480px]`) on mobile
