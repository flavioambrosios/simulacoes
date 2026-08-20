$ErrorActionPreference = 'Stop'

$root = 'C:\Users\flavi\OneDrive\simulacoes'

$pairs = @(
    @('Concepcao','Concepção'), @('concepcao','concepção'),
    @('O que e','O que é'), @('o que e','o que é'),
    @('Qual e','Qual é'), @('qual e','qual é'),
    @('Essa e','Essa é'), @('essa e','essa é'),
    @('Ele e','Ele é'), @('ele e','ele é'),
    @('Nao e','Não é'), @('nao e','não é'),
    @('Conclusao','Conclusão'), @('conclusao','conclusão'),
    @('planejamento pedagogico','planejamento pedagógico'),
    @('supervisao humana','supervisão humana'),
    @('Simulacao','Simulação'), @('simulacao','simulação'),
    @('Simulacoes','Simulações'), @('simulacoes','simulações'),
    @('Fisica','Física'), @('fisica','física'),
    @('Optica','Óptica'), @('optica','óptica'),
    @('Pagina','Página'), @('pagina','página'),
    @('Paginas','Páginas'), @('paginas','páginas'),
    @('Secao','Seção'), @('secao','seção'),
    @('Colecoes','Coleções'), @('colecoes','coleções'),
    @('Radiacao','Radiação'), @('radiacao','radiação'),
    @('Inducao','Indução'), @('inducao','indução'),
    @('Fenomeno','Fenômeno'), @('fenomeno','fenômeno'),
    @('Mecanico','Mecânico'), @('mecanico','mecânico'),
    @('Atomo','Átomo'), @('atomo','átomo'),
    @('Atomica','Atômica'), @('atomica','atômica'),
    @('Eletrico','Elétrico'), @('eletrico','elétrico'),
    @('Eletricos','Elétricos'), @('eletricos','elétricos'),
    @('Forca','Força'), @('forca','força'),
    @('Observacoes','Observações'), @('observacoes','observações'),
    @('Exercicios','Exercícios'), @('exercicios','exercícios'),
    @('Versao','Versão'), @('versao','versão'),
    @('Rapido','Rápido'), @('rapido','rápido'),
    @('Catalogo','Catálogo'), @('catalogo','catálogo'),
    @('Incorporacao','Incorporação'), @('incorporacao','incorporação'),
    @('Area','Área'), @('area','área'),
    @('Areas','Áreas'), @('areas','áreas'),
    @('Relacao','Relação'), @('relacao','relação'),
    @('Variacao','Variação'), @('variacao','variação'),
    @('Diferenca','Diferença'), @('diferenca','diferença'),
    @('Diferencas','Diferenças'), @('diferencas','diferenças'),
    @('Termica','Térmica'), @('termica','térmica'),
    @('Termicas','Térmicas'), @('termicas','térmicas'),
    @('Conversoes','Conversões'), @('conversoes','conversões'),
    @('Interpretacao','Interpretação'), @('interpretacao','interpretação'),
    @('Exploracao','Exploração'), @('exploracao','exploração'),
    @('Maquina','Máquina'), @('maquina','máquina'),
    @('Ligacao','Ligação'), @('ligacao','ligação'),
    @('Conexao','Conexão'), @('conexao','conexão'),
    @('Equacoes','Equações'), @('equacoes','equações'),
    @('Reflexao','Reflexão'), @('reflexao','reflexão'),
    @('Refracao','Refração'), @('refracao','refração'),
    @('Formacao','Formação'), @('formacao','formação'),
    @('Quantico','Quântico'), @('quantico','quântico'),
    @('Aplicacoes','Aplicações'), @('aplicacoes','aplicações'),
    @('Fotossintese','Fotossíntese'), @('fotossintese','fotossíntese'),
    @('Experiencia','Experiência'), @('experiencia','experiência'),
    @('Niveis','Níveis'), @('niveis','níveis'),
    @('Emissao','Emissão'), @('emissao','emissão'),
    @('Eletron','Elétron'), @('eletron','elétron'),
    @('Eletrons','Elétrons'), @('eletrons','elétrons'),
    @('Eletrica','Elétrica'), @('eletrica','elétrica'),
    @('Espectrometro','Espectrômetro'), @('espectrometro','espectrômetro'),
    @('Trajetorias','Trajetórias'), @('trajetorias','trajetórias'),
    @('Razao','Razão'), @('razao','razão'),
    @('Dilatacao','Dilatação'), @('dilatacao','dilatação'),
    @('Contracao','Contração'), @('contracao','contração'),
    @('Graficos','Gráficos'), @('graficos','gráficos'),
    @('Animacao','Animação'), @('animacao','animação'),
    @('Particulas','Partículas'), @('particulas','partículas'),
    @('Sensivel','Sensível'), @('sensivel','sensível'),
    @('Mudancas','Mudanças'), @('mudancas','mudanças'),
    @('Foton','Fóton'), @('foton','fóton'),
    @('Fotons','Fótons'), @('fotons','fótons'),
    @('Propagacao','Propagação'), @('propagacao','propagação'),
    @('Visivel','Visível'), @('visivel','visível'),
    @('Absorcao','Absorção'), @('absorcao','absorção'),
    @('Cenarios','Cenários'), @('cenarios','cenários'),
    @('Frequencia','Frequência'), @('frequencia','frequência'),
    @('Tensao','Tensão'), @('tensao','tensão'),
    @('Resistencia','Resistência'), @('resistencia','resistência'),
    @('Potencia','Potência'), @('potencia','potência'),
    @('Transicao','Transição'), @('transicao','transição'),
    @('Eficiencia','Eficiência'), @('eficiencia','eficiência'),
    @('Responsavel','Responsável'), @('responsavel','responsável'),
    @('Numero','Número'), @('numero','número'),
    @('Formula','Fórmula'), @('formula','fórmula'),
    @('Pratica','Prática'), @('pratica','prática'),
    @('Util','Útil'), @('util','útil'),
    @('Tambem','Também'), @('tambem','também'),
    @('Nao','Não'), @('nao','não'),
    @('Nivel','Nível'), @('nivel','nível'),
    @('Uteis','Úteis'), @('uteis','úteis'),
    @('Praticas','Práticas'), @('praticas','práticas'),
    @('Referencias','Referências'), @('referencias','referências'),
    @('Bibliograficas','Bibliográficas'), @('bibliograficas','bibliográficas'),
    @('Moleculas','Moléculas'), @('moleculas','moléculas'),
    @('Energeticos','Energéticos'), @('energeticos','energéticos'),
    @('Contemporanea','Contemporânea'), @('contemporanea','contemporânea'),
    @('Medio','Médio'), @('medio','médio'),
    @('Introducao','Introdução'), @('introducao','introdução'),
    @('Lampadas','Lâmpadas'), @('lampadas','lâmpadas'),
    @('Semaforos','Semáforos'), @('semaforos','semáforos'),
    @('Capitulo','Capítulo'), @('capitulo','capítulo'),
    @('Serie','Série'), @('serie','série'),
    @('Termodinamica','Termodinâmica'), @('termodinamica','termodinâmica'),
    @('Magnetico','Magnético'), @('magnetico','magnético'),
    @('Magnetica','Magnética'), @('magnetica','magnética'),
    @('Instrucoes','Instruções'), @('instrucoes','instruções'),
    @('Propria','Própria'), @('propria','própria'),
    @('Opcoes','Opções'), @('opcoes','opções'),
    @('Avaliacoes','Avaliações'), @('avaliacoes','avaliações')
)

