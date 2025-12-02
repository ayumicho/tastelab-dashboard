# Templates Directory

This directory contains all HTML templates for the TasteLab Dashboard. Templates are built using Jinja2 templating engine and follow Flask's template inheritance pattern for consistent layout and maintainability.

## Overview

The templates use a base template (`base.html`) that provides the core structure, navigation, and styling. All other templates extend this base to maintain consistent appearance and functionality across the application.

## Template Hierarchy

```
base.html (Base template)
├── home.html (Dashboard home)
├── login.html (Authentication)
├── signup.html (User registration)
├── profile.html (User profile)
├── add-experiment.html (Create experiments)
├── single-experiment.html (Experiment details)
├── cv.html (Computer Vision results)
├── nlp.html (NLP model results)
├── help.html (User assistance)
├── privacy-policy.html (Privacy information)
├── terms-of-service.html (Terms of use)
├── 404.html (Not found error)
└── 500.html (Server error)
```

## Core Templates

### `base.html`
The foundational template that all other templates extend. Contains:
- HTML document structure
- Navigation bar
- Footer
- CSS/JavaScript imports
- Flash message handling
- Common UI components

**Usage:**
```jinja
{% extends 'base.html' %}
{% block content %}
    <!-- Your content here -->
{% endblock %}
```

### `home.html`
Main dashboard landing page displaying:
- Experiment overview
- Quick statistics
- Recent activity
- Navigation to key features

**Route:** `/` (found in `views.py`)

## Authentication Templates

### `login.html`
User authentication page with:
- Username/email input
- Password field
- Link to signup page

**Route:** `/login`

### `signup.html`
User registration page featuring:
- Registration form
- Email validation
- Password requirements

**Route:** `/signup`

### `logout.html`
Logout confirmation page
- Confirms successful logout
- Redirect options

**Route:** `/logout`

## User Management

### `profile.html`
User profile page displaying:
- User information
- Account settings
- Change password option

**Route:** `/profile`

## Experiment Management

### `add-experiment.html`
Experiment creation interface with:
- Experiment details form
- Participant information
- Data upload options
- Submission controls

**Route:** `/experiments/create`

### `single-experiment.html`
Detailed view of individual experiments showing:
- Experiment metadata
- Participant data
- Analysis results
- Visualization charts
- Export options

**Route:** `/experiments/<id>`

## Model Output Templates

### `cv.html`
Computer Vision model results page displaying:
- Image analysis results
- Detected emotions from facial expressions
- Confidence scores
- Visual annotations
- Comparison charts

**Route:** `/cv` or `/experiments/<id>/cv`

### `nlp.html`
Natural Language Processing model results page displaying:
- Text emotion analysis
- Sentiment classification
- Keyword extraction
- Response summaries

**Route:** `/nlp` or `/experiments/<id>/nlp`

## Information Pages

### `help.html`
User assistance and documentation page featuring:
- Feature explanations
- Step-by-step guides
- FAQ section
- Troubleshooting tips

**Route:** `/help`

### `privacy-policy.html`
Privacy policy and data handling information:
- Data collection practices
- Usage of personal information
- User rights
- Contact information

**Route:** `/privacy-policy`

### `terms-of-service.html`
Terms and conditions for using the dashboard:
- User responsibilities
- Acceptable use policy
- Service limitations
- Legal disclaimers

**Route:** `/terms-of-service`

## Error Templates

### `404.html`
Custom 404 Not Found error page with:
- Friendly error message
- Navigation suggestions
- Link back to home

**Triggered:** When requesting non-existent routes

### `500.html`
Custom 500 Internal Server Error page with:
- Error notification
- Support contact information
- Safe navigation options

**Triggered:** On server-side exceptions

## Template Conventions

### Block Structure
Templates use the following main blocks:
- `{% block title %}` - Page title
- `{% block content %}` - Main page content
- `{% block scripts %}` - Page-specific JavaScript
- `{% block styles %}` - Page-specific CSS

### Flash Messages
Flash messages are displayed using:
```jinja
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <!-- Display messages -->
    {% endif %}
{% endwith %}
```

### Static Files
Reference static files using:
```jinja
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/script.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}">
```

### URL Generation
Generate URLs dynamically using:
```jinja
<a href="{{ url_for('route_name') }}">Link</a>
<a href="{{ url_for('route_name', param=value) }}">Link with params</a>
```

## Styling Approach

Templates use a combination of:
- **Bootstrap 5** - Core UI framework
- **Custom CSS** - Located in `static/css/`
- **Inline styles** - Minimal, for specific cases
- **Responsive design** - Mobile-first approach

## JavaScript Integration

Page-specific JavaScript is included in the `scripts` block:
```jinja
{% block scripts %}
<script src="{{ url_for('static', filename='js/custom.js') }}"></script>
<script>
    // Inline JavaScript specific to this page
</script>
{% endblock %}
```

## Best Practices

### Creating New Templates

1. **Extend base.html** for consistent layout:
   ```jinja
   {% extends 'base.html' %}
   ```

2. **Define meaningful titles**:
   ```jinja
   {% block title %}Descriptive Page Title{% endblock %}
   ```

3. **Organize content logically**:
   ```jinja
   {% block content %}
   <div class="container">
       <h1>Page Heading</h1>
       <!-- Your content -->
   </div>
   {% endblock %}
   ```

4. **Use template includes** for reusable components:
   ```jinja
   {% include 'components/card.html' %}
   ```

### Data Display

- Use Jinja2 filters for formatting: `{{ data|format }}`
- Implement proper escaping: `{{ user_input|escape }}`
- Handle missing data gracefully: `{{ value|default('N/A') }}`

### Forms

- Include CSRF tokens: `{{ form.hidden_tag() }}`
- Add proper validation feedback
- Use consistent styling across forms

## Adding New Templates

When adding new templates:

1. Create the template file in the appropriate directory
2. Extend `base.html` for consistent layout
3. Define required blocks (`title`, `content`)
4. Add corresponding route in `views.py`
5. Update this README with template documentation
6. Test responsiveness on multiple devices

## Related Files

- **Routes:** Defined in `views.py` in the root directory
- **Styles:** Located in `static/css/`
- **Scripts:** Located in `static/js/`
- **Base Layout:** `base.html` contains shared structure

---

**Last Updated:** December 2025