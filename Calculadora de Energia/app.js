// Dados dos eletrodomésticos (ATUALIZADO)
const eletrodomesticos = {
    geladeira: [150, 200, 250],
    tv: [120, 150, 200],
    arcondicionado: [800, 1200, 1500],
    ventilador: [50, 80, 100],
    maquinalavar: [500, 1000, 1500],
    // NOVOS ELETRODOMÉSTICOS:
    fogaoeletrico: [6000, 6500, 7000, 7500, 8000],
    fornoeletrico: [5000],
    microondas: [1400],
    lavaloucas: [1500, 2000, 2500, 2700],
    cafeteira: [300],
    liquidificador: [400],
    batedeira: [450],
    torneiraeletrica: [3500, 4000, 4500, 5000, 5500],
    chuveiroeletrico: [3000, 4000, 5000, 5500],
    aspirador: [600, 800, 1000],
    ferro: [750, 1000, 1250, 1500],
    secadora: [2000, 2500, 3000, 3500],
    lampada: [5, 7, 9, 12, 15],
    outro1: [10, 25, 50, 75, 100],
    outro2: [100, 250, 500, 750, 1000],
    outro3: [1000, 2000, 3000, 4000, 5000, 6000]
};

// Variáveis globais
let usuario = {};
let eletrosSelecionados = [];
let consumoTotal = 0;
let tempoInicial = null;
let intervaloConsumo = null;
let tempoDecorrido = 0;

// URL do Google Apps Script (substitua pela sua URL)
const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwVQ3-wTtaU8TO8rwDd7AbB6C2xkCq_9pcaCaDxu0DIf15L2pc031wfPOfRAgYsqEoWhg/exec";

// ==================== EVENT LISTENERS ====================

// Botão PRÓXIMO
// Botão PRÓXIMO - atualizado com novos campos
document.getElementById('btnProximo').addEventListener('click', () => {
    usuario.nome = document.getElementById('nome').value;
    usuario.email = document.getElementById('email').value;
    usuario.serie = document.getElementById('serie').value; // NOVO
    usuario.turma = document.getElementById('turma').value; // NOVO
    usuario.qtdFamiliares = parseInt(document.getElementById('qtdFamiliares').value);
    
    // Validação atualizada
    if (!usuario.nome || !usuario.email || !usuario.serie || !usuario.turma || isNaN(usuario.qtdFamiliares)) {
        alert('Preencha todos os campos!');
        return;
    }
    
    document.getElementById('userForm').classList.add('hidden');
    document.getElementById('eletroForm').classList.remove('hidden');
});

// Preenche opções de potência
document.getElementById('eletroSelect').addEventListener('change', (e) => {
    const potenciaSelect = document.getElementById('potenciaSelect');
    potenciaSelect.innerHTML = '<option value="">Selecione a potência (W)</option>';
    
    if (e.target.value && eletrodomesticos[e.target.value]) {
        eletrodomesticos[e.target.value].forEach(potencia => {
            const option = document.createElement('option');
            option.value = potencia;
            option.textContent = `${potencia}W`;
            potenciaSelect.appendChild(option);
        });
    }
});

// Botão ADICIONAR
document.getElementById('btnAddEletro').addEventListener('click', () => {
    const eletro = document.getElementById('eletroSelect').value;
    const potencia = parseInt(document.getElementById('potenciaSelect').value);
    
    if (eletro && potencia) {
        eletrosSelecionados.push({ 
            id: Date.now() + Math.random(),
            nome: eletro, 
            potencia, 
            ativo: false, 
            inicio: null,
            consumo: 0
        });
        atualizarListaEletros();
        
        // Limpa seleção
        document.getElementById('eletroSelect').value = '';
        document.getElementById('potenciaSelect').innerHTML = '<option value="">Selecione a potência (W)</option>';
    } else {
        alert('Selecione um eletrodoméstico e uma potência!');
    }
});

