function createDatasetForChart(kData, categories){
    const colors = [
        "rgb(102, 194, 165)",  // Turquoise
        "rgb(252, 141, 98)",   // Light Salmon
        "rgb(141, 160, 203)",  // Light Blue
        "rgb(231, 138, 195)",  // Light Pink
        "rgb(166, 216, 84)",   // Light Green
        "rgb(255, 217, 47)",   // Yellow
        "rgb(229, 196, 148)",  // Tan
        "rgb(179, 179, 179)",  // Grey
        "rgb(127, 127, 127)",  // Dark Grey
        "rgb(188, 189, 34)"    // Olive Green
    ];

    const datasets = [];

    for (let idx=0; idx<kData.length; idx++){
        let a_dataset = {
            label: categories[idx],
            data: kData[idx],
            fill: false,
            borderColor: colors[idx%colors.length],
            tension: 0.1
        };

        datasets.push(a_dataset);
    }

    return datasets;
}

function updateChart(chart, labels, newDatasets){
    // mutates the chart

    chart.data.labels = labels;
    chart.data.datasets = [];
    newDatasets.forEach(dataset => {
        chart.data.datasets.push(dataset);
    });

    chart.update();
}

function populateLineChartWithinAContext(context, labels, datasets){
    return new Chart(context, {
        type: 'line',
        data: {
        labels: labels,
        datasets: datasets
        },options: {
            scales: {

                x: {
                    type: 'time',
                    time: {
                        unit: 'month',

                    },
                    title: {
                        display: true,
                        text: 'Month',
                        displayFormats: {
                            quarter: 'MMM YYYY'
                        }
                    }
                },

                y: {
                    title: {
                        display: true,
                        text: 'Hour'
                    }
                }

            }
        }
    });
}


