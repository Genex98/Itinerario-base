const tipoGuion = document.getElementById('tipoGuion');
const pregameFields = document.getElementById('pregameFields');
const initFields = document.getElementById('initFields');

// Función para mostrar/ocultar campos según selección
function actualizarCampos() {
    const seleccion = tipoGuion.value;
    
    if (seleccion === 'pregame') {
        // Modo PRE.GAME - Mostrar fechas y horas
        pregameFields.style.display = 'block';
        initFields.style.display = 'none';
        // Hacer requeridos los campos de PRE.GAME
        document.getElementById('fecha_evento').required = true;
        document.querySelector('input[name="hora_inicio"]').required = true;
        document.querySelector('input[name="hora_fin"]').required = true;
        document.querySelector('input[name="tiempo_estimado"]').required = true;
        // No requerir el select de INIT
        document.getElementById('selectInit').required = false;
    } else {
        // Modo INIT - Mostrar solo el select de INIT
        pregameFields.style.display = 'none';
        initFields.style.display = 'block';
        // No requerir campos de PRE.GAME
        document.getElementById('fecha_evento').required = false;
        document.querySelector('input[name="hora_inicio"]').required = false;
        document.querySelector('input[name="hora_fin"]').required = false;
        document.querySelector('input[name="tiempo_estimado"]').required = false;
        // Hacer requerido el select de INIT
        document.getElementById('selectInit').required = true;
    }
}

// Escuchar cambios en el selector
tipoGuion.addEventListener('change', actualizarCampos);

// Ejecutar al cargar la página
actualizarCampos();

// Función para verificar duplicados
async function verificarDuplicado() {
    const titulo = document.getElementById('titulo')?.value;
    const tipo = tipoGuion.value;
    const warning = document.getElementById('duplicadoWarning');
    
    if (titulo && titulo.length > 3) {
        let valorComparar = titulo;
        
        if (tipo === 'init') {
            const selectInit = document.getElementById('selectInit')?.value;
            valorComparar = titulo + '|' + selectInit;
        } else {
            const fecha = document.getElementById('fecha_evento')?.value;
            valorComparar = titulo + '|' + fecha;
        }
        
        const response = await fetch('/guiones/api/verificar-duplicado', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({titulo: titulo, valor: valorComparar, tipo: tipo})
        });
        const data = await response.json();
        warning.style.display = data.existe ? 'block' : 'none';
    }
}

document.getElementById('titulo')?.addEventListener('blur', verificarDuplicado);
document.getElementById('fecha_evento')?.addEventListener('change', verificarDuplicado);
document.getElementById('selectInit')?.addEventListener('change', verificarDuplicado);
tipoGuion?.addEventListener('change', verificarDuplicado);