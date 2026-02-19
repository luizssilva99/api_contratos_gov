/* ===== GovAnalytics - Dashboard JavaScript ===== */

// State
let currentPage = 1;
let currentDetailedPage = 1;
const perPage = 10;
let selectedStatuses = [];
let exportData = [];

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    showLoading();
    fetchData();
});

// ===== Loading =====
function showLoading() {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

// ===== Data Fetching =====
function buildQueryParams(page = 1) {
    const params = new URLSearchParams();

    const categoria = document.getElementById('filter-categoria')?.value;
    if (categoria) params.set('categoria', categoria);

    const departamento = document.getElementById('filter-departamento')?.value;
    if (departamento) params.set('departamento', departamento);

    selectedStatuses.forEach(s => params.append('status', s));

    const dataInicio = document.getElementById('filter-data-inicio')?.value;
    const dataFim = document.getElementById('filter-data-fim')?.value;
    if (dataInicio) params.set('data_inicio', dataInicio);
    if (dataFim) params.set('data_fim', dataFim);

    // Multi-select: Ano
    const anoSelect = document.getElementById('filter-ano');
    if (anoSelect) {
        Array.from(anoSelect.selectedOptions).forEach(o => params.append('ano', o.value));
    }

    // Multi-select: UF
    const ufSelect = document.getElementById('filter-uf');
    if (ufSelect) {
        Array.from(ufSelect.selectedOptions).forEach(o => params.append('uf', o.value));
    }

    params.set('page', page);
    params.set('per_page', perPage);

    return params.toString();
}

function fetchData(page = 1) {
    const qs = buildQueryParams(page);
    fetch(`/api/data/?${qs}`)
        .then(r => r.json())
        .then(data => {
            populateFilters(data.filter_options);
            updateKPIs(data.kpis);
            updateCharts(data.charts);
            updateTable(data.table);
            updateActiveFiltersBar();
            updateSidebarFooter(data.total_registros_base, data.metadata);
            exportData = data.export_data || [];
            hideLoading();
        })
        .catch(err => {
            console.error('Erro ao carregar dados:', err);
            hideLoading();
        });
}

// ===== Filters =====
let filtersPopulated = false;

function populateFilters(options) {
    if (filtersPopulated) return;
    filtersPopulated = true;

    // Categoria
    const catSelect = document.getElementById('filter-categoria');
    if (catSelect && options.categorias) {
        options.categorias.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            catSelect.appendChild(opt);
        });
        catSelect.addEventListener('change', () => { currentPage = 1; fetchData(1); });
    }

    // Departamento
    const deptSelect = document.getElementById('filter-departamento');
    if (deptSelect && options.departamentos) {
        options.departamentos.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d;
            opt.textContent = d;
            deptSelect.appendChild(opt);
        });
        deptSelect.addEventListener('change', () => { currentPage = 1; fetchData(1); });
    }

    // Status chips
    const statusContainer = document.getElementById('status-chips-container');
    if (statusContainer && options.statuses) {
        statusContainer.innerHTML = '';
        options.statuses.forEach(s => {
            const chip = document.createElement('span');
            chip.className = 'status-chip';
            chip.textContent = s;
            chip.dataset.status = s;
            chip.addEventListener('click', () => toggleStatus(s, chip));
            statusContainer.appendChild(chip);
        });
    }

    // Ano
    const anoSelect = document.getElementById('filter-ano');
    if (anoSelect && options.anos) {
        anoSelect.innerHTML = '';
        options.anos.forEach(a => {
            const opt = document.createElement('option');
            opt.value = a;
            opt.textContent = a;
            anoSelect.appendChild(opt);
        });
        anoSelect.addEventListener('change', () => { currentPage = 1; fetchData(1); });
    }

    // UF
    const ufSelect = document.getElementById('filter-uf');
    if (ufSelect && options.ufs) {
        ufSelect.innerHTML = '';
        options.ufs.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u;
            opt.textContent = u;
            ufSelect.appendChild(opt);
        });
        ufSelect.addEventListener('change', () => { currentPage = 1; fetchData(1); });
    }

    // Date filters
    document.getElementById('filter-data-inicio')?.addEventListener('change', () => { currentPage = 1; fetchData(1); });
    document.getElementById('filter-data-fim')?.addEventListener('change', () => { currentPage = 1; fetchData(1); });
}

function toggleStatus(status, chipEl) {
    const idx = selectedStatuses.indexOf(status);
    if (idx >= 0) {
        selectedStatuses.splice(idx, 1);
        chipEl.classList.remove('active');
    } else {
        selectedStatuses.push(status);
        chipEl.classList.add('active');
    }
    currentPage = 1;
    fetchData(1);
}

