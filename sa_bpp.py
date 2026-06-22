import os, random, time, math, re, copy

DIRETORIO = os.path.dirname(os.path.abspath(__file__))

arquivos = [
    "bpp_formato.txt", 
    "_BP-1_n50C1000.txt",
    "_BP-2_n100C1000.txt",
    "_BP-4_n200C1000.txt",
    "_BP-6_n500C150.rtf", 
    "_BP-7_n1000C150.rtf"
]

# --- 1. LEITURA DE ARQUIVO ---
def ler_arquivo(caminho):
    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
    
    nums = [int(x) for x in re.findall(r'\b\d+\b', txt)]
    if len(nums) < 2: 
        return 0, 0, []
        
    n = nums[0]
    C = nums[1]
    itens = nums[2:2+n] 
    return n, C, itens

# --- 2. HEURÍSTICAS AUXILIARES BASE ---

def next_fit(itens, C):
    bins = []
    for item in itens:
        if not bins or sum(bins[-1]) + item > C:
            bins.append([item])
        else:
            bins[-1].append(item)
    return bins

def first_fit(itens, C):
    bins = []
    for item in itens:
        colocou = False
        for b in bins:
            if sum(b) + item <= C:
                b.append(item)
                colocou = True
                break
        if not colocou:
            bins.append([item])
    return bins

def last_fit(itens, C):
    bins = []
    for item in itens:
        colocou = False
        for b in reversed(bins):
            if sum(b) + item <= C:
                b.append(item)
                colocou = True
                break
        if not colocou:
            bins.append([item])
    return bins

def best_fit(itens, C):
    bins = []
    for item in itens:
        melhor_bin = None
        menor_sobra = C + 1
        for b in bins:
            sobra = C - (sum(b) + item)
            if sobra >= 0 and sobra < menor_sobra:
                menor_sobra = sobra
                melhor_bin = b
        if melhor_bin is not None:
            melhor_bin.append(item)
        else:
            bins.append([item])
    return bins

def worst_fit(itens, C):
    bins = []
    for item in itens:
        pior_bin = None
        maior_sobra = -1
        for b in bins:
            sobra = C - (sum(b) + item)
            if sobra >= 0 and sobra > maior_sobra:
                maior_sobra = sobra
                pior_bin = b
        if pior_bin is not None:
            pior_bin.append(item)
        else:
            bins.append([item])
    return bins

# --- 3. GERENCIADOR DE ORDENAÇÃO (D e I) ---
def gerar_solucao_inicial(tipo_heuristica, itens, C):
    if tipo_heuristica.endswith("D"):
        itens_processados = sorted(itens, reverse=True)
    elif tipo_heuristica.endswith("I"):
        itens_processados = sorted(itens)
    else:
        itens_processados = list(itens)
        
    nome_base = tipo_heuristica[:2]
    if nome_base == "NF": return next_fit(itens_processados, C)
    if nome_base == "FF": return first_fit(itens_processados, C)
    if nome_base == "LF": return last_fit(itens_processados, C) 
    if nome_base == "BF": return best_fit(itens_processados, C)
    if nome_base == "WF": return worst_fit(itens_processados, C)
    return first_fit(itens_processados, C)

# --- 4. MOVIMENTO DE VIZINHANÇA ---
def gera_vizinho(bins, C):
    novo = copy.deepcopy(bins)
    if len(novo) <= 1: return novo

    idx_origem = random.randint(0, len(novo) - 1)
    if not novo[idx_origem]: return novo
    
    item = random.choice(novo[idx_origem])
    novo[idx_origem].remove(item)
    
    bins_destino = list(range(len(novo)))
    bins_destino.remove(idx_origem)
    random.shuffle(bins_destino)
    
    colocou = False
    for i in bins_destino:
        if sum(novo[i]) + item <= C:
            novo[i].append(item)
            colocou = True
            break
            
    if not colocou:
        novo.append([item])
        
    return [b for b in novo if b]