// Botão INICIAR MONITORAMENTO
document.getElementById('btnIniciarMonitoramento').addEventListener('click', () => {
    if (eletrosSelecionados.length === 0) {
        alert('Adicione pelo menos um eletrodoméstico!');
        return;
    }
    
    document.getElementById('eletroForm').classList.add('hidden');
    document.getElementById('monitoramento').classList.remove('hidden');
    tempoInicial = new Date();
    tempoDecorrido = 0;
    
    iniciarMonitoramentoTempoReal();
    atualizarControlesEletro();
    atualizarEletroAtivos();
});

// Botão FINALIZAR DIA
document.getElementById('btnFinalizar').addEventListener('click', finalizarMonitoramento);

// Botão REINICIAR
document.getElementById('btnReiniciar').addEventListener('click', () => {
    location.reload();
});

// Botão ENVIAR EMAIL
document.getElementById('btnEnviarEmail').addEventListener('click', enviarEmailResultado);

// ==================== FUNÇÕES PRINCIPAIS ====================

function atualizarListaEletros() {
    const eletroList = document.getElementById('eletroList');
    eletroList.innerHTML = eletrosSelecionados.map(eletro => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span>${eletro.nome} (${eletro.potencia}W)</span>
            <button class="btn btn-sm btn-danger" onclick="removerEletro(${eletro.id})">
                Remover
            </button>
        </div>
    `).join('');
}

function removerEletro(id) {
    eletrosSelecionados = eletrosSelecionados.filter(e => e.id !== id);
    atualizarListaEletros();
}

function atualizarControlesEletro() {
    const controlesDiv = document.getElementById('controlesEletro');
    controlesDiv.innerHTML = eletrosSelecionados.map(eletro => `
        <div class="card mb-2">
            <div class="card-body">
                <h5 class="card-title">${eletro.nome} (${eletro.potencia}W)</h5>
                <p>Status: <span class="${eletro.ativo ? 'text-success' : 'text-danger'}">${eletro.ativo ? 'LIGADO' : 'DESLIGADO'}</span></p>
                <button class="btn ${eletro.ativo ? 'btn-danger' : 'btn-success'}" onclick="toggleEletro(${eletro.id})">
                    ${eletro.ativo ? 'Desligar' : 'Ligar'}
                </button>
                ${eletro.ativo ? `<p class="mt-2">Consumo: ${eletro.consumo.toFixed(3)} kWh</p>` : ''}
            </div>
        </div>
    `).join('');
}

function toggleEletro(id) {
    const eletro = eletrosSelecionados.find(e => e.id === id);
    if (eletro) {
        eletro.ativo = !eletro.ativo;
        eletro.inicio = eletro.ativo ? new Date() : null;
        atualizarControlesEletro();
        atualizarEletroAtivos();
    }
}

function atualizarEletroAtivos() {
    const eletroAtivosDiv = document.getElementById('eletroAtivos');
    const eletrosAtivos = eletrosSelecionados.filter(e => e.ativo);
    
    if (eletrosAtivos.length === 0) {
        eletroAtivosDiv.innerHTML = '<div class="alert alert-info">Nenhum eletrodoméstico ativo no momento.</div>';
    } else {
        eletroAtivosDiv.innerHTML = eletrosAtivos.map(eletro => `
            <div class="list-group-item">
                <h5>${eletro.nome} (${eletro.potencia}W)</h5>
                <p>Ligado às: ${eletro.inicio.toLocaleTimeString()}</p>
                <p>Consumo: ${eletro.consumo.toFixed(3)} kWh</p>
            </div>
        `).join('');
    }
}

function iniciarMonitoramentoTempoReal() {
    if (intervaloConsumo) clearInterval(intervaloConsumo);
    
    intervaloConsumo = setInterval(() => {
        tempoDecorrido += 1;
        
        // Atualiza consumo dos aparelhos ativos
        const horasDecorridas = 1 / 3600; // 1 segundo em horas
        eletrosSelecionados.forEach(eletro => {
            if (eletro.ativo) {
                eletro.consumo += (eletro.potencia * horasDecorridas) / 1000;
            }
        });
        
        // Atualiza consumo total
        consumoTotal = eletrosSelecionados.reduce((total, eletro) => total + (eletro.ativo ? eletro.consumo : 0), 0);
        
        // Atualiza displays
        document.getElementById('consumoAtual').textContent = `Consumo: ${consumoTotal.toFixed(3)} kWh`;
        
        const horas = Math.floor(tempoDecorrido / 3600);
        const minutos = Math.floor((tempoDecorrido % 3600) / 60);
        const segundos = tempoDecorrido % 60;
        document.getElementById('tempoDecorrido').textContent = 
            `Tempo: ${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
        
    }, 1000);
}

