# Grafana Dashboard Import Instructions

## Quick Import

1. **Open Grafana** in your browser (usually http://localhost:3000)

2. **Navigate to Dashboards** → **Import**

3. **Import each dashboard file:**

### Overview Dashboard
1. Click **Upload JSON file**
2. Select: `output/dashboards/overview-dashboard.json`
3. Click **Import**

### Python Services Dashboard
1. Click **Upload JSON file**
2. Select: `output/dashboards/python-services-dashboard.json`
3. Click **Import**

### Nodejs Services Dashboard
1. Click **Upload JSON file**
2. Select: `output/dashboards/nodejs-services-dashboard.json`
3. Click **Import**

### Infrastructure Dashboard
1. Click **Upload JSON file**
2. Select: `output/dashboards/infrastructure-dashboard.json`
3. Click **Import**

## Manual Import

If you prefer to copy-paste:

1. Open each `.json` file in a text editor
2. Copy the entire JSON content
3. In Grafana, go to **Dashboards** → **Import**
4. Paste the JSON into the **Import via panel json** field
5. Click **Import**

## Dashboard Features

- **Overview Dashboard**: High-level metrics across all services
- **Language-Specific Dashboards**: Detailed metrics for Python, Node.js, Java services
- **Infrastructure Dashboard**: Database, message queue, and system metrics

## Customization

After importing, you can:
- Modify panel queries to match your specific metrics
- Add new panels for custom metrics
- Adjust time ranges and refresh intervals
- Set up alerts based on dashboard metrics

## Troubleshooting

- **No data showing?** Check that your services are instrumented and sending telemetry
- **Missing metrics?** Verify that the metric names match your actual telemetry
- **Import errors?** Ensure the JSON files are valid and complete
