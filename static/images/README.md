# Static Images

This folder contains **static image assets** for the repository UI.  
These files are served directly as part of the web application’s static files.

## Usage

- Place logos, favicons, icons, and other project-specific images here.  
- Reference them in templates or stylesheets using the static path, for example:

  ```jinja
  <img src="{{ url_for('static', filename='images/my-logo.png') }}" alt="Site logo">
