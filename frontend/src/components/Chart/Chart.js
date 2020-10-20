import React from 'react';
import Plot from 'react-plotly.js';

const Chart = (props) => {

    let xaxis = {
        zeroline: false,
        showline: true,
    }
    let yaxis = {
        zeroline: false,
        showline: true
    }
    let yaxis2 = {
        overlaying: 'y',
        side: 'right'
    }

    let enableYaxis2 = false;

    let trace = {
        x: props.historyData.map((elm, idx) => idx),
        y: props.historyData,
        mode: 'lines+markers',
        type: 'scatter'
    }
    xaxis = { ...xaxis, title: 'data point' };
    yaxis = { ...yaxis, title: 'Hardness' };


const layout = {
    xaxis: xaxis,
    yaxis: yaxis,
    yaxis2: enableYaxis2?yaxis2:{},
    margin: { t: 40, r: 50, l: 50, b: 60, pad: 4 },
    showlegend: true,
    legend: { "orientation": "v", x: 1.2, xanchor: 'right', y: 1, yanchor: 'top' },
    autosize: true,
    height: undefined,
    width: undefined,
    // paper_bgcolor: '#f5f5f5',
    // plot_bgcolor: '#f5f5f5',
    font: { color: "dimgray", family: "Arial", size: 10 }
};

const config = {
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'pan2d', 'zoom2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleSpikelines'],
    responsive: false,
    toImageButtonOptions: {
        format: 'png', // one of png, svg, jpeg, webp
        filename: 'custom_image',
        height: 600,
        width: 800,
        scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
    },
}

return (
    <Plot
        style={{ width: "100%", height: "100%" }}
        data={[trace]}
        layout={layout}
        config={config}
        useResizeHandler
    />
);
}

export default Chart;
