// parseCSV simplificado. Suporta aspas, mas não quebras de linha dentro de aspas para manter simples.
function parseCSV(text) {
    const delimiter = text.indexOf(';') !== -1 ? ';' : ',';
    const lines = text.split(/\r?\n/).filter(l => l.trim() !== '');
    if (lines.length === 0) return [];

    const headers = lines[0].split(delimiter).map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
    
    // Identificar os índices das colunas que queremos
    const cols_to_keep = {
        'user_id': headers.findIndex(h => ['user id', 'userid', 'id'].includes(h.replace(/[_ -]/g, ''))),
        'username': headers.findIndex(h => ['username', 'usuario', 'user', 'handle'].includes(h.replace(/[_ -]/g, ''))),
        'fullname': headers.findIndex(h => ['fullname', 'nome', 'full name'].includes(h.replace(/[_ -]/g, '')))
    };

    if (cols_to_keep.username === -1) {
        throw new Error("Coluna Username não encontrada");
    }

    let output = "User Id,Username,Fullname\n";
    for (let i = 1; i < lines.length; i++) {
        // Split simples, ignorando vírgulas dentro de aspas não é totalmente trivial sem regex complexo,
        // mas para reduzir arquivo de IG vamos usar um split basico ou regex simples.
        // Regex para split por delimitador ignorando dentro de aspas:
        const re = new RegExp(`(?:^|${delimiter})(?=(?:[^"]*"[^"]*")*[^"]*$)(?![^"]*"[^"]*${delimiter})`, 'g');
        const parts = lines[i].split(re).map(p => p.startsWith(delimiter) ? p.substring(1) : p);
        
        const uid = cols_to_keep.user_id !== -1 && parts[cols_to_keep.user_id] ? parts[cols_to_keep.user_id].trim() : '';
        const un = parts[cols_to_keep.username] ? parts[cols_to_keep.username].trim() : '';
        const fn = cols_to_keep.fullname !== -1 && parts[cols_to_keep.fullname] ? parts[cols_to_keep.fullname].trim() : '';

        // Escapar aspas para CSV
        const escapeCSV = (val) => val.includes(',') || val.includes('"') ? `"${val.replace(/"/g, '""')}"` : val;
        
        output += `${escapeCSV(uid)},${escapeCSV(un)},${escapeCSV(fn)}\n`;
    }

    return new Blob([output], { type: 'text/csv' });
}

async function reduzirArquivo(file) {
    const text = await file.text();
    try {
        const reducedBlob = parseCSV(text);
        // Verificar tamanho original e reduzido (só para log)
        console.log(`Original: ${file.size} bytes, Reduzido: ${reducedBlob.size} bytes`);
        return new File([reducedBlob], file.name, { type: 'text/csv' });
    } catch (e) {
        // Em caso de erro no parser simplificado, devolve o arquivo original
        console.warn("Falha ao reduzir, enviando original", e);
        return file;
    }
}
