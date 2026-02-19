/* ===== GovAnalytics - Dashboard JavaScript ===== */

// State
let currentPage = 1;
let currentDetailedPage = 1;
// const perPage = 25; // Removed in favor of dynamic per-tab limit
let activeTab = 'visao-geral';
let selectedStatuses = [];
let exportData = [];

// Column Configuration (Friendly Names & Tooltips)
// Column Configuration (Friendly Names & Tooltips & Widths)
const COLUMN_CONFIG = {
    'id': { label: 'ID', title: 'Identificador único do registro', width: '60px' },
    'numero': { label: 'Nº Contrato', title: 'Número do contrato', width: '120px' },
    'numeroProcesso': { label: 'Nº Processo', title: 'Número do processo administrativo', width: '150px' },
    'nome_fornecedor': { label: 'Fornecedor', title: 'Nome/Razão Social do fornecedor', width: '250px' },
    'fornecedor_nome': { label: 'Fornecedor (Nome)', title: 'Nome do fornecedor', width: '250px' },
    'objeto': { label: 'Objeto', title: 'Descrição do objeto contratado', width: '350px' },
    'valorInicialCompra': { label: 'Valor Inicial (R$)', title: 'Valor inicial da contratação', width: '130px' },
    'valorFinalCompra': { label: 'Valor Final (R$)', title: 'Valor final após aditivos', width: '130px' },
    'diferenca_valor': { label: 'Diferença (R$)', title: 'Variação entre valor final e inicial', width: '130px' },
    'dataAssinatura': { label: 'Data Assinatura', title: 'Data de assinatura do contrato', width: '110px' },
    'dataInicioVigencia': { label: 'Início Vigência', title: 'Data de início da vigência', width: '110px' },
    'dataFimVigencia': { label: 'Fim Vigência', title: 'Data de fim da vigência', width: '110px' },
    'dias_vigencia': { label: 'Dias Restantes', title: 'Dias até o fim da vigência', width: '100px' },
    'situacaoContrato': { label: 'Situação', title: 'Situação atual do contrato', width: '140px' },
    'tipo_contrato': { label: 'Tipo', title: 'Classificação do contrato', width: '160px' },
    'modalidadeCompra': { label: 'Modalidade', title: 'Modalidade de licitação/compra', width: '180px' },
    'uf_gestora': { label: 'UF', title: 'Unidade Federativa Gestora', width: '60px' },
    'ano_assinatura': { label: 'Ano', title: 'Ano de assinatura', width: '70px' },
    'fundamentoLegal': { label: 'Fundamento Legal', title: 'Base legal da contratação', width: '200px' },
    'uasg': { label: 'UASG', title: 'Código da Unidade Administrativa de Serviços Gerais', width: '90px' },
    'dataPublicacaoDOU': { label: 'Publicação DOU', title: 'Data de publicação no Diário Oficial', width: '110px' },
    'ug_nome': { label: 'Unidade Gestora', title: 'Nome da Unidade Gestora', width: '220px' },
    'ug_orgao_vinculado': { label: 'Órgão Vinculado', title: 'Órgão superior vinculado', width: '220px' },
    'ug_codigo': { label: 'Cód. UG', title: 'Código da Unidade Gestora', width: '100px' },
    'fornecedor_cnpjFormatado': { label: 'CNPJ', title: 'CNPJ do fornecedor', width: '140px' },
    'compra_numero': { label: 'Nº Compra', title: 'Número da compra', width: '120px' }
};

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
    const pPage = (activeTab === 'dados-detalhados') ? 25 : 10;
    params.set('per_page', pPage);

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

function formatCurrency(val) {
    if (val === null || val === undefined || val === '') return '-';
    const num = parseFloat(val);
    if (isNaN(num)) return val;
    return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function getDiferencaHtml(val) {
    if (val === null || val === undefined || val === 0) {
        return '<span style="color:#94A3B8;font-weight:500">—</span>';
    }
    const color = val > 0 ? '#EF4444' : '#22C55E'; // Vermelho se aumentou, Verde se diminuiu (economia)
    // Val > 0 means Final > Initial (Start Low, End High -> Bad?)
    // Context: "Valor Final Compra" vs "Valor Inicial". Increase might be additive.
    // Let's use neutral or standard accounting.
    // If it's a cost, increase is bad (red), decrease is good (green).
    // Assuming context of public contracts.
    const formatted = val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    const sign = val > 0 ? '+' : '';
    return `<span style="color:${color};font-weight:600">${sign}${formatted}</span>`;
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
            const valorIni = formatCurrency(row.valorInicialCompra);
            const valorFim = formatCurrency(row.valorFinalCompra);

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td title="${row.nome_fornecedor || '-'}">${row.nome_fornecedor || '-'}</td>
                <td title="${row.objeto || '-'}">${row.objeto || '-'}</td>
                <td>${valorIni}</td>
                <td>${valorFim}</td>
                <td>${getDiferencaHtml(row.diferenca_valor)}</td>
                <td>${row.dataAssinatura || '-'}</td>
                <td>${row.dataFimVigencia || '-'}</td>
                <td>${getDiasVigenciaHtml(row.dias_vigencia)}</td>
                <td><span class="status-badge ${statusClass}">${row.situacaoContrato || '-'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Detailed table (Dynamic Columns)
    if (detailedTbody) {
        const thead = document.querySelector('#detailed-table thead');
        const columns = tableData.columns || Object.keys(tableData.records[0] || {});

        // Rebuild header
        if (thead) {
            let headerHtml = '<tr>';
            columns.forEach(col => {
                const config = COLUMN_CONFIG[col] || { label: col, title: col, width: '150px' };
                headerHtml += `<th title="${config.title}" style="min-width: ${config.width}">${config.label}</th>`;
            });
            headerHtml += '</tr>';
            thead.innerHTML = headerHtml;
        }

        detailedTbody.innerHTML = '';
        let detailedRows = ''; // Accumulate rows
        tableData.records.forEach(row => {
            let rowHtml = '<tr>';
            columns.forEach(col => {
                let val = row[col];
                // Simple formatting for known types
                if (typeof val === 'number') {
                    // Heuristic for money columns
                    if (col.toLowerCase().includes('valor') && !col.toLowerCase().includes('id')) {
                        val = formatCurrency(val);
                    } else {
                        val = val.toString();
                    }
                }
                if (val === null || val === undefined) val = '-';
                rowHtml += `<td title="${val}">${val.toString().substring(0, 100)}${val.toString().length > 100 ? '...' : ''}</td>`;
            });
            rowHtml += '</tr>';
            detailedRows += rowHtml;
        });
        detailedTbody.innerHTML = detailedRows;
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
// ===== Tabs =====
function switchTab(tabName) {
    if (activeTab === tabName) return;
    activeTab = tabName;

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });

    // Reload data to respect new per_page limit (10 vs 25)
    currentPage = 1;
    fetchData(1);
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