function finalizarMonitoramento() {
    if (intervaloConsumo) {
        clearInterval(intervaloConsumo);
        intervaloConsumo = null;
    }
    
    // Calcula consumo final
    consumoTotal = eletrosSelecionados.reduce((total, eletro) => total + eletro.consumo, 0);
    
    // Atualiza resultados
    document.getElementById('totalKWh').textContent = consumoTotal.toFixed(3);
    mostrarConsumoPorAparelho();
    gerarSugestaoEconomia();
    criarGraficoPizza(); // ← ADICIONE ESTA LINHA
    
    // Mostra tela de resultados
    document.getElementById('monitoramento').classList.add('hidden');
    document.getElementById('resultado').classList.remove('hidden');
}

function mostrarConsumoPorAparelho() {
    const consumoDiv = document.getElementById('consumoPorAparelho');
    
    // Agrupa consumo por tipo de eletrodoméstico
    const consumoAgrupado = {};
    eletrosSelecionados.forEach(eletro => {
        if (eletro.consumo > 0) {
            if (!consumoAgrupado[eletro.nome]) {
                consumoAgrupado[eletro.nome] = 0;
            }
            consumoAgrupado[eletro.nome] += eletro.consumo;
        }
    });
    
    // Converte para array e ordena
    const aparelhosAgrupados = Object.entries(consumoAgrupado)
        .map(([nome, consumo]) => ({ nome, consumo }))
        .sort((a, b) => b.consumo - a.consumo);
    
    consumoDiv.innerHTML = aparelhosAgrupados.map(eletro => `
        <div class="d-flex justify-content-between align-items-center border-bottom py-2">
            <span>${eletro.nome}</span>
            <span class="fw-bold">${eletro.consumo.toFixed(3)} kWh</span>
        </div>
    `).join('');
}

function gerarSugestaoEconomia() {
    const consumoTotal = parseFloat(document.getElementById('totalKWh').textContent);
    const economiaPotencial = (consumoTotal * 0.1).toFixed(3);
    
    const sugestaoCompleta = `
        🎯 **PLANO DE ECONOMIA DE 10%** 🎯
        
        📊 Consumo atual: ${consumoTotal.toFixed(3)} kWh
        💰 Economia potencial: ${economiaPotencial} kWh
        
        ⚡ **AÇÕES RECOMENDADAS:**
        Observe o gráfico de pizza acima e identifique os eletromésticos 
        que mais consomem eenergia e analise o que poderia ser feiro  
        para diminuir este consumo, como por exemplo:
        • Reduzir tempo de uso de tederminados eletordomésticos 
        • Dae preferência a lâmpadas que consomem menos.
        • Concentrar o uso de alguns eletromésticos e um ou dos dias na semana.
        • Avalie se o gás não é fonte energia mais barata.
        • Faça o possível para usar luz natural durante o dia.
               
        💡 **BENEFÍCIO:** Economia de R$ ${(economiaPotencial * 0.85).toFixed(2)} por mês!
    `;
    
    document.getElementById('sugestaoEconomia').innerHTML = sugestaoCompleta.replace(/\n/g, '<br>');
    document.getElementById('economiaPotencial').textContent = economiaPotencial;
    
    return sugestaoCompleta;
}

// Opção mobile-friendly
function criarGraficoPizza() {
    const ctx = document.getElementById('graficoConsumo').getContext('2d');
    
    // Agrupa e soma consumo por tipo de eletrodoméstico
    const consumoAgrupado = {};
    eletrosSelecionados.forEach(eletro => {
        if (eletro.consumo > 0) {
            if (!consumoAgrupado[eletro.nome]) {
                consumoAgrupado[eletro.nome] = 0;
            }
            consumoAgrupado[eletro.nome] += eletro.consumo;
        }
    });
    
    // Converte para array e ordena por consumo (maior primeiro)
    const aparelhosAgrupados = Object.entries(consumoAgrupado)
        .map(([nome, consumo]) => ({ nome, consumo }))
        .sort((a, b) => b.consumo - a.consumo);
    
    // Prepara dados para o gráfico
    const labels = aparelhosAgrupados.map(eletro => eletro.nome);
    const dados = aparelhosAgrupados.map(eletro => eletro.consumo);
    
    // Cores para o gráfico
    const cores = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#8AC926', '#1982C4', '#6A4C93', '#F25C54', '#2A9D8F', '#E76F51',
        '#588157', '#3A86FF', '#FB5607', '#8338EC'
    ];
    
    // Cria o gráfico
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: dados,
                backgroundColor: cores,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 11,
                            weight: 'bold'
                        },
                        padding: 10,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            return data.labels.map((label, i) => {
                                const value = data.datasets[0].data[i];
                                const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                
                                return {
                                    text: `${label} (${percentage}%)`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    strokeStyle: data.datasets[0].borderColor[i],
                                    lineWidth: data.datasets[0].borderWidth[i],
                                    hidden: false,
                                    index: i
                                };
                            });
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            return `${label}: ${value.toFixed(2)} kWh`;
                        }
                    }
                }
            }
        }
    });
}


async function enviarEmailResultado() {
    const emailProfessor = document.getElementById('emailDestino').value;
    const nomeAluno = document.getElementById('nomeAluno').value;
    const emailAluno = document.getElementById('emailAluno').value;
    const mensagemAluno = document.getElementById('mensagemAluno').value;
    const emailStatus = document.getElementById('emailStatus');
    
    if (!nomeAluno) {
        emailStatus.innerHTML = '<div class="alert alert-warning">Digite seu nome para enviar!</div>';
        return;
    }

    // Prepara dados para o professor
    / Atualize os dados do email para incluir série e turma
const dadosProfessor = {
    to_email: emailProfessor,
    nome_aluno: nomeAluno,
    email_aluno: emailAluno || 'Não informado',
    serie_aluno: usuario.serie, // NOVO
    turma_aluno: usuario.turma, // NOVO
    consumo_total: consumoTotal.toFixed(3),
    sugestao: document.getElementById('sugestaoEconomia').textContent,
    mensagem_aluno: mensagemAluno,
    data: new Date().toLocaleDateString('pt-BR'),
    tipo: 'RELATORIO_PROFESSOR'
};

    // Prepara dados para o aluno (cópia)
    const dadosAluno = {
        to_email: emailAluno,
        nome_aluno: nomeAluno,
        consumo_total: consumoTotal.toFixed(3),
        sugestao: document.getElementById('sugestaoEconomia').textContent,
        mensagem_aluno: mensagemAluno,
        data: new Date().toLocaleDateString('pt-BR'),
        tipo: 'COPIA_ALUNO'
    };

    emailStatus.innerHTML = '<div class="alert alert-info">Enviando resultados...</div>';
    
    try {
        // Envia para o professor
        await fetch(SCRIPT_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dadosProfessor)
        });
        
        // Se o aluno informou email, envia cópia
        if (emailAluno) {
            await fetch(SCRIPT_URL, {
                method: 'POST',
                mode: 'no-cors',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosAluno)
            });
            
            emailStatus.innerHTML = `
                <div class="alert alert-success">
                    ✅ Resultado enviado para o professor e para seu email!
                </div>
            `;
        } else {
            emailStatus.innerHTML = `
                <div class="alert alert-success">
                    ✅ Resultado enviado para o professor!
                    <br><small>(Você não informou email para receber cópia)</small>
                </div>
            `;
        }
        
    } catch (error) {
        emailStatus.innerHTML = `
            <div class="alert alert-danger">
                ❌ Erro ao enviar. Tente novamente.
            </div>
        `;
    }
}

console.log('app.js carregado!');
