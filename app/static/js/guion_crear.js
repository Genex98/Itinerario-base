// app/static/js/guion_crear.js

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    
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
            if (document.getElementById('fecha_evento')) {
                document.getElementById('fecha_evento').required = true;
            }
            const horaInicio = document.querySelector('input[name="hora_inicio"]');
            const horaFin = document.querySelector('input[name="hora_fin"]');
            const tiempoEstimado = document.querySelector('input[name="tiempo_estimado"]');
            if (horaInicio) horaInicio.required = true;
            if (horaFin) horaFin.required = true;
            if (tiempoEstimado) tiempoEstimado.required = true;
            // No requerir el select de INIT
            const selectInit = document.getElementById('selectInit');
            if (selectInit) selectInit.required = false;
        } else {
            // Modo INIT - Mostrar solo el select de INIT
            pregameFields.style.display = 'none';
            initFields.style.display = 'block';
            // No requerir campos de PRE.GAME
            if (document.getElementById('fecha_evento')) {
                document.getElementById('fecha_evento').required = false;
            }
            const horaInicio = document.querySelector('input[name="hora_inicio"]');
            const horaFin = document.querySelector('input[name="hora_fin"]');
            const tiempoEstimado = document.querySelector('input[name="tiempo_estimado"]');
            if (horaInicio) horaInicio.required = false;
            if (horaFin) horaFin.required = false;
            if (tiempoEstimado) tiempoEstimado.required = false;
            // Hacer requerido el select de INIT
            const selectInit = document.getElementById('selectInit');
            if (selectInit) selectInit.required = true;
        }
    }
    
    // Función para verificar duplicados
    async function verificarDuplicado() {
        const titulo = document.getElementById('titulo')?.value;
        const tipo = tipoGuion?.value;
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
            
            try {
                const response = await fetch('/guiones/api/verificar-duplicado', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({titulo: titulo, valor: valorComparar, tipo: tipo})
                });
                const data = await response.json();
                if (warning) {
                    warning.style.display = data.existe ? 'block' : 'none';
                }
            } catch (error) {
                console.error('Error al verificar duplicado:', error);
            }
        }
    }
    
    // Escuchar cambios en el selector
    if (tipoGuion) {
        tipoGuion.addEventListener('change', actualizarCampos);
        tipoGuion.addEventListener('change', verificarDuplicado);
    }
    
    // Ejecutar al cargar la página
    actualizarCampos();
    
    // Agregar event listeners
    const tituloInput = document.getElementById('titulo');
    const fechaEvento = document.getElementById('fecha_evento');
    const selectInit = document.getElementById('selectInit');
    
    if (tituloInput) tituloInput.addEventListener('blur', verificarDuplicado);
    if (fechaEvento) fechaEvento.addEventListener('change', verificarDuplicado);
    if (selectInit) selectInit.addEventListener('change', verificarDuplicado);
});