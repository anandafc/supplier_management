/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class SupplierDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            supplierId: false,
            dateRange: 'this_month',
            dashboardData: {
                approvedRfqCount: 0,
                totalAmount: 0,
                productBreakdown: {},
                productImages: {},
            },
            suppliers: [],
        });

        this.chartInstances = {};  // Store chart instances to manage destruction
        this.loadInitialData();
    }

    async loadInitialData() {
        // Load suppliers
        const suppliers = await this.orm.searchRead(
            'res.partner',
            [['supplier_rank', '>', 0]],
            ['id', 'name']
        );
        this.state.suppliers = suppliers;

        // Load initial dashboard data
        await this.loadDashboardData();
    }

    async loadDashboardData() {
        const data = {
            supplier_id: this.state.supplierId,
            date_range: this.state.dateRange,
        };

        // Create the dashboard record with current filters
        const dashboardIds = await this.orm.create('supplier_management.dashboard', [data]);

        // Check if the record creation is successful and valid
        if (dashboardIds && dashboardIds.length > 0) {
            const dashboardId = dashboardIds[0];  // Assuming the result is an array with the created record's ID
            const response = await this.orm.read('supplier_management.dashboard', [dashboardId], [
                'approved_rfq_count',
                'total_amount',
                'product_breakdown'
            ]);

            if (response.length) {
                this.state.dashboardData = {
    approvedRfqCount: response[0].approved_rfq_count,
    totalAmount: response[0].total_amount,
    productBreakdown: response[0].product_breakdown && response[0].product_breakdown !== ""
        ? JSON.parse(response[0].product_breakdown)
        : {},
    productImages: {},  // Ensure productImages is initialized as an empty object
};
                // Fetch product images based on product names in the breakdown
                await this.loadProductImages(Object.keys(this.state.dashboardData.productBreakdown));
                this.renderCharts();  // Call the function to render charts
            }
        } else {
            console.error("Dashboard creation failed or returned invalid IDs");
        }
    }
    async loadProductImages(products) {
        // Fetch product images for the products in the breakdown
        const productImages = {};
        for (const productName of products) {
            const product = await this.orm.searchRead('product.product', [['name', '=', productName]], ['name', 'image_1920']);
            if (product && product.length > 0 && product[0].image_1920) {
                // Convert image_1920 to a URL
                const imageUrl = `data:image/png;base64,${product[0].image_1920}`;
                productImages[productName] = imageUrl;
            } else {
                // If no image, use a placeholder image
                productImages[productName] = '/web/static/src/img/placeholder.png';
            }
        }
        // Store the fetched images
        this.state.dashboardData.productImages = productImages;
    }


    renderCharts() {
        // Destroy the existing charts before creating new ones
        if (this.chartInstances.approvedRfqChart) {
            this.chartInstances.approvedRfqChart.destroy();
        }

        if (this.chartInstances.productBreakdownChart) {
            this.chartInstances.productBreakdownChart.destroy();
        }

        // Render Approved RFQs Chart (Bar Chart)
        const approvedRfqChartElement = document.getElementById('approvedRfqChart');
        if (approvedRfqChartElement) {
            const approvedRfqChartCtx = approvedRfqChartElement.getContext('2d');
            this.chartInstances.approvedRfqChart = new Chart(approvedRfqChartCtx, {
                type: 'bar',
                data: {
                    labels: ['Approved RFQs'], // Label for the chart
                    datasets: [{
                        label: 'Approved RFQs',
                        data: [this.state.dashboardData.approvedRfqCount], // Approved RFQ count value
                        backgroundColor: '#36a2eb', // Bar color
                        borderColor: '#4e73df', // Border color
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Render Product Breakdown Chart (Pie Chart)
        const productBreakdownChartElement = document.getElementById('productBreakdownChart');
        if (productBreakdownChartElement) {
            const productBreakdownChartCtx = productBreakdownChartElement.getContext('2d');
            const productNames = Object.keys(this.state.dashboardData.productBreakdown);
            const productQuantities = Object.values(this.state.dashboardData.productBreakdown);

            this.chartInstances.productBreakdownChart = new Chart(productBreakdownChartCtx, {
                type: 'pie',
                data: {
                    labels: productNames,  // Labels from product names
                    datasets: [{
                        label: 'Product Breakdown',
                        data: productQuantities, // Quantities for each product
                        backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'], // Pie slice colors
                        hoverBackgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    return tooltipItem.label + ': ' + tooltipItem.raw + ' units';
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    onSupplierChange(ev) {
        this.state.supplierId = parseInt(ev.target.value) || false;
        this.loadDashboardData();
    }

    onDateRangeChange(ev) {
        this.state.dateRange = ev.target.value;
        this.loadDashboardData();
    }

    static template = 'supplier_management.SupplierDashboard';
}

registry.category("actions").add("supplier_dashboard", SupplierDashboard);
