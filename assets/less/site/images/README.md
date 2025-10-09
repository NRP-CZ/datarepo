# Image Assets for InvenioRDM

This folder contains custom image assets to be used in the repository UI
(e.g. background images or other graphics) and processed by Invenio's build
pipeline (Rspack).

## How to use

1. Add images assets into this folder  
2. Reference them in via @less import alias e.g.:  
   ```css
   background-image: url(~@less/site/images/my-background.webp);
   ```
