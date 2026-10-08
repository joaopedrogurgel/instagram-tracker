let analiseAtual = null;
let abaAtivaContexto = null; // 'seguidores', 'seguindo', 'cruzada'
let abaAtivaGrupo = null;
let listaExibida = [];

document.addEventListener('DOMContentLoaded', () => {
    const ids = ['seguidores_antigo', 'seguidores_novo', 'seguindo_antigo', 'seguindo_novo'];
    
    ids.forEach(id => {
        document.getElementById(id).addEventListener('change', atualizarBotaoComparar);
    });

    document.getElementById('btn-comparar').addEventListener('click', aoComparar);
    document.getElementById('btn-nova-analise').addEventListener('click', limparResultados);
    
    document.getElementById('busca').addEventListener('input', (e) => {
        const termo = e.target.value.toLowerCase();
        const filtrada = listaExibida.filter(p => {
            const un = p.username || p.username_novo;
            const nm = (p.nome || (p.perfil && p.perfil.nome)) || '';
            return un.toLowerCase().includes(termo) || nm.toLowerCase().includes(termo);
        });
        renderizarLista(filtrada, document.getElementById('lista-perfis'));
    });
    
    document.getElementById('btn-exportar').addEventListener('click', () => {
        if (!abaAtivaContexto || !abaAtivaGrupo) return;
        gerarCSV(listaExibida, `${abaAtivaContexto}_${abaAtivaGrupo}`);
    });
});

function atualizarBotaoComparar() {
    const f = {
        sa: document.getElementById('seguidores_antigo').files[0],
        sn: document.getElementById('seguidores_novo').files[0],
        pa: document.getElementById('seguindo_antigo').files[0],
        pn: document.getElementById('seguindo_novo').files[0]
    };

    const hasSeguidores = f.sa && f.sn;
    const hasSeguindo = f.pa && f.pn;
    const hasCruzada = f.sn && f.pn;

    let analises = [];
    if (hasSeguidores) analises.push("Seguidores");
    if (hasSeguindo) analises.push("Seguindo");
    if (hasCruzada) analises.push("Cruzada");

    const btn = document.getElementById('btn-comparar');
    const ind = document.getElementById('analises-indicador');

    if (analises.length > 0) {
        btn.disabled = false;
        ind.textContent = "Análises que serão geradas: " + analises.join(' · ');
    } else {
        btn.disabled = true;
        ind.textContent = "Análises que serão geradas: Nenhuma";
    }
}

async function aoComparar() {
    const f = {
        seguidores_antigo: document.getElementById('seguidores_antigo').files[0],
        seguidores_novo: document.getElementById('seguidores_novo').files[0],
        seguindo_antigo: document.getElementById('seguindo_antigo').files[0],
        seguindo_novo: document.getElementById('seguindo_novo').files[0]
    };

    document.getElementById('btn-comparar').disabled = true;
    document.getElementById('mensagens').textContent = 'Processando...';

    try {
        analiseAtual = await compararArquivos(f);
        exibirResultados(analiseAtual);
    } catch (e) {
        mostrarErro(e.mensagem || e.message || 'Erro desconhecido');
        document.getElementById('btn-comparar').disabled = false;
    }
}

function exibirResultados(dados) {
    document.getElementById('upload-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';
    
    const abasCtx = document.getElementById('abas-analise');
    abasCtx.innerHTML = '';
    
    let primeiraAba = null;
    
    dados.analises_executadas.forEach(ctx => {
        const btn = document.createElement('button');
        btn.className = 'tab';
        btn.textContent = ctx.charAt(0).toUpperCase() + ctx.slice(1);
        btn.onclick = () => selecionarContexto(ctx);
        abasCtx.appendChild(btn);
        if (!primeiraAba) primeiraAba = ctx;
    });
    
    if (primeiraAba) selecionarContexto(primeiraAba);
}

function selecionarContexto(ctx) {
    abaAtivaContexto = ctx;
    
    // Atualizar UI das abas de contexto
    Array.from(document.getElementById('abas-analise').children).forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase() === ctx);
    });
    
    const resumoPanel = document.getElementById('resumo');
    resumoPanel.innerHTML = '';
    
    const abasGrupo = document.getElementById('abas-grupo');
    abasGrupo.innerHTML = '';
    
    const analise = analiseAtual[ctx];
    const mapNomes = {
        "deixaram_de_seguir": "Deixaram de seguir",
        "novos_seguidores": "Novos seguidores",
        "deixei_de_seguir": "Deixei de seguir",
        "passei_a_seguir": "Passei a seguir",
        "mantidos": "Mantidos",
        "renomeados": "Renomeados",
        "mutuos": "Mútuos",
        "nao_retribuem": "Não seguem de volta",
        "fas": "Fãs"
    };

    // Construir resumo e abas de grupo
    let primeiroGrupo = null;
    
    Object.keys(analise.resumo).forEach(k => {
        if (k.startsWith('total') || k === 'houve_mudanca') return;
        if (analise.resumo[k] === null || analise.resumo[k] === undefined) return;
        
        // Resumo item
        const div = document.createElement('div');
        div.className = 'resumo-item';
        div.innerHTML = `<span>${mapNomes[k] || k}</span><span class="resumo-valor">${analise.resumo[k]}</span>`;
        resumoPanel.appendChild(div);
        
        // Aba de grupo
        if (analise[k] !== undefined) {
            const btn = document.createElement('button');
            btn.className = 'tab';
            btn.textContent = mapNomes[k] || k;
            btn.onclick = () => selecionarGrupo(k);
            abasGrupo.appendChild(btn);
            if (!primeiroGrupo) primeiroGrupo = k;
        }
    });

    if (!analise.resumo.houve_mudanca && ctx !== 'cruzada') {
        mostrarErro('Nenhuma mudança entre os arquivos.');
    } else {
        document.getElementById('mensagens').textContent = '';
    }

    if (primeiroGrupo) selecionarGrupo(primeiroGrupo);
}

function selecionarGrupo(grupo) {
    abaAtivaGrupo = grupo;
    
    Array.from(document.getElementById('abas-grupo').children).forEach(btn => {
        // Simple comparison with mapping
        const mapNomes = {
            "deixaram_de_seguir": "Deixaram de seguir",
            "novos_seguidores": "Novos seguidores",
            "deixei_de_seguir": "Deixei de seguir",
            "passei_a_seguir": "Passei a seguir",
            "mantidos": "Mantidos",
            "renomeados": "Renomeados",
            "mutuos": "Mútuos",
            "nao_retribuem": "Não seguem de volta",
            "fas": "Fãs"
        };
        btn.classList.toggle('active', btn.textContent === mapNomes[grupo]);
    });
    
    listaExibida = analiseAtual[abaAtivaContexto][grupo];
    document.getElementById('busca').value = '';
    renderizarLista(listaExibida, document.getElementById('lista-perfis'));
}
