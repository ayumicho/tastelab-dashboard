# TasteLab Dashboard - CSS Documentation

This directory contains all stylesheets that power the tastelab dashboard application. The CSS is organized into a base stylesheet used across all pages and feature-specific stylesheets for individual components.

## Directory Structure

```
static/
├── css/
│   ├── base.css                      # Core styles used across all pages
│   ├── detection-tracking.css        # Participant tracking & heatmap features
│   ├── docs.css                      # privacy policy & terms of service
│   ├── experiments.css               # Experiment management & listings
│   ├── help.css                      # FAQ & support documentation
│   ├── home.css                      # Dashboard overview page
│   ├── manual-annotation.css         # Manual labeling interface
│   ├── profile.css                   # User profile settings
│   ├── signup.css                    # Authentication pages
│   ├── single-experiment.css         # Detailed experiment view
│   └── speech-to-text.css            # NLP transcription & analysis
└── images/                           # Icons, logos, visual assets
```

## Base CSS - Global Styles

**File:** `base.css`

The base stylesheet provides foundational styles used across all HTML pages and includes:

- **Typography** - Headings (h1-h3), text hierarchy, and font weights
- **Page Layout** - Container, grid system, sidebar, and main content areas
- **Sidebar Navigation** - Navigation links, active states, and hover effects
- **Header & Hero Sections** - Gradient headers with decorative backgrounds
- **Overview Cards** - Dashboard card components with borders and shadows
- **Search Bar** - Search input styling with icons and focus states
- **Navbar** - Custom navigation bar styling
- **Cards** - General card components with hover effects
- **Dropdown Menus** - Custom dropdown styling
- **Buttons** - Button variants (primary, secondary, etc.)
- **Icons & Images** - Icon containers and image styling
- **Loading & Overlay** - Loading spinners and overlay components
- **Utilities** - Highlight boxes and helper classes
- **Animations** - Spin and pulse keyframe animations
- **Responsive Design** - Media queries for mobile, tablet, and desktop

### Color Palette

The dashboard uses a warm orange/brown color scheme:

```css
Primary Orange:     #ed8936
Secondary Orange:   #dd6b20
Light Orange:       #F4A261
Lighter Orange:     #F9C5A0
Text Dark:          #2d3748
Text Medium:        #718096
Text Light:         #a0aec0
Background Light:   #f8f9fa
```

For charts we use:

```css
Coral Red:          #f56565
Vivid Orange:       #f97316
Pumpkin Orange:     #ed8936
Peach:              #f6ad55
Pale Goldenrod:     #fbd38d
Golden Yellow:      #ecc94b
Mint Green:         #68d391
Teal:               #38b2ac
Aquamarine:         #81e6d9
Sky Blue:           #63b3ed
Cerulean Blue:      #4299e1
Slate Purple:       #667eea
Light Gray:         #e5e7eb
Purple:             #9f7aea
Lilac:              #a78bfa
Magenta:            #c084fc
Medium Purple:      #b794f6
```


## Page-Specific CSS Files

### 1. **docs.css** (8 sections)
Styles for privacy policy, terms of service, and documentation pages.

**Includes:**
- Document layout and typography
- Section headers and subheaders
- Lists and bullet points
- Link styling

**Used by:** Privacy Policy, Terms of Service pages

### 2. **home.css** (15 sections)
Main dashboard overview page styling.

**Includes:**
- Dashboard cards and metrics display
- Quick action buttons
- Overview statistics
- Card layouts and grid systems

**Used by:** Dashboard homepage

---

### 3. **detection-tracking.css** (12 sections)
Participant tracking, heatmaps, and detection analysis.

**Includes:**
- Heatmap SVG styling
- Timeline playback controls
- Zone table formatting
- Participant tracking indicators
- Analysis status badges

**Used by:** Tracking & Detection analytics page

---
### 4. **experiments.css** (17 sections)
Experiment management and listing pages.

**Includes:**
- Experiment card layouts
- Tab navigation styling
- Search and filter controls
- Experiment status badges
- Archive/restore button states
- Form inputs for experiment creation
- Empty state messaging

**Used by:** Experiments, Create Experiment pages

---

### 5. **dashboard-detail.css** (13 sections)
Individual experiment metrics and analytics dashboard.

**Includes:**
- Quick action card styling
- Experiment overview cards
- Analysis metrics with color gradients
- Chart card wrappers
- Activity feeds and top experiments lists
- Status indicators
- Color-themed small cards

**Used by:** Dashboard detail/metrics view

---
### 6. **manual-annotation.css** (14 sections)
Manual data labeling and annotation interface.

**Includes:**
- Summary statistics boxes
- Job card layouts with progress bars
- Annotation modals
- Person selection grids
- Image grid for labeling
- Loading states and toasts
- Saving overlay animations

**Used by:** Manual annotation/labeling page

---

### 7. **help.css** (10 sections)
FAQ, help documentation, and support pages.

**Includes:**
- Topic card grid
- FAQ accordion styling
- Content boxes (note, alert, warning)
- Step-by-step lists
- Legal section cards
- Footer contact button

**Used by:** Help & Support documentation page

---

### 8. **profile.css** (10 sections)
User profile settings and preferences.

**Includes:**
- Profile header with avatar
- File upload section with drag-and-drop
- Form input styling
- Modal dialogs
- Security notice boxes
- Stats cards grid

