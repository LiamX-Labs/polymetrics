// Polymetrics Charts JavaScript
// Chart data and positions data are injected by the template's extra_scripts block
// chartData and allPositionsData variables are defined in the template

let currentPage = 1;
const rowsPerPage = 50;
let filteredData = [];

// Global Plotly layout configuration for dark theme
const darkLayout = {
    paper_bgcolor: 'rgba(0, 0, 0, 0)',
    plot_bgcolor: 'rgba(255, 255, 255, 0.02)',
    font: {
        color: '#E5E7EB',
        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif'
    },
    xaxis: {
        gridcolor: 'rgba(124, 58, 237, 0.1)',
        zerolinecolor: 'rgba(124, 58, 237, 0.2)',
        color: '#9CA3AF'
    },
    yaxis: {
        gridcolor: 'rgba(124, 58, 237, 0.1)',
        zerolinecolor: 'rgba(124, 58, 237, 0.2)',
        color: '#9CA3AF'
    },
    hoverlabel: {
        bgcolor: 'rgba(15, 10, 30, 0.9)',
        bordercolor: 'rgba(124, 58, 237, 0.5)',
        font: {color: '#E5E7EB'}
    }
};

const plotConfig = {
    responsive: true,
    displayModeBar: false
};

// Tab switching
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    // Initialize charts when Charts tab is opened
    if (tabName === 'charts') {
        initializeCharts();
    } else if (tabName === 'overview') {
        initializeOverviewCharts();
    }
}

// Initialize overview charts (smaller versions)
function initializeOverviewCharts() {
    if (typeof chartData === 'undefined' || !chartData || !chartData.cumulative_pnl) {
        console.log('No chart data available for overview');
        return;
    }

    // Mini Cumulative PnL
    const cumulativePnlMini = {
        x: chartData.cumulative_pnl.timestamps,
        y: chartData.cumulative_pnl.values,
        type: 'scatter',
        mode: 'lines',
        line: {color: '#7C3AED', width: 2},
        fill: 'tozeroy',
        fillcolor: 'rgba(124, 58, 237, 0.1)'
    };

    Plotly.newPlot('cumulative-pnl-mini', [cumulativePnlMini], {
        ...darkLayout,
        margin: {t: 10, r: 10, b: 40, l: 60},
        height: 300,
        xaxis: {...darkLayout.xaxis, title: 'Date'},
        yaxis: {...darkLayout.yaxis, title: 'Cumulative PnL ($)'},
        hovermode: 'x unified'
    }, plotConfig);

    // Mini Win/Loss Pie
    const winLossPieMini = {
        values: chartData.win_loss.values,
        labels: chartData.win_loss.labels,
        type: 'pie',
        marker: {colors: ['#10B981', '#EF4444', '#F97316']},
        textinfo: 'label+percent',
        hole: 0.4
    };

    Plotly.newPlot('win-loss-pie-mini', [winLossPieMini], {
        ...darkLayout,
        margin: {t: 10, r: 10, b: 10, l: 10},
        height: 300,
        showlegend: true
    }, plotConfig);
}

// Initialize all charts
function initializeCharts() {
    if (typeof chartData === 'undefined' || !chartData || !chartData.cumulative_pnl) {
        console.log('No chart data available');
        return;
    }

    // 1. Cumulative PnL
    const cumulativePnl = {
        x: chartData.cumulative_pnl.timestamps,
        y: chartData.cumulative_pnl.values,
        type: 'scatter',
        mode: 'lines',
        line: {color: '#7C3AED', width: 3},
        fill: 'tozeroy',
        fillcolor: 'rgba(124, 58, 237, 0.1)',
        name: 'Cumulative PnL'
    };

    Plotly.newPlot('cumulative-pnl', [cumulativePnl], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Date', showgrid: true},
        yaxis: {...darkLayout.yaxis, title: 'Cumulative PnL ($)', showgrid: true},
        hovermode: 'x unified'
    }, plotConfig);

    // 2. Win/Loss Pie
    const winLossPie = {
        values: chartData.win_loss.values,
        labels: chartData.win_loss.labels,
        type: 'pie',
        marker: {colors: ['#10B981', '#EF4444', '#F97316']},
        textinfo: 'label+percent',
        hole: 0.4
    };

    Plotly.newPlot('win-loss-pie', [winLossPie], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 20, l: 20},
        height: 400,
        showlegend: true
    }, plotConfig);

    // 3. PnL Histogram
    const pnlHist = {
        x: chartData.pnl_distribution,
        type: 'histogram',
        marker: {color: '#F97316'},
        nbinsx: 30
    };

    Plotly.newPlot('pnl-histogram', [pnlHist], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Realized PnL ($)'},
        yaxis: {...darkLayout.yaxis, title: 'Frequency'},
        shapes: [{
            type: 'line',
            x0: 0, x1: 0,
            y0: 0, y1: 1,
            yref: 'paper',
            line: {color: '#EF4444', width: 2, dash: 'dash'}
        }]
    }, plotConfig);

    // 4. Outcome Bar Chart
    const outcomeBar = {
        x: chartData.outcome_pnl.outcomes,
        y: chartData.outcome_pnl.values,
        type: 'bar',
        marker: {color: chartData.outcome_pnl.values.map(v => v >= 0 ? '#10B981' : '#EF4444')}
    };

    Plotly.newPlot('outcome-bar', [outcomeBar], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Outcome'},
        yaxis: {...darkLayout.yaxis, title: 'Total PnL ($)'}
    }, plotConfig);

    // 5. Hourly PnL
    const hourlyBar = {
        x: chartData.hourly_pnl.hours,
        y: chartData.hourly_pnl.values,
        type: 'bar',
        marker: {color: '#7C3AED'}
    };

    Plotly.newPlot('hourly-bar', [hourlyBar], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Hour (UTC)', tickmode: 'linear'},
        yaxis: {...darkLayout.yaxis, title: 'Total PnL ($)'},
        shapes: [{
            type: 'line',
            x0: -0.5, x1: 23.5,
            y0: 0, y1: 0,
            line: {color: '#EF4444', width: 1, dash: 'dash'}
        }]
    }, plotConfig);

    // 6. Position Size Distribution
    const positionSizeHist = {
        x: chartData.position_sizes,
        type: 'histogram',
        marker: {color: '#7C3AED'},
        nbinsx: 25
    };

    Plotly.newPlot('position-size-hist', [positionSizeHist], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Position Size (shares)'},
        yaxis: {...darkLayout.yaxis, title: 'Frequency'}
    }, plotConfig);

    // 7. ROI Distribution
    const roiHist = {
        x: chartData.roi_distribution,
        type: 'histogram',
        marker: {color: '#F97316'},
        nbinsx: 30
    };

    Plotly.newPlot('roi-histogram', [roiHist], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'ROI (%)'},
        yaxis: {...darkLayout.yaxis, title: 'Frequency'},
        shapes: [{
            type: 'line',
            x0: 0, x1: 0,
            y0: 0, y1: 1,
            yref: 'paper',
            line: {color: '#E5E7EB', width: 2}
        }]
    }, plotConfig);

    // 8. Drawdown Chart
    const drawdownTrace = {
        x: Array.from({length: chartData.drawdown.length}, (_, i) => i),
        y: chartData.drawdown,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: 'rgba(239, 68, 68, 0.3)',
        line: {color: '#EF4444', width: 2}
    };

    Plotly.newPlot('drawdown-chart', [drawdownTrace], {
        ...darkLayout,
        margin: {t: 20, r: 20, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Position Number'},
        yaxis: {...darkLayout.yaxis, title: 'Drawdown ($)'}
    }, plotConfig);

    // 9. Entry Price vs PnL Scatter
    const entryPnlScatter = {
        x: chartData.entry_vs_pnl.entry_prices,
        y: chartData.entry_vs_pnl.pnl,
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 8,
            color: chartData.entry_vs_pnl.pnl,
            colorscale: [[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
            showscale: true,
            colorbar: {title: 'PnL ($)', tickfont: {color: '#E5E7EB'}, titlefont: {color: '#E5E7EB'}}
        }
    };

    Plotly.newPlot('entry-pnl-scatter', [entryPnlScatter], {
        ...darkLayout,
        margin: {t: 20, r: 80, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Average Entry Price ($)'},
        yaxis: {...darkLayout.yaxis, title: 'Realized PnL ($)'},
        shapes: [{
            type: 'line',
            x0: 0, x1: 1,
            xref: 'paper',
            y0: 0, y1: 0,
            line: {color: '#EF4444', width: 1, dash: 'dash'}
        }]
    }, plotConfig);

    // 10. Position Size vs PnL Scatter
    const sizePnlScatter = {
        x: chartData.size_vs_pnl.sizes,
        y: chartData.size_vs_pnl.pnl,
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 8,
            color: chartData.size_vs_pnl.pnl,
            colorscale: [[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
            showscale: true,
            colorbar: {title: 'PnL ($)', tickfont: {color: '#E5E7EB'}, titlefont: {color: '#E5E7EB'}}
        }
    };

    Plotly.newPlot('size-pnl-scatter', [sizePnlScatter], {
        ...darkLayout,
        margin: {t: 20, r: 80, b: 60, l: 70},
        height: 400,
        xaxis: {...darkLayout.xaxis, title: 'Position Size (shares)'},
        yaxis: {...darkLayout.yaxis, title: 'Realized PnL ($)'},
        shapes: [{
            type: 'line',
            x0: 0, x1: 1,
            xref: 'paper',
            y0: 0, y1: 0,
            line: {color: '#EF4444', width: 1, dash: 'dash'}
        }]
    }, plotConfig);
}

// Table filtering
function filterPositions() {
    const searchTerm = document.getElementById('search-positions').value.toLowerCase();
    filteredData = allPositionsData.filter(row => {
        return Object.values(row).some(val =>
            String(val).toLowerCase().includes(searchTerm)
        );
    });
    currentPage = 1;
    renderTable();
    renderPagination();
}

// Render table with pagination
function renderTable() {
    if (typeof allPositionsData === 'undefined' || !allPositionsData) {
        console.log('No positions data available');
        return;
    }

    if (filteredData.length === 0) {
        filteredData = allPositionsData;
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = filteredData.slice(start, end);

    const tbody = document.getElementById('positions-tbody');
    if (!tbody) return;

    tbody.innerHTML = pageData.map(row => `
        <tr>
            <td>${row.timestamp}</td>
            <td>${row.market}</td>
            <td>${row.outcome}</td>
            <td>$${row.entry_price}</td>
            <td>${row.size}</td>
            <td>$${row.exit_price}</td>
            <td>${row.trades}</td>
            <td class="${row.pnl >= 0 ? 'positive-value' : 'negative-value'}">$${row.pnl.toFixed(2)}</td>
            <td class="${row.roi >= 0 ? 'positive-value' : 'negative-value'}">${row.roi.toFixed(2)}%</td>
        </tr>
    `).join('');
}

// Render pagination controls
function renderPagination() {
    if (typeof allPositionsData === 'undefined' || !allPositionsData) {
        return;
    }

    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
    const pagination = document.getElementById('pagination');
    if (!pagination) return;

    let html = '';
    html += `<button onclick="changePage(1)" ${currentPage === 1 ? 'disabled' : ''}>First</button>`;
    html += `<button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>`;

    // Show page numbers (with ellipsis for large page counts)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        html += `<button onclick="changePage(1)">1</button>`;
        if (startPage > 2) html += `<span style="padding: 8px;">...</span>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button onclick="changePage(${i})" class="${i === currentPage ? 'active' : ''}">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<span style="padding: 8px;">...</span>`;
        html += `<button onclick="changePage(${totalPages})">${totalPages}</button>`;
    }

    html += `<button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
    html += `<button onclick="changePage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>Last</button>`;

    pagination.innerHTML = html;
}

// Change page
function changePage(page) {
    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTable();
    renderPagination();
    window.scrollTo({top: 0, behavior: 'smooth'});
}
