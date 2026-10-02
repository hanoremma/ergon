const cheerio = require("cheerio");

const DEFAULT_UA =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
  "AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/124.0.0.0 Safari/537.36";

const JOB_CONTENT_SELECTORS = [
  "main",
  "article",
  "[role='main']",
  "[class*='job-description']",
  "[class*='jobDescription']",
  "[class*='description']",
  "[id*='job-description']",
  "[id*='jobDescription']",
  "[class*='job-details']",
  "[class*='jobDetails']",
  "[class*='job-body']",
  "[class*='jobBody']",
  "[class*='posting-content']",
  "[class*='vacancy']",
  "[class*='job-content']",
  "[class*='loker']",
];

const WAIT_SELECTORS = [
  "main",
  "article",
  "[role='main']",
  "[class*='job-description']",
  "[class*='jobDescription']",
  "[class*='description']",
  "[id*='job-description']",
  "[id*='jobDescription']",
  "[class*='job-details']",
  "[class*='jobDetails']",
  "[class*='job-body']",
  "[class*='posting-content']",
  "[class*='vacancy']",
];

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function textFromHtml(html) {
  const $ = cheerio.load(html);
  const structured = [];

  $('script[type="application/ld+json"]').each((_, element) => {
    try {
      const data = JSON.parse($(element).contents().text());
      const records = Array.isArray(data) ? data : [data];
      for (const record of records) {
        const candidates = record["@graph"] || [record];
        for (const candidate of candidates) {
          if (candidate["@type"] === "JobPosting") {
            const hiringOrganization = candidate.hiringOrganization;
            structured.push([
              candidate.title,
              hiringOrganization && hiringOrganization.name,
              candidate.description,
              candidate.qualifications,
              candidate.responsibilities,
              candidate.jobLocation && JSON.stringify(candidate.jobLocation),
            ].filter(Boolean).join("\n"));
          }
        }
      }
    } catch {
      // Ignore malformed structured-data blocks and continue with page content.
    }
  });

  $(
    "script, style, noscript, svg, nav, footer, header, aside, " +
    "[aria-hidden='true'], [role='navigation'], [role='banner'], [role='contentinfo']"
  ).remove();

  let bestContent = "";
  for (const selector of JOB_CONTENT_SELECTORS) {
    $(selector).each((_, element) => {
      const candidate = $(element).text().replace(/\s+/g, " ").trim();
      if (candidate.length > bestContent.length) bestContent = candidate;
    });
  }

  const h1Text = $("h1").first().text().replace(/\s+/g, " ").trim();
  if (h1Text && bestContent.length < 400 && !bestContent.includes(h1Text)) {
    bestContent = `${h1Text}\n${bestContent}`.trim();
  }

  const pageText = bestContent || $("body").text();
  const combined = [...structured, pageText]
    .filter(Boolean)
    .join("\n")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return combined.slice(0, 20000);
}

async function waitForJobContent(page, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const found = await page.evaluate((selectors) => {
        return selectors.some((selector) => {
          try {
            return Boolean(document.querySelector(selector));
          } catch {
            return false;
          }
        });
      }, WAIT_SELECTORS);
      if (found) return true;
    } catch {
      return false;
    }
    await sleep(250);
  }
  return false;
}

async function renderUrl(url) {
  const puppeteer = require("puppeteer");
  const launchArgs = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
  ];
  if (process.env.PUPPETEER_NO_SANDBOX === "1") {
    launchArgs.push("--no-sandbox", "--disable-setuid-sandbox");
  }

  const browser = await puppeteer.launch({
    headless: true,
    args: launchArgs,
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 900 });
    await page.setUserAgent(DEFAULT_UA);
    await page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, "webdriver", {
        get: () => undefined,
      });
    });

    try {
      await page.goto(url, {
        waitUntil: "networkidle2",
        timeout: 15000,
      });
    } catch {
      await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout: 12000,
      });
    }

    await waitForJobContent(page, 6000);

    try {
      await page.evaluate(async () => {
        window.scrollTo(0, Math.min(600, document.body.scrollHeight / 3));
      });
    } catch {
      // Ignore scroll failures on locked-down pages.
    }
    await sleep(500);

    return textFromHtml(await page.content());
  } finally {
    await browser.close();
  }
}

async function main() {
  const mode = process.argv[2];
  let text;
  if (mode === "html") {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    text = textFromHtml(Buffer.concat(chunks).toString("utf8"));
  } else if (mode === "render") {
    const url = process.argv[3];
    if (!url) throw new Error("A URL is required for render mode.");
    text = await renderUrl(url);
  } else {
    throw new Error(`Unsupported mode: ${mode || "(missing)"}`);
  }
  process.stdout.write(JSON.stringify({ text }));
}

if (require.main === module) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}

module.exports = {
  textFromHtml,
  JOB_CONTENT_SELECTORS,
  WAIT_SELECTORS,
};
