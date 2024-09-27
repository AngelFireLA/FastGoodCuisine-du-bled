// Fetch existing food types and names from the backend to populate the datalist
window.onload = function() {
    fetch('/get-food-data')
    .then(response => response.json())
    .then(data => {
        const typeDatalist = document.getElementById('food-types');
        const nameDatalist = document.getElementById('names');

        // Populate type datalist
        data.types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            typeDatalist.appendChild(option);
        });

        // Populate name datalist
        data.names.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            nameDatalist.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching food data:', error));
};
