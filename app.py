from flask import Flask, request, Response
from datetime import datetime, timedelta
import re

app = Flask(__name__)

vendas = []
despesas = []
pagamentos_fiado = []

produtos = {
    'pao': {'preco': 1.50, 'custo': 0.60},
    'leite': {'preco': 3.00, 'custo': 1.50},
    'cafe': {'preco': 2.50, 'custo': 1.00},
}

despesas_permitidas = ['agua', 'água', 'luz', 'telefone', 'internet', 'aluguel']

def formatar_venda(v):
    fiado_str = f" - Fiado para {v['cliente'].capitalize()}" if v['fiado'] else ""
    data = datetime.strftime(v['data'], "%d/%m")
    return f"[{data}] {v['produto'].capitalize()}: R${v['valor']:.2f} (Custo: R${v['custo_total']:.2f}){fiado_str}"

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

    vendas_periodo = [v for v in vendas if v['data'].date() >= data_limite and not v['fiado']]
    despesas_periodo = [d for d in despesas if d['data'].date() >= data_limite]

    total_vendas = sum(v['valor'] for v in vendas_periodo)
    total_custo = sum(v['custo_total'] for v in vendas_periodo)
    total_despesas = sum(d['valor'] for d in despesas_periodo)
    lucro = total_vendas - total_custo
    saldo = lucro - total_despesas

    relatorio = f"\n📊 *Relatório {periodo.capitalize()}*\n\n"
    relatorio += "*Vendas à vista:*\n"
    relatorio += "\n".join(formatar_venda(v) for v in vendas_periodo) or "Nenhuma"
    relatorio += f"\n\n💵 Total Vendas: R${total_vendas:.2f}\n"
    relatorio += f"💸 Custos: R${total_custo:.2f}\n"
    relatorio += f"📈 Lucro: R${lucro:.2f}\n"
    relatorio += f"📉 Despesas: R${total_despesas:.2f}\n"
    relatorio += f"💰 Saldo Final: R${saldo:.2f}"
    return relatorio

