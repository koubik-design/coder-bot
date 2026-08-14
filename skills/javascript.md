# JavaScript & Node.js Skill Standards

## 1. Syntax & Modern ES Standards
* Target modern ECMAScript standards (ES2022+).
* Never use the `var` keyword. Use `const` by default, and `let` only when variable reassignment is required.
* Always enforce strict equality comparison (`===` and `!==`) instead of loose equality (`==` and `!=`).
* Use arrow functions (`() => {}`) for callbacks and inline expressions to maintain `this` lexical binding.
* Prefer template literals (`` `string ${var}` ``) over string concatenation with `+`.

## 2. Asynchronous Programming
* Avoid nested callback structures ("callback hell"). Use modern `async/await` syntax.
* Always wrap `await` calls in `try...catch` blocks to capture rejected promises.
* Execute independent asynchronous operations concurrently using `Promise.all()` or `Promise.allSettled()`.
* Avoid floating promises; always handle or return promises produced inside functions.

## 3. Object & Array Manipulation
* Use object and array destructuring for clean property assignment.
* Use spread operators (`...`) for immutable state updates and array copying.
* Prefer higher-order array methods (`.map()`, `.filter()`, `.reduce()`, `.find()`) over standard `for` loops.
* Use optional chaining (`?.`) and nullish coalescing (`??`) for safe property access.

## 4. Error Handling
* Create custom error classes extending built-in `Error` for domain-specific errors.
* Always attach meaningful descriptive messages and status codes to thrown errors.
* Never swallow errors silently inside empty `catch` blocks.
* Emit structured error logs containing stack traces in server environments.

## 5. DOM & Browser Interactivity
* Sanitize user input before inserting content into the DOM using `textContent` instead of `innerHTML`.
* Use event delegation to attach listeners efficiently to parent containers.
* Wrap resize, scroll, or input event listeners in `debounce` or `throttle` helpers.
* Prefer `fetch()` API or `axios` for browser HTTP requests.

## 6. Node.js Architecture
* Organize code modularly using ES Modules (`import`/`export`) or CommonJS (`require`).
* Keep environment variables isolated inside `.env` files accessed via `process.env`.
* Implement Graceful Shutdown mechanisms handling `SIGTERM` and `SIGINT` signals.
* Avoid blocking the Node.js event loop with synchronous operations like `fs.readFileSync`.

## 7. Security Best Practices
* Sanitize all outgoing parameters to prevent Cross-Site Scripting (XSS) attacks.
* Enforce Cross-Origin Resource Sharing (CORS) rules on public API routes.
* Never log sensitive credentials, authorization tokens, or user passwords.
* Avoid dynamic evaluation functions like `eval()` or dynamic `Function()` constructor.

## 8. Code Formatting & Linting
* Adhere to StandardJS or Airbnb JavaScript style guidelines.
* Format statements with consistent semicolon usage and double/single quote styles.
* Limit function line count to 30 lines and parameter count to 3 arguments max.

## 9. Performance Tuning
* Use dynamic import calls (`import()`) for code splitting and lazy loading heavy modules.
* Avoid leaking memory by removing event listeners when components unmount or destroy.
* Use `WeakMap` or `WeakSet` for memory-sensitive caching keys.

## 10. Testing Protocols
* Write component and integration tests using Jest or Vitest framework.
* Mock API dependencies using `msw` (Mock Service Worker).
* Ensure edge-case inputs (null, undefined, empty strings) are thoroughly tested.
