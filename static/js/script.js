let formDataList = [];

function generateForm() {
    const container = document.getElementById('formContainer');
    container.innerHTML = '';  // Clear any existing form

    const names = document.getElementById('elementNames').value.split(',');
    const n = names.length;
    if (n <= 0 || names[0].trim() === '') {
        alert('Please enter valid element names.');
        return;
    }

    for (let i = 0; i < n; i++) {
        const elementName = names[i].trim().toUpperCase();
        const elementDiv = document.createElement('div');
        elementDiv.className = 'form-row';
        elementDiv.innerHTML = `
            <div class="form-column">
                <label>Name: <input type="text" name="elementName${i}" value="${elementName}" readonly></label>
                <label>Content: <input type="number" name="elementContent${i}" step="0.01" required></label>
                <label>Molecular Weight: <input type="number" name="molecularWeight${i}" step="0.01" required></label>
            </div>

            <div class="form-column">
                <label>Oxidation State A1: <input type="checkbox" name="oxidationA${i}_1"></label>
                <label>Magnetic Moment A1: <input type="number" name="magneticMomentA${i}_1" step="0.01"></label>
                <label>Radii A1: <input type="number" name="radiiA${i}_1" step="0.01"></label>
            </div>

            <div class="form-column">
                <label>Oxidation State A2: <input type="checkbox" name="oxidationA${i}_2"></label>
                <label>Magnetic Moment A2: <input type="number" name="magneticMomentA${i}_2" step="0.01"></label>
                <label>Radii A2: <input type="number" name="radiiA${i}_2" step="0.01"></label>
            </div>

            <div class="form-column">
                <label>Oxidation State B1: <input type="checkbox" name="oxidationB${i}_1"></label>
                <label>Magnetic Moment B1: <input type="number" name="magneticMomentB${i}_1" step="0.01"></label>
                <label>Radii B1: <input type="number" name="radiiB${i}_1" step="0.01"></label>
            </div>

            <div class="form-column">
                <label>Oxidation State B2: <input type="checkbox" name="oxidationB${i}_2"></label>
                <label>Magnetic Moment B2: <input type="number" name="magneticMomentB${i}_2" step="0.01"></label>
                <label>Radii B2: <input type="number" name="radiiB${i}_2" step="0.01"></label>
            </div>
        `;
        container.appendChild(elementDiv);
    }

    const additionalFields = document.createElement('div');
    additionalFields.className = 'form-row';
    additionalFields.innerHTML = `
        <label>Saturation Magnetization: <input type="number" name="saturationMagnetization" step="0.01"></label>
        <label>Lattice Constant: <input type="number" name="latticeConstant" step="0.01"></label>
        <label>Initial Gauss: ${Array.from({ length: 4 * n }, (_, j) => `<input type="number" name="initialGauss${j}" step="0.01">`).join('')}</label>
        <label>Radii of Oxygen (default = 1.28 Å): <input type="number" name="radiiOxygen" value="1.28" step="0.01"></label>
    `;
    container.appendChild(additionalFields);

    const buttonsDiv = document.createElement('div');
    buttonsDiv.className = 'form-row';
    buttonsDiv.innerHTML = `
        <button type="button" onclick="addData()">Add</button>
        <button type="button" onclick="recalculateData()">Recalculate</button>
    `;
    container.appendChild(buttonsDiv);
}

function addData() {
    const form = document.getElementById('formContainer');
    const formData = new FormData(form);
    const dataObj = {};
    formData.forEach((value, key) => {
        dataObj[key] = value;
    });

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataObj),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            formDataList.push(dataObj);
            updateStoredData();
        } else {
            alert(data.message);
        }
    });
}

function recalculateData() {
    const index = prompt("Enter the index of the data to recalculate (starting from 0):");
    if (index === null || isNaN(index) || index < 0 || index >= formDataList.length) {
        alert("Invalid index.");
        return;
    }

    const form = document.getElementById('formContainer');
    const formData = new FormData(form);
    const dataObj = {};
    formData.forEach((value, key) => {
        dataObj[key] = value;
    });

    fetch('/recalculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index, data: dataObj }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            formDataList[Number(index)] = dataObj;
            updateStoredData();
        } else {
            alert(data.message);
        }
    });
}

function updateStoredData() {
    const container = document.getElementById('storedDataContainer');
    container.innerHTML = "<h2>Stored Data</h2>";
    formDataList.forEach((data, index) => {
        const dataDiv = document.createElement('div');
        dataDiv.className = 'form-row';
        dataDiv.innerHTML = `<strong>Data ${index}:</strong> ${JSON.stringify(data)}`;
        container.appendChild(dataDiv);
    });
}
