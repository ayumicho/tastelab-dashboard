# Static Directory

This directory contains all static assets for the TasteLab Dashboard, including stylesheets, JavaScript files, and images. Static files are served directly by Flask and cached by the browser for optimal performance.

## Overview

The static directory is organized into three main subdirectories, each serving specific asset types:

```
static/
├── css/          # Stylesheets and CSS files
├── js/           # JavaScript files and modules
└── images/       # Images, icons, and visual assets
```

## Directory Structure

### `css/`
Contains all stylesheet files for the application:
- Custom CSS for dashboard components
- Theme configurations
- Responsive design rules
- Component-specific styles

**See:** [`css/README.md`](css/README.md) for detailed documentation

### `js/`
Houses all JavaScript files including:
- Client-side functionality
- Interactive components
- Chart libraries
- Form validation
- AJAX requests

**See:** [`js/README.md`](js/README.md) for detailed documentation

### `images/`
Stores all visual assets:
- Logos and branding
- Icons and graphics
- UI elements
- Placeholder images
- Background images

**See:** [`images/README.md`](images/README.md) for detailed documentation

## Accessing Static Files

### In Templates (Jinja2)

Use Flask's `url_for()` function to generate URLs:

```jinja
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/main.js') }}"></script>

<!-- Images -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

### In CSS Files

Reference other static files using relative paths:

```css
/* Background image */
.hero {
    background-image: url('../images/background.jpg');
}

/* Icon */
.icon {
    background: url('../images/icons/star.svg') no-repeat;
}
```

### In JavaScript Files

Access static files dynamically:

```javascript
// Construct image path
const logoPath = '/static/images/logo.png';

// Fetch data
fetch('/static/data/config.json')
    .then(response => response.json())
    .then(data => console.log(data));
```

## File Organization Best Practices

### Naming Conventions

- **CSS files:** Use kebab-case (e.g., `single-experiment.css`)
- **JS files:** Use kebab-case (e.g., `chart-handler.js`, `form-validation.js`)
- **Images:** Use descriptive, lowercase names (e.g., `user-avatar.png`, `experiment-icon.svg`)

## Asset Optimization

### Images
- Compress images before adding to repository
- Use appropriate formats:
  - **JPEG** for photographs
  - **PNG** for images with transparency
  - **SVG** for logos and icons
  - **WebP** for modern browsers
- Provide multiple resolutions for responsive images

### CSS
- Minify CSS files for production
- Combine related stylesheets when possible
- Use CSS preprocessing (Sass/SCSS) if needed
- Remove unused styles

### JavaScript
- Minify JavaScript for production
- Bundle related scripts
- Use async/defer attributes for non-critical scripts
- Remove console logs in production

## Caching Strategy

Flask serves static files with appropriate cache headers. For cache-busting during updates:

```python
# In config.py or main.py
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
```

To force reload after updates, append version query string:

```jinja
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}?v=1.0.1">
```

## External Libraries

External CSS and JavaScript libraries can be included via CDN or locally:

### CDN (Recommended for common libraries)
```html
<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Local (For custom or modified libraries)
Place in `static/js/vendor/` or `static/css/vendor/`

## Security Considerations

- **Never store sensitive data** in static files (credentials, API keys, tokens)
- **Validate file uploads** before saving to `static/images/uploads/`
- **Set appropriate permissions** on static directories
- **Sanitize filenames** to prevent path traversal attacks
- **Use HTTPS** to serve static content in production

## Performance Tips

1. **Minimize HTTP requests** - Combine CSS/JS files when possible
2. **Enable compression** - Use gzip compression for text files
3. **Leverage browser caching** - Set appropriate cache headers
4. **Optimize images** - Compress and resize before uploading
5. **Use lazy loading** - Load images as needed
6. **Defer non-critical scripts** - Load JavaScript asynchronously

## Adding New Assets

When adding new static files:

1. **Place in appropriate subdirectory**
   ```
   static/css/    → Stylesheets
   static/js/     → JavaScript
   static/images/ → Images
   ```

2. **Follow naming conventions**
   - Use descriptive, lowercase names
   - Use hyphens for word separation
   - Include file version if necessary

3. **Optimize before adding**
   - Compress images
   - Minify CSS/JS for production
   - Remove unnecessary code

4. **Update documentation**
   - Add entry to relevant README
   - Document dependencies
   - Note browser compatibility

5. **Test across browsers**
   - Verify functionality
   - Check responsive behavior
   - Test loading performance

## Development vs Production

### Development
- Use unminified files for easier debugging
- Include source maps
- Enable verbose error messages
- Hot reload for rapid development

### Production
- Use minified and compressed files
- Remove source maps
- Disable debug output
- Enable caching
- Optimize asset delivery

## Troubleshooting

### Static files not loading
- Check file path is correct
- Verify file exists in static directory
- Clear browser cache
- Check Flask static folder configuration
- Inspect browser console for 404 errors

### CSS not applying
- Verify CSS link in template
- Check for syntax errors in CSS
- Ensure proper specificity
- Clear browser cache
- Check for conflicting styles

### JavaScript not executing
- Check browser console for errors
- Verify script tag placement
- Ensure dependencies are loaded first
- Check for syntax errors
- Verify CORS settings for external scripts

---

**Last Updated:** December 2025