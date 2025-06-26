// static/js/progreso.js
document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos del elemento oculto
    const graficoData = document.getElementById('grafico-data');
    
    if (!graficoData) {
        console.log('No hay datos disponibles para los gráficos');
        return;
    }

    try {
        // Parsear datos
        const fechasPesos = JSON.parse(graficoData.dataset.fechasPesos || '[]');
        const pesos = JSON.parse(graficoData.dataset.pesos || '[]');
        const fechasGrasas = JSON.parse(graficoData.dataset.fechasGrasas || '[]');
        const grasas = JSON.parse(graficoData.dataset.grasas || '[]');

        console.log('Datos de peso:', { fechasPesos, pesos });
        console.log('Datos de grasa:', { fechasGrasas, grasas });

        // Configuración común para los gráficos
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        parser: 'YYYY-MM-DDTHH:mm:ss',
                        displayFormats: {
                            day: 'DD/MM',
                            week: 'DD/MM',
                            month: 'MM/YY'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true
                    }
                }
            }
        };

        // Crear gráfico de peso
        const pesoCanvas = document.getElementById('pesoChart');
        if (pesoCanvas && fechasPesos.length > 0 && pesos.length > 0) {
            const pesoCtx = pesoCanvas.getContext('2d');
            
            new Chart(pesoCtx, {
                type: 'line',
                data: {
                    labels: fechasPesos,
                    datasets: [{
                        label: 'Peso (kg)',
                        data: pesos,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: 'rgb(75, 192, 192)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        y: {
                            ...commonOptions.scales.y,
                            title: {
                                display: true,
                                text: 'Peso (kg)'
                            }
                        }
                    }
                }
            });
        } else {
            // Mostrar mensaje de no hay datos
            const pesoChartContainer = pesoCanvas?.parentElement;
            if (pesoChartContainer) {
                pesoChartContainer.innerHTML = '<h2 class="chart-title">📊 Progreso de Peso (kg)</h2><p class="no-chart-data">No hay datos de peso disponibles</p>';
            }
        }

        // Crear gráfico de grasa corporal
        const grasaCanvas = document.getElementById('grasaChart');
        if (grasaCanvas && fechasGrasas.length > 0 && grasas.length > 0) {
            const grasaCtx = grasaCanvas.getContext('2d');
            
            new Chart(grasaCtx, {
                type: 'line',
                data: {
                    labels: fechasGrasas,
                    datasets: [{
                        label: 'Grasa Corporal (%)',
                        data: grasas,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        y: {
                            ...commonOptions.scales.y,
                            title: {
                                display: true,
                                text: 'Grasa Corporal (%)'
                            },
                            min: 0,
                            max: 50
                        }
                    }
                }
            });
        } else {
            // Mostrar mensaje de no hay datos
            const grasaChartContainer = grasaCanvas?.parentElement;
            if (grasaChartContainer) {
                grasaChartContainer.innerHTML = '<h2 class="chart-title">📊 Progreso de Grasa Corporal (%)</h2><p class="no-chart-data">No hay datos de grasa corporal disponibles</p>';
            }
        }

    } catch (error) {
        console.error('Error al crear los gráficos:', error);
    }
});