@app.route('/mensagem', methods=['POST'])
def mensagem():
    texto = request.form.get('Body', '').strip().lower()
    agora = datetime.now()

    # Regex
    venda_qtd = re.match(r'vendi (\d+) (\w+)', texto)
    venda_valor = re.match(r'vendi (\d+(?:\.\d+)?) reais de (\w+)', texto)

    fiado_qtd = re.match(r'vendi (\d+) (\w+) fiado para (.+)', texto)
    fiado_valor = re.match(r'vendi (\d+(?:\.\d+)?) reais de (\w+) fiado para (.+)', texto)

    pagamento = re.match(r'(\w+) pagou (\d+(?:\.\d+)?)( reais)?', texto)
    despesa = re.match(r'gastei (\d+(?:\.\d+)?) com ([\wçãáéíóúâêô]+)', texto)

    if texto in ['relatorio diario', 'relatório diário']:
        return Response(gerar_relatorio('diario'), status=200, mimetype='text/plain')

    elif texto in ['relatorio semanal', 'relatório semanal']:
        return Response(gerar_relatorio('semanal'), status=200, mimetype='text/plain')

    elif texto in ['relatorio mensal', 'relatório mensal']:
        return Response(gerar_relatorio('mensal'), status=200, mimetype='text/plain')

    elif texto in ['relatorio fiado', 'relatório fiado']:
        relatorio = "\n📄 *Controle de Fiado*\n\n"
        por_cliente = {}

        for v in vendas:
            if v['fiado']:
                por_cliente[v['cliente']] = por_cliente.get(v['cliente'], 0) + v['valor']

        for p in pagamentos_fiado:
            por_cliente[p['cliente']] = por_cliente.get(p['cliente'], 0) - p['valor']

        total_fiado = sum(valor for valor in por_cliente.values())

        for cliente, valor in por_cliente.items():
            relatorio += f"{cliente.capitalize()}: R${valor:.2f}\n"

        relatorio += f"\n🔢 Total em aberto: R${total_fiado:.2f}"
        return Response(relatorio, status=200, mimetype='text/plain')

    elif venda_valor:
        valor, produto = float(venda_valor[1]), venda_valor[2]
        if produto in produtos:
            preco = produtos[produto]['preco']
            custo = produtos[produto]['custo']
            qtd = valor / preco
            custo_total = qtd * custo
            vendas.append({'produto': produto, 'quantidade': qtd, 'valor': valor, 'custo_total': custo_total, 'fiado': False, 'cliente': None, 'data': agora})
            resposta = f"✅ Venda de R${valor:.2f} de {produto} registrada com sucesso!"
            return Response(resposta, status=200, mimetype='text/plain')
        return Response(f"❌ Produto '{produto}' não cadastrado.", status=200, mimetype='text/plain')

    elif venda_qtd and not fiado_qtd:
        qtd, produto = int(venda_qtd[1]), venda_qtd[2]
        if produto in produtos:
            preco = produtos[produto]['preco']
            custo = produtos[produto]['custo']
            total = qtd * preco
            vendas.append({'produto': produto, 'quantidade': qtd, 'valor': total, 'custo_total': qtd * custo, 'fiado': False, 'cliente': None, 'data': agora})
            return Response(f"✅ Venda de {qtd} {produto}(s) registrada com sucesso!", status=200, mimetype='text/plain')
        return Response(f"❌ Produto '{produto}' não cadastrado.", status=200, mimetype='text/plain')

    elif fiado_qtd:
        qtd, produto, cliente = int(fiado_qtd[1]), fiado_qtd[2], fiado_qtd[3]
        if produto in produtos:
            preco = produtos[produto]['preco']
            custo = produtos[produto]['custo']
            total = qtd * preco
            vendas.append({'produto': produto, 'quantidade': qtd, 'valor': total, 'custo_total': qtd * custo, 'fiado': True, 'cliente': cliente, 'data': agora})
            return Response(f"📌 Venda fiado de {qtd} {produto}(s) para {cliente.capitalize()} registrada.", status=200, mimetype='text/plain')
        return Response(f"❌ Produto '{produto}' não cadastrado.", status=200, mimetype='text/plain')

    elif fiado_valor:
        valor, produto, cliente = float(fiado_valor[1]), fiado_valor[2], fiado_valor[3]
        if produto in produtos:
            preco = produtos[produto]['preco']
            custo = produtos[produto]['custo']
            qtd = valor / preco
            custo_total = qtd * custo
            vendas.append({'produto': produto, 'quantidade': qtd, 'valor': valor, 'custo_total': custo_total, 'fiado': True, 'cliente': cliente, 'data': agora})
            return Response(f"📌 Venda fiado de R${valor:.2f} de {produto} para {cliente.capitalize()} registrada.", status=200, mimetype='text/plain')
        return Response(f"❌ Produto '{produto}' não cadastrado.", status=200, mimetype='text/plain')

    elif pagamento:
        cliente, valor = pagamento[1], float(pagamento[2])
        pagamentos_fiado.append({'cliente': cliente, 'valor': valor})
        return Response(f"💰 Pagamento de R${valor:.2f} registrado para {cliente.capitalize()}.", status=200, mimetype='text/plain')

    elif despesa:
        valor, tipo = float(despesa[1]), despesa[2]
        if tipo in despesas_permitidas:
            despesas.append({'tipo': tipo, 'valor': valor, 'data': agora})
            return Response(f"✅ Despesa registrada de R${valor:.2f} com {tipo}.", status=200, mimetype='text/plain')
        return Response("❌ Tipo de despesa não permitida.", status=200, mimetype='text/plain')

    # Ajuda
    resposta = (
        "Olá, Seu Jorge! Exemplos:\n"
        "🛒 Vendas: 'Vendi 2 pao', 'Vendi 30 reais de leite'\n"
        "📌 Fiado: 'Vendi 3 cafe fiado para João'\n"
        "📉 Despesas: 'Gastei 15 com água'\n"
        "💰 Pagamentos: 'João pagou 10 reais'\n"
        "📊 Relatórios: 'relatório diário', 'relatório semanal', 'relatório mensal', 'relatório fiado'"
    )
    return Response(resposta, status=200, mimetype='text/plain')

if __name__ == '__main__':
    app.run(port=5001, debug=True)












