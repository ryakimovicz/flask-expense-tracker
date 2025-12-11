document.addEventListener('DOMContentLoaded', function() {
    
    fetch('/api/chart-data')
        .then(response => response.json())
        .then(data => {
            
            const ctx = document.getElementById('expenseChart').getContext('2d');
            
            if (data.labels.length === 0) {
                // Si no hay datos, no dibujamos nada o mostramos mensaje
                return;
            }

            new Chart(ctx, {
                type: 'doughnut', // Tipo de gráfico: 'pie', 'bar', 'line', 'doughnut'
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Gastos por Categoría',
                        data: data.data,
                        backgroundColor: [
                            '#3b82f6', // Azul (Comida)
                            '#10b981', // Verde (Transporte)
                            '#f59e0b', // Amarillo (Servicios)
                            '#ef4444', // Rojo (Entretenimiento)
                            '#8b5cf6', // Violeta (Otros)
                            '#6b7280'  // Gris (Extra)
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Distribución de Gastos'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error cargando el gráfico:', error));
});