# --- 5. SIMULATED ANNEALING ---
def sa(itens, C, heuristica_inicial="FFD", t0=100.0, alpha=0.95, iter_max=400):
    sol_atual = gerar_solucao_inicial(heuristica_inicial, itens, C)
    custo_atual = len(sol_atual)
    
    melhor_sol = copy.deepcopy(sol_atual)
    melhor_custo = custo_atual
    
    temp = t0
    t_inicio = time.time()
    
    while temp > 0.01:
        for _ in range(iter_max):
            vizinho = gera_vizinho(sol_atual, C)
            custo_viz = len(vizinho)
            
            delta = custo_viz - custo_atual
            
            if delta < 0 or random.random() < math.exp(-delta / temp):
                sol_atual = vizinho
                custo_atual = custo_viz
                
                if custo_atual < melhor_custo:
                    melhor_sol = copy.deepcopy(sol_atual)
                    melhor_custo = custo_atual
                    
        temp *= alpha
        
    t_fim = time.time() - t_inicio
    return melhor_sol, melhor_custo, len(gerar_solucao_inicial(heuristica_inicial, itens, C)), t_fim

# --- 6. EXECUÇÃO PRINCIPAL ---
def main():
    # Muda a heurística para testar o comportamento (NFD, FFD, LFD, BFD, WFD, NFI, FFI, LFI, BFI e WFI)
    HEURISTICA_TESTADA = "LFI" 
    
    print("=" * 100)
    print(f"RODANDO SIMULATED ANNEALING COM HEURÍSTICA INICIAL: {HEURISTICA_TESTADA}")
    print("=" * 100)
    print(f"{'INSTÂNCIA':<20} | {'N':<5} | {'C':<5} | {'INICIAL':<7} | {'PIOR':<5} | {'MÉDIA':<6} | {'MELHOR':<7} | {'% PERDA':<7} | {'TEMPO(s)':<8}")
    print("-" * 100)

    for arq in arquivos:
        caminho = os.path.join(DIRETORIO, arq)
        if not os.path.exists(caminho): continue
            
        n, C, itens = ler_arquivo(caminho)
        if n == 0 or C == 0 or not itens: continue

        melhor_global = [] 
        custo_global = float('inf')
        
        custos_finais_rodadas = []
        tempos = []
        custo_inicial_heuristica = 0

        for rodada in range(3):
            sol, custo, c_inicial, t = sa(itens, C, heuristica_inicial=HEURISTICA_TESTADA)
            
            if rodada == 0: 
                custo_inicial_heuristica = c_inicial
                
            custos_finais_rodadas.append(custo)
            tempos.append(t)
            
            if custo < custo_global:
                custo_global = custo
                melhor_global = sol

        pior = max(custos_finais_rodadas)
        melhor = min(custos_finais_rodadas)
        media = sum(custos_finais_rodadas) / len(custos_finais_rodadas)
        t_medio = sum(tempos) / len(tempos)
        
        peso_total = sum(itens)
        espaco_total = len(melhor_global) * C
        perda = ((espaco_total - peso_total) / espaco_total) * 100 if espaco_total > 0 else 0

        nome = arq.split('_n')[0].replace('_', '') if '_n' in arq else "BP-0"
        
        print(f"{nome:<20} | {n:<5} | {C:<5} | {custo_inicial_heuristica:<7} | {pior:<5} | {media:<6.2f} | {melhor:<7} | {perda:>6.2f}% | {t_medio:<8.4f}")
        
        with open(os.path.join(DIRETORIO, f"resultado_{HEURISTICA_TESTADA}_{nome}.txt"), "w") as f:
            f.write(f"Resultado {nome} com Inicial {HEURISTICA_TESTADA}\nBins Usados: {melhor}\nPerda: {perda:.2f}%\n\n")
            for i, b in enumerate(melhor_global):
                f.write(f"Bin {i+1} ({sum(b)}/{C}): {b}\n")

if __name__ == "__main__":
    main()