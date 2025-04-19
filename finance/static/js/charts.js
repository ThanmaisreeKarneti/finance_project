document.addEventListener("DOMContentLoaded", function () {
    try {
        const barElement = document.getElementById("bargraph");
        const pieElement = document.getElementById("pieChart");
        const lineElement = document.getElementById("linegraph");

        if (!barElement || !pieElement || !lineElement) {
            throw new Error("Missing chart elements");
        }

        const barLabels = JSON.parse(barElement.dataset.labels);
        const barData = JSON.parse(barElement.dataset.values);

        const pieLabels = JSON.parse(pieElement.dataset.labels);
        const pieData = JSON.parse(pieElement.dataset.values);

        const lineLabels = JSON.parse(lineElement.dataset.labels);
        const lineData = JSON.parse(lineElement.dataset.values);

        // Bar Chart
        new Chart(barElement.getContext("2d"), {
            type: 'bar',
            data: {
                labels: barLabels,
                datasets: [{
                    label: 'Expenses per Month',
                    data: barData,
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                }
            }
        });

        // Pie Chart
        new Chart(pieElement.getContext("2d"), {
            type: 'pie',
            data: {
                labels: pieLabels,
                datasets: [{
                    data: pieData,
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ₹${value}`;
                            }
                        }
                    }
                }
            }
        });

        // Line Chart (Modified for Last  Months)
        new Chart(lineElement.getContext("2d"), {
            type: 'line',
            data: {
                labels: lineLabels, // Use last  months labels
                datasets: [{
                    label: 'Expenses for Last  Months',
                    data: lineData, // Use expenses data for last  months
                    fill: false,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                }
            }
        });

    } catch (e) {
        console.error("Error loading charts:", e);
    }
});
