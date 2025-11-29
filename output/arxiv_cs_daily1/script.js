// output/arxiv_cs_daily/script.js

function getCategoryFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('cat');
}

function filterPapersByCategory(category) {
    if (!category) return [];
    return papers.filter(paper => paper.category.includes(category));
}

function renderPaperList(papersToRender, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (papersToRender.length === 0) {
        container.innerHTML = '<p>No papers found for this category.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'paper-list';

    papersToRender.forEach(paper => {
        const li = document.createElement('li');
        li.className = 'paper-item';
        li.innerHTML = `
            <h3><a href="detail.html?id=${encodeURIComponent(paper.id)}">${paper.title}</a></h3>
            <p class="authors">${paper.authors.join(', ')}</p>
        `;
        ul.appendChild(li);
    });

    container.appendChild(ul);
}

function renderPaperDetail(paperId, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const paper = papers.find(p => p.id === paperId);
    if (!paper) {
        container.innerHTML = '<p>Paper not found.</p>';
        return;
    }

    // Format the submitted date
    const date = new Date(paper.submitted);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Generate BibTeX citation
    const authorsForBibTeX = paper.authors.map(author => {
        const parts = author.split(' ');
        if (parts.length >= 2) {
            const lastName = parts[parts.length - 1];
            const firstNames = parts.slice(0, -1).join(' ');
            return `${lastName}, ${firstNames}`;
        }
        return author;
    }).join(' and ');

    const bibtex = `@article{${paper.id.replace(/[^a-zA-Z0-9]/g, '')},
  title={${paper.title}},
  author={${authorsForBibTeX}},
  journal={arXiv preprint arXiv:${paper.id.split('v')[0]}},
  year={${date.getFullYear()}},
  url={https://arxiv.org/abs/${paper.id.split('v')[0]}}
}`;

    container.innerHTML = `
        <div class="paper-detail">
            <h1>${paper.title}</h1>
            <p class="authors">by ${paper.authors.join(', ')}</p>
            <p class="submitted">Submitted on ${formattedDate}</p>
            <div class="abstract">
                <h2>Abstract</h2>
                <p>${paper.abstract}</p>
            </div>
            <div class="links">
                <a href="${paper.pdf_url}" target="_blank" rel="noopener">Download PDF</a>
            </div>
            <div class="bibtex-section">
                <h2>Citation</h2>
                <pre><code>${bibtex}</code></pre>
                <button id="copy-bibtex-btn">Copy BibTeX</button>
            </div>
        </div>
    `;

    // Add event listener to copy BibTeX
    const copyBtn = document.getElementById('copy-bibtex-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(bibtex).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy BibTeX: ', err);
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname.split('/').pop();

    if (currentPath === 'category.html') {
        const category = getCategoryFromUrl();
        if (category) {
            const filteredPapers = filterPapersByCategory(category);
            renderPaperList(filteredPapers, 'paper-list-container');
        } else {
            document.getElementById('paper-list-container').innerHTML = '<p>No category specified.</p>';
        }
    } else if (currentPath === 'detail.html') {
        const urlParams = new URLSearchParams(window.location.search);
        const paperId = urlParams.get('id');
        if (paperId) {
            renderPaperDetail(paperId, 'paper-detail-container');
        } else {
            document.getElementById('paper-detail-container').innerHTML = '<p>No paper ID specified.</p>';
        }
    }
});