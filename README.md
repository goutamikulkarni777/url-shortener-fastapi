# High-Performance Production-Ready URL Shortener

A clean, full-stack MVC web service built with FastAPI, SQLite, and SQLAlchemy. This application implements a decoupled backend API architecture with a responsive, single-page frontend interface to process, store, validate, and dynamically redirect short URL tokens.

## 🚀 Architectural Highlights

*   **Separation of Concerns (MVC Layout):** Completely decoupled backend endpoints (`app.py`), relational database schemas, frontend presentation structures (`templates/`), and layout stylesheets (`static/`).
*   **Optimal Lookup Efficiencies:** Uses an optimized SQLite relational schema utilizing SQLAlchemy ORM with structural indexing on unique token hashes, achieving a theoretical time complexity of $O(1)$ for redirection routing.
*   **Data Integrity & Validation:** Built-in regular expression validation layers to verify safe URLs and a custom md5 salt-hashing mechanism to dynamically mitigate routing string collisions.
*   **Asynchronous Frontend Integration:** Integrated a native browser JavaScript `Fetch API` layout to asynchronously communicate with backend microservices without triggering full page reloads.

---

## 📂 Repository Structure

```text
url-shortener/
│
├── static/
│   └── css/
│       └── style.css      # Custom interface styling
│
├── templates/
│   └── index.html         # Asynchronous single-page user interface
│
├── app.py                 # Core engine, DB configuration, and API routes
├── requirements.txt       # Project microservices dependencies
└── .gitignore             # Strict local environment file exclusions
