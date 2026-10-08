function gerarCSV(dados, nomeArquivo) {
    if (!dados || dados.length === 0) return;

    let csvContent = "User Id,Username,Fullname,Privado,Verificado\n";

    dados.forEach(p => {
        // Proteção contra CSV injection prefixando com apóstrofo
        let username = p.username;
        if (/^[=+\-@]/.test(username)) username = "'" + username;
        
        let nome = p.nome || '';
        if (/^[=+\-@]/.test(nome)) nome = "'" + nome;

        const escapeCSV = (val) => {
            val = String(val);
            if (val.includes(',') || val.includes('"')) {
                return `"${val.replace(/"/g, '""')}"`;
            }
            return val;
        };

        const linha = [
            escapeCSV(p.user_id || ''),
            escapeCSV(username),
            escapeCSV(nome),
            p.privado ? "YES" : "NO",
            p.verificado ? "YES" : "NO"
        ].join(',');

        csvContent += linha + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${nomeArquivo}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
