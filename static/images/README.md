# Images Directory

This directory contains all visual assets for the TasteLab Dashboard.

## Overview

Images are organized into subdirectories by type and purpose for easy management and optimized loading. All images should be optimized for web use before being added to the repository.

## File Structure

```
images/

```

## Image Guidelines

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

## Adding New Images

When adding new images:

1. **Optimize first** - Compress and resize
2. **Choose correct format** - JPEG/PNG/SVG
3. **Use descriptive name** - Follow naming conventions
4. **Place in correct subdirectory**
5. **Test responsiveness** - Check on multiple devices
6. **Verify accessibility** - Add alt text
7. **Update documentation** - Note in README if significant

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