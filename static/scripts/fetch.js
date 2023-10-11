function fetchData(event, dataRequired, dataFilter, isCalculationPerWorker) {
    const clickedButton = event.target;

    const startMonth = clickedButton.parentElement.querySelector(".startMonth").value;
    const endMonth = clickedButton.parentElement.querySelector(".endMonth").value;


    // Make an API request using fetch
    fetch(fetch_base_url +
        `?dataRequired=${dataRequired}&dataFilter=${dataFilter}&startMonth=${startMonth}&endMonth=${endMonth}&isCalculationPerWorker=${isCalculationPerWorker}`)
        .then(response => response.json())
        .then(data => {

            // preprocessing
            if (isCalculationPerWorker){
                [rawDatasets, rawLabels, categories] = data;
            }else{
                [rawDatasets, rawLabels] = data;
                categories = ["Total Sum"];
                rawDatasets = [rawDatasets];
            }

            console.log(rawLabels)
            console.log(rawDatasets)
            console.log(categories)
            const labels = rawLabels.map(dateString => new Date(dateString));
            const datasets = createDatasetForChart(rawDatasets, categories);

            console.log(datasets)
            console.log(labels)

            // update the chart
            const cardContainer = clickedButton.parentElement.parentElement;
            const canvas = cardContainer.querySelector("canvas");
            const targetChart = Chart.getChart(canvas);
            if (targetChart != null){
                targetChart.destroy();
            }

            populateLineChartWithinAContext(canvas, labels, datasets);
            // updateChart(targetChart, labels, datasets);


        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}