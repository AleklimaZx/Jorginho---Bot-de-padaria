from flask import Flask, request, Response
from datetime import datetime, timedelta
import re
import gspread
from google.oauth2.service_account import Credentials
import requests
import unicodedata # Adicionado para normalização de texto

app = Flask(__name__)

# Dados na memória (idealmente seriam persistidos em um banco de dados ou carregados da planilha)
# Adicionados alguns dados iniciais para facilitar o teste do relatório
vendas = [
    {'produto': 'pao', 'quantidade': 5, 'valor': 7.50, 'custo_total': 3.00, 'fiado': False, 'cliente': None, 'data': datetime.now() - timedelta(hours=2)},
    {'produto': 'cafe', 'quantidade': 2, 'valor': 5.00, 'custo_total': 2.00, 'fiado': False, 'cliente': None, 'data': datetime.now() - timedelta(hours=1)},
]
despesas = [
    {'descricao': 'agua', 'valor': 10.00, 'data': datetime.now() - timedelta(hours=3)}, # Exemplo de despesa do dia atual
    {'descricao': 'eletricidade', 'valor': 50.00, 'data': datetime.now() - timedelta(days=10)},
]
fiados = []
pagamentos_fiado = []

# Função para normalizar texto (mantida para uso geral, mas para produtos, usaremos o alias)
def normalize_text(text):
    text = text.lower().strip()
    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Pode adicionar regras de singularização mais complexas aqui se necessário para outros usos
    return text

# Mapeamento de termos para produtos base (para lidar com plurais, acentos e sinônimos)
produtos_alias = {
    'pao': 'pao',
    'pães': 'pao',
    'paes': 'pao',
    'leite': 'leite',
    'cafe': 'cafe',
    'cafés': 'cafe',
    'cafes': 'cafe',
    'agua': 'agua',
    'águas': 'agua',
    'aguas': 'agua',
    # Adicione mais aliases conforme necessário
    # Ex: 'refrigerante': 'refrigerante', 'refrigerantes': 'refrigerante'
}

# Informações de preço e custo dos produtos base (chaves são as formas normalizadas)
produtos_info = {
    'pao': {'preco': 1.50, 'custo': 0.60},
    'leite': {'preco': 3.00, 'custo': 1.50},
    'cafe': {'preco': 2.50, 'custo': 1.00},
    'agua': {'preco': 2.00, 'custo': 0.80}, 
}

# Novo mapeamento para pluralização e acentuação das palavras a serem exibidas na resposta
plural_forms = {
    'pao': {'singular': 'pão', 'plural': 'pães'},
    'cafe': {'singular': 'café', 'plural': 'cafés'},
    'leite': {'singular': 'leite', 'plural': 'leites'},
    'agua': {'singular': 'água', 'plural': 'águas'},
    # Adicione mais produtos conforme necessário
}

# Função auxiliar para obter o nome do produto no singular ou plural com acento
def get_product_display_name(quantidade, produto_base):
    forms = plural_forms.get(produto_base)
    if not forms:
        # Se não tiver uma forma específica, tenta adicionar 's' para plural e usa a original como singular
        if quantidade > 1:
            return produto_base + 's' if not produto_base.endswith('s') else produto_base
        return produto_base
    
    if quantidade == 1:
        return forms['singular']
    else:
        return forms['plural']

# === Conectar à Planilha ===
def conectar_planilha():
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_url('https://docs.google.com/spreadsheets/d/1DUj0TDw2xBU1o6oufZnbrXkRdpOcVb5WMzpn0X4b8yQ/edit')
    return planilha

# === Verificar conexão com internet ===
def verificar_conexao():
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    except requests.ConnectionError: # Especificar o tipo de erro para melhor tratamento
        print("Erro de conexão com a internet.")
        return False
    except Exception as e: # Capturar outras exceções
        print(f"Ocorreu um erro ao verificar a conexão: {e}")
        return False

# === Registrar dados na planilha ===
def registrar_venda(venda):
    if verificar_conexao():
        try:
            planilha = conectar_planilha()
            aba = planilha.worksheet('Vendas')
            aba.append_row([str(venda['data']), venda['produto'], venda['quantidade'], venda['valor'],
                            venda['custo_total'], 'Fiado' if venda['fiado'] else 'À vista', venda['cliente'] or ""])
            print(f"Venda de {venda['produto']} registrada na planilha.")
        except Exception as e:
            print(f"Erro ao registrar venda na planilha: {e}")
    else:
        print("Sem conexão para registrar venda na planilha.")

