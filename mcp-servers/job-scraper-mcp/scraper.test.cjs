const test = require("node:test");
const assert = require("node:assert/strict");
const {
  textFromHtml,
  JOB_CONTENT_SELECTORS,
  WAIT_SELECTORS,
} = require("./scraper.cjs");

test("extracts job posting structured data and excludes navigation", () => {
  const html = `
    <html><body>
      <nav>Navigation text that should not appear</nav>
      <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "JobPosting",
          "title": "Backend Engineer",
          "hiringOrganization": {"name": "Example Co"},
          "description": "Build APIs and maintain production services.",
          "qualifications": "Experience with Python and PostgreSQL."
        }
      </script>
      <main><h1>Backend Engineer</h1><p>Apply now.</p></main>
    </body></html>`;

  const result = textFromHtml(html);
  assert.match(result, /Backend Engineer/);
  assert.match(result, /Example Co/);
  assert.match(result, /Python and PostgreSQL/);
  assert.doesNotMatch(result, /Navigation text/);
});

test("falls back to the main page content when structured data is absent", () => {
  const result = textFromHtml(
    "<html><body><main><h1>Data Analyst</h1><p>Analyze product data.</p></main></body></html>"
  );
  assert.match(result, /Data Analyst/);
  assert.match(result, /Analyze product data/);
});

test("prefers job-description class containers over chrome text", () => {
  const html = `
    <html><body>
      <nav>Site nav that should not appear</nav>
      <div class="job-description">
        <h2>Responsibilities</h2>
        <p>Own the payment ledger service end to end.</p>
      </div>
      <footer>Footer noise that should not appear</footer>
    </body></html>`;

  const result = textFromHtml(html);
  assert.match(result, /Own the payment ledger/);
  assert.doesNotMatch(result, /Site nav/);
  assert.doesNotMatch(result, /Footer noise/);
});

test("includes expanded board-oriented selectors", () => {
  assert.ok(Array.isArray(JOB_CONTENT_SELECTORS));
  assert.ok(Array.isArray(WAIT_SELECTORS));
  for (const selector of [
    "main",
    "[class*='jobDescription']",
    "[class*='job-details']",
    "[class*='jobDetails']",
    "[class*='vacancy']",
  ]) {
    assert.ok(JOB_CONTENT_SELECTORS.includes(selector), selector);
    assert.ok(WAIT_SELECTORS.includes(selector), selector);
  }
});
