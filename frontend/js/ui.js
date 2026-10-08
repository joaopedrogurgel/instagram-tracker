function limparResultados() {
    document.getElementById('upload-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('mensagens').textContent = '';
    
    // Clear inputs
    ['seguidores_antigo', 'seguidores_novo', 'seguindo_antigo', 'seguindo_novo'].forEach(id => {
        document.getElementById(id).value = '';
    });
    
    document.getElementById('btn-comparar').disabled = true;
    document.getElementById('analises-indicador').textContent = 'Análises que serão geradas: Nenhuma';
}

function mostrarErro(mensagem) {
    document.getElementById('mensagens').textContent = mensagem;
}

function renderizarLista(perfis, container) {
    container.innerHTML = '';
    if (!perfis || perfis.length === 0) {
        const li = document.createElement('li');
        li.className = 'perfil-item';
        li.textContent = 'Nenhum perfil nesta lista.';
        container.appendChild(li);
        return;
    }

    perfis.forEach(p => {
        // If it's a "renomeado", the structure is slightly different
        const isRenomeado = p.username_antigo !== undefined;
        const perfilData = isRenomeado ? p.perfil : p;
        
        const li = document.createElement('li');
        li.className = 'perfil-item';
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'perfil-info';
        
        const unSpan = document.createElement('span');
        unSpan.className = 'perfil-username';
        if (isRenomeado) {
            unSpan.textContent = `${p.username_antigo} → ${p.username_novo}`;
        } else {
            unSpan.textContent = perfilData.username;
        }
        infoDiv.appendChild(unSpan);
        
        if (perfilData.nome) {
            const nomeSpan = document.createElement('span');
            nomeSpan.className = 'perfil-nome';
            nomeSpan.textContent = perfilData.nome;
            infoDiv.appendChild(nomeSpan);
        }
        
        if (perfilData.privado || perfilData.verificado) {
            const badgesDiv = document.createElement('div');
            badgesDiv.className = 'badges';
            if (perfilData.privado) {
                const b = document.createElement('span');
                b.className = 'badge';
                b.textContent = 'Privado';
                badgesDiv.appendChild(b);
            }
            if (perfilData.verificado) {
                const b = document.createElement('span');
                b.className = 'badge';
                b.textContent = 'Verificado';
                badgesDiv.appendChild(b);
            }
            infoDiv.appendChild(badgesDiv);
        }
        
        li.appendChild(infoDiv);
        
        if (perfilData.url) {
            const link = document.createElement('a');
            link.className = 'perfil-link';
            link.href = perfilData.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = 'abrir perfil ↗';
            li.appendChild(link);
        }
        
        container.appendChild(li);
    });
}
