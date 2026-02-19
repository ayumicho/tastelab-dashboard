# TasteLab Dashboard - Images Directory

This directory contains visual assets for the TasteLab Dashboard application.

## Directory Structure

```
images/
├── logo.png           # TasteLab Dashboard logo
├── 400.png            # 400 Bad Request error page
└── 500.png            # 500 Server Error page
```

## Images

### Logo (`logo.png`)
- **Usage:** Header navigation, branding
- **Format:** PNG with transparency
- **Usage in templates:**
```html
<img src="{{ url_for('static', filename='images/logo.png') }}" 
     alt="TasteLab Dashboard" 
     class="logo">
```

### Error Pages

**400 Error (`error-400.png`)**
- **Purpose:** Display on HTTP 400 Bad Request errors
- **Route:** Error handling page
- **Usage in templates:**
```html
<img src="{{ url_for('static', filename='images/error-400.png') }}" 
     alt="400 Bad Request">
```

**500 Error (`500.png`)**
- **Purpose:** Display on HTTP 500 Server Error
- **Route:** Error handling page
- **Usage in templates:**
```html
<img src="{{ url_for('static', filename='images/error-500.png') }}" 
     alt="500 Server Error">
```

## Adding New Images

1. Optimize image file (compress, resize as needed)
2. Add to this directory
3. Use appropriate Flask URL helper:
```python
url_for('static', filename='images/filename.png')
```
4. Update this README

## Naming Convention

- Use lowercase with hyphens: `logo.png`, `400.png`
- Be descriptive: `500.png` not `error5.png`
- No spaces in filenames

---

**Last Updated:** January 2026
**Maintained by:** Ayumi Cho