def registrar_fiado(venda):
    if verificar_conexao():
        try:
            planilha = conectar_planilha()
            aba = planilha.worksheet('Fiado')
            aba.append_row([str(venda['data']), venda['cliente'], venda['produto'], venda['quantidade'],
                            venda['valor'], venda['custo_total'], "Não"])
            print(f"Fiado de {venda['produto']} para {venda['cliente']} registrado na planilha.")
        except Exception as e:
            print(f"Erro ao registrar fiado na planilha: {e}")
    else:
        print("Sem conexão para registrar fiado na planilha.")

def registrar_despesa(desp):
    if verificar_conexao():
        try:
            planilha = conectar_planilha()
            aba = planilha.worksheet('Despesas')
            aba.append_row([str(desp['data']), desp['descricao'], desp['valor']])
            print(f"Despesa de {desp['descricao']} registrada na planilha.")
        except Exception as e:
            print(f"Erro ao registrar despesa na planilha: {e}")
    else:
        print("Sem conexão para registrar despesa na planilha.")

def registrar_pagamento(pag):
    if verificar_conexao():
        try:
            planilha = conectar_planilha()
            aba = planilha.worksheet('Pagamentos Fiado')
            aba.append_row([str(pag['data']), pag['cliente'], pag['valor']])
            print(f"Pagamento de {pag['cliente']} registrado na planilha.")
        except Exception as e:
            print(f"Erro ao registrar pagamento na planilha: {e}")
    else:
        print("Sem conexão para registrar pagamento na planilha.")

# === Aplicar pagamento fiado ===
def aplicar_pagamento_fiado(cliente, valor_pago):
    # Buscar fiados pendentes para o cliente
    pendentes = [f for f in fiados if f['cliente'].lower() == cliente.lower() and not f.get('pago')]
    
    # Sort by date to pay older debts first
    pendentes.sort(key=lambda x: x['data']) 

    for f in pendentes:
        if valor_pago >= f['valor']:
            f['pago'] = True
            valor_pago -= f['valor']
            print(f"Fiado de R${f['valor']:.2f} de {f['produto']} para {f['cliente']} marcado como pago.")
        else:
            f['valor'] -= valor_pago
            print(f"Restam R${f['valor']:.2f} no fiado de {f['produto']} para {f['cliente']}.")
            valor_pago = 0
        if valor_pago == 0:
            break
    
    if valor_pago > 0:
        print(f"Sobrou R${valor_pago:.2f} do pagamento de {cliente}. Não há mais fiados pendentes para cobrir.")


# === Funções auxiliares ===
def formatar_venda(v):
    fiado_str = f" - Fiado para {v.get('cliente', '').capitalize()}" if v.get('fiado') else ""
    data = datetime.strftime(v['data'], "%d/%m")
    display_name = get_product_display_name(v['quantidade'], v['produto'])
    return f"[{data}] {display_name.capitalize()}: R${v['valor']:.2f} (Custo: R${v['custo_total']:.2f}){fiado_str}"

def formatar_fiado(f):
    pago = "✅ Pago" if f.get('pago', False) else "❌ Em aberto"
    data = datetime.strftime(f['data'], "%d/%m")
    display_name = get_product_display_name(f['quantidade'], f['produto'])
    return f"[{data}] {f['cliente'].capitalize()} - {display_name.capitalize()}: R${f['valor']:.2f} ({pago})"

def gerar_relatorio_fiado():
    if not fiados:
        return "📜 Nenhum fiado registrado."
    
    relatorio = "📜 Fiados em aberto:\n\n"
    fiados_em_aberto = [f for f in fiados if not f.get('pago', False)]
    
    if not fiados_em_aberto:
        return "📜 Nenhum fiado em aberto no momento."

    # Agrupar fiados por cliente para um relatório mais conciso
    fiado_por_cliente = {}
    for f in fiados_em_aberto:
        cliente = f['cliente'].capitalize()
        if cliente not in fiado_por_cliente:
            fiado_por_cliente[cliente] = 0
        fiado_por_cliente[cliente] += f['valor']
    
    for cliente, total_fiado in fiado_por_cliente.items():
        relatorio += f"Cliente: {cliente} - Total Fiado: R${total_fiado:.2f}\n"
    
    relatorio += "\nDetalhes:\n"
    for f in fiados_em_aberto:
        relatorio += formatar_fiado(f) + "\n"
    
    return relatorio


