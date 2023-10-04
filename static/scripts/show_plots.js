const ctx = document.getElementById('chart1');

new Chart(ctx, {
    type: 'line',
    data: {
    labels: workSessionDates,
    datasets: [{
        label: 'Working Hours per Month',
        data: workHours,
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
                    text: 'Month'
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