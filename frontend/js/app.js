
document.addEventListener("DOMContentLoaded", () => {
    loadData();
});

async function loadData() {
    try {
        // KPIs
        const kpis = await fetch("/api/kpis").then(r => r.json());
        renderKPIs(kpis);

        // Revenue trend (default)
        const trend = await fetch("/api/revenue-trend").then(r => r.json());
        renderChart(trend);

        // Segments
        const segments = await fetch("/api/segments").then(r => r.json());
        renderSegments(segments);

        // Insights
        const insights = await fetch("/api/insights").then(r => r.json());
        renderInsights(insights);

        // Top products
        const products = await fetch("/api/top-products").then(r => r.json());
        renderTopProducts(products);

    } catch (e) {
        console.error("Error:", e);
    }
}

// KPI
function renderKPIs(data) {
    const grid = document.getElementById("kpi-grid");
    grid.innerHTML = "";

    const list = [
        ["Revenue", "$" + data.revenue.value],
        ["Orders", data.orders.value],
        ["Customers", data.customers.value],
        ["AOV", "$" + data.aov.value]
    ];

    list.forEach(k => {
        const div = document.createElement("div");
        div.className = "bg-slate-900 p-4 rounded";

        div.innerHTML = `
            <p>${k[0]}</p>
            <h2>${k[1]}</h2>
        `;

        grid.appendChild(div);
    });
}

// Chart
function renderChart(data) {
    const ctx = document.getElementById("revenueChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: "Revenue",
                    data: data.values,
                    borderColor: "blue"
                },
                {
                    label: "Forecast",
                    data: data.forecast,
                    borderColor: "purple"
                }
            ]
        }
    });
}

// Segments
function renderSegments(data) {
    const ctx = document.getElementById("segmentsChart").getContext("2d");

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values
            }]
        }
    });
}

// Insights
function renderInsights(data) {
    const container = document.getElementById("insights-container");
    container.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");

        div.className = "bg-slate-900 p-3 rounded";

        div.innerHTML = `
            <h4>${item.title}</h4>
            <p>${item.message}</p>
        `;

        container.appendChild(div);
    });
}

// Products
function renderTopProducts(data) {
    const container = document.getElementById("top-products-container");
    container.innerHTML = "";

    data.forEach(p => {
        const div = document.createElement("div");

        div.className = "bg-slate-900 p-2 rounded";

        div.innerHTML = `
            ${p.product_name} - $${p.revenue}
        `;

        container.appendChild(div);
    });
}