def gerar_relatorio(periodo):
    hoje = datetime.now()
    if periodo == 'diario':
        data_limite = hoje.date()
    elif periodo == 'semanal':
        data_limite = (hoje - timedelta(days=7)).date()
    elif periodo == 'mensal':
        data_limite = (hoje - timedelta(days=30)).date()
    else:
        return "❌ Período inválido."

    vendas_periodo = [v for v in vendas if v['data'].date() >= data_limite and not v.get('fiado', False)]
    despesas_periodo = [d for d in despesas if d['data'].date() >= data_limite]

    total_vendas = sum(v['valor'] for v in vendas_periodo)
    total_custo = sum(v['custo_total'] for v in vendas_periodo)
    total_despesas = sum(d['valor'] for d in despesas_periodo)

    lucro = total_vendas - total_custo
    saldo = lucro - total_despesas

    relatorio = f"\n📊 Relatório {periodo.capitalize()}\n\n"
    relatorio += "Vendas à vista:\n"
    relatorio += "\n".join(formatar_venda(v) for v in vendas_periodo) or "Nenhuma"
    relatorio += f"\n\n💵 Total Vendas: R${total_vendas:.2f}\n"
    relatorio += f"💸 Custos: R${total_custo:.2f}\n"
    relatorio += f"📈 Lucro: R${lucro:.2f}\n"
    relatorio += f"📉 Despesas: R${total_despesas:.2f}\n"
    relatorio += f"💰 Saldo Final: R${saldo:.2f}"
    return relatorio

