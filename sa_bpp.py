import os, random, time, math, re, copy

DIRETORIO = r"C:\Users\Miguel Mota\Desktop\trabalho_valdisio"

arquivos = [
    "bpp_formato.txt", 
    "_BP-1_n50C1000.txt",
    "_BP-2_n100C1000.txt",
    "_BP-4_n200C1000.txt",
    "_BP-6_n500C150.rtf", 
    "_BP-7_n1000C150.rtf"
]

# extrai so os numeros do arquivo ignorando formatacao do rtf
def ler_arquivo(caminho):
    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
    
    nums = [int(x) for x in re.findall(r'\b\d+\b', txt)]
    if len(nums) < 2: return None, None, None
        
    n = nums[0]
    C = nums[1]
    itens = nums[2:2+n] 
    return n, C, itens

# heuristica first-fit decreasing pra solucao inicial
def ffd(itens, C):
    itens_ord = sorted(itens, reverse=True)
    bins = []
    for item in itens_ord:
        colocou = False
        for b in bins:
            if sum(b) + item <= C:
                b.append(item)
                colocou = True
                break
        if not colocou:
            bins.append([item])
    return bins

# perturba a solucao trocando um item de bin
def gera_vizinho(bins, C):
    novo = copy.deepcopy(bins)
    if len(novo) <= 1: return novo

    idx = random.randint(0, len(novo) - 1)
    if not novo[idx]: return novo
    
    item = random.choice(novo[idx])
    novo[idx].remove(item)
    
    colocou = False
    for i, b in enumerate(novo):
        if i != idx and sum(b) + item <= C:
            b.append(item)
            colocou = True
            break
            
    if not colocou:
        novo.append([item])
        
    return [b for b in novo if b]

# algoritmo principal do simulated annealing
def sa(itens, C, t0=100.0, alpha=0.95, iter_max=2500):
    sol_atual = ffd(itens, C)
    custo_atual = len(sol_atual)
    
    melhor_sol = copy.deepcopy(sol_atual)
    melhor_custo = custo_atual
    
    historico = [custo_atual] # salva todos os custos pra tabela
    
    temp = t0
    t_inicio = time.time()
    
    while temp > 1.0:
        for _ in range(iter_max):
            vizinho = gera_vizinho(sol_atual, C)
            custo_viz = len(vizinho)
            historico.append(custo_viz)
            
            delta = custo_viz - custo_atual
            
            # criterio de aceitacao do sa
            if delta < 0 or random.random() < math.exp(-delta / temp):
                sol_atual = vizinho
                custo_atual = custo_viz
                
                if custo_atual < melhor_custo:
                    melhor_sol = copy.deepcopy(sol_atual)
                    melhor_custo = custo_atual
                    
        temp *= alpha
        
    t_fim = time.time() - t_inicio
    return melhor_sol, melhor_custo, historico, t_fim

def main():
    print("-" * 90)
    print("INSTÂNCIA            | N     | C     | INICIAL | PIOR  | MÉDIA  | MELHOR  | % PERDA | TEMPO(s)")
    print("-" * 90)

    for arq in arquivos:
        caminho = os.path.join(DIRETORIO, arq)
        if not os.path.exists(caminho): continue
            
        n, C, itens = ler_arquivo(caminho)
        if n is None: continue

        melhor_global = None
        custo_global = float('inf')
        
        todos_custos = []
        tempos = []
        inicial_1 = None

        # roda 3 vezes como o prof pediu
        for rodada in range(3):
            sol, custo, hist, t = sa(itens, C)
            
            if rodada == 0: inicial_1 = hist[0]
                
            todos_custos.extend(hist)
            tempos.append(t)
            
            if custo < custo_global:
                custo_global = custo
                melhor_global = sol

        pior = max(todos_custos)
        melhor = min(todos_custos)
        media = sum(todos_custos) / len(todos_custos)
        t_medio = sum(tempos) / 3
        
        # calcula % de perda: (espaco total - peso total) / espaco total
        peso_total = sum(itens)
        espaco_total = len(melhor_global) * C
        perda = ((espaco_total - peso_total) / espaco_total) * 100

        nome = arq.split('_n')[0].replace('_', '') if '_n' in arq else "BP-0"
        
        print(f"{nome:<20} | {n:<5} | {C:<5} | {inicial_1:<7} | {pior:<5} | {media:<6.2f} | {melhor:<7} | {perda:>6.2f}% | {t_medio:<8.4f}")
        
        # gera os arquivos de distribuicao pra colocar no relatorio
        with open(os.path.join(DIRETORIO, f"resultado_distribuicao_{nome}.txt"), "w") as f:
            f.write(f"Resultado {nome}\nBins Usados: {melhor}\nPerda: {perda:.2f}%\n\n")
            for i, b in enumerate(melhor_global):
                f.write(f"Bin {i+1} ({sum(b)}/{C}): {b}\n")

if __name__ == "__main__":
    main()