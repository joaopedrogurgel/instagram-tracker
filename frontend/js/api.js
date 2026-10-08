async function compararArquivos(filesObj) {
    const formData = new FormData();
    
    for (const [key, file] of Object.entries(filesObj)) {
        if (file) {
            const reducedFile = await reduzirArquivo(file);
            formData.append(key, reducedFile);
        }
    }

    const response = await fetch('/comparar', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        let erro;
        try {
            erro = await response.json();
        } catch(e) {
            throw new Error("Erro na comunicação com o servidor.");
        }
        throw erro.erro;
    }

    return await response.json();
}
