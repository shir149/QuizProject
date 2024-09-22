function answers_chart(content) {
    var chart_data = JSON.parse(content);
    let answersChart= document.getElementById('answersChart').getContext('2d');

    // Global options
    Chart.defaults.font.size = 30;
    Chart.defaults.color = 'black';
    Chart.defaults.plugins.legend.display = false;
    Chart.defaults.plugins.tooltip.enabled = false;
    Chart.defaults.layout.padding = 0;

    let massPopChart = new Chart(answersChart, {
        type: 'bar', // bar, horizontalBar, pie, line, doughnut, radar, polarArea
        data: {
            labels: chart_data.labels,
            datasets: [{
                data: chart_data.data,
                backgroundColor: chart_data.colours,
            }]
        },
        options: {
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: false,
                    max: chart_data.max_y
                }
            },
            tooltips: {
                enabled: false
            },
            hover: {mode: null},
            animation: {
                onComplete: function() {
                    var chartInstance = this,
                      ctx = chartInstance.ctx;

                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    var metasets = this._metasets;

                    this.data.datasets.forEach(function(dataset, i) {
                        dataset.data.forEach(function(bar_value, index) {
                            var co_ordinates = metasets[i].data[index]
                            var fillColor = metasets[i]._dataset.backgroundColor[index];
                            ctx.fillStyle = fillColor;
                            var y_origin = co_ordinates.base;
                            var x = co_ordinates.x
                            var y = co_ordinates.y
                            var width = co_ordinates.width;
                            ctx.fillRect(x - width/2, y_origin + 20, width, 20);
                            //ctx.restore();
                            ctx.fillText(chart_data.result_labels[index], x, y - 5);
                        });
                    });
                }
            }
        }
    });
}
