let formDataList = [];

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

// function recalculateData() {
//     const index = prompt("Enter the index of the data to recalculate (starting from 0):");
//     if (index === null || isNaN(index) || index < 0 || index >= formDataList.length) {
//         alert("Invalid index.");
//         return;
//     }
//
//     const form = document.getElementById('formContainer');
//     const formData = new FormData(form);
//     const dataObj = {};
//     formData.forEach((value, key) => {
//         dataObj[key] = value;
//     });
//
//     fetch('/recalculate', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({index, data: dataObj}),
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 formDataList[Number(index)] = dataObj;
//                 updateStoredData();
//             } else {
//                 alert(data.message);
//             }
//         });
// }