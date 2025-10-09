# Templates

This folder holds custom Jinja2 templates for overriding the default InvenioRDM UI.  
See the official docs: [Customize templates](https://inveniordm.docs.cern.ch/operate/customize/look-and-feel/templates/).

## File overview

- **css.html**  
  Injects custom CSS styles into the rendered pages.  
  Use this file to load additional stylesheets or apply project-specific styling overrides.

- **footer.html**  
  Defines the footer section of the site.  
  Customize it to add branding, links, or other project-specific information at the bottom of every page.

- **header_frontpage.html**  
  Specialized header used on the repository’s front page (landing page).  
  Typically contains a simplified or more visual header layout compared to the standard header.

- **header.html**  
  Defines the main site header used across most repository pages.  
  Modify this to customize the navigation bar, branding, or global links.

- **javascript.html**  
  Injects custom JavaScript into the rendered pages.  
  Use this file for additional scripts, analytics, or behavior overrides.

- **page.html**  
  Base layout for rendering pages.  
  Other templates extend this file to ensure consistent structure across the site.

## Notes

- All templates are written in Jinja2 (with optional use of JinjaX), following the Invenio theming system.  
- To apply changes, restart the development server or re-build assets if necessary.  
- Keep customizations minimal and well-documented to simplify future upgrades of Invenio repository.