**Used by:** User Profile page

---

### 9. **signup.css** (13 sections)
Authentication and registration pages.

**Includes:**
- Background patterns and gradients
- Signup/login card styling
- Form layout and inputs
- Password strength indicators
- Validation message styling
- Submit button with loading state
- Footer navigation links
- Success message animations

**Used by:** Login, Signup pages

---

### 10. **single-experiment.css** (15 sections)
Detailed experiment view with multi-modal analytics.

**Includes:**
- Back navigation button
- Header section styling
- Metric card displays
- Two-column comparison layout
- Panel card containers
- Heatmap wrapper
- Timeline control styling
- Zone table formatting
- Transcription display
- Emotion tags and sentiment indicators
- Action panel buttons

**Used by:** Single Experiment page

---

### 11. **speech-to-text.css** (10 sections)
Natural Language Processing analysis and transcription.

**Includes:**
- Content grid layout (sidebar + main)
- Card and column stack styling
- Color-themed icons
- Scrollable transcript areas
- Custom scrollbar styling
- Action item formatting
- Complex moment highlights
- Emotion tags and badges
- Question item styling
- Transcript row formatting

**Used by:** Speech-to-Text page

---

## CSS Organization System

All CSS files follow a consistent section-based organization system for easy navigation:

### Header Format
```css
/* ==================== Section Name ==================== */
```

### Section Examples
Each file is divided into logical sections such as:
- Layout & Grid
- Typography
- Cards
- Forms
- Buttons
- Colors/Themes
- Animations
- Responsive

This organization makes it easy to:
- Find specific styles quickly
- Understand the purpose of each section
- Maintain consistent structure across files
- Onboard new developers

## Design System Guidelines

### Spacing
- Use consistent `gap` values: `0.5rem`, `1rem`, `1.5rem`, `2rem`
- Padding follows the same scale: `0.75rem`, `1rem`, `1.5rem`, `2rem`

### Border Radius
- Small: `6px` - small components, tags
- Medium: `10px`, `12px` - form inputs, buttons
- Large: `16px`, `20px` - cards, main containers

### Box Shadows
- Light: `0 2px 8px rgba(0, 0, 0, 0.05)`
- Medium: `0 4px 12px rgba(0, 0, 0, 0.08)`
- Heavy: `0 10px 30px rgba(0, 0, 0, 0.12)`

### Transitions
- Standard: `all 0.3s ease`
- Quick: `all 0.2s ease`
- Smooth: `all 0.5s ease`

## Best Practices

### 1. **Use Base CSS for Shared Styles**
Always apply shared styles from `base.css` before adding page-specific overrides.

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
```

### 2. **Follow Section Organization**
When adding new styles, place them in the appropriate section or create a new one with the standard header format.

### 3. **Color Consistency**
Use the defined color palette for all colors to maintain visual consistency across the application.

### 4. **Responsive Design**
Always include mobile and tablet breakpoints:
- Mobile: `max-width: 768px`
- Tablet: `max-width: 992px`, `max-width: 1024px`
- Desktop: `min-width: 1200px`

### 5. **Avoid Redundant Comments**
Use semantic class names and section headers instead of inline comments. The file organization is self-documenting.

### 6. **Group Related Styles**
Keep related styles (like button variants) in the same section rather than scattered throughout the file.


## Getting Started

### For New Developers

1. **Start with `base.css`** to understand the foundational styling
2. **Review the page-specific CSS** for features you're working on
3. **Use the section headers** to navigate and find relevant styles
4. **Follow the existing patterns** for consistency

### Adding New Styles

1. Determine if the style is global (base.css) or page-specific
2. Find the appropriate section or create one
3. Follow the existing naming conventions and formatting
4. Update this README if adding new files or major sections

## HTML Integration

Include CSS files in your HTML templates in this order:

```html
<!-- Global Styles -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">

<!-- Page-Specific Styles -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
```

## Common Selectors

### Card Components
- `.card` - General card with shadow
- `.overview-card` - Dashboard overview card of all experiments
- `.experiment-card` - Experiment listing card

### Buttons
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.btn-action` - Action button variant
- `.btn-feature` - Feature call-to-action

### Layout
- `.container` - Main content wrapper
- `.header-section` - Top header area
- `.content-grid` - Grid layout container
- `.column-stack` - Vertical stack layout

### Status/Badge
- `.status-badge` - Status indicator
- `.card-badge` - Card badge
- `.emotion-tag` - Sentiment/emotion tag
- `.analysis-status-badge` - Analysis status badge

## Troubleshooting

### Styles Not Applying
1. Check CSS file is linked in HTML
2. Verify correct file name (case-sensitive on Linux/Mac)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Check browser DevTools for specificity conflicts

### Responsive Issues
1. Add appropriate media query breakpoints
2. Test on actual devices or use browser DevTools
3. Check for fixed widths vs flexible layouts

### Color Not Matching
1. Verify hex code from color palette
2. Check for opacity/transparency values
3. Ensure correct state (normal, hover, active)

## Resources

- **Color Palette:** See "Base CSS - Global Styles" section above
- **Spacing Scale:** Documented in "Design System Guidelines"
- **Icons:** FontAwesome (check `images/` folder)
- **Fonts:** System fonts (see Typography in base.css)
---

**Last Updated:** January 2026  
**Maintained by:** Ayumi Chotoe