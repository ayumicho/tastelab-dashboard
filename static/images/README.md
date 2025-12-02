# Images Directory

This directory contains all visual assets for the TasteLab Dashboard.

## Overview

Images are organized into subdirectories by type and purpose for easy management and optimized loading. All images should be optimized for web use before being added to the repository.

## File Structure

```
images/
├── logos/                     # Brand logos and variations
│   ├── logo.png               # Primary logo
│   ├── logo-white.png         # White version for dark backgrounds
│   ├── logo-icon.png          # Icon-only version
│   └── favicon.ico            # Browser favicon
├── icons/                     # UI icons and symbols
│   ├── experiment.svg         # Experiment icon
│   ├── user.svg               # User profile icon
│   ├── chart.svg              # Chart/analytics icon
│   ├── upload.svg             # Upload icon
│   └── settings.svg           # Settings icon
├── backgrounds/               # Background images
│   ├── hero-bg.jpg            # Homepage hero background
│   ├── pattern.png            # Pattern overlay
│   └── gradient.svg           # Gradient backgrounds
├── illustrations/             # Illustrations and graphics
│   ├── empty-state.svg        # Empty state illustration
│   ├── error-404.svg          # 404 error illustration
│   └── success.svg            # Success state illustration
├── ui/                        # UI elements and components
│   ├── avatar-placeholder.png # Default user avatar
│   ├── card-placeholder.jpg   # Card image placeholder
│   └── loader.gif             # Loading spinner
├── uploads/                   # User-uploaded images
│   ├── experiments/           # Experiment-related uploads
│   └── profiles/              # Profile pictures
└── screenshots/               # Application screenshots
    ├── dashboard.png          # Dashboard preview
    └── features.png           # Features showcase
```

## Image Guidelines

### Logos

**Primary Logo (`logo.png`)**
- Format: PNG with transparency
- Dimensions: 200x60px (or proportional)
- Usage: Main navigation, headers, emails
- Background: Transparent

**Logo Variations**
- `logo-white.png` - For dark backgrounds
- `logo-icon.png` - Icon-only (square format)
- `favicon.ico` - Browser favicon (16x16, 32x32, 48x48)

**Usage in templates:**
```html
<img src="{{ url_for('static', filename='images/logos/logo.png') }}" 
     alt="TasteLab Dashboard" 
     class="logo">
```

### Icons

**Format Requirements**
- Preferred: SVG (scalable, small file size)
- Alternative: PNG with transparency
- Color: Match brand colors or neutral gray
- Size: Typically 24x24px or 48x48px

**Icon Categories**
- Navigation icons
- Action icons (edit, delete, save)
- Status indicators
- Feature icons

**Usage in templates:**
```html
<img src="{{ url_for('static', filename='images/icons/experiment.svg') }}" 
     alt="Experiment" 
     class="icon">
```

**Usage in CSS:**
```css
.icon-experiment {
    background-image: url('../images/icons/experiment.svg');
    width: 24px;
    height: 24px;
}
```

### Backgrounds

**Hero Backgrounds**
- Format: JPEG (photographs) or SVG (gradients/patterns)
- Dimensions: At least 1920x1080px
- File size: < 500KB (optimize before upload)
- Quality: 85% compression for photos

**Patterns and Textures**
- Format: PNG (repeating patterns) or SVG
- Dimensions: Small tileable sections
- Transparency: Use when overlaying content

**Usage in CSS:**
```css
.hero-section {
    background-image: url('../images/backgrounds/hero-bg.jpg');
    background-size: cover;
    background-position: center;
}

.pattern-overlay {
    background-image: url('../images/backgrounds/pattern.png');
    background-repeat: repeat;
}
```

### Illustrations

**Empty States**
- Show when no data is available
- Friendly, non-technical appearance
- Include helpful messaging
- Format: SVG preferred

**Error Pages**
- 404 Not Found illustration
- 500 Server Error illustration
- Connection error illustration
- Format: SVG for scalability

**Success States**
- Confirmation illustrations
- Completion graphics
- Achievement badges

### UI Elements

**Avatar Placeholder**
- Default user profile image
- Format: PNG or SVG
- Dimensions: 200x200px
- Neutral, professional design

**Card Placeholders**
- Used while images load
- Match card dimensions
- Low file size
- Subtle design

**Loaders/Spinners**
- Animated loading indicators
- Format: GIF, SVG, or CSS animation
- Match brand colors
- Small file size (< 50KB)

### User Uploads

**Experiment Images**
- Participant photos
- Product images
- Reference materials
- Stored in: `uploads/experiments/`

**Profile Pictures**
- User avatars
- Stored in: `uploads/profiles/`
- Processed to standard size (200x200px)

**Upload Handling:**
```python
# Example in Flask route
UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

## File Formats

### When to Use Each Format

**JPEG (.jpg, .jpeg)**
- Use for: Photographs, complex images
- Pros: Small file size, good compression
- Cons: No transparency, lossy compression
- Best for: Backgrounds, photos, large images

**PNG (.png)**
- Use for: Graphics with transparency, screenshots
- Pros: Lossless, supports transparency
- Cons: Larger file size than JPEG
- Best for: Logos, icons, UI elements

**SVG (.svg)**
- Use for: Vectors, icons, simple graphics
- Pros: Infinitely scalable, small size, editable
- Cons: Not suitable for photographs
- Best for: Icons, logos, illustrations

**GIF (.gif)**
- Use for: Simple animations
- Pros: Animated, wide support
- Cons: Limited colors (256), larger than video
- Best for: Loading spinners, small animations

**WebP (.webp)**
- Use for: Modern browsers
- Pros: Better compression than JPEG/PNG
- Cons: Limited browser support
- Best for: Optimized web images

## Image Optimization

### Before Adding Images

1. **Resize to appropriate dimensions**
   - Don't upload larger images than needed
   - Use 2x size for retina displays

2. **Compress images**
   - Use tools like TinyPNG, ImageOptim
   - Target: < 200KB for most images
   - Maintain visual quality

3. **Use correct format**
   - Photos → JPEG
   - Transparent graphics → PNG
   - Icons/vectors → SVG

4. **Optimize SVGs**
   - Remove unnecessary metadata
   - Minify SVG code
   - Use SVGO or similar tools

### Responsive Images

Serve different sizes for different devices:

```html
<img 
    src="{{ url_for('static', filename='images/hero-mobile.jpg') }}"
    srcset="{{ url_for('static', filename='images/hero-mobile.jpg') }} 480w,
            {{ url_for('static', filename='images/hero-tablet.jpg') }} 768w,
            {{ url_for('static', filename='images/hero-desktop.jpg') }} 1200w"
    sizes="(max-width: 480px) 480px,
           (max-width: 768px) 768px,
           1200px"
    alt="Dashboard Hero">
```

### Lazy Loading

Load images only when visible:

```html
<img 
    src="{{ url_for('static', filename='images/placeholder.jpg') }}"
    data-src="{{ url_for('static', filename='images/actual-image.jpg') }}"
    alt="Experiment Result"
    loading="lazy">
```

## Naming Conventions

### File Naming Rules

1. **Use lowercase** - `user-avatar.png` not `User-Avatar.png`
2. **Use hyphens** - `hero-background.jpg` not `hero_background.jpg`
3. **Be descriptive** - `experiment-chart-icon.svg` not `icon1.svg`
4. **Include size if multiple** - `logo-small.png`, `logo-large.png`
5. **Avoid spaces** - Use hyphens instead

### Examples

✅ **Good Names:**
- `dashboard-hero-background.jpg`
- `user-profile-placeholder.png`
- `experiment-icon-24px.svg`
- `success-illustration.svg`

❌ **Bad Names:**
- `IMG_1234.jpg`
- `icon1.svg`
- `background image.png`
- `Screenshot 2025-09-15.png`

## Accessibility

### Alt Text

Always provide descriptive alt text:

```html
<!-- Decorative images -->
<img src="..." alt="">

<!-- Functional images -->
<img src="..." alt="Delete experiment">

<!-- Informative images -->
<img src="..." alt="Bar chart showing emotion analysis results">
```

### Color Contrast

Ensure sufficient contrast for:
- Text overlaid on images
- Icons against backgrounds
- Important UI elements

Use tools like WebAIM Contrast Checker.

## Performance Optimization

### Image Loading Strategies

**Critical Images** (above the fold)
- Load immediately
- Preload if necessary
- Optimize for fast delivery

**Non-Critical Images** (below the fold)
- Use lazy loading
- Load on scroll
- Progressive JPEG for photos

**Background Images**
```css
/* Optimize background loading */
.hero {
    background-image: url('../images/placeholder.jpg');
}

.hero.loaded {
    background-image: url('../images/hero-background.jpg');
}
```

### CDN Usage

For production, consider using a CDN:
- Faster delivery
- Better caching
- Geographic distribution
- Reduced server load

## Best Practices

### Image Management

1. **Keep images organized** - Use subdirectories
2. **Remove unused images** - Regular cleanup
3. **Document special images** - Note in README
4. **Version control** - Track image changes
5. **Backup originals** - Keep high-res versions

### File Size Targets

- **Icons:** < 10KB each
- **Logos:** < 50KB
- **UI elements:** < 100KB
- **Backgrounds:** < 500KB
- **Photos:** < 200KB (compressed)
- **Illustrations:** < 100KB

### Security

1. **Validate uploads** - Check file types
2. **Scan for malware** - Especially user uploads
3. **Limit file sizes** - Prevent abuse
4. **Use secure storage** - For sensitive images
5. **Control access** - Proper permissions

## Adding New Images

When adding new images:

1. **Optimize first** - Compress and resize
2. **Choose correct format** - JPEG/PNG/SVG
3. **Use descriptive name** - Follow naming conventions
4. **Place in correct subdirectory**
5. **Test responsiveness** - Check on multiple devices
6. **Verify accessibility** - Add alt text
7. **Update documentation** - Note in README if significant

## Common Image Sizes

### Standard Dimensions

```
Logos:
- Full logo: 200x60px
- Icon: 64x64px
- Favicon: 16x16, 32x32, 48x48

Avatars:
- Profile: 200x200px
- Thumbnail: 48x48px
- Icon: 32x32px

Cards:
- Card image: 400x300px
- Thumbnail: 200x150px

Backgrounds:
- Desktop: 1920x1080px
- Tablet: 1024x768px
- Mobile: 480x800px

Icons:
- Small: 16x16px
- Medium: 24x24px
- Large: 48x48px
```

## Troubleshooting

### Image not displaying
- Check file path is correct
- Verify file exists in directory
- Check file permissions
- Clear browser cache
- Inspect console for 404 errors

### Image too large/slow
- Compress image file
- Reduce dimensions
- Use appropriate format
- Implement lazy loading
- Consider using WebP

### Blurry images
- Use correct dimensions (not upscaled)
- Provide 2x size for retina
- Check compression quality
- Verify image source quality

---

**Last Updated:** December 2025