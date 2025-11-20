// ==========================================
// 1. LÓGICA DEL FILTRO (MENÚ IZQUIERDO)
// ==========================================
function filtrar(categoria, btnElement) {
    // a) Quitamos el color dorado al botón anterior
    document.querySelectorAll('.menu-item').forEach(btn => {
        btn.classList.remove('active');
    });

    // b) Le ponemos color dorado al botón que acabas de clickear
    btnElement.classList.add('active');

    // c) Cambiamos el título central
    const titulos = { 
        'todos': 'Todos los Eventos', 
        'futbol': 'Fútbol', 
        'basket': 'Baloncesto', 
        'tenis': 'Tenis' 
    };
    // Si existe el título lo ponemos, si no, ponemos "Eventos"
    const tituloElement = document.getElementById('titulo-filtro');
    if(tituloElement) {
        tituloElement.innerText = titulos[categoria] || 'Eventos';
    }

    // d) Ocultamos o mostramos las tarjetas según su categoría
    const tarjetas = document.querySelectorAll('.match-card');
    
    tarjetas.forEach(card => {
        const categoriaTarjeta = card.getAttribute('data-categoria');
        
        if (categoria === 'todos' || categoriaTarjeta === categoria) {
            card.style.display = 'grid'; // Mostrar
        } else {
            card.style.display = 'none'; // Ocultar
        }
    });
}

// ==========================================
// 2. LÓGICA DEL CUPÓN (CARRITO)
// ==========================================

// Aquí guardaremos las apuestas en memoria
let carrito = [];

function toggleApuesta(idPartido, partidoNombre, seleccion, cuota, tipo) {
    // Creamos un ID único (Ej: "101_1" -> Partido 101, Gana Local)
    const uniqueId = idPartido + '_' + tipo;

    // Buscamos si ya está en el carrito
    const existeIndex = carrito.findIndex(item => item.uid === uniqueId);

    if (existeIndex > -1) {
        // SI YA EXISTE: Lo borramos (es como desmarcar)
        carrito.splice(existeIndex, 1);
        
        // Le quitamos el color amarillo al botón
        const btn = document.getElementById('btn_' + uniqueId);
        if(btn) btn.classList.remove('selected');

    } else {
        // SI NO EXISTE: Lo agregamos

        // Regla de oro: No puedes apostar al Local y al Visitante del mismo partido.
        // Primero borramos cualquier apuesta vieja de ESTE partido.
        carrito = carrito.filter(item => item.idPartido !== idPartido);
        
        // Quitamos el color amarillo a los otros botones de este partido
        // Buscamos todos los botones que empiecen con "btn_IDPARTIDO_"
        document.querySelectorAll(`[id^='btn_${idPartido}_']`).forEach(b => {
            b.classList.remove('selected');
        });

        // Agregamos la nueva apuesta
        carrito.push({
            uid: uniqueId,
            idPartido: idPartido,
            partido: partidoNombre,
            seleccion: seleccion,
            cuota: cuota
        });
        
        // Pintamos de amarillo el nuevo botón
        const btn = document.getElementById('btn_' + uniqueId);
        if(btn) btn.classList.add('selected');
    }

    // Actualizamos la vista del ticket
    renderizarTicket();
}

// Función que "dibuja" el ticket en la barra derecha
function renderizarTicket() {
    const container = document.getElementById('lista-apuestas');
    const form = document.getElementById('form-final');
    
    // Limpiamos el HTML actual
    container.innerHTML = '';

    // Si no hay apuestas, mostramos mensaje vacío
    if (carrito.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; margin-top: 20px;">Selecciona una cuota.</p>';
        form.style.display = 'none'; // Ocultamos el botón de pagar
        return;
    }

    // Si hay apuestas, mostramos el formulario
    form.style.display = 'block';
    let cuotaTotal = 1;

    // Recorremos el carrito y creamos los elementos visuales
    carrito.forEach((item, index) => {
        cuotaTotal *= parseFloat(item.cuota); // Multiplicamos cuotas
        
        const div = document.createElement('div');
        div.className = 'ticket-item';
        div.innerHTML = `
            <div style="color: var(--accent); font-weight:bold;">${item.seleccion}</div>
            <div style="font-size:11px; color:#ccc;">${item.partido}</div>
            <div style="text-align:right; font-weight:bold;">${item.cuota}</div>
            
            <button class="btn-delete" onclick="borrarItem(${index}, '${item.uid}')">X</button>
        `;
        container.appendChild(div);
    });

    // Actualizamos los textos de total
    document.getElementById('total-cuota').innerText = cuotaTotal.toFixed(2);
    
    // IMPORTANTE: Guardamos el carrito en el input oculto para enviarlo a Python
    document.getElementById('input-json').value = JSON.stringify(carrito);
    
    // Recalculamos la ganancia
    calcularGanancia();
}

// Borrar una apuesta desde la X del ticket
function borrarItem(index, uid) {
    carrito.splice(index, 1); // Borrar del array
    
    // Quitar color amarillo del botón
    const btn = document.getElementById('btn_' + uid);
    if(btn) btn.classList.remove('selected');
    
    renderizarTicket();
}

// Calcular ganancia (Monto * Cuota)
function calcularGanancia() {
    const montoInput = document.getElementById('monto');
    if(!montoInput) return;

    const monto = parseFloat(montoInput.value) || 0;
    const cuota = parseFloat(document.getElementById('total-cuota').innerText);
    
    const ganancia = (monto * cuota).toFixed(2);
    document.getElementById('ganancia').innerText = '$' + ganancia;
}