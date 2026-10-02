"""Offline unit checks for job-scraper-mcp helpers (no live URL scraping)."""
from server import (
    _host_matches,
    _partial_job_data_from_text,
    _usable_job_text,
    CSR_HEAVY_JOB_HOSTS,
)


def test_usable_job_text_rejects_blocked_pages() -> None:
    long_page = "Job description " + ("detail content " * 20)
    assert _usable_job_text(long_page)
    assert not _usable_job_text("Just a moment... " + ("x" * 300))
    assert not _usable_job_text("Checking your browser before accessing. " + ("y" * 200))
    assert not _usable_job_text("Are you a robot? " + ("z" * 250))
    assert not _usable_job_text("short")


def test_host_matches_csr_hosts() -> None:
    assert _host_matches("www.linkedin.com", CSR_HEAVY_JOB_HOSTS)
    assert _host_matches("id.glints.com", CSR_HEAVY_JOB_HOSTS)
    assert _host_matches("jobstreet.co.id", CSR_HEAVY_JOB_HOSTS)
    assert not _host_matches("example.com", CSR_HEAVY_JOB_HOSTS)


def test_partial_job_data_parses_labeled_fields() -> None:
    raw = (
        "Position: Backend Engineer\n"
        "Company: Acme Indonesia\n"
        "Location: Jakarta Selatan\n"
        "Salary: Rp 12.000.000 - Rp 18.000.000\n"
        "Build and maintain payment services."
    )
    data = _partial_job_data_from_text(raw, ["direct failed"])
    assert data.position == "Backend Engineer"
    assert data.company == "Acme Indonesia"
    assert data.location == "Jakarta Selatan"
    assert "Rp 12.000.000" in data.salary_range
    assert data.raw_text.startswith("Position: Backend Engineer")
    assert any("regex parsial" in note for note in data.extraction_notes)


def test_partial_job_data_without_labels_keeps_raw_text() -> None:
    raw = "We are hiring someone great for an interesting engineering role in Jakarta."
    data = _partial_job_data_from_text(raw, ["note"])
    assert data.position == ""
    assert data.raw_text == raw[:500]
    assert any("tidak menemukan field berlabel" in note for note in data.extraction_notes)


if __name__ == "__main__":
    test_usable_job_text_rejects_blocked_pages()
    test_host_matches_csr_hosts()
    test_partial_job_data_parses_labeled_fields()
    test_partial_job_data_without_labels_keeps_raw_text()
    print("offline server checks OK")
