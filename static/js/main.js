// ==========================================
// 1. LÓGICA DEL FILTRO (MENÚ IZQUIERDO)
// ==========================================
function filtrar(categoria, btnElement) {
    document.querySelectorAll('.menu-item').forEach(btn => {
        btn.classList.remove('active');
    });

    btnElement.classList.add('active');

    const titulos = { 
        'todos': 'Todos los Eventos', 
        'futbol': 'Fútbol', 
        'basket': 'Baloncesto', 
        'tenis': 'Tenis' 
    };

    const tituloElement = document.getElementById('titulo-filtro');
    if(tituloElement) {
        tituloElement.innerText = titulos[categoria] || 'Eventos';
    }

    
    const tarjetas = document.querySelectorAll('.match-card');
    
    tarjetas.forEach(card => {
        const categoriaTarjeta = card.getAttribute('data-categoria');
        
        if (categoria === 'todos' || categoriaTarjeta === categoria) {
            card.style.display = 'grid';
        } else {
            card.style.display = 'none'; 
        }
    });
}

// ==========================================
// 2. LÓGICA DEL CUPÓN (CARRITO)
// ==========================================


let carrito = [];

function toggleApuesta(idPartido, partidoNombre, seleccion, cuota, tipo) {
    const uniqueId = idPartido + '_' + tipo;

    const existeIndex = carrito.findIndex(item => item.uid === uniqueId);

    if (existeIndex > -1) {
        carrito.splice(existeIndex, 1);
        
        const btn = document.getElementById('btn_' + uniqueId);
        if(btn) btn.classList.remove('selected');

    } else {
        
        carrito = carrito.filter(item => item.idPartido !== idPartido);
        
        
        document.querySelectorAll(`[id^='btn_${idPartido}_']`).forEach(b => {
            b.classList.remove('selected');
        });

       
        carrito.push({
            uid: uniqueId,
            idPartido: idPartido,
            partido: partidoNombre,
            seleccion: seleccion,
            cuota: cuota
        });
        
        
        const btn = document.getElementById('btn_' + uniqueId);
        if(btn) btn.classList.add('selected');
    }

    
    renderizarTicket();
}


function renderizarTicket() {
    const container = document.getElementById('lista-apuestas');
    const form = document.getElementById('form-final');
    
    
    container.innerHTML = '';

    
    if (carrito.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; margin-top: 20px;">Selecciona una cuota.</p>';
        form.style.display = 'none'; 
        return;
    }

    
    form.style.display = 'block';
    let cuotaTotal = 1;

    
    carrito.forEach((item, index) => {
        cuotaTotal *= parseFloat(item.cuota);
        
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

    
    document.getElementById('total-cuota').innerText = cuotaTotal.toFixed(2);
    
   
    document.getElementById('input-json').value = JSON.stringify(carrito);
    
    
    calcularGanancia();
}

function borrarItem(index, uid) {
    carrito.splice(index, 1); 
    
    
    const btn = document.getElementById('btn_' + uid);
    if(btn) btn.classList.remove('selected');
    
    renderizarTicket();
}

function calcularGanancia() {
    const montoInput = document.getElementById('monto');
    if(!montoInput) return;

    const monto = parseFloat(montoInput.value) || 0;
    const cuota = parseFloat(document.getElementById('total-cuota').innerText);
    
    const ganancia = (monto * cuota).toFixed(2);
    document.getElementById('ganancia').innerText = '$' + ganancia;
}