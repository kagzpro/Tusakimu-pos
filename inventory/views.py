{% extends "base.html" %}
{% load static %}

{% block title %}Sales Report - Tusakimu Enterprises{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="mb-1">Sales Report</h2>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb mb-0">
                    <li class="breadcrumb-item"><a href="{% url 'inventory:dashboard' %}">Dashboard</a></li>
                    <li class="breadcrumb-item active">Sales Report</li>
                </ol>
            </nav>
        </div>
        <div class="btn-group">
            <button class="btn btn-success" onclick="exportReport()">
                <i class="fas fa-download"></i> Export CSV
            </button>
            <button class="btn btn-primary" onclick="window.print()">
                <i class="fas fa-print"></i> Print
            </button>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                Total Revenue
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">UGX {{ total_revenue|floatformat:0 }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-money-bill-wave fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-success shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                Total Cost
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">UGX {{ total_cost|floatformat:0 }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-chart-line fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-info shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                Total Profit
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">UGX {{ total_profit|floatformat:0 }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-chart-line fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                Profit Margin
                            </div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_margin|floatformat:1 }}%</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-percent fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="card-title mb-0">
                <i class="fas fa-filter"></i> Filter Sales
            </h5>
        </div>
        <div class="card-body">
            <form method="get" class="row g-3" id="filterForm">
                <div class="col-md-2">
                    <label class="form-label">Date From</label>
                    <input type="date" class="form-control" name="date_from" value="{{ date_from }}">
                </div>
                <div class="col-md-2">
                    <label class="form-label">Date To</label>
                    <input type="date" class="form-control" name="date_to" value="{{ date_to }}">
                </div>
                <div class="col-md-2">
                    <label class="form-label">Category</label>
                    <select class="form-select" name="category">
                        <option value="">All Categories</option>
                        {% for category in categories %}
                        <option value="{{ category.id }}" {% if category_id == category.id|stringformat:"i" %}selected{% endif %}>
                            {{ category.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Product Name</label>
                    <input type="text" class="form-control" name="product_name" value="{{ product_name }}" placeholder="Search product...">
                </div>
                <div class="col-md-2">
                    <label class="form-label">Customer</label>
                    <select class="form-select" name="customer">
                        <option value="">All Customers</option>
                        {% for customer in customers %}
                        <option value="{{ customer.id }}" {% if customer_id == customer.id|stringformat:"i" %}selected{% endif %}>
                            {{ customer.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Location</label>
                    <select class="form-select" name="location">
                        <option value="">All Locations</option>
                        {% for location in locations %}
                        <option value="{{ location.id }}" {% if location_id == location.id|stringformat:"i" %}selected{% endif %}>
                            {{ location.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-12">
                    <div class="btn-group">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-search"></i> Apply Filters
                        </button>
                        <a href="{% url 'inventory:sales_report' %}" class="btn btn-outline-secondary">
                            <i class="fas fa-times"></i> Clear Filters
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Product Sales Table -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="card-title mb-0">
                <i class="fas fa-boxes"></i> Product-wise Sales Analysis
            </h5>
        </div>
        <div class="card-body p-0">
            {% if product_sales %}
            <div class="table-responsive">
                <table class="table table-hover mb-0" id="productSalesTable">
                    <thead class="table-dark">
                        <tr>
                            <th>Product</th>
                            <th>SKU</th>
                            <th>Category</th>
                            <th class="text-center">Quantity Sold</th>
                            <th class="text-end">Revenue (UGX)</th>
                            <th class="text-end">Cost (UGX)</th>
                            <th class="text-end">Profit (UGX)</th>
                            <th class="text-center">Margin</th>
                            <th>Units Breakdown</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in product_sales %}
                        <tr>
                            <td>
                                <strong>{{ product.product.name }}</strong>
                                <br>
                                <small class="text-muted">Base: {{ product.product.base_unit }}</small>
                            </span>
                            <td><code>{{ product.product.sku }}</code></span>
                            <td>
                                {% if product.product.category %}
                                <span class="badge bg-light text-dark">{{ product.product.category.name }}</span>
                                {% else %}
                                <span class="text-muted">-</span>
                                {% endif %}
                            </span>
                            <td class="text-center">
                                <span class="badge bg-primary fs-6">{{ product.quantity|floatformat:0 }}</span>
                            </span>
                            <td class="text-end fw-bold text-success">UGX {{ product.revenue|floatformat:0 }}</span>
                            <td class="text-end text-muted">UGX {{ product.cost|floatformat:0 }}</span>
                            <td class="text-end fw-bold text-info">UGX {{ product.profit|floatformat:0 }}</span>
                            <td class="text-center">
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar {% if product.margin > 30 %}bg-success{% elif product.margin > 15 %}bg-info{% else %}bg-warning{% endif %}" 
                                         role="progressbar" 
                                         style="width: {{ product.margin|floatformat:0 }}%;"
                                         aria-valuenow="{{ product.margin|floatformat:0 }}" 
                                         aria-valuemin="0" 
                                         aria-valuemax="100">
                                        {{ product.margin|floatformat:0 }}%
                                    </div>
                                </div>
                            </span>
                            <td>
                                {% for unit_name, unit_data in product.units_sold.items %}
                                <span class="badge bg-secondary me-1 mb-1">
                                    {{ unit_name|title }}: {{ unit_data.quantity|floatformat:0 }} 
                                    (UGX {{ unit_data.revenue|floatformat:0 }})
                                </span>
                                {% endfor %}
                            </span>
                        </tr>
                        {% endfor %}
                    </tbody>
                    <tfoot class="table-light">
                        <tr class="fw-bold">
                            <td colspan="3" class="text-end">Totals:</td>
                            <td class="text-center">{{ total_quantity|floatformat:0 }}</td>
                            <td class="text-end text-success">UGX {{ total_revenue|floatformat:0 }}</td>
                            <td class="text-end">UGX {{ total_cost|floatformat:0 }}</td>
                            <td class="text-end text-info">UGX {{ total_profit|floatformat:0 }}</td>
                            <td class="text-center">{{ total_margin|floatformat:1 }}%</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            {% else %}
            <div class="text-center py-5">
                <div class="mb-4">
                    <i class="fas fa-chart-line fa-4x text-muted"></i>
                </div>
                <h5 class="text-muted">No sales data found</h5>
                <p class="text-muted">Try adjusting your filters or create some sales first.</p>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Unit Summary Card -->
    {% if unit_summary %}
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="card-title mb-0">
                <i class="fas fa-balance-scale"></i> Unit-wise Sales Summary
            </h5>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Product</th>
                            <th>Unit</th>
                            <th class="text-center">Quantity Sold</th>
                            <th class="text-end">Revenue (UGX)</th>
                            <th class="text-end">Base Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for key, unit in unit_summary.items %}
                        <tr>
                            <td>{{ unit.product_name }}</span>
                            <td><span class="badge bg-info">{{ unit.unit_name|title }}</span></span>
                            <td class="text-center">{{ unit.quantity_sold|floatformat:0 }}</span>
                            <td class="text-end">UGX {{ unit.revenue|floatformat:0 }}</span>
                            <td class="text-end">{{ unit.base_quantity|floatformat:0 }} base units</span>
                        </tr>
                        {% endfor %}
                    </tbody>
                    <tfoot class="table-light">
                        <tr class="fw-bold">
                            <td colspan="2" class="text-end">Totals:</td>
                            <td class="text-center">{{ total_quantity|floatformat:0 }}</td>
                            <td class="text-end">UGX {{ total_revenue|floatformat:0 }}</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Payment Methods Summary -->
    {% if payment_method_summary %}
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="card-title mb-0">
                <i class="fas fa-credit-card"></i> Payment Methods Summary
            </h5>
        </div>
        <div class="card-body">
            <div class="row">
                {% for method, data in payment_method_summary.items %}
                <div class="col-md-3 mb-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <i class="fas 
                                {% if 'Cash' in method %}fa-money-bill-wave
                                {% elif 'Mobile' in method %}fa-mobile-alt
                                {% elif 'Card' in method %}fa-credit-card
                                {% elif 'Bank' in method %}fa-university
                                {% else %}fa-receipt{% endif %} 
                                fa-2x text-primary mb-2"></i>
                            <h6 class="mb-1">{{ method }}</h6>
                            <p class="mb-0">
                                <strong>{{ data.count }}</strong> transactions
                            </p>
                            <p class="mb-0 text-success">
                                UGX {{ data.total_amount|floatformat:0 }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endif %}
</div>

<script>
function exportReport() {
    // Get current filter parameters
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'csv');
    
    window.location.href = `/inventory/sales-report/export/?${params.toString()}`;
}

// Optional: Add chart functionality
document.addEventListener('DOMContentLoaded', function() {
    // You can add Chart.js here for visualizations if desired
    console.log('Sales report loaded');
});

// Print functionality
function printReport() {
    window.print();
}
</script>

<style>
.card.border-left-primary { border-left: 4px solid #4e73df !important; }
.card.border-left-success { border-left: 4px solid #1cc88a !important; }
.card.border-left-info { border-left: 4px solid #36b9cc !important; }
.card.border-left-warning { border-left: 4px solid #f6c23e !important; }

.progress {
    border-radius: 10px;
    background-color: #e9ecef;
}

.progress-bar {
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: bold;
    line-height: 20px;
}

.table-responsive {
    overflow-x: auto;
}

@media print {
    .btn-group, .card-header .btn, #filterForm, .btn {
        display: none !important;
    }
    .card {
        border: none !important;
        box-shadow: none !important;
        page-break-inside: avoid;
    }
    .progress {
        border: 1px solid #ddd;
    }
    .progress-bar {
        background-color: #ddd !important;
        color: #000 !important;
    }
}
</style>
{% endblock %}
