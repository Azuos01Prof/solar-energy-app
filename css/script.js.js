function saveTable(tableType) {
    let tableData = [];
    
    if (tableType === 'monitoracao') {
        const rows = document.querySelectorAll('#monitoracao-table tbody tr');
        rows.forEach(row => {
            const ano = row.cells[0].textContent;
            const inputs = row.querySelectorAll('input');
            const meses = Array.from(inputs).map(input => input.value);
            
            tableData.push({
                ano: ano,
                meses: meses
            });
        });
    } else if (tableType === 'consumo') {
        // Similar para consumo/injeção
        const consumoRows = document.querySelectorAll('#consumo-table tbody tr');
        const injecaoRows = document.querySelectorAll('#injecao-table tbody tr');
        
        // Implementar lógica similar
    }
    
    // Enviar dados para o servidor
    fetch('/update_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            table_type: tableType,
            data: tableData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Dados salvos com sucesso!');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar dados.');
    });
}

// Event listeners para inputs
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.table-input');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            // Validação básica
            const value = this.value;
            if (value && isNaN(value)) {
                alert('Por favor, insira um valor numérico.');
                this.value = '';
            }
        });
    });
});