function Replace-Words([string]$text) {
    $out = $text
    foreach ($pair in $pairs) {
        $from = $pair[0]
        $to = $pair[1]
        $rx = '\b' + [Regex]::Escape($from) + '\b'
        $out = [Regex]::Replace($out, $rx, $to)
    }
    return $out
}

function Normalize-JsStrings([string]$code) {
    $regex = [Regex]::new('''((?:\\.|[^''\\])*)''|"((?:\\.|[^"\\])*)"|`((?:\\.|[^`\\])*)`')
    return $regex.Replace($code, {
        param($m)
        $raw = $m.Value
        $q = $raw.Substring(0,1)
        $inner = $raw.Substring(1, $raw.Length - 2)

        # Só mexe em frases com espaço (texto de interface), evitando IDs/chaves/rotas.
        if ($inner -notmatch '\s') { return $raw }

        $newInner = Replace-Words $inner
        return $q + $newInner + $q
    })
}

function Process-HtmlScripts([string]$html) {
    $scriptBlockRegex = [Regex]'(?is)<script\b[^>]*>.*?</script>'
    $matches = $scriptBlockRegex.Matches($html)
    if ($matches.Count -eq 0) {
        return Replace-Words $html
    }

    $parts = New-Object System.Collections.Generic.List[string]
    $cursor = 0
    foreach ($m in $matches) {
        if ($m.Index -gt $cursor) {
            $parts.Add((Replace-Words $html.Substring($cursor, $m.Index - $cursor)))
        }

        $block = $m.Value
        $innerRegex = [Regex]'(?is)^(<script\\b[^>]*>)(.*?)(</script>)$'
        $innerMatch = $innerRegex.Match($block)
        if (-not $innerMatch.Success) {
            $parts.Add($block)
        } else {
            $open = $innerMatch.Groups[1].Value
            $code = $innerMatch.Groups[2].Value
            $close = $innerMatch.Groups[3].Value
            $newCode = Normalize-JsStrings $code
            $parts.Add($open + $newCode + $close)
        }

        $cursor = $m.Index + $m.Length
    }

    if ($cursor -lt $html.Length) {
        $parts.Add((Replace-Words $html.Substring($cursor)))
    }

    return ($parts -join '')
}

$files = Get-ChildItem -Path $root -Recurse -File | Where-Object {
    ($_.Extension -in '.html', '.js') -and
    ($_.FullName -notmatch '\\.git\\') -and
    ($_.FullName -notmatch '\\_shared\\backups\\') -and
    ($_.Name -notmatch 'backup') -and
    ($_.Name -notmatch '^_temp_')
}

$changed = New-Object System.Collections.Generic.List[string]
foreach ($f in $files) {
    $old = Get-Content -Path $f.FullName -Raw -Encoding UTF8
    $new = $old

    if ($f.Extension -eq '.html') {
        $new = Process-HtmlScripts $old
    } else {
        $new = Normalize-JsStrings $old
    }

    if ($new -ne $old) {
        Set-Content -Path $f.FullName -Value $new -Encoding UTF8
        $changed.Add(([IO.Path]::GetRelativePath($root, $f.FullName).Replace('\\', '/')))
    }
}

"ARQUIVOS ALTERADOS: $($changed.Count)"
$changed | Sort-Object