// ===== Active Filters Bar =====
function updateActiveFiltersBar() {
    const bar = document.getElementById('active-filters-bar');
    if (!bar) return;

    const filters = [];

    const cat = document.getElementById('filter-categoria')?.value;
    if (cat) filters.push({ label: `Tipo: ${cat}`, type: 'categoria' });

    const dept = document.getElementById('filter-departamento')?.value;
    if (dept) filters.push({ label: `Modalidade: ${dept}`, type: 'departamento' });

    selectedStatuses.forEach(s => {
        filters.push({ label: `Situação: ${s}`, type: 'status', value: s });
    });

    const di = document.getElementById('filter-data-inicio')?.value;
    const df = document.getElementById('filter-data-fim')?.value;
    if (di || df) {
        filters.push({ label: `Período: ${di || '...'} → ${df || '...'}`, type: 'data' });
    }

    const anoSel = document.getElementById('filter-ano');
    if (anoSel) {
        Array.from(anoSel.selectedOptions).forEach(o => {
            filters.push({ label: `Ano Assinatura: ${o.value}`, type: 'ano', value: o.value });
        });
    }

    const ufSel = document.getElementById('filter-uf');
    if (ufSel) {
        Array.from(ufSel.selectedOptions).forEach(o => {
            filters.push({ label: `UF Gestora: ${o.value}`, type: 'uf', value: o.value });
        });
    }

    if (filters.length === 0) {
        bar.innerHTML = `<span class="filters-bar-icon">📋</span><span class="filters-bar-label">Mostrando todos os registros</span>`;
        return;
    }

    let html = `<span class="filters-bar-icon">🔍</span><span class="filters-bar-label">Filtros Ativos:</span>`;
    filters.forEach((f, i) => {
        html += `<span class="filter-chip">${f.label} <span class="chip-x" onclick="removeFilter('${f.type}', '${f.value || ''}')">×</span></span>`;
    });
    html += `<span class="clear-all-link" onclick="clearAllFilters()">Limpar Todos</span>`;
    bar.innerHTML = html;
}

function removeFilter(type, value) {
    switch (type) {
        case 'categoria':
            document.getElementById('filter-categoria').value = '';
            break;
        case 'departamento':
            document.getElementById('filter-departamento').value = '';
            break;
        case 'status':
            const idx = selectedStatuses.indexOf(value);
            if (idx >= 0) selectedStatuses.splice(idx, 1);
            document.querySelectorAll('.status-chip').forEach(c => {
                if (c.dataset.status === value) c.classList.remove('active');
            });
            break;
        case 'data':
            document.getElementById('filter-data-inicio').value = '';
            document.getElementById('filter-data-fim').value = '';
            break;
        case 'ano':
            const anoSel = document.getElementById('filter-ano');
            Array.from(anoSel.options).forEach(o => { if (o.value === value) o.selected = false; });
            break;
        case 'uf':
            const ufSel = document.getElementById('filter-uf');
            Array.from(ufSel.options).forEach(o => { if (o.value === value) o.selected = false; });
            break;
    }
    currentPage = 1;
    fetchData(1);
}

function clearAllFilters() {
    document.getElementById('filter-categoria').value = '';
    document.getElementById('filter-departamento').value = '';
    document.getElementById('filter-data-inicio').value = '';
    document.getElementById('filter-data-fim').value = '';
    selectedStatuses = [];
    document.querySelectorAll('.status-chip').forEach(c => c.classList.remove('active'));
    const anoSel = document.getElementById('filter-ano');
    if (anoSel) Array.from(anoSel.options).forEach(o => o.selected = false);
    const ufSel = document.getElementById('filter-uf');
    if (ufSel) Array.from(ufSel.options).forEach(o => o.selected = false);
    currentPage = 1;
    fetchData(1);
}

