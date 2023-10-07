const createDatasetForChart = (kData, labels) => {
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
            label: labels[idx],
            data: kData[idx],
            fill: false,
            borderColor: colors[idx%colors.length],
            tension: 0.1
        };

        datasets.push(a_dataset);
    }

    return datasets;
}


// viz 1
const ctx = document.getElementById('chart1');
new Chart(ctx, {
    type: 'line',
    data: {
    labels: earningsMetricLabels,
    datasets: [{
        label: 'Working Hours per Month',
        data: earningsMetricValues,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
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

const topKDataset = createDatasetForChart(earningsMetricTopKValues, earningsMetricTopKWorkerNames)


// viz 2
const ctx2 = document.getElementById('chart2');
new Chart(ctx2, {
    type: 'line',
    data: {
    labels: earningsMetricTopKLabels,
    datasets: topKDataset
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