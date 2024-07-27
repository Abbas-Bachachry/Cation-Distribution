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
        const elementName = names[i].trim();
        const elementDiv = document.createElement('div');
        elementDiv.className = 'form-row';
        elementDiv.innerHTML = `
            <label>Name: <input type="text" name="elementName${i}" value="${elementName}" required></label>
            <label>Content: <input type="number" name="elementContent${i}" step="0.01" required></label>
            <label>Molecular Weight: <input type="number" name="molecularWeight${i}" step="0.01" required></label>

            <label>Oxidation State A1: <input type="checkbox" name="oxidationA${i}_1"></label>
            <label>Magnetic Moment A1: <input type="number" name="magneticMomentA${i}_1" step="0.01"></label>
            <label>Oxidation State A2: <input type="checkbox" name="oxidationA${i}_2"></label>
            <label>Magnetic Moment A2: <input type="number" name="magneticMomentA${i}_2" step="0.01"></label>

            <label>Oxidation State B1: <input type="checkbox" name="oxidationB${i}_1"></label>
            <label>Magnetic Moment B1: <input type="number" name="magneticMomentB${i}_1" step="0.01"></label>
            <label>Oxidation State B2: <input type="checkbox" name="oxidationB${i}_2"></label>
            <label>Magnetic Moment B2: <input type="number" name="magneticMomentB${i}_2" step="0.01"></label>

            <label>Radii A1: <input type="number" name="radiiA${i}_1" step="0.01"></label>
            <label>Radii A2: <input type="number" name="radiiA${i}_2" step="0.01"></label>

            <label>Radii B1: <input type="number" name="radiiB${i}_1" step="0.01"></label>
            <label>Radii B2: <input type="number" name="radiiB${i}_2" step="0.01"></label>
        `;
        container.appendChild(elementDiv);
    }

    const additionalFields = document.createElement('div');
    additionalFields.className = 'form-row';
    additionalFields.innerHTML = `
        <label>Saturation Magnetization: <input type="number" name="saturationMagnetization" step="0.01"></label>
        <label>Lattice Constant: <input type="number" name="latticeConstant" step="0.01"></label>
        <label>Initial Gauss: <input type="number" name="initialGauss1" step="0.01"> 
        <input type="number" name="initialGauss2" step="0.01"> 
        <input type="number" name="initialGauss3" step="0.01"> 
        <input type="number" name="initialGauss4" step="0.01"></label>
        <label>Radii of Oxygen (default = 1.28 Å): <input type="number" name="radiiOxygen" value="1.28" step="0.01"></label>
    `;
    container.appendChild(additionalFields);

    const buttonsDiv = document.createElement('div');
    buttonsDiv.className = 'form-row';
    buttonsDiv.innerHTML = `
        <button type="submit">Submit</button>
        <button type="button" onclick="generateForm()">Recalculate/Calculate</button>
    `;
    container.appendChild(buttonsDiv);
}