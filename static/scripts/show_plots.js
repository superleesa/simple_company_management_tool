

// defining functions
const process_data = (dateStringToWorkedHours) => {

    const sortedDates = Object.keys(dateStringToWorkedHours).sort();
    const workedDates = [];
    const workedHours = [];

    for (let key of sortedDates){
        workedDates.push(new Date(key));
        workedHours.push(dateStringToWorkedHours[key]);
    }

    return [workedDates, workedHours];
}

const create_dataset_for_kData = (kData, label) => {
    const dataset = [];

    for (let workedHours in kData){
        let a_dataset = {
            label: label,
            data: kData,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        };

        dataset.push(a_dataset);
    }

    return dataset;
}

// viz 1
const ctx = document.getElementById('chart1');
new Chart(ctx, {
    type: 'line',
    data: {
    labels: workedDates,
    datasets: [{
        label: 'Working Hours per Month',
        data: workedHours,
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

topWorkingHoursWorkers.map(process_data)

// viz 2
const ctx2 = document.getElementById('chart2');
new Chart(ctx2, {
    type: 'line',
    data: {
    labels: workedDates,
    datasets: [{
        label: 'Working Hours per Month',
        data: workedHours,
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