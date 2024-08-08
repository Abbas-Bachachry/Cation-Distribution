function toggleColumn(checkbox, columnName) {
    const inputs = document.querySelectorAll(`input[name^="${columnName}"]`);
    if (checkbox.checked) {
        inputs.forEach(input => {
            input.removeAttribute('disabled');
            input.value = '';
        });
    } else {
        inputs.forEach(input => {
            input.value = 0;
            input.setAttribute('disabled', 'true');
        });
    }
}

function enableDisabledInputs() {
    var disabledInputs = document.querySelectorAll('input[disabled]')
    disabledInputs.forEach(function (input) {
        input.removeAttribute('disabled')
    })
}

function validateForm() {
    const saturationMagnetization = document.getElementById('saturationMagnetization').value;
    const latticeConstant = document.getElementById('latticeConstant').value;

    if (!saturationMagnetization && !latticeConstant) {
        alert('Either Saturation Magnetization or Lattice Constant must be filled.');
        return false;
    }

    enableDisabledInputs();
    return true;
}

document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function () {
        const columnName = this.name.replace('oxidation', '');
        toggleColumn(this, columnName);
    });
});