# === Rota principal ===
@app.route('/mensagem', methods=['POST'])
def mensagem():
    texto_original = request.form.get('Body', '').strip()
    texto = texto_original.lower() # Convert to lowercase for initial matching
    agora = datetime.now()

    # Regex patterns (updated for precision and to accept comma or dot for decimals)
    # Note: Using '(.+?)' for product/description that can be multiple words.
    
    # Despesas explícitas: "gastei 15,30 com água", "gastei 50 com material de limpeza"
    despesa_explicita = re.match(r'gastei (\d+(?:[.,]\d+)?) (?:com|em) (.+)', texto)
    # Despesas implícitas: "100 reais com água", "30.50 com comida"
    despesa_implicita = re.match(r'(\d+(?:[.,]\d+)?) (?:reais com|com|em) (.+)', texto)
    # Pagamentos de fiado: "João pagou 10 reais", "Maria pagou 25,50"
    pagamento = re.match(r'(.+) pagou (\d+(?:[.,]\d+)?) reais', texto)
    # Vendas por quantidade: "vendi 2 pao", "vendi 3 cafés fiado para joão"
    venda_qtd = re.match(r'vendi (\d+) (.+?)(?: fiado para (.+))?$', texto)
    # Vendas por valor: "vendi 30,50 reais de leite", "vendi 100.00 reais de cafés fiado para maria"
    venda_valor = re.match(r'vendi (\d+(?:[.,]\d+)?) reais de (.+?)(?: fiado para (.+))?$', texto)


    # --- Ordem de verificação: Despesas e Pagamentos primeiro para evitar conflitos ---
    
    # --- Despesa Explícita ("gastei X com Y") ---
    if despesa_explicita:
        valor_str, descricao_raw = despesa_explicita[1], despesa_explicita[2]
        valor = float(valor_str.replace(',', '.'))
        descricao = descricao_raw.strip()
        
        desp = {'descricao': descricao, 'valor': valor, 'data': agora}
        despesas.append(desp)
        registrar_despesa(desp)
        return Response(f"🧾 Despesa de R${valor:.2f} com '{descricao}' registrada!", status=200, mimetype='text/plain')

    # --- Despesa Implícita ("X reais com Y" ou "X com Y") ---
    elif despesa_implicita:
        valor_str, descricao_raw = despesa_implicita[1], despesa_implicita[2]
        valor = float(valor_str.replace(',', '.'))
        descricao = descricao_raw.strip()
        
        desp = {'descricao': descricao, 'valor': valor, 'data': agora}
        despesas.append(desp)
        registrar_despesa(desp)
        return Response(f"🧾 Despesa de R${valor:.2f} com '{descricao}' registrada!", status=200, mimetype='text/plain')

    # --- Pagamento de Fiado ---
    elif pagamento:
        cliente_raw, valor_str = pagamento[1], pagamento[2]
        valor = float(valor_str.replace(',', '.'))
        cliente = cliente_raw.strip().capitalize()
        
        pagamentos_fiado.append({'cliente': cliente, 'valor': valor, 'data': agora})
        aplicar_pagamento_fiado(cliente, valor)
        registrar_pagamento({'cliente': cliente, 'valor': valor, 'data': agora})
        return Response(f"✅ {cliente} pagou R${valor:.2f} de fiado!", status=200, mimetype='text/plain')

    # --- Relatórios ---
    elif texto in ['relatorio diario', 'relatório diário']:
        return Response(gerar_relatorio('diario'), status=200, mimetype='text/plain')
    elif texto in ['relatorio semanal', 'relatório semanal']:
        return Response(gerar_relatorio('semanal'), status=200, mimetype='text/plain')
    elif texto in ['relatorio mensal', 'relatório mensal']:
        return Response(gerar_relatorio('mensal'), status=200, mimetype='text/plain')
    elif texto in ['relatorio fiado', 'relatório fiado']:
        return Response(gerar_relatorio_fiado(), status=200, mimetype='text/plain')

    # --- Venda por Valor ---
    elif venda_valor:
        valor_str, produto_raw = venda_valor[1], venda_valor[2]
        # Correção: O cliente é o grupo 3 no regex venda_valor
        fiado = venda_valor[3] is not None
        cliente = venda_valor[3] if fiado else None # Corrigido de venda_valor[4] para venda_valor[3]
        
        # Para depuração:
        print(f"DEBUG (Venda por Valor): Grupos capturados: {venda_valor.groups()}")
        print(f"DEBUG (Venda por Valor): Produto Raw: '{produto_raw}', Fiado: {fiado}, Cliente: '{cliente}'")

        valor = float(valor_str.replace(',', '.'))
        
        # Obter a forma base do produto usando o mapeamento de aliases
        produto_base = produtos_alias.get(produto_raw, None)

        if produto_base and produto_base in produtos_info:
            preco = produtos_info[produto_base]['preco']
            custo = produtos_info[produto_base]['custo']
            # Calcular quantidade baseada no valor total e preço unitário
            qtd = valor / preco
            custo_total = qtd * custo

            venda = {'produto': produto_base, 'quantidade': qtd, 'valor': valor, 'custo_total': custo_total,
                     'fiado': fiado, 'cliente': cliente, 'data': agora}

            produto_display_name = get_product_display_name(qtd, produto_base)

            if fiado:
                fiados.append(venda)
                registrar_fiado(venda)
                return Response(f"✅ Venda fiado de R${valor:.2f} de {produto_display_name} para {cliente.capitalize()} registrada!", status=200, mimetype='text/plain')
            else:
                vendas.append(venda)
                registrar_venda(venda)
                return Response(f"✅ Venda de R${valor:.2f} de {produto_display_name} registrada!", status=200, mimetype='text/plain')
        else:
            return Response(f"❌ Produto '{produto_raw}' não cadastrado. Tente cadastrar ou usar um produto existente.", status=200, mimetype='text/plain')

    # --- Venda por Quantidade ---
    elif venda_qtd:
        qtd_str, produto_raw = venda_qtd[1], venda_qtd[2]
        # Correção: O cliente é o grupo 3 no regex venda_qtd
        fiado = venda_qtd[3] is not None
        cliente = venda_qtd[3] if fiado else None # Corrigido de venda_qtd[4] para venda_qtd[3]
        
        # Para depuração:
        print(f"DEBUG (Venda por Quantidade): Grupos capturados: {venda_qtd.groups()}")
        print(f"DEBUG (Venda por Quantidade): Qtd: '{qtd_str}', Produto Raw: '{produto_raw}', Fiado: {fiado}, Cliente: '{cliente}'")

        qtd = int(qtd_str)
        
        # Obter a forma base do produto usando o mapeamento de aliases
        produto_base = produtos_alias.get(produto_raw, None)

        if produto_base and produto_base in produtos_info:
            preco = produtos_info[produto_base]['preco']
            custo = produtos_info[produto_base]['custo']
            total = qtd * preco
            custo_total = qtd * custo

            venda = {'produto': produto_base, 'quantidade': qtd, 'valor': total, 'custo_total': custo_total,
                     'fiado': fiado, 'cliente': cliente, 'data': agora}

            produto_display_name = get_product_display_name(qtd, produto_base)

            if fiado:
                fiados.append(venda)
                registrar_fiado(venda)
                return Response(f"✅ Venda fiado de {qtd} {produto_display_name} para {cliente.capitalize()} registrada!", status=200, mimetype='text/plain')
            else:
                vendas.append(venda)
                registrar_venda(venda)
                return Response(f"✅ Venda de {qtd} {produto_display_name} registrada!", status=200, mimetype='text/plain')
        else:
            return Response(f"❌ Produto '{produto_raw}' não cadastrado. Tente cadastrar ou usar um produto existente.", status=200, mimetype='text/plain')


    # --- Mensagem de Ajuda Padrão ---
    resposta = (
        "Olá, Seu Jorge! Eu não entendi sua mensagem. Por favor, use um dos formatos abaixo:\n"
        "🛒 Vendas: 'Vendi 2 pão', 'Vendi 30,50 reais de leite', 'Vendi 3 cafés fiado para João'\n"
        "📉 Despesas: 'Gastei 15 com água', 'Gastei 50,25 em material de limpeza', '100 reais com água'\n"
        "💰 Pagamentos: 'João pagou 10 reais'\n"
        "📊 Relatórios: 'relatório diário', 'relatório semanal', 'relatório mensal', 'relatório fiado'"
    )
    return Response(resposta, status=200, mimetype='text/plain')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
