# Tailwind CSS vs Normal CSS - Comparison

## Example 1: Simple Card Component

### Normal CSS Approach
```jsx
// Card.jsx
import './Card.css'

function Card() {
  return (
    <div className="card">
      <h2 className="card-title">Hello</h2>
      <p className="card-description">This is a card</p>
      <button className="card-button">Click Me</button>
    </div>
  )
}
```

```css
/* Card.css */
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin: 16px;
  max-width: 400px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.card-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 16px;
}

.card-button {
  background-color: #3b82f6;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.card-button:hover {
  background-color: #2563eb;
}
```

### Tailwind CSS Approach
```jsx
function Card() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 m-4 max-w-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-2">Hello</h2>
      <p className="text-sm text-gray-600 leading-relaxed mb-4">This is a card</p>
      <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 font-medium transition-colors">
        Click Me
      </button>
    </div>
  )
}
```

---

## Example 2: Responsive Button

### Normal CSS Approach
```jsx
// Button.jsx
import './Button.css'

function Button() {
  return <button className="responsive-btn">Submit</button>
}
```

```css
/* Button.css */
.responsive-btn {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  width: 100%;
  margin-bottom: 16px;
}

.responsive-btn:hover {
  background-color: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.responsive-btn:active {
  transform: translateY(0);
}

/* Mobile */
@media (min-width: 640px) {
  .responsive-btn {
    width: auto;
    padding: 10px 20px;
    font-size: 14px;
  }
}

/* Tablet */
@media (min-width: 768px) {
  .responsive-btn {
    width: auto;
    padding: 12px 24px;
    font-size: 16px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .responsive-btn {
    width: auto;
    padding: 12px 32px;
    font-size: 18px;
  }
}
```

### Tailwind CSS Approach
```jsx
function Button() {
  return (
    <button className="w-full sm:w-auto px-4 sm:px-6 lg:px-8 py-2 sm:py-3 lg:py-3 text-sm sm:text-base lg:text-lg font-semibold bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0 mb-4">
      Submit
    </button>
  )
}
```

---

## Example 3: Form Input

### Normal CSS Approach
```jsx
// Input.jsx
import './Input.css'

function Input() {
  return (
    <div className="form-group">
      <label className="form-label">Email</label>
      <input type="email" className="form-input" placeholder="Enter email" />
    </div>
  )
}
```

```css
/* Input.css */
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}
```

### Tailwind CSS Approach
```jsx
function Input() {
  return (
    <div className="flex flex-col mb-4">
      <label className="text-sm font-medium text-gray-700 mb-2">Email</label>
      <input 
        type="email" 
        placeholder="Enter email"
        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 placeholder-gray-400"
      />
    </div>
  )
}
```

---

## Key Differences

| Aspect | Normal CSS | Tailwind CSS |
|--------|-----------|-------------|
| **File Size** | CSS file separate, can get large | Pre-generated, can be optimized via PurgeCSS |
| **Development Speed** | Slower (write CSS, name classes, maintain separate files) | Faster (utility classes directly in HTML) |
| **Naming** | Need meaningful class names (`.card`, `.button-primary`) | Descriptive utility names (`.bg-blue-500`, `.p-4`) |
| **Customization** | Edit CSS file | Modify tailwind.config.js |
| **Responsive Design** | Media queries needed | Breakpoint prefixes (sm:, md:, lg:) |
| **State Handling** | Write `:hover`, `:focus` in CSS | Use prefixes (hover:, focus:, active:) |
| **Reusability** | Component-based CSS classes | Utility class combinations |
| **Consistency** | Manual discipline | Built-in design system (colors, spacing, etc.) |
| **Learning Curve** | CSS knowledge required | Learn Tailwind utility names |
| **Bundle Size** | Smaller if CSS is well-maintained | Larger initially but optimized in production |

---

## When to Use Each

### Use Normal CSS When:
- Building simple static sites
- Working with legacy projects
- You prefer semantic class names
- You want maximum control over every pixel
- Team is not familiar with utility-first CSS

### Use Tailwind CSS When:
- Building modern React/Vue applications
- You want rapid prototyping
- Need consistent design system
- Building responsive designs frequently
- Team wants to move fast without writing CSS files
- You prefer staying in the HTML/JSX layer

