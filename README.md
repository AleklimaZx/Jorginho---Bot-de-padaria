# 
 Bot de Controle Financeiro por WhatsApp
 Este é um bot simples, criado em **Python com Flask**, para ajudar a gerenciar as finanças de um
 pequeno negócio diretamente pelo WhatsApp.
 Ele permite registrar **vendas, despesas, fiados e pagamentos** de forma rápida, além de gerar
 relatórios **diários, semanais e mensais**.--
## 
 Funcionalidades- **Registro de Vendas**: Registre vendas por quantidade ou valor total. - **Controle de Fiado**:
 Adicione fiados para clientes e marque os pagamentos realizados. - **Registro de Despesas**:
 Anote gastos para ter um controle completo do fluxo de caixa. - **Relatórios Automáticos**: Gere
 relatórios de vendas, custos, lucros e despesas de forma organizada. - **Integração com Google
 Sheets**: Todos os dados são salvos automaticamente em planilhas do Google.--
## 
 Como Usar
 Basta enviar mensagens no WhatsApp com os seguintes comandos:
 | Categoria | Comando | Exemplo | |-----------|---------|---------| | Venda por Quantidade | `vendi ` |
 `vendi 3 pães` | | Venda por Valor | `vendi reais de ` | `vendi 20 reais de café` | | Fiado | `vendi fiado
 para ` | `vendi 5 cafés fiado para Maria` | | Despesa | `gastei com ` | `gastei 15.50 com água` | |
 Despesa Rápida | ` reais com ` | `100 reais com aluguel` | | Pagamento de Fiado | ` pagou reais` |
 `João pagou 50 reais` | | Relatório Diário | `relatório diário` | - | | Relatório Semanal | `relatório
 semanal` | - | | Relatório Mensal | `relatório mensal` | - | | Relatório de Fiado | `relatório fiado` | - |--
## 
 Instalação e Configuração
 ### Pré-requisitos - Uma conta **Twilio** com o **Sandbox para WhatsApp** configurado. - Uma
 conta **Google** com acesso ao **Google Sheets**. - **Python 3.7+** instalado.
 ### 1. Clonar o Repositório ```bash git clone
 https://github.com/seu-usuario/nome-do-seu-repositorio.git cd nome-do-seu-repositorio ```
 ### 2. Configurar o Ambiente ```bash python -m venv venv source venv/bin/activate # No Windows:
 venv\Scripts\activate pip install -r requirements.txt ```
 ### 3. Google Sheets 1. **Crie as Planilhas**: no Google Sheets com abas `Vendas`, `Despesas`,
 `Fiado` e `Pagamentos Fiado`. 2. **Habilite a API**: no [Google Cloud
 Console](https://console.cloud.google.com). 3. **Crie Credenciais**: gere um `credentials.json` e
 salve na pasta raiz. 4. **Compartilhe a Planilha**: com o e-mail da conta de serviço (presente no
 `credentials.json`).
 ### 4. Executar o Bot ```bash python app.py ``` O bot ficará disponível em **http://localhost:5001**.
 > Para expor seu servidor, use o [ngrok](https://ngrok.com/) e aponte para o Twilio.
 ### 5. Configurar no Twilio 1. Vá em **Programmable Messaging > WhatsApp > Sandbox**. 2. No
 campo **WHEN A MESSAGE COMES IN**, cole a URL pública do ngrok adicionando
 `/mensagem`. - Exemplo: `https://seu-tunnel.ngrok.io/mensagem` 3. Clique em **Save**.
--
## 
 Contribuições Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*
 com suas sugestões.--
## 
 Licença Este projeto está licenciado sob a **Licença MIT**
