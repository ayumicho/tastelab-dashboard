# TasteLab Dashboard - Static Directory

This directory contains all static assets for the TasteLab Dashboard, including stylesheets and images. Static files are served directly by Flask and cached by the browser.

## Directory Structure

```
static/
├── css/          # Stylesheets (11 files, 127 sections)
└── images/       # Images and visual assets (3 files)
```

## Subdirectories

### `css/`
Contains organized stylesheets for the application:
- **base.css** - Global styles used across all pages
- **Page-specific CSS** - Dedicated styles for each feature

**See:** [`css/README.md`](css/README.md) for detailed documentation

### `images/`
Stores application visual assets:
- **logo.png** - TasteLab Dashboard logo
- **400.png** - 400 error page
- **500.png** - 500 error page

**See:** [`images/README.md`](images/README.md) for detailed documentation

## Using Static Files in Templates

Use Flask's `url_for()` function to generate URLs:

```jinja
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">

<!-- Images -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="TasteLab Logo">
```

## Naming Conventions

- **CSS files:** `kebab-case.css` (e.g., `dashboard.css`, `experiment-detail.css`)
- **Images:** `lowercase-with-hyphens.png` (e.g., `logo.png`, `400.png`, `500.png`)

## Adding New Assets

1. Place in appropriate subdirectory (`css/` or `images/`)
2. Follow naming conventions
3. Optimize before adding (compress images, minify CSS)
4. Update relevant README file
5. Link in Flask templates using `url_for()`

## Security

- Never store sensitive data (credentials, API keys) in static files
- Validate and sanitize any user uploads
- Use HTTPS in production

---

**Last Updated:** January 2026

**Maintained by:** Ayumi Chotoe