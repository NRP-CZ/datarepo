# Font Customization

This folder / portion of the project handles custom fonts for the UI. For full guidance see the  
[official InvenioRDM docs](https://inveniordm.docs.cern.ch/operate/customize/look-and-feel/font/) on fonts.

---

## How to use

1. Place your font files in this direcotry
2. Define `@font-face` in your overrides file (typically something like `site.overrides.less`)  
3. Set the font variables (body, header, etc.) in your site variables file so the new fonts are applied  
4. Rebuild the frontend assets (e.g. via `invenio-cli assets build -d`) for changes to appear

---

## Tips

- Use common formats (woff2, ttf) for good browser support  
- If you're using `invenio-cli assets watch`, you may need to stop/start after adding new font files so changes aren’t missed  
- Keep names consistent and documented so other developers know which fonts are used where
