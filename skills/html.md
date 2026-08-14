# HTML5 & Accessibility (a11y) Skill Standards

## 1. Document Structure & Semantics
* Always declare the document type using standard `<!DOCTYPE html>`.
* Always specify the main language of the document on the root element, e.g., `<html lang="en">`.
* Structure web page architecture using semantic layout tags (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`).
* Avoid `<div>` soup! Never use a `<div>` or `<span>` when a meaningful HTML5 semantic tag exists.
* Maintain a strict hierarchical heading order (`<h1>` down to `<h6>`). Never skip heading levels.

## 2. Accessibility & ARIA Guidelines
* Every image element `<img>` MUST include a descriptive `alt` attribute. Use `alt=""` for purely decorative images.
* All interactive elements (buttons, links, inputs) must be keyboard accessible with visible focus indicators.
* Use explicit `<label>` elements connected via `for` attributes to corresponding input fields.
* Add `aria-label` or `aria-labelledby` attributes to interactive elements lacking visible text context.
* Use `role="status"` or `aria-live="polite"` for dynamic content containers that update dynamically.

## 3. Forms & User Input
* Always wrap related input fields inside `<fieldset>` elements grouped by `<legend>` tags.
* Use specific HTML5 input types (`type="email"`, `type="tel"`, `type="url"`, `type="number"`) to trigger correct mobile keyboards.
* Enforce native form validation attributes (`required`, `minlength`, `maxlength`, `pattern`).
* Provide clear, permanently visible instructions or inline error messages for invalid form fields.

## 4. Media & Embedded Content
* Include `<track>` elements with valid subtitles or captions for `<video>` and `<audio>` elements.
* Set explicit `width` and `height` attributes on image tags to prevent Layout Shifts (CLS).
* Use the `<picture>` element with `<source>` tags to serve modern image formats like AVIF or WebP gracefully.
* Lazy-load off-screen images using the native `loading="lazy"` attribute.

## 5. Search Engine Optimization (SEO) & Head Tags
* Include essential `<meta>` elements: character encoding `<meta charset="UTF-8">` and viewport settings.
* Provide unique, concise `<title>` elements for every page on the application.
* Add essential Open Graph (OG) meta tags for rich link previews on social platforms like Discord or X.
* Specify canonical link tags (`<link rel="canonical">`) to prevent duplicate indexing issues.

## 6. Performance Optimization
* Defer execution of external JavaScript files using the `defer` or `async` script attributes.
* Preconnect to critical third-party origin domains using `<link rel="preconnect">`.
* Preload essential custom web fonts using `<link rel="preload" as="font">`.

## 7. Security Best Practices
* Always add `rel="noopener noreferrer"` to external links opening in new windows (`target="_blank"`).
* Avoid inline event handling attributes like `onclick=""` or `onload=""`. Use external script listeners.
* Ensure content security policies (CSP) restrict inline style and script injections.

## 8. Clean Code & Formatting
* Use standard 2-space or 4-space indentation consistently throughout the document.
* Keep element attribute order predictable: `class`, `id`, `name`, `type`, `src`/`href`, `alt`, `aria-*`.
* Lowercase all HTML tags, attribute names, and document declarations.

## 9. Cross-Browser Compatibility
* Avoid using experimental HTML tags without checking browser compatibility specifications.
* Test layout and structure behavior across desktop, tablet, and mobile viewports.

## 10. Document Validation
* Ensure final output validates cleanly with zero errors against the W3C Markup Validation Service.
