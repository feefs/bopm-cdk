function enableButton() {
    document.getElementById('submit').classList.remove('disabled')
}

function disableButton() {
    document.getElementById('submit').classList.add('disabled')
}

function markValid(id) {
    document.getElementById(id).classList.remove('invalid')
}

function markInvalid(id) {
    document.getElementById(id).classList.add('invalid')
}

function getInputValues() {
    let ticker = document.getElementById('form-ticker').value
    let days = document.getElementById('form-days').value
    let strike = document.getElementById('form-strike').value
    let type = document.getElementById('form-type').value
    let depth = document.getElementById('form-depth').value

    return [ticker, days, strike, type, depth]
}

function checkInputValues() {
    let [ticker, days, strike, type, depth] = getInputValues()
    let values = [ticker, days, strike, type, depth]
    if (values.every(v => v !== "")) {
        let valid = true
        if (isNaN(days) || Number(days) <= 0 || Number(days) > 60) {
            valid = false
            markInvalid('form-days')
        } else {
            markValid('form-days')
        }
        if (isNaN(strike) || Number(strike) <= 0) {
            valid = false
            markInvalid('form-strike')
        } else {
            markValid('form-strike')
        }
        if (!['call', 'c', 'put', 'p'].includes(type.toLowerCase())) {
            valid = false
            markInvalid('form-type')
        } else {
            markValid('form-type')
        }
        if (isNaN(depth) || !/^[0-9]+$/.test(depth) || parseInt(depth) <= 0 || parseInt(depth) > 200) {
            valid = false
            markInvalid('form-depth')
        } else {
            markValid('form-depth')
        }
        if (valid) {
            enableButton()
            return true
        }   
    }
    disableButton()
    return false
}

function getFormattedInputValues() {
    let [ticker, days, strike, type, depth] = getInputValues()
    return [ticker, Number(days), Number(strike), type, parseInt(depth)]
}

async function createPlot() {
    if (!document.getElementById('submit').classList.contains('disabled')) {
        document.getElementById('submit').classList.add('disabled')
        let [ticker, days, strike, type, depth] = getFormattedInputValues()

        let response = await fetch(
            ' https://eydivgdv44.execute-api.us-west-1.amazonaws.com/prod/bopm',
            {
                method: 'POST',
                mode: 'cors',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    'ticker': ticker,
                    'days': days,
                    'strike': strike,
                    'type': type,
                    'depth': depth
                })
            }
        )

        let json = await response.json()
        let body = JSON.parse(json['body'])
        if (json.statusCode === 200) {
            console.log('Success')
            plot(body['points'], body['depth'])
            document.getElementById('stats').innerHTML = `
            ${body['ticker']} Price: $${Number(body['price']).toFixed(2)}<br>
            Modeled Option Price: $${Number(body['points'][0][2]).toFixed(2)}<br>
            Risk-Free Rate: ${Number(body['risk_free_rate']).toFixed(5)}<br>
            252-Day EWMA Volatility: ${Number(body['ewm_volatility']).toFixed(4)}
            `
        } else {
            console.log('Failure')
            console.log(body['error'])
        }
        document.getElementById('submit').classList.remove('disabled')
    }
}

function linspace(start, stop, count) {
    let result = []
    step = (stop - start) / (count - 1)
    for (let i = 0; i < count; i++) {
        result.push(start)
        start += step
    }
    return result
}

function plot(arr, depth) {
    let price = arr[0][2]

    let priceTrace = {
        type: 'scatter3d',
        x: [arr[0][0]],
        y: [arr[0][1]],
        z: [price],
        mode: 'markers',
        marker: {size: 5, color: ['orange']}
    }
    
    let boundaryTrace = {
        type: 'surface',
        x: linspace(0, arr[arr.length - 1][0], 100),
        y: linspace(-depth, depth, 100),
        z: Array(100).fill(Array(100).fill(price)),
        colorscale: [[0, 'orange'], [1, 'orange']],
        opacity: 0.25,
        showscale: false
    }

    let trace = {
        type: 'scatter3d',
        x: arr.map(row => row[0]),
        y: arr.map(row => row[1]),
        z: arr.map(row => row[2]),
        mode: 'markers',
        marker: {size: 2, color: arr.map(row => row[2] >= price ? 'green' : 'red')}
    }

    let layout = {
        showlegend: false,
        scene: {
            xaxis: {title: 'x (years)', nticks: 5, color: 'white'},
            yaxis: {title: 'y (movement)', nticks: 10, color: 'white'},
            zaxis: {title: 'z ($)', nticks: 5, color: 'white'},
            camera: {
                up: {x: 0.1, y: 0.08, z: 1},
                center: {x: -0.1, y: 0.04, z: -0.15},
                eye: {x: -1.5, y: -1.3, z: 0.1}
            }
        },
        width: 400,
        height: 300,
        margin: {l: 0, r: 0, t: 0, b: 0},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    }

    Plotly.newPlot(document.getElementById('plot'), [trace, boundaryTrace, priceTrace], layout)
}