// ===== KPIs =====
function formatCurrency(value) {
    return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function updateKPIs(kpis) {
    document.getElementById('kpi-valor-total-value').textContent = formatCurrency(kpis.valor_total);
    document.getElementById('kpi-contratos-value').textContent = kpis.total_contratos.toLocaleString('pt-BR');
    document.getElementById('kpi-bens-value').textContent = `${kpis.pct_bens}%`;
    document.getElementById('kpi-servicos-value').textContent = `${kpis.pct_servicos}%`;

    // Bars
    document.getElementById('kpi-bens-bar').style.width = `${kpis.pct_bens}%`;
    document.getElementById('kpi-servicos-bar').style.width = `${kpis.pct_servicos}%`;

    // YoY Badge
    const badge = document.getElementById('kpi-badge-yoy');
    if (kpis.variacao_yoy !== null && kpis.variacao_yoy !== undefined) {
        const sign = kpis.variacao_yoy >= 0 ? '+' : '';
        badge.textContent = `${sign}${kpis.variacao_yoy}%`;
        badge.className = `kpi-badge ${kpis.variacao_yoy >= 0 ? 'positive' : 'negative'}`;
    } else {
        badge.textContent = '—';
        badge.className = 'kpi-badge neutral';
    }
}

// ===== Charts =====
const chartColors = ['#2563EB', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#1D4ED8', '#3B82F6'];
const plotlyLayout = {
    font: { family: 'Inter, sans-serif', color: '#1E293B' },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 10, b: 30, l: 10, r: 10 },
};

function updateCharts(charts) {
    renderDonutChart(charts.tipo_distribuicao);
    renderUFChart(charts.uf_top);
    renderEvolutionChart(charts.evolucao);
}

function renderDonutChart(data) {
    const labels = Object.keys(data);
    const values = Object.values(data);

    const total = values.reduce((a, b) => a + b, 0);

    Plotly.newPlot('chart-donut', [{
        type: 'pie',
        labels: labels,
        values: values,
        hole: 0.6,
        marker: { colors: chartColors },
        textinfo: 'percent',
        textposition: 'outside',
        hovertemplate: '<b>%{label}</b><br>%{value} contratos<br>%{percent}<extra></extra>',
    }], {
        ...plotlyLayout,
        height: 300,
        showlegend: true,
        legend: { orientation: 'h', y: -0.15, font: { size: 11 } },
        annotations: [{
            text: `${total}<br><span style="font-size:11px;color:#94A3B8">Total</span>`,
            showarrow: false,
            font: { size: 18, family: 'Inter', color: '#1E293B', weight: 700 },
            x: 0.5, y: 0.5,
        }],
    }, { responsive: true, displayModeBar: false });
}

function renderUFChart(data) {
    const ufs = data.map(d => d.uf).reverse();
    const counts = data.map(d => d.count).reverse();

    Plotly.newPlot('chart-uf', [{
        type: 'bar',
        x: counts,
        y: ufs,
        orientation: 'h',
        marker: {
            color: chartColors.slice(0, data.length).reverse(),
            cornerradius: 4,
        },
        text: counts,
        textposition: 'outside',
        hovertemplate: '<b>%{y}</b>: %{x} contratos<extra></extra>',
    }], {
        ...plotlyLayout,
        height: 300,
        margin: { t: 10, b: 30, l: 100, r: 40 },
        xaxis: { showgrid: false, showticklabels: false, zeroline: false },
        yaxis: { showgrid: false, automargin: true },
    }, { responsive: true, displayModeBar: false });
}

function renderEvolutionChart(data) {
    const anos = data.map(d => d.ano);
    const qtds = data.map(d => d.qtd);

    Plotly.newPlot('chart-evolution', [{
        type: 'scatter',
        x: anos,
        y: qtds,
        mode: 'lines+markers',
        fill: 'tozeroy',
        fillcolor: 'rgba(37, 99, 235, 0.08)',
        line: { color: '#2563EB', width: 2.5, shape: 'spline' },
        marker: { color: '#2563EB', size: 6 },
        hovertemplate: '<b>%{x}</b>: %{y} contratos<extra></extra>',
    }], {
        ...plotlyLayout,
        height: 250,
        margin: { t: 10, b: 40, l: 50, r: 20 },
        xaxis: { showgrid: false, dtick: 1, title: '' },
        yaxis: { showgrid: true, gridcolor: '#E2E8F0', zeroline: false },
    }, { responsive: true, displayModeBar: false });
}

// ===== Table =====
function getStatusBadgeClass(status) {
    if (!status) return 'other';
    const s = status.toLowerCase();
    if (s.includes('ativo') || s.includes('vigente')) return 'ativo';
    if (s.includes('encerrado') || s.includes('concluído') || s.includes('concluido')) return 'encerrado';
    if (s.includes('cancelado') || s.includes('rescindido') || s.includes('rescisão')) return 'cancelado';
    return 'other';
}

// ===== Dias Vigência Color =====
function getDiasVigenciaHtml(dias) {
    if (dias === null || dias === undefined) {
        return '<span style="color:#94A3B8;font-weight:500">—</span>';
    }
    let color;
    if (dias <= 0) {
        color = '#DC2626'; // vermelho escuro - vencido
    } else if (dias <= 30) {
        color = '#EF4444'; // vermelho
    } else if (dias <= 60) {
        color = '#F97316'; // laranja
    } else if (dias <= 90) {
        color = '#FB923C'; // laranja claro
    } else if (dias <= 180) {
        color = '#EAB308'; // amarelo
    } else if (dias <= 365) {
        color = '#84CC16'; // verde claro
    } else {
        color = '#22C55E'; // verde
    }
    const label = dias <= 0 ? `${dias}d (vencido)` : `${dias}d`;
    return `<span style="color:${color};font-weight:600">${label}</span>`;
}

function updateTable(tableData) {
    const tbody = document.getElementById('table-body');
    const detailedTbody = document.getElementById('detailed-table-body');

    // Summary table
    if (tbody) {
        tbody.innerHTML = '';
        tableData.records.forEach(row => {
            const statusClass = getStatusBadgeClass(row.situacaoContrato);
            const valor = typeof row.valorInicialCompra === 'number'
                ? row.valorInicialCompra.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
                : row.valorInicialCompra;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td title="${row.nome_fornecedor || '-'}">${row.nome_fornecedor || '-'}</td>
                <td title="${row.objeto || '-'}">${(row.objeto || '-').substring(0, 60)}${(row.objeto || '').length > 60 ? '...' : ''}</td>
                <td>${valor}</td>
                <td>${row.dataAssinatura || '-'}</td>
                <td>${getDiasVigenciaHtml(row.dias_vigencia)}</td>
                <td><span class="status-badge ${statusClass}">${row.situacaoContrato || '-'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Detailed table
    if (detailedTbody) {
        detailedTbody.innerHTML = '';
        tableData.records.forEach(row => {
            const statusClass = getStatusBadgeClass(row.situacaoContrato);
            const valor = typeof row.valorInicialCompra === 'number'
                ? row.valorInicialCompra.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
                : row.valorInicialCompra;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.numero || '-'}</td>
                <td title="${row.nome_fornecedor || '-'}">${row.nome_fornecedor || '-'}</td>
                <td title="${row.objeto || '-'}">${(row.objeto || '-').substring(0, 50)}${(row.objeto || '').length > 50 ? '...' : ''}</td>
                <td>${valor}</td>
                <td>${row.tipo_contrato || '-'}</td>
                <td>${row.modalidadeCompra || '-'}</td>
                <td>${row.uf_gestora || '-'}</td>
                <td>${row.dataAssinatura || '-'}</td>
                <td><span class="status-badge ${statusClass}">${row.situacaoContrato || '-'}</span></td>
            `;
            detailedTbody.appendChild(tr);
        });
    }

    // Pagination (both tabs use same data)
    renderPagination('pagination', tableData.page, tableData.total_pages, false);
    renderPagination('detailed-pagination', tableData.page, tableData.total_pages, true);
    currentPage = tableData.page;
}

function renderPagination(containerId, page, totalPages, isDetailed) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <button class="pagination-btn" onclick="goToPage(${page - 1}, ${isDetailed})" ${page <= 1 ? 'disabled' : ''}>← Anterior</button>
        <span class="pagination-info">Página ${page} de ${totalPages}</span>
        <button class="pagination-btn" onclick="goToPage(${page + 1}, ${isDetailed})" ${page >= totalPages ? 'disabled' : ''}>Próxima →</button>
    `;
}

function goToPage(page, isDetailed) {
    if (page < 1) return;
    currentPage = page;
    showLoading();
    fetchData(page);
}

// ===== Tabs =====
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
}

// ===== Sidebar Footer =====
function updateSidebarFooter(totalRegistros, metadata) {
    const totalEl = document.getElementById('sidebar-total-registros');
    const updateEl = document.getElementById('sidebar-update-time');
    if (totalEl) totalEl.textContent = `${totalRegistros.toLocaleString('pt-BR')} registros carregados`;
    if (updateEl) updateEl.textContent = `Atualizado: ${metadata}`;
}

// ===== Export =====
function exportCSV() {
    if (!exportData || exportData.length === 0) {
        alert('Nenhum dado para exportar.');
        return;
    }

    const headers = Object.keys(exportData[0]);
    const csvRows = [headers.join(';')];

    exportData.forEach(row => {
        const values = headers.map(h => {
            let val = row[h] ?? '';
            val = String(val).replace(/"/g, '""');
            return `"${val}"`;
        });
        csvRows.push(values.join(';'));
    });

    const csvContent = '\uFEFF' + csvRows.join('\n'); // BOM for Excel
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `contratos_govanalytics_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}
