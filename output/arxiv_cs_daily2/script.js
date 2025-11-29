// output/arxiv_cs_daily/script.js

/**
 * Global variable `papers` is expected to be defined in data.js.
 * It should be an array of paper objects with fields: id, title, authors, abstract,
 * pdf_url, submitted (ISO string), category, and bibtex.
 */

/**
 * Filters papers by a given category and returns them sorted by submission date (newest first).
 * @param {string} category - The category to filter by (e.g., 'cs.AI', 'cs.LG').
 * @returns {Array} - Array of paper objects matching the category, sorted by 'submitted' descending.
 */
function getPapersByCategory(category) {
    if (!Array.isArray(papers)) {
        console.error('Global variable `papers` is not an array.');
        return [];
    }

    try {
        return papers
            .filter(paper => paper.category === category)
            .sort((a, b) => new Date(b.submitted) - new Date(a.submitted));
    } catch (error) {
        console.error('Error filtering or sorting papers:', error);
        return [];
    }
}

/**
 * Renders a list of papers into a specified container element.
 * Each paper is displayed as a list item with title (linked to detail page), authors, and submission date.
 * @param {Array} papers - Array of paper objects to render.
 * @param {string} containerId - ID of the HTML container element (e.g., 'paper-list').
 */
function renderPaperList(papers, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found.`);
        return;
    }

    // Clear existing content
    container.innerHTML = '';

    if (!Array.isArray(papers) || papers.length === 0) {
        container.innerHTML = '<p>No papers found.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'paper-list';

    papers.forEach(paper => {
        const li = document.createElement('li');
        li.className = 'paper-item';

        // Title as link to detail page
        const titleLink = document.createElement('a');
        titleLink.href = `detail.html?id=${encodeURIComponent(paper.id)}`;
        titleLink.textContent = paper.title || 'Untitled';
        titleLink.className = 'paper-title';

        // Authors
        const authorsDiv = document.createElement('div');
        authorsDiv.className = 'paper-authors';
        authorsDiv.textContent = `Authors: ${paper.authors?.join(', ') || 'Unknown'}`;

        // Submission date
        const dateDiv = document.createElement('div');
        dateDiv.className = 'paper-date';
        const date = paper.submitted ? new Date(paper.submitted).toLocaleDateString() : 'Unknown date';
        dateDiv.textContent = `Submitted: ${date}`;

        li.appendChild(titleLink);
        li.appendChild(authorsDiv);
        li.appendChild(dateDiv);
        ul.appendChild(li);
    });

    container.appendChild(ul);
}

/**
 * Renders detailed information for a specific paper into a container.
 * Includes title, authors, abstract, PDF link, submission date, BibTeX, and a 'Copy BibTeX' button.
 * @param {string} paperId - The ID of the paper to display.
 * @param {string} containerId - ID of the HTML container element (e.g., 'paper-detail').
 */
function renderPaperDetail(paperId, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found.`);
        return;
    }

    if (!Array.isArray(papers)) {
        console.error('Global variable `papers` is not an array.');
        container.innerHTML = '<p>Error loading paper details.</p>';
        return;
    }

    const paper = papers.find(p => p.id === paperId);
    if (!paper) {
        container.innerHTML = '<p>Paper not found.</p>';
        return;
    }

    // Clear existing content
    container.innerHTML = '';

    // Title
    const titleEl = document.createElement('h1');
    titleEl.textContent = paper.title || 'Untitled';
    titleEl.className = 'detail-title';

    // Authors
    const authorsEl = document.createElement('p');
    authorsEl.className = 'detail-authors';
    authorsEl.innerHTML = `<strong>Authors:</strong> ${paper.authors?.join(', ') || 'Unknown'}`;

    // Abstract
    const abstractEl = document.createElement('div');
    abstractEl.className = 'detail-abstract';
    abstractEl.innerHTML = `<strong>Abstract:</strong><br>${paper.abstract?.replace(/\n/g, '<br>') || 'No abstract available.'}`;

    // PDF Link
    const pdfLinkEl = document.createElement('p');
    pdfLinkEl.className = 'detail-pdf';
    if (paper.pdf_url) {
        const pdfLink = document.createElement('a');
        pdfLink.href = paper.pdf_url;
        pdfLink.target = '_blank';
        pdfLink.rel = 'noopener noreferrer';
        pdfLink.textContent = 'Download PDF';
        pdfLinkEl.appendChild(document.createTextNode('PDF: '));
        pdfLinkEl.appendChild(pdfLink);
    } else {
        pdfLinkEl.textContent = 'PDF: Not available';
    }

    // Submitted Date
    const submittedEl = document.createElement('p');
    submittedEl.className = 'detail-submitted';
    const date = paper.submitted ? new Date(paper.submitted).toLocaleDateString() : 'Unknown';
    submittedEl.innerHTML = `<strong>Submitted:</strong> ${date}`;

    // BibTeX
    const bibtexEl = document.createElement('div');
    bibtexEl.className = 'detail-bibtex';
    bibtexEl.innerHTML = '<strong>BibTeX:</strong>';
    const pre = document.createElement('pre');
    pre.textContent = paper.bibtex || 'No BibTeX available.';
    pre.className = 'bibtex-content';
    bibtexEl.appendChild(pre);

    // Copy BibTeX Button
    const copyButton = document.createElement('button');
    copyButton.textContent = 'Copy BibTeX';
    copyButton.className = 'copy-bibtex-btn';
    copyButton.onclick = () => {
        const bibtexText = paper.bibtex || '';
        if (!bibtexText) {
            alert('No BibTeX to copy.');
            return;
        }
        navigator.clipboard.writeText(bibtexText)
            .then(() => {
                const originalText = copyButton.textContent;
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy BibTeX: ', err);
                alert('Failed to copy BibTeX. Please try again.');
            });
    };

    bibtexEl.appendChild(copyButton);

    // Assemble all elements
    container.appendChild(titleEl);
    container.appendChild(authorsEl);
    container.appendChild(abstractEl);
    container.appendChild(pdfLinkEl);
    container.appendChild(submittedEl);
    container.appendChild(bibtexEl);
}