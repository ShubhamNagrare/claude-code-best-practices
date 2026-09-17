# Spec: Refund Policy Page

## Overview
Add a dedicated Refund Policy page accessible from the app footer, mirroring the existing Terms and Privacy pages. This page will document the app's refund procedures and policies. The page is public (no authentication required) but will respect the user's login state to conditionally show the logout link in the header.

## Depends on
No prior features — this is independent and can be developed in parallel with other work.

## Routes
- `GET /refund-policy` — display the refund policy page — public

## Database changes
No database changes.

## Templates

### Create
- `templates/refund-policy.html` — new legal page template (structure mirrors `privacy.html` and `terms.html`)

### Modify
- `templates/_footer.html` — add a link to `/refund-policy` between the existing Terms and Privacy links

## Files to change
- `main.py` — add `@app.get("/refund-policy")` route handler
- `templates/_footer.html` — add refund-policy link

## Files to create
- `templates/refund-policy.html` — new legal page

## New dependencies
No new dependencies.

## Rules for implementation
- Follow the structure of `privacy.html` and `terms.html` exactly
- Use Jinja2 templating: include `_header.html` and `_footer.html` partials
- Set `class="has-header"` on `<body>` to account for fixed header padding
- Placeholder text is acceptable; refund policy content can be generic/template language
- Pass `authenticated` and `username` to the template context (auto-populated from request session by the route handler)
- Route handler signature: `def refund_policy_page(request: Request)` → `TemplateResponse("refund-policy.html", {...})`
- CSS class `legal-wrapper` wraps the page content (shared with terms/privacy)
- No changes to `style.css` needed — reuse existing `.legal-wrapper` and `.card` styles

## Definition of done
- [ ] Route handler `GET /refund-policy` renders the refund policy template
- [ ] Template includes `_header.html` (with topbar) and `_footer.html` (with links)
- [ ] Page displays with correct fixed-header padding (body has `has-header` class)
- [ ] Footer link to `/refund-policy` appears and is clickable
- [ ] Refund policy link appears in footer alongside Terms and Privacy
- [ ] Unauthenticated users can access the page (no redirect to `/login`)
- [ ] Authenticated users see the page with logout link visible in header
- [ ] Manual browser test: navigate to `/refund-policy` from footer link, verify layout